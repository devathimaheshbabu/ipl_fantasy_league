"""
IPL Fantasy Stats Scraper - Selenium Version
=============================================
This script scrapes player statistics from the official IPL Fantasy website.
It uses Selenium WebDriver to automate browser interactions and handles OTP-based login.

Features:
- Mobile OTP authentication
- Session management (saves cookies to avoid repeated logins)
- Automated data extraction from player stats page
- SQLite database storage with timestamps

Author: Claude Code
Date: 2026-04-17
"""

import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess

# Import database module
from database import save_to_database


class IPLStatsScraperSelenium:
    """
    A web scraper class for extracting IPL Fantasy player statistics.

    This class handles:
    - Browser automation using Selenium
    - OTP-based login with mobile number
    - Session persistence using cookies
    - Player stats extraction from the fantasy website
    - Data storage in SQLite database with timestamps
    """

    def __init__(self):
        """
        Initialize the scraper with required URLs and configuration.

        Attributes:
            login_url (str): URL for the login page with OTP
            stats_url (str): URL for the player statistics page
            session_file (str): File path to store session cookies for reuse
            driver (WebDriver): Selenium WebDriver instance (initialized later)
        """
        self.login_url = "https://fantasy.iplt20.com/my11c/static/login.html?ru=/classic/home"
        self.stats_url = "https://fantasy.iplt20.com/classic/stats"
        self.session_file = "session_cookies.json"
        self.driver = None

    def start_browser(self):
        """
        Initialize and configure Chrome browser with Selenium WebDriver.

        This method:
        1. Sets up Chrome options to bypass security restrictions
        2. Configures browser to avoid automation detection
        3. Loads ChromeDriver from local directory
        4. Attempts to restore previous session using saved cookies

        Raises:
            FileNotFoundError: If chromedriver.exe is not found
            Exception: If browser fails to start

        Note:
            Requires chromedriver.exe in the same directory as this script.
            Run setup_chromedriver.py to download it if missing.
        """
        print("Starting Chrome browser...")

        chrome_options = Options()

        # ============================================================
        # Chrome Arguments: Bypass corporate security restrictions
        # ============================================================
        # These arguments help the script work in corporate environments
        # by disabling various security features that might block automation

        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
        chrome_options.add_argument('--disable-software-rasterizer')  # Disable software rendering
        chrome_options.add_argument('--disable-extensions')  # Disable browser extensions
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Hide automation flags
        chrome_options.add_argument('--disable-web-security')  # Disable web security (for CORS)
        chrome_options.add_argument('--allow-running-insecure-content')  # Allow HTTP on HTTPS pages
        chrome_options.add_argument('--ignore-certificate-errors')  # Ignore SSL certificate errors
        chrome_options.add_argument('--remote-debugging-port=9222')  # Enable remote debugging

        # ============================================================
        # Disable Automation Detection
        # ============================================================
        # These settings make Selenium harder to detect by websites
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # ============================================================
        # Set Realistic User Agent
        # ============================================================
        # Makes the browser appear as a regular Chrome browser (not automated)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36')

        # ============================================================
        # ChromeDriver Setup
        # ============================================================
        # Use the local chromedriver.exe that matches Chrome version
        chromedriver_path = Path(__file__).parent / "chromedriver.exe"

        if not chromedriver_path.exists():
            print(f"\nError: chromedriver.exe not found at: {chromedriver_path}")
            print("\nPlease run: python setup_chromedriver.py")
            raise FileNotFoundError("chromedriver.exe not found")

        try:
            # Create Chrome service with logging enabled for debugging
            service = Service(
                str(chromedriver_path),
                log_output='chromedriver.log'  # Logs will be saved to this file
            )
            # Initialize Chrome browser with configured options
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()  # Maximize window for better visibility
        except Exception as e:
            print(f"\nError: Could not start Chrome browser.")
            print(f"Details: {e}")
            print("\nCheck chromedriver.log for detailed error information")
            raise

        # ============================================================
        # Session Restoration
        # ============================================================
        # Try to restore previous session using saved cookies
        # This avoids needing to login with OTP every time
        if Path(self.session_file).exists():
            print("Found saved session...")
            self.driver.get(self.stats_url)  # Navigate to stats page
            self.load_cookies()  # Load saved cookies
            self.driver.refresh()  # Refresh page with cookies

    def save_cookies(self):
        """
        Save browser cookies to a JSON file for session persistence.

        This allows the script to maintain login state between runs,
        avoiding the need to enter OTP every time.

        Cookies are saved to: session_cookies.json
        """
        cookies = self.driver.get_cookies()
        with open(self.session_file, 'w') as f:
            json.dump(cookies, f)
        print("Session cookies saved!")

    def load_cookies(self):
        """
        Load previously saved cookies from JSON file.

        This method:
        1. Reads cookies from session_cookies.json
        2. Converts expiry times to integers (required by Selenium)
        3. Adds each cookie to the current browser session

        Note:
            Silently handles errors if cookie file is corrupted or invalid
        """
        try:
            with open(self.session_file, 'r') as f:
                cookies = json.load(f)

            for cookie in cookies:
                # Selenium requires expiry to be an integer, not float
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)

            print("Session cookies loaded!")
        except Exception as e:
            print(f"Error loading cookies: {e}")

    def is_logged_in(self) -> bool:
        """
        Check if the user is currently logged into the IPL Fantasy website.

        This method verifies login status by:
        1. Navigating to the stats page
        2. Checking if URL contains "login" (indicates redirect to login)
        3. Looking for "Login" or "Sign In" text on the page

        Returns:
            bool: True if logged in, False otherwise

        Note:
            Waits 10 seconds for page to load before checking
        """
        try:
            self.driver.get(self.stats_url)
            time.sleep(10)  # Wait for page to fully load

            # ============================================================
            # Method 1: Check URL for login redirect
            # ============================================================
            current_url = self.driver.current_url
            if "login" in current_url.lower():
                return False

            # ============================================================
            # Method 2: Look for login/sign-in buttons/text
            # ============================================================
            try:
                self.driver.find_element(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'Sign In')]")
                return False  # Found login element, so not logged in
            except:
                return True  # No login element found, so already logged in

        except Exception as e:
            print(f"Error checking login: {e}")
            return False

    def login(self, mobile_number: str):
        """
        Perform mobile OTP-based login to IPL Fantasy website.

        Login flow:
        1. Navigate to login page
        2. Enter mobile number
        3. Click "Send OTP" button
        4. Wait for user to manually enter OTP from their phone
        5. Auto-submit OTP (page auto-submits on OTP entry)
        6. Wait for login to complete
        7. Save session cookies for future use

        Args:
            mobile_number (str): 10-digit mobile number for OTP login

        Raises:
            Exception: If login process fails at any step

        Note:
            This is an interactive method - requires user to enter OTP in terminal
        """
        print("\n=== Starting Login Process ===")

        # ============================================================
        # Step 1: Navigate to Login Page
        # ============================================================
        self.driver.get(self.login_url)
        time.sleep(10)  # Wait for page to fully load

        print(f"Entering mobile number: {mobile_number}")

        try:
            # ============================================================
            # Step 2: Enter Mobile Number
            # ============================================================
            # Wait for mobile input field to appear (max 10 seconds)
            # Uses multiple selectors to find the input field reliably
            mobile_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//input[@type='tel' or @type='text' or contains(@placeholder, 'mobile') or contains(@placeholder, 'phone')]"
                ))
            )
            mobile_input.clear()  # Clear any pre-filled value
            mobile_input.send_keys(mobile_number)  # Type the mobile number
            time.sleep(1)  # Brief pause after typing

            # ============================================================
            # Step 3: Click "Send OTP" Button
            # ============================================================
            send_otp_btn = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Send') or contains(text(), 'OTP') or @type='submit']"
            )
            send_otp_btn.click()
            print("OTP request sent! Check your mobile.")
            time.sleep(5)  # Wait for OTP to be sent

            # ============================================================
            # Step 4: Get OTP from User (Manual Input)
            # ============================================================
            # This requires the user to check their phone and enter the OTP
            otp = input("\nEnter the OTP you received: ")

            # ============================================================
            # Step 5: Enter OTP on the Website
            # ============================================================
            # Wait for OTP input field to appear
            otp_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//input[contains(@placeholder, 'OTP') or contains(@placeholder, 'otp')]"
                ))
            )
            otp_input.clear()
            otp_input.send_keys(otp)  # Type the OTP
            time.sleep(5)  # Wait for OTP to be processed

            # ============================================================
            # Step 6: OTP Auto-Submit (No Button Click Needed)
            # ============================================================
            # Note: The website automatically submits OTP after entry
            # No need to click verify button - these lines are commented out
            ## verify_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Verify') or contains(text(), 'Submit') or @type='submit']")
            ## verify_btn.click()

            # ============================================================
            # Step 7: Wait for Login to Complete
            # ============================================================
            print("Verifying OTP...")
            time.sleep(10)  # Wait for page to redirect after successful login

            # ============================================================
            # Step 8: Save Session for Future Use
            # ============================================================
            self.save_cookies()  # Save cookies to avoid future OTP logins
            print("Login successful!\n")

        except Exception as e:
            # ============================================================
            # Error Handling: Capture Screenshot for Debugging
            # ============================================================
            print(f"Error during login: {e}")
            self.driver.save_screenshot("login_error.png")
            print("Screenshot saved as login_error.png")
            raise

    def scrape_stats(self):
        """
        Scrape player statistics from the IPL Fantasy stats page.

        This method:
        1. Navigates to the stats page
        2. Waits for player data to load
        3. Extracts player information from list items
        4. Returns data in tabular format

        Returns:
            list: 2D list with format:
                  [['Player Name', 'Team', 'Credits', 'Total Points'],
                   ['Rajat Patidar', 'RCB', '9', '380'],
                   ['Ishan Kishan', 'SRH', '10.5', '367'],
                   ...]

                  Returns empty list if extraction fails

        Note:
            - Takes screenshots for debugging if issues occur
            - Saves HTML page source if data extraction fails
            - Skips player items that don't have complete data
        """
        print("Navigating to stats page...")
        self.driver.get(self.stats_url)
        time.sleep(10)  # Wait for page to load

        print("Extracting stats data...")

        try:
            # ============================================================
            # Step 1: Wait for Player List to Load
            # ============================================================
            print("Waiting for player list to load...")
            time.sleep(5)  # Additional wait for JavaScript to render data

            # Take a screenshot for debugging purposes
            self.driver.save_screenshot("stats_page_loaded.png")
            print("Screenshot saved as stats_page_loaded.png")

            # ============================================================
            # Step 2: Find All Player List Items
            # ============================================================
            # The stats page uses a list structure: <ul><li>...</li><li>...</li></ul>
            # Each <li> represents one player
            player_items = self.driver.find_elements(By.CSS_SELECTOR, "ul > li")
            print(f"Found {len(player_items)} list items on page")

            if not player_items:
                print("No list items found!")
                return []

            # ============================================================
            # Step 3: Initialize Data Structure
            # ============================================================
            # Create a 2D list with headers in the first row
            data = []
            data.append(['Player Name', 'Team', 'Credits', 'Total Points'])

            # ============================================================
            # Step 4: Extract Data from Each Player Item
            # ============================================================
            for idx, item in enumerate(player_items):
                try:
                    # --------------------------------------------------------
                    # Extract Player Name
                    # --------------------------------------------------------
                    # CSS selector: .m11c-plyrSel__name span
                    name_elem = item.find_element(By.CSS_SELECTOR, ".m11c-plyrSel__name span")
                    player_name = name_elem.text.strip()

                    # --------------------------------------------------------
                    # Extract Team Abbreviation (e.g., RCB, SRH, RR)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-plyrSel__team span
                    try:
                        team_elem = item.find_element(By.CSS_SELECTOR, ".m11c-plyrSel__team span")
                        team = team_elem.text.strip()
                    except:
                        team = "N/A"  # If team element not found, use N/A

                    # --------------------------------------------------------
                    # Extract Credits (Player's fantasy value)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-tbl__cell--pts span
                    credits_elem = item.find_element(By.CSS_SELECTOR, ".m11c-tbl__cell--pts span")
                    credits = credits_elem.text.strip()

                    # --------------------------------------------------------
                    # Extract Total Points (Player's fantasy points scored)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-tbl__cell--amt span
                    points_elem = item.find_element(By.CSS_SELECTOR, ".m11c-tbl__cell--amt span")
                    points = points_elem.text.strip()

                    # --------------------------------------------------------
                    # Add Player Data to List (Only if All Fields Present)
                    # --------------------------------------------------------
                    if player_name and credits and points:
                        data.append([player_name, team, credits, points])
                        # Optional: Uncomment below to see each player as extracted
                        # print(f"{idx + 1}. {player_name} ({team}) | Credits: {credits} | Points: {points}")

                except Exception as e:
                    # --------------------------------------------------------
                    # Skip Items Without Expected Structure
                    # --------------------------------------------------------
                    # Some list items may be navigation elements or ads
                    # Silently skip them and continue with next item
                    continue

            # ============================================================
            # Step 5: Validate and Return Data
            # ============================================================
            if len(data) > 1:  # More than just headers
                print(f"\n✓ Successfully extracted {len(data) - 1} players!")
                return data
            else:
                # --------------------------------------------------------
                # No Data Found - Save Debug Information
                # --------------------------------------------------------
                print("No player data found with CSS selectors.")

                # Save HTML source code for manual inspection
                print("Saving page source for debugging...")
                with open("page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("Page source saved to page_source.html")

                return []

        except Exception as e:
            # ============================================================
            # Error Handling: Capture Debug Information
            # ============================================================
            print(f"Error extracting data: {e}")
            self.driver.save_screenshot("scraping_error.png")
            print("Screenshot saved as scraping_error.png")
            import traceback
            traceback.print_exc()
            return []

    def save_to_database(self, data, db_path="ipl_stats.db"):
        """
        Save scraped player statistics to SQLite database.

        This method:
        1. Connects to SQLite database
        2. Creates table if it doesn't exist
        3. Replaces old data with fresh data (snapshot mode)
        4. Adds timestamp to track when data was scraped
        5. Displays summary and sample data

        Args:
            data (list): 2D list with headers in first row
                        [['Player Name', 'Team', 'Credits', 'Total Points'],
                         ['Player 1', 'RCB', '9', '380'],
                         ...]
            db_path (str): Path to SQLite database file (default: "ipl_stats.db")

        Returns:
            bool: True if successful, False otherwise

        Note:
            - Database file is created in the same directory as the script
            - Each run replaces old data with fresh data
            - Timestamps track when data was scraped
        """
        if not data:
            print("No data to save!")
            return False

        # ============================================================
        # Save to SQLite Database
        # ============================================================
        print(f"\nSaving data to SQLite database: {db_path}")
        success = save_to_database(data, db_path)

        return success

    def run(self, mobile_number: str):
        """
        Main execution flow - orchestrates the entire scraping process.

        This method:
        1. Starts the Chrome browser
        2. Checks if user is already logged in (using saved cookies)
        3. If not logged in, performs OTP login
        4. Scrapes player statistics from the stats page
        5. Saves data to SQLite database with timestamp
        6. Ensures browser is closed at the end

        Args:
            mobile_number (str): 10-digit mobile number for OTP login

        Returns:
            bool: True if scraping and database save successful, False otherwise

        Note:
            Browser is always closed at the end, even if errors occur
        """
        try:
            # ============================================================
            # Step 1: Initialize Browser
            # ============================================================
            self.start_browser()

            # ============================================================
            # Step 2: Verify Login Status
            # ============================================================
            # Check if we can use saved session (cookies)
            if not self.is_logged_in():
                print("Not logged in. Starting login...")
                self.login(mobile_number)
            else:
                print("Already logged in!")

            # ============================================================
            # Step 3: Extract Player Statistics
            # ============================================================
            data = self.scrape_stats()

            # ============================================================
            # Step 4: Save to SQLite Database
            # ============================================================
            if data:
                success = self.save_to_database(data)
                return success
            else:
                print("No data extracted. Please check the page structure.")
                return False

        except Exception as e:
            # ============================================================
            # Error Handling: Print Full Traceback
            # ============================================================
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # ============================================================
            # Cleanup: Always Close Browser
            # ============================================================
            # This ensures browser is closed even if errors occur
            self.close()

    def close(self):
        """
        Clean up browser resources and close the browser window.

        This method should always be called at the end to:
        - Free up system memory
        - Close browser windows
        - Terminate ChromeDriver process

        Note:
            Called automatically in the finally block of run() method
        """
        if self.driver:
            self.driver.quit()  # Close browser and terminate driver
            print("Browser closed.")



# ============================================================================
# Main Execution Block
# ============================================================================
# This block runs only when script is executed directly (not when imported)

if __name__ == "__main__":
    import sys

    # ========================================================================
    # Parse Command Line Arguments
    # ========================================================================
    # Script expects mobile number as first argument
    # Usage: python ipl_scraper_selenium.py 9876543210

    if len(sys.argv) < 2:
        # No mobile number provided - show usage instructions
        print("Usage: python ipl_scraper_selenium.py <mobile_number>")
        print("Example: python ipl_scraper_selenium.py 9876543210")
        sys.exit(1)  # Exit with error code

    mobile = sys.argv[1]  # Get mobile number from first argument

    # ========================================================================
    # Execute Scraper
    # ========================================================================
    # Create scraper instance and run the entire process
    print(f"Starting IPL Fantasy Stats Scraper for mobile: {mobile}")
    print("=" * 60)

    scraper = IPLStatsScraperSelenium()
    scraper.run(mobile)

    print("=" * 60)
    print("Scraping completed!")