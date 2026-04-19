# Daily LookerStudio → Google Sheets Pipeline — Setup Guide

## 1. Install Python dependencies

```bash
pip install browser-cookie3 playwright pandas gspread
playwright install chromium
```

> Python 3.10+ is required (the code uses `list[dict]` built-in generics).

---

## 2. Google Sheets credentials

Choose **one** of the two authentication methods below.

### Option A — Service Account (recommended for cron / servers)

1. Open [Google Cloud Console](https://console.cloud.google.com/) → **IAM & Admin → Service Accounts**.
2. Create a service account (e.g. `looker-pipeline@your-project.iam.gserviceaccount.com`).
3. Grant it **Editor** role on the project (or share each target Sheet with its email directly).
4. Create a JSON key: **Keys → Add Key → Create new key → JSON**. Download the file.
5. Place the file somewhere safe, e.g. `~/.config/gspread/service_account.json`.
6. Export the path before running:

   ```bash
   export GSPREAD_CREDS_PATH=~/.config/gspread/service_account.json
   ```

### Option B — OAuth2 saved token (for local/desktop use)

1. In Google Cloud Console enable the **Google Sheets API** and **Google Drive API**.
2. Create an **OAuth 2.0 Desktop** client ID and download `credentials.json`.
3. Run the one-time flow:

   ```bash
   python3 - <<'EOF'
   import gspread
   gc = gspread.oauth(credentials_filename="credentials.json")
   print("Authorised. Token saved to ~/.config/gspread/")
   EOF
   ```

4. This saves a token file to `~/.config/gspread/authorized_user.json`.
5. Export the path:

   ```bash
   export GSPREAD_CREDS_PATH=~/.config/gspread/authorized_user.json
   ```

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
export GSPREAD_CREDS_PATH=~/.config/gspread/service_account.json
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
0 11 * * * GSPREAD_CREDS_PATH=~/.config/gspread/service_account.json \
  LOOKER_REPORT_URL="https://datastudio.google.com/reporting/<YOUR_REPORT_ID>/page/<PAGE_ID>" \
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
| Google credentials expiry | `gspread.exceptions.APIError: 401` | Service account keys don't expire by default; OAuth2 tokens auto-refresh if the refresh token is valid — re-run the OAuth flow if it fails |
| Column count change in report | `ValueError: Column count mismatch` | Update `EXPECTED_COLUMNS` in `looker_config.py` after confirming the new schema |
| LookerStudio login session expired | Page loads login screen instead of report | Log back into Google in Chrome and verify the session cookie is fresh |
| macOS cron Full Disk Access denied | `PermissionError` on Cookies file | Grant Full Disk Access to `/usr/sbin/cron` in System Settings → Privacy & Security |
