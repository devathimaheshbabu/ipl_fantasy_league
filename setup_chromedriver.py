"""
ChromeDriver Setup Script
==========================
This script automatically downloads the correct ChromeDriver version
that matches your installed Google Chrome browser.

Purpose:
    - Detects installed Chrome version
    - Downloads matching ChromeDriver from Google's official repository
    - Extracts chromedriver.exe to the current directory

Usage:
    python setup_chromedriver.py

Requirements:
    - Google Chrome installed on Windows
    - Internet connection
    - requests library (pip install requests)

Author: Claude Code
Date: 2026-04-16
"""

import requests
import zipfile
import os
import json
from pathlib import Path


def get_chrome_version():
    """
    Automatically detect the installed Google Chrome version on Windows.

    This function:
    1. Checks common Chrome installation paths
    2. Uses PowerShell to read Chrome executable version
    3. Returns the major version number (e.g., "146" from "146.0.7680.178")

    Returns:
        str: Major version number (e.g., "146"), or None if detection fails

    Note:
        Checks both 64-bit and 32-bit installation paths
    """
    import subprocess

    # Common Chrome installation paths on Windows
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # 64-bit
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  # 32-bit
    ]

    # Try each path until Chrome is found
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                # Use PowerShell to read file version info
                # This is more reliable than running chrome.exe --version
                result = subprocess.run(
                    ['powershell.exe', '-Command',
                     f"(Get-Item '{chrome_path}').VersionInfo.FileVersion"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.strip()  # e.g., "146.0.7680.178"
                print(f"Detected Chrome version: {version}")
                return version.split('.')[0]  # Return major version only: "146"
            except:
                # If this path fails, try the next one
                continue

    # Chrome not found in any common location
    print("Could not detect Chrome version automatically.")
    return None

def download_chromedriver(version=None):
    """
    Download ChromeDriver that matches the specified Chrome version.

    This function:
    1. Gets Chrome version (auto-detect or user input)
    2. Queries Google's Chrome for Testing API for matching ChromeDriver
    3. Downloads the ChromeDriver zip file
    4. Extracts chromedriver.exe to current directory
    5. Cleans up temporary files

    Args:
        version (str, optional): Chrome major version (e.g., "146").
                                If None, will auto-detect or prompt user.

    Returns:
        bool: True if download successful, False otherwise

    Note:
        Downloads from Google's official Chrome for Testing repository:
        https://googlechromelabs.github.io/chrome-for-testing/
    """

    print("Downloading ChromeDriver...")

    # ========================================================================
    # Step 1: Get Chrome Version
    # ========================================================================
    if not version:
        # Try to auto-detect installed Chrome version
        version = get_chrome_version()

    if not version:
        # Auto-detection failed, ask user for version
        print("Please enter your Chrome major version (e.g., 146):")
        version = input().strip()

    print(f"Looking for ChromeDriver version {version}...")

    # ========================================================================
    # Step 2: Find Matching ChromeDriver Version
    # ========================================================================
    try:
        # --------------------------------------------------------------------
        # Query Chrome for Testing API - Known Good Versions
        # --------------------------------------------------------------------
        # This endpoint contains all available ChromeDriver versions
        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(versions_url, timeout=30)
        data = response.json()

        versions_list = data.get('versions', [])

        # --------------------------------------------------------------------
        # Search for Version Matching Our Chrome
        # --------------------------------------------------------------------
        # Example: If Chrome is 146.0.7680.178, we look for 146.x.x.x
        win64_url = None
        for v in reversed(versions_list):  # Start from latest (better compatibility)
            v_number = v.get('version', '')

            # Check if version starts with our major version (e.g., "146.")
            if v_number.startswith(f"{version}."):
                # Found a matching version!
                downloads = v.get('downloads', {})
                chromedriver_downloads = downloads.get('chromedriver', [])

                # Look for Windows 64-bit version
                for download in chromedriver_downloads:
                    if download.get('platform') == 'win64':
                        win64_url = download.get('url')
                        print(f"Found matching ChromeDriver version: {v_number}")
                        break

                if win64_url:
                    break  # Found it, stop searching

        # --------------------------------------------------------------------
        # Fallback: Use Latest Stable Version
        # --------------------------------------------------------------------
        if not win64_url:
            print(f"Error: Could not find ChromeDriver for Chrome version {version}")
            print("\nTrying latest stable version instead...")

            # Query the latest stable version endpoint
            api_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
            response = requests.get(api_url, timeout=10)
            data = response.json()

            channels = data.get('channels', {})
            stable = channels.get('Stable', {})
            downloads = stable.get('downloads', {})
            chromedriver_downloads = downloads.get('chromedriver', [])

            # Find Windows 64-bit version
            for download in chromedriver_downloads:
                if download.get('platform') == 'win64':
                    win64_url = download.get('url')
                    break

        # Check if we found a download URL
        if not win64_url:
            print("Error: Could not find ChromeDriver download URL")
            return False

        print(f"Downloading from: {win64_url}")

        # ====================================================================
        # Step 3: Download ChromeDriver Zip File
        # ====================================================================
        response = requests.get(win64_url, timeout=60)
        zip_path = "chromedriver.zip"

        # Save downloaded zip file
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        print("Extracting ChromeDriver...")

        # ====================================================================
        # Step 4: Extract chromedriver.exe from Zip
        # ====================================================================
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # The zip file contains a folder structure like:
            # chromedriver-win64/
            #   └── chromedriver.exe
            # We need to find and extract just the .exe file

            for file in zip_ref.namelist():
                if file.endswith('chromedriver.exe'):
                    # Extract file with its folder structure
                    zip_ref.extract(file)

                    # Move chromedriver.exe to current directory
                    extracted_path = Path(file)  # e.g., "chromedriver-win64/chromedriver.exe"
                    if extracted_path.exists():
                        # Rename (move) to root: "chromedriver.exe"
                        extracted_path.rename('chromedriver.exe')

                        # Clean up the extracted folder (chromedriver-win64/)
                        parent_dir = extracted_path.parent
                        if parent_dir.exists() and parent_dir != Path('.'):
                            import shutil
                            shutil.rmtree(parent_dir)  # Delete the folder
                    break  # Found and extracted, no need to continue

        # ====================================================================
        # Step 5: Clean Up Temporary Files
        # ====================================================================
        os.remove(zip_path)  # Delete the downloaded zip file

        # ====================================================================
        # Step 6: Verify Success
        # ====================================================================
        if os.path.exists('chromedriver.exe'):
            # Success!
            print("✓ ChromeDriver successfully downloaded to: chromedriver.exe")
            print("You can now run: python ipl_scraper_selenium.py <mobile_number>")
            return True
        else:
            # Something went wrong during extraction
            print("Error: ChromeDriver extraction failed")
            return False

    except Exception as e:
        # ====================================================================
        # Error Handling: Provide Manual Download Instructions
        # ====================================================================
        print(f"Error downloading ChromeDriver: {e}")
        print("\nManual download instructions:")
        print("1. Go to: https://googlechromelabs.github.io/chrome-for-testing/")
        print("2. Download 'chromedriver' for win64")
        print("3. Extract chromedriver.exe to this folder")
        return False


# ============================================================================
# Main Execution Block
# ============================================================================
# This block runs when the script is executed directly

if __name__ == "__main__":
    print("=== ChromeDriver Setup ===\n")

    # Attempt to download and setup ChromeDriver
    success = download_chromedriver()

    if not success:
        # Download failed - wait for user to acknowledge before closing
        input("\nPress Enter to exit...")
