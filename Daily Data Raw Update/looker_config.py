import os
LOOKER_REPORT_URL = os.environ["LOOKER_REPORT_URL"]
CHROME_PROFILE_PATH = "~/Library/Application Support/Google/Chrome/Default"
COOKIE_DOMAINS = [".google.com", "datastudio.google.com"]
SHEET1_NAME = "Raw Export"
SHEET2_NAME = "MTD Mirror"
EXPECTED_COLUMNS = 29
CHROMIUM_EXECUTABLE_PATH = os.environ.get(
    "CHROMIUM_EXECUTABLE_PATH",
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
)
DOWNLOAD_DIR = "~/Downloads"
LOG_FILE = "pipeline.log"
SHEET1_URL = os.environ.get("SHEET1_URL", "")
SHEET2_URL = os.environ.get("SHEET2_URL", "")
