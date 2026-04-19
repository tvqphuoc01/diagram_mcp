# Daily LookerStudio → Google Sheets Pipeline — Setup Guide

## 1. Install Python dependencies

```bash
pip install browser-cookie3 playwright pandas requests
playwright install chromium
```

> Python 3.10+ is required (the code uses `list[dict]` built-in generics).

---

## 2. Google Sheets authentication — no credentials file needed

Authentication uses **the same Chrome cookies** that browser_cookie3 already
reads for LookerStudio. The pipeline extracts your `SAPISID` cookie and builds
a `SAPISIDHASH` token accepted by the Google Sheets API v4.

**Requirements:**
- Google Chrome is installed and you are logged into your Google account in Chrome.
- Chrome is **closed** when the pipeline runs (open Chrome locks the Cookies DB on macOS).
- The Google account you are logged in with must have **Editor** access to the target Sheets.

No service account, no OAuth consent screen, no credentials file required.

---

## 3. Fill in the Sheet URLs

Open `looker_config.py` and replace the two empty strings:

```python
SHEET1_URL = "https://docs.google.com/spreadsheets/d/<YOUR_SHEET1_ID>/edit"
SHEET2_URL = "https://docs.google.com/spreadsheets/d/<YOUR_SHEET2_ID>/edit"
```

The sheet must already exist. The pipeline will create the named worksheet tabs
(`Raw Export` / `MTD Mirror`) if they are missing.

If using a service account, share each spreadsheet with the service account
email (Editor permission).

---

## 4. Chrome profile & cookies

The pipeline reads your Chrome auth cookies so it can access LookerStudio
without an interactive login. Make sure:

- Google Chrome is **installed** on the machine running the script.
- You are **logged into your Google account** in Chrome.
- Chrome is **closed** when the pipeline runs (an open Chrome locks the Cookies
  database on macOS).

The default profile path in `looker_config.py` is macOS:

```
~/Library/Application Support/Google/Chrome/Default
```

On **Linux**, change it to:

```
~/.config/google-chrome/Default
```

On **Windows** (WSL), change it to (using the Windows-side path via `/mnt/c`):

```
/mnt/c/Users/<YourName>/AppData/Local/Google/Chrome/User Data/Default
```

---

## 5. Run the pipeline manually

```bash
cd "/path/to/Daily Data Raw Update"
export LOOKER_REPORT_URL="https://datastudio.google.com/reporting/<YOUR_REPORT_ID>/page/<PAGE_ID>"
python3 looker_to_sheets.py
```

Successful output ends with:

```
2025-01-15T11:00:05|INFO|DONE|Pipeline completed successfully (1423 rows)
```

Check `pipeline.log` for the machine-parseable record:

```
2025-01-15T11:00:05|SUCCESS|rows=1423|error=
```

---

## 6. Schedule with cron (11:00 AM daily)

```bash
crontab -e
```

Add this line (adjust paths):

```cron
0 11 * * * LOOKER_REPORT_URL="https://datastudio.google.com/reporting/<YOUR_REPORT_ID>/page/<PAGE_ID>" \
  /usr/bin/python3 "/path/to/Daily Data Raw Update/looker_to_sheets.py" \
  >> "/path/to/Daily Data Raw Update/cron.log" 2>&1
```

> On macOS, use `launchd` instead of cron, or grant cron **Full Disk Access**
> in System Settings → Privacy & Security so it can read the Chrome profile.

---

## 7. Known risks & mitigations

| Risk | Symptom | Mitigation |
|---|---|---|
| Chrome profile locked | `sqlite3.OperationalError: database is locked` | Close Chrome before the scheduled run; or copy the Cookies file to a temp location before reading |
| LookerStudio UI selector drift | `RuntimeError: Could not open … menu` | Every selector has a text-based fallback; update the CSS selectors in `looker_to_sheets.py` after a UI change |
| Download path wrong / full disk | `TimeoutError: No new CSV` | Verify `DOWNLOAD_DIR` in config; ensure free space; check browser download permissions |
| Google session expiry | Sheets API returns 401/403 | Log back into Google in Chrome to refresh the session cookies, then re-run |
| Column count change in report | `ValueError: Column count mismatch` | Update `EXPECTED_COLUMNS` in `looker_config.py` after confirming the new schema |
| LookerStudio login session expired | Page loads login screen instead of report | Log back into Google in Chrome and verify the session cookie is fresh |
| macOS cron Full Disk Access denied | `PermissionError` on Cookies file | Grant Full Disk Access to `/usr/sbin/cron` in System Settings → Privacy & Security |
