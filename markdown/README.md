# IPL Fantasy Stats Scraper

A Python web scraper that extracts player statistics from the official IPL Fantasy website (fantasy.iplt20.com). The project includes **two versions**: one using **Selenium** and one using **Playwright**.

## Features

- 📱 **Mobile OTP Authentication** - Login with mobile number and OTP
- 💾 **Session Management** - Saves cookies to avoid repeated logins
- 🗄️ **SQLite Database** - Stores scraped data in local database with timestamps
- 🔍 **Query Tools** - View and analyze stored statistics
- 🔄 **Two Implementations** - Choose between Selenium or Playwright

## Prerequisites

- Python 3.7+
- Google Chrome installed (for Selenium version)
- Active mobile number for OTP login
- Internet connection

## Project Structure

```
new_app/
├── ipl_scraper_selenium.py          # Selenium version
├── ipl_scraper.py                   # Playwright version
├── database.py                      # SQLite database manager
├── view_stats.py                    # Query tool to view database
├── setup_chromedriver.py            # ChromeDriver download helper (Selenium)
├── requirements_selenium.txt        # Selenium dependencies
├── requirements.txt                 # Playwright dependencies
├── ipl_stats.db                     # SQLite database (auto-created)
└── README.md                        # This file
```

## Installation

### Option 1: Selenium Version

```bash
# 1. Install dependencies
pip install -r requirements_selenium.txt

# 2. Download ChromeDriver (matches your Chrome version)
python setup_chromedriver.py

# 3. Run the scraper
python ipl_scraper_selenium.py 9876543210
```

### Option 2: Playwright Version

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Run the scraper
python ipl_scraper.py 9876543210
```

## Usage

Both versions use the same command-line syntax:

```bash
python ipl_scraper_selenium.py <mobile_number>
# OR
python ipl_scraper.py <mobile_number>
```

**Example:**
```bash
python ipl_scraper_selenium.py 9876543210
```

### What Happens When You Run It

1. **Browser Opens** - Chrome/Chromium launches automatically
2. **Session Check** - Script checks if you're already logged in
3. **Login (if needed)**:
   - Navigates to login page
   - Enters your mobile number
   - Sends OTP to your phone
   - Waits for you to enter OTP in terminal
   - Auto-submits and completes login
4. **Data Extraction** - Scrapes player stats (name, team, credits, points)
5. **Database Save** - Stores data in `ipl_stats.db` with timestamp
6. **Browser Closes** - Automatically closes browser

### Output Files

**Both Versions:**
- `ipl_stats.db` - SQLite database with player statistics and timestamps
- `session_cookies.json` (Selenium) or `session.json` (Playwright) - Saved login session
- `login_error.png` - Screenshot if login fails (Selenium only)
- `scraping_error.png` or `scraping_error_playwright.png` - Screenshot if scraping fails
- `stats_page_loaded.png` or `stats_page_loaded_playwright.png` - Debug screenshots

### Viewing Database

After scraping, view your data using the provided query tool:

```bash
# View all players (ordered by points)
python view_stats.py

# View top 10 players
python view_stats.py --limit 10

# View specific team
python view_stats.py --team RCB

# Search for player
python view_stats.py --player "Virat"

# Show database summary
python view_stats.py --summary

# Show team statistics
python view_stats.py --teams
```

**Database Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `player_name` | TEXT | Player's full name |
| `team` | TEXT | Team abbreviation (RCB, SRH, etc.) |
| `credits` | REAL | Fantasy value/price |
| `total_points` | INTEGER | Season fantasy points |
| `scraped_at` | TIMESTAMP | When data was scraped |

## Comparison: Selenium vs Playwright

| Feature | Selenium | Playwright |
|---------|----------|------------|
| **Setup** | Manual ChromeDriver download | Auto-manages browsers |
| **Browser** | Uses system Chrome | Downloads own Chromium |
| **Speed** | Slightly slower | Faster |
| **Stability** | Very stable | Very stable |
| **Corporate Env** | May need ChromeDriver approval | May need Chromium download approval |
| **File Size** | ~10 MB (ChromeDriver) | ~300 MB (Chromium) |
| **Recommended For** | Corporate laptops | Personal machines |

## Configuration

### Increase Wait Times

If the website is slow, you can increase wait times in the code:

**Selenium version** (`ipl_scraper_selenium.py`):
```python
# Line 124: After loading login page
time.sleep(10)  # Increase to 15 or 20 if needed
```

**Playwright version** (`ipl_scraper.py`):
```python
# Line 114: After loading login page
time.sleep(10)  # Increase to 15 or 20 if needed
```

### Change Output Filename

**Selenium version** (`ipl_scraper_selenium.py`):
```python
# Line 254
def save_to_excel(self, data, filename="ipl_stats.xlsx"):
```

**Playwright version** (`ipl_scraper.py`):
```python
# Line 254
def save_to_excel(self, data, filename="ipl_stats_playwright.xlsx"):
```

## Troubleshooting

### Error: "chromedriver.exe not found" (Selenium)

**Solution:**
```bash
python setup_chromedriver.py
```

### Error: "Chrome instance exited" (Selenium)

**Cause:** ChromeDriver version doesn't match Chrome version

**Solution:**
1. Delete `chromedriver.exe`
2. Run `python setup_chromedriver.py` again

### Error: "Browser executable not found" (Playwright)

**Solution:**
```bash
playwright install chromium
```

### OTP Not Received

1. Check your mobile number is correct
2. Wait 30-60 seconds for OTP
3. Request OTP again if needed
4. Check mobile network connection

### "No data extracted"

1. Check if you're logged in (delete session files and retry)
2. Website structure may have changed
3. Check screenshot files for debugging
4. Increase wait times in the code

## Session Management

Both versions save login sessions to avoid repeated OTP logins:

**To force fresh login:**
```bash
# Selenium
rm session_cookies.json

# Playwright
rm session.json
```

Sessions typically last 24-48 hours.

## Data Fields Stored

The scrapers extract and store the following fields in SQLite database:

| Column | Description | Example |
|--------|-------------|---------|
| **Player Name** | Full name | Rajat Patidar |
| **Team** | Team abbreviation | RCB |
| **Credits** | Fantasy value | 9 |
| **Total Points** | Season points | 380 |
| **Scraped At** | Timestamp when scraped | 2026-04-17 14:30:25 |

## Legal & Ethical Considerations

⚠️ **Important:**
- This script is for **educational purposes only**
- Ensure you comply with the website's Terms of Service
- Do not overload the website with excessive requests
- Use responsibly and ethically

## Support

If you encounter issues:

1. Check the screenshots generated (e.g., `login_error.png`)
2. Review the terminal output for error messages
3. Verify all prerequisites are installed
4. Try increasing wait times if website is slow
5. Delete session files and try fresh login

## Author

Created by: Claude Code
Date: 2026-04-16

## License

This project is provided as-is for educational purposes.
