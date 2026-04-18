"""
IPL Fantasy League Pipeline
============================
Main orchestration script to update fantasy league data and webpage.

Usage:
    python run_fantasy_league.py

Steps:
    1. Sync Excel roster to database
    2. Calculate team points with multipliers
    3. Generate HTML dashboard
    4. Ready for deployment to GitHub Pages

Author: Claude Code
Date: 2026-04-17
"""

import sys
import os
from pathlib import Path
from fantasy_league import FantasyLeagueManager
from web_generator import generate_dashboard_html
from database import IPLStatsDatabase

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num, total_steps, description):
    """Print formatted step indicator."""
    print(f"\n[{step_num}/{total_steps}] {description}")
    print("-" * 70)


def get_all_teams_from_excel(excel_path):
    """
    Get list of all unique team names from Excel file.

    Args:
        excel_path (str): Path to Excel file

    Returns:
        list: List of unique team names
    """
    import openpyxl
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    teams = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[2]:  # Column C: Fantasy Team
            teams.add(row[2])

    return sorted(list(teams))


def main():
    """
    Main pipeline execution.
    """
    # Configuration
    excel_path = "input_data/Player_details_team_level.xlsx"
    db_path = "ipl_stats.db"
    output_dir = "docs"

    print_header("IPL Fantasy League Pipeline")
    print(f"Excel: {excel_path}")
    print(f"Database: {db_path}")
    print(f"Output: {output_dir}/")

    try:
        # Initialize database with fantasy tables
        print_step(0, 3, "Initializing Database")
        db = IPLStatsDatabase(db_path)
        db.connect()
        db.create_table()  # Ensure players table exists
        db.create_fantasy_tables()  # Create fantasy league tables
        db.close()
        print("✓ Database initialized with all tables")

        # Get all teams from Excel
        teams = get_all_teams_from_excel(excel_path)
        print(f"\n✓ Found {len(teams)} teams in Excel:")
        for i, team in enumerate(teams, 1):
            print(f"  {i}. {team}")

        # Check if Excel file exists
        if not Path(excel_path).exists():
            print(f"✗ Error: Excel file not found at {excel_path}")
            print(f"  Please ensure the file exists before running this script.")
            return False

        # Step 1: Sync Excel to Database (All Teams)
        print_step(1, 3, "Syncing Excel to Database (All Teams)")

        all_teams_data = []

        for team_name in teams:
            print(f"\n  Processing: {team_name}")
            print(f"  {'-' * 60}")

            manager = FantasyLeagueManager(db_path)
            manager.connect()

            try:
                summary = manager.sync_excel_to_database(excel_path, team_name)

                print(f"  ✓ Sync completed")
                print(f"    Total Players: {summary['total_players']}")
                print(f"    Changes Detected: {summary['changes_detected']}")
                print(f"    Changes Processed: {summary['changes_processed']}")

                if summary['changes_detected'] > 0:
                    print(f"    ⚠ {summary['changes_detected']} change(s) detected!")

            finally:
                manager.close()

        # Step 2: Calculate Team Points (All Teams)
        print_step(2, 3, "Calculating Team Points (All Teams)")

        for team_name in teams:
            print(f"\n  Team: {team_name}")
            print(f"  {'-' * 60}")

            manager = FantasyLeagueManager(db_path)
            manager.connect()

            try:
                points_data = manager.calculate_team_points(team_name)

                print(f"  ✓ Points calculated")
                print(f"    Total Points: {points_data['total_points']}")
                print(f"    Captain ({points_data['captain_name']}): {points_data['captain_points']}")
                print(f"    Vice-Captain ({points_data['vc_name']}): {points_data['vc_points']}")
                print(f"    Regular Players: {points_data['regular_points']}")

                # Save snapshot to history
                manager.save_points_snapshot(points_data)

                # Get team stats and change history
                team_stats = manager.get_team_stats(team_name)
                change_history = manager.get_change_history(team_name, limit=10)

                # Store data for dashboard
                all_teams_data.append({
                    'team_name': team_name,
                    'points_data': points_data,
                    'team_stats': team_stats,
                    'change_history': change_history
                })

            finally:
                manager.close()

        # Step 3: Generate Combined HTML Dashboard
        print_step(3, 3, "Generating Combined HTML Dashboard")

        from web_generator import generate_multi_team_dashboard
        html_file = generate_multi_team_dashboard(all_teams_data, output_dir)

        print(f"✓ Dashboard generated successfully")
        print(f"  File: {html_file}")
        print(f"  You can open this file in your browser to preview")

        # Final Summary
        print_header("Pipeline Completed Successfully!")
        print("\n✓ All steps completed without errors")
        print(f"\n📊 Final Stats:")
        for team_data in all_teams_data:
            print(f"  • {team_data['team_name']}: {team_data['points_data']['total_points']} points")
        print(f"  • Dashboard: {output_dir}/index.html")

        print(f"\n🚀 Next Steps:")
        print(f"  1. Open {output_dir}/index.html in your browser to preview")
        print(f"  2. Run: python deploy_to_github.py")
        print(f"  3. Share your GitHub Pages URL with friends!")

        print("\n" + "=" * 70 + "\n")

        return True

    except FileNotFoundError as e:
        print(f"\n✗ Error: File not found - {e}")
        print(f"  Please ensure all required files exist.")
        return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
