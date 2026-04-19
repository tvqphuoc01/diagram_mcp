"""
LookerStudio → Google Sheets daily pipeline.
All tuneable values live in looker_config.py.
Credentials path is read from env var GSPREAD_CREDS_PATH.
"""

import os
import re
import sys
import time
import glob
import logging
import datetime
import pathlib

import browser_cookie3
import pandas as pd
import gspread
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

import looker_config as cfg


# ---------------------------------------------------------------------------
# Logging — machine-parseable, pipe-delimited
# ---------------------------------------------------------------------------

def _build_logger() -> logging.Logger:
    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s",
                            datefmt="%Y-%m-%dT%H:%M:%S")
    # file handler
    fh = logging.FileHandler(cfg.LOG_FILE)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    # stdout handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = _build_logger()


# ---------------------------------------------------------------------------
# Step A — Cookie extraction
# ---------------------------------------------------------------------------

def extract_cookies() -> list[dict]:
    """Read Chrome auth cookies for Google domains without interactive login."""
    profile_path = pathlib.Path(cfg.CHROME_PROFILE_PATH).expanduser()
    log.info("STEP_A|Extracting cookies from %s", profile_path)

    raw_cookies: list = []
    try:
        raw_cookies = list(browser_cookie3.chrome(
            cookie_file=str(profile_path / "Cookies"),
            domain_name=".google.com",
        ))
    except Exception as exc:
        log.warning("STEP_A|browser_cookie3 raised %s — trying without explicit path", exc)
        raw_cookies = list(browser_cookie3.chrome(domain_name=".google.com"))

    # Filter to only the configured domains
    wanted = set(cfg.COOKIE_DOMAINS)
    cookies = [
        {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "secure": bool(c.secure),
            "http_only": bool(getattr(c, "http_only", False)),
            "same_site": "None",
        }
        for c in raw_cookies
        if any(c.domain.endswith(d.lstrip(".")) for d in wanted)
    ]
    log.info("STEP_A|Found %d matching cookies", len(cookies))
    return cookies


# ---------------------------------------------------------------------------
# Step B — Headless Playwright: load report
# ---------------------------------------------------------------------------

def _wait_for_report(page) -> None:
    """Wait until the LookerStudio canvas is fully rendered."""
    try:
        page.wait_for_selector("div[data-testid='canvas-container']", timeout=30_000)
    except PWTimeoutError:
        # text-based fallback: wait until page body contains report content signal
        log.warning("STEP_B|Primary selector timed out — trying text fallback")
        page.wait_for_function(
            "() => document.body.innerText.includes('Gift tracking')",
            timeout=30_000,
        )


def launch_browser_and_load_report(playwright, cookies: list[dict]):
    """Launch headless Chromium, inject cookies, navigate to report."""
    log.info("STEP_B|Launching headless Chromium")
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=cfg.CHROMIUM_EXECUTABLE_PATH or None,
    )
    context = browser.new_context(accept_downloads=True)

    context.add_cookies(cookies)
    page = context.new_page()

    log.info("STEP_B|Navigating to %s", cfg.LOOKER_REPORT_URL)
    page.goto(cfg.LOOKER_REPORT_URL, wait_until="networkidle", timeout=60_000)
    _wait_for_report(page)
    log.info("STEP_B|Report loaded")
    return browser, context, page


# ---------------------------------------------------------------------------
# Step C — Date filter
# ---------------------------------------------------------------------------

def _click_by_css_or_text(page, css_selector: str, text: str) -> bool:
    """Try CSS selector first; fall back to clicking by visible text."""
    try:
        el = page.query_selector(css_selector)
        if el:
            el.click()
            return True
    except Exception:
        pass
    # text fallback
    try:
        page.get_by_text(text, exact=False).first.click()
        return True
    except Exception:
        return False


def apply_date_filter(page) -> None:
    """Set date range to 1st of current month → today."""
    today = datetime.date.today()
    start = today.replace(day=1)
    log.info("STEP_C|Applying date filter %s → %s", start, today)

    # Open the date range picker
    opened = _click_by_css_or_text(
        page,
        "div[data-testid='date-range-control'] button",
        "Date range",
    )
    if not opened:
        raise RuntimeError("STEP_C|Could not open date range picker")

    page.wait_for_timeout(800)

    def _fill_date_field(css: str, label: str, value: str) -> None:
        try:
            field = page.query_selector(css)
            if field:
                field.triple_click()
                field.type(value)
                return
        except Exception:
            pass
        # text fallback: find input near label text
        page.get_by_label(label, exact=False).first.fill(value)

    date_fmt = "%m/%d/%Y"
    _fill_date_field("input[aria-label='Start date']", "Start date", start.strftime(date_fmt))
    _fill_date_field("input[aria-label='End date']",   "End date",   today.strftime(date_fmt))

    # Click Apply
    applied = _click_by_css_or_text(page, "button[data-testid='apply-btn']", "Apply")
    if not applied:
        raise RuntimeError("STEP_C|Could not click Apply on date picker")

    page.wait_for_timeout(2_000)
    log.info("STEP_C|Date filter applied")


# ---------------------------------------------------------------------------
# Step D — CSV export
# ---------------------------------------------------------------------------

def _poll_for_new_csv(download_dir: pathlib.Path, before: set[str], timeout: float = 15.0) -> str:
    """Poll download_dir until a new .csv appears; return its path."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = set(glob.glob(str(download_dir / "*.csv")))
        new_files = current - before
        if new_files:
            return max(new_files, key=os.path.getmtime)
        time.sleep(0.5)
    raise TimeoutError(f"STEP_D|No new CSV in {download_dir} after {timeout}s")


def export_csv(page, context) -> str:
    """Open ⋮ menu on Gift tracking table, export as CSV, return file path."""
    download_dir = pathlib.Path(cfg.DOWNLOAD_DIR).expanduser()
    before = set(glob.glob(str(download_dir / "*.csv")))

    log.info("STEP_D|Opening Gift tracking table context menu")

    # Locate the table header or container that matches "Gift tracking"
    try:
        table_header = page.get_by_text("Gift tracking", exact=False).first
        table_header.hover()
        page.wait_for_timeout(400)
    except Exception as exc:
        log.warning("STEP_D|Could not hover table header: %s", exc)

    # Click the three-dot (⋮) menu — CSS first, text fallback
    menu_opened = _click_by_css_or_text(
        page,
        "button[aria-label='More options'], button[data-testid='widget-menu-button']",
        "More options",
    )
    if not menu_opened:
        # last-resort: find any ⋮ button near Gift tracking text
        page.keyboard.press("Escape")
        raise RuntimeError("STEP_D|Could not open Gift tracking ⋮ menu")

    page.wait_for_timeout(500)

    # Click Export
    export_clicked = _click_by_css_or_text(page, "[data-testid='export-option']", "Export")
    if not export_clicked:
        raise RuntimeError("STEP_D|Could not click Export menu item")

    page.wait_for_timeout(500)

    # Choose CSV format if a dialog appears
    try:
        csv_radio = page.query_selector("input[value='CSV'], input[aria-label='CSV']")
        if csv_radio:
            csv_radio.click()
    except Exception:
        _click_by_css_or_text(page, "label[for*='csv']", "CSV")

    page.wait_for_timeout(300)

    # Click the Export / Download button inside the dialog
    with context.expect_download(timeout=20_000) as dl_info:
        _click_by_css_or_text(page, "button[data-testid='export-download-btn']", "Export")

    download = dl_info.value
    save_path = str(download_dir / download.suggested_filename)
    download.save_as(save_path)
    log.info("STEP_D|CSV downloaded to %s", save_path)
    return save_path


# ---------------------------------------------------------------------------
# Step E — Parse + validate
# ---------------------------------------------------------------------------

def parse_and_validate(csv_path: str) -> pd.DataFrame:
    log.info("STEP_E|Parsing %s", csv_path)
    df = pd.read_csv(csv_path)
    if df.shape[1] != cfg.EXPECTED_COLUMNS:
        raise ValueError(
            f"STEP_E|Column count mismatch: expected {cfg.EXPECTED_COLUMNS}, "
            f"got {df.shape[1]}. Columns: {list(df.columns)}"
        )
    log.info("STEP_E|Validated — %d rows × %d cols", len(df), df.shape[1])
    return df


# ---------------------------------------------------------------------------
# Step F — Write to Google Sheets
# ---------------------------------------------------------------------------

def _open_sheet(gc: gspread.Client, url: str, sheet_name: str) -> gspread.Worksheet:
    spreadsheet = gc.open_by_url(url)
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=5000, cols=50)


def write_to_sheets(df: pd.DataFrame) -> None:
    creds_path = os.environ.get("GSPREAD_CREDS_PATH", "")
    if not creds_path:
        raise EnvironmentError(
            "STEP_F|Environment variable GSPREAD_CREDS_PATH is not set"
        )

    creds_path = pathlib.Path(creds_path).expanduser()
    log.info("STEP_F|Authenticating gspread from %s", creds_path)

    # Support both service-account JSON and OAuth2 saved token
    if creds_path.suffix == ".json":
        gc = gspread.service_account(filename=str(creds_path))
    else:
        gc = gspread.oauth(credentials_filename=str(creds_path))

    rows = [df.columns.tolist()] + df.astype(str).values.tolist()

    for url, name in [
        (cfg.SHEET1_URL, cfg.SHEET1_NAME),
        (cfg.SHEET2_URL, cfg.SHEET2_NAME),
    ]:
        if not url:
            log.warning("STEP_F|URL for sheet '%s' is empty — skipping", name)
            continue
        ws = _open_sheet(gc, url, name)
        ws.clear()
        ws.update(rows, value_input_option="USER_ENTERED")
        log.info("STEP_F|Wrote %d rows to '%s'", len(df), name)


# ---------------------------------------------------------------------------
# Step G — Structured log entry
# ---------------------------------------------------------------------------

def _log_result(row_count: int, success: bool, error: str = "") -> None:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    status = "SUCCESS" if success else "FAILURE"
    # machine-parseable pipe-delimited record
    with open(cfg.LOG_FILE, "a") as fh:
        fh.write(f"{ts}|{status}|rows={row_count}|error={error}\n")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    row_count = 0
    try:
        cookies = extract_cookies()

        with sync_playwright() as pw:
            browser, context, page = launch_browser_and_load_report(pw, cookies)
            try:
                apply_date_filter(page)
                csv_path = export_csv(page, context)
            finally:
                browser.close()

        df = parse_and_validate(csv_path)
        row_count = len(df)
        write_to_sheets(df)
        _log_result(row_count, success=True)
        log.info("DONE|Pipeline completed successfully (%d rows)", row_count)

    except Exception as exc:
        error_msg = str(exc).replace("\n", " ")
        _log_result(row_count, success=False, error=error_msg)
        log.error("DONE|Pipeline failed: %s", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
