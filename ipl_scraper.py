"""
IPL Fantasy Stats Scraper - Playwright Version
===============================================
This script scrapes player statistics from the official IPL Fantasy website.
It uses Playwright for browser automation and handles OTP-based login.

Features:
- Mobile OTP authentication
- Session management (saves cookies to avoid repeated logins)
- Automated data extraction from player stats page
- SQLite database storage with timestamps

Differences from Selenium version:
- Uses Playwright instead of Selenium WebDriver
- No need for separate ChromeDriver download
- Playwright manages browser binaries automatically

Author: Claude Code
Date: 2026-04-17
"""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Import database module
from database import save_to_database


class IPLStatsScraper:
    """
    A web scraper class for extracting IPL Fantasy player statistics using Playwright.

    This class handles:
    - Browser automation using Playwright
    - OTP-based login with mobile number
    - Session persistence using cookies
    - Player stats extraction from the fantasy website
    - Data storage in SQLite database with timestamps
    """

    def __init__(self):
        """
        Initialize the scraper with required URLs and configuration.

        Attributes:
            base_url (str): Base URL of the IPL Fantasy website
            login_url (str): URL for the login page with OTP
            stats_url (str): URL for the player statistics page
            session_file (str): File path to store session cookies for reuse
            playwright: Playwright instance (initialized later)
            browser: Browser instance (initialized later)
            context: Browser context instance (initialized later)
            page: Page instance (initialized later)
        """
        self.base_url = "https://fantasy.iplt20.com"
        self.login_url = "https://fantasy.iplt20.com/my11c/static/login.html?ru=/classic/home"
        self.stats_url = "https://fantasy.iplt20.com/classic/stats"
        self.session_file = "session.json"
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        """
        Initialize and configure Chromium browser with Playwright.

        This method:
        1. Starts Playwright and launches Chromium browser
        2. Creates a new browser context
        3. Attempts to restore previous session using saved cookies
        4. Creates a new page for interactions

        Note:
            - Browser runs in headed mode (visible window)
            - Playwright automatically manages Chromium binaries
            - Session cookies loaded from session.json if available
        """
        print("Starting browser...")

        # ============================================================
        # Step 1: Initialize Playwright and Launch Browser
        # ============================================================
        self.playwright = sync_playwright().start()
        # Launch Chromium browser (headless=False shows browser window)
        self.browser = self.playwright.chromium.launch(headless=False)

        # ============================================================
        # Step 2: Create Browser Context with Session Restoration
        # ============================================================
        # Load existing session if available to avoid repeated logins
        if Path(self.session_file).exists():
            print("Loading saved session...")
            with open(self.session_file, 'r') as f:
                cookies = json.load(f)
            # Create context and add saved cookies
            self.context = self.browser.new_context()
            self.context.add_cookies(cookies)
        else:
            # No saved session, create fresh context
            self.context = self.browser.new_context()

        # ============================================================
        # Step 3: Create New Page
        # ============================================================
        self.page = self.context.new_page()

    def save_session(self):
        """
        Save browser cookies to a JSON file for session persistence.

        This allows the script to maintain login state between runs,
        avoiding the need to enter OTP every time.

        Cookies are saved to: session.json
        """
        cookies = self.context.cookies()
        with open(self.session_file, 'w') as f:
            json.dump(cookies, f)
        print("Session saved!")

    def is_logged_in(self) -> bool:
        """
        Check if the user is currently logged into the IPL Fantasy website.

        This method verifies login status by:
        1. Navigating to the stats page
        2. Looking for "Login" or "Sign In" text on the page

        Returns:
            bool: True if logged in, False otherwise

        Note:
            Waits 10 seconds for page to load before checking
        """
        try:
            # Navigate to stats page
            self.page.goto(self.stats_url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(10)  # Increased wait time for page to fully load

            # ============================================================
            # Check for Login/Sign In Elements
            # ============================================================
            # If we find these elements, user is not logged in
            login_elements = self.page.locator("text=/login|sign in/i").count()
            if login_elements > 0:
                return False  # Found login button, not logged in
            return True  # No login button found, already logged in

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

        Note:
            This is an interactive method - requires user to enter OTP in terminal
        """
        print("\n=== Starting Login Process ===")

        # ============================================================
        # Step 1: Navigate to Login Page
        # ============================================================
        self.page.goto(self.login_url, wait_until="domcontentloaded")
        time.sleep(10)  # Increased wait time for page to fully load

        print(f"Entering mobile number: {mobile_number}")

        # ============================================================
        # Step 2: Enter Mobile Number
        # ============================================================
        # Use Playwright's locator to find mobile input field
        # Tries multiple selectors to find the field reliably
        mobile_input = self.page.locator(
            "input[type='tel'], input[type='text'], input[placeholder*='mobile'], input[placeholder*='phone']"
        ).first
        mobile_input.fill(mobile_number)
        time.sleep(10)  # Increased wait after entering mobile number

        # ============================================================
        # Step 3: Click "Send OTP" Button
        # ============================================================
        self.page.click("button:has-text('Send'), button:has-text('OTP'), button[type='submit']")
        print("OTP sent! Check your mobile.")
        time.sleep(10)  # Increased wait for OTP to be sent

        # ============================================================
        # Step 4: Get OTP from User (Manual Input)
        # ============================================================
        # This requires the user to check their phone and enter the OTP
        otp = input("\nEnter the OTP you received: ")

        # ============================================================
        # Step 5: Enter OTP on the Website
        # ============================================================
        otp_input = self.page.locator(
            "input[type='tel'], input[type='text'], input[placeholder*='otp'], input[placeholder*='OTP']"
        ).first
        otp_input.fill(otp)
        time.sleep(10)  # Increased wait for OTP to be processed

        # ============================================================
        # Step 6: OTP Auto-Submit (No Button Click Needed)
        # ============================================================
        # Note: The website automatically submits OTP after entry
        # No need to click verify button - these lines are commented out
        ## self.page.click("button:has-text('Verify'), button:has-text('Submit'), button[type='submit']")

        # ============================================================
        # Step 7: Wait for Login to Complete
        # ============================================================
        print("Verifying OTP...")
        time.sleep(15)  # Increased wait for page to redirect after successful login

        # ============================================================
        # Step 8: Save Session for Future Use
        # ============================================================
        self.save_session()  # Save cookies to avoid future OTP logins
        print("Login successful!\n")

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
        self.page.goto(self.stats_url, wait_until="domcontentloaded")
        time.sleep(10)  # Wait for page to load

        print("Extracting stats data...")

        try:
            # ============================================================
            # Step 1: Wait for Player List to Load
            # ============================================================
            print("Waiting for player list to load...")
            time.sleep(5)  # Additional wait for JavaScript to render data

            # Take a screenshot for debugging purposes
            self.page.screenshot(path="stats_page_loaded_playwright.png")
            print("Screenshot saved as stats_page_loaded_playwright.png")

            # ============================================================
            # Step 2: Find All Player List Items
            # ============================================================
            # The stats page uses a list structure: <ul><li>...</li><li>...</li></ul>
            # Each <li> represents one player
            player_items = self.page.locator("ul > li").all()
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
                    name_elem = item.locator(".m11c-plyrSel__name span").first
                    player_name = name_elem.text_content().strip()

                    # --------------------------------------------------------
                    # Extract Team Abbreviation (e.g., RCB, SRH, RR)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-plyrSel__team span
                    try:
                        team_elem = item.locator(".m11c-plyrSel__team span").first
                        team = team_elem.text_content().strip()
                    except:
                        team = "N/A"  # If team element not found, use N/A

                    # --------------------------------------------------------
                    # Extract Credits (Player's fantasy value)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-tbl__cell--pts span
                    credits_elem = item.locator(".m11c-tbl__cell--pts span").first
                    credits = credits_elem.text_content().strip()

                    # --------------------------------------------------------
                    # Extract Total Points (Player's fantasy points scored)
                    # --------------------------------------------------------
                    # CSS selector: .m11c-tbl__cell--amt span
                    points_elem = item.locator(".m11c-tbl__cell--amt span").first
                    points = points_elem.text_content().strip()

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
                with open("page_source_playwright.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                print("Page source saved to page_source_playwright.html")

                return []

        except Exception as e:
            # ============================================================
            # Error Handling: Capture Debug Information
            # ============================================================
            print(f"Error extracting data: {e}")
            self.page.screenshot(path="scraping_error_playwright.png")
            print("Screenshot saved as scraping_error_playwright.png")
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
        1. Starts the Chromium browser
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
        - Terminate Playwright processes

        Note:
            Called automatically in the finally block of run() method
        """
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
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
    # Usage: python ipl_scraper.py 9876543210

    if len(sys.argv) < 2:
        # No mobile number provided - show usage instructions
        print("Usage: python ipl_scraper.py <mobile_number>")
        print("Example: python ipl_scraper.py 9876543210")
        sys.exit(1)  # Exit with error code

    mobile = sys.argv[1]  # Get mobile number from first argument

    # ========================================================================
    # Execute Scraper
    # ========================================================================
    # Create scraper instance and run the entire process
    print(f"Starting IPL Fantasy Stats Scraper (Playwright) for mobile: {mobile}")
    print("=" * 60)

    scraper = IPLStatsScraper()
    scraper.run(mobile)

    print("=" * 60)
    print("Scraping completed!")