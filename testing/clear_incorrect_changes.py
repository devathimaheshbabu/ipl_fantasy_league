"""
Clear Incorrect Player Replacement Records
==========================================
This script removes incorrectly processed player replacement records
for teams that actually performed ranking swaps (not full replacements).

Usage: python clear_incorrect_changes.py

Teams affected:
- FC Barca Risers: Sai Kishore (incorrectly marked as replacement)
- DP: Zeeshan Ansari (incorrectly marked as replacement)
- Badu Title Hunters: Rahul Tripathi (incorrectly marked as replacement)

Author: Claude Code
Date: 2026-04-17
"""

import sqlite3
import sys
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

def clear_incorrect_changes():
    """Remove incorrect player replacement records from change history."""

    # Connect to database
    conn = sqlite3.connect('ipl_stats.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Teams and players with incorrect replacements
    teams_to_fix = {
        'FC Barca Risers': 'Sai Kishore',
        'DP': 'Zeeshan Ansari',
        'Badu Title Hunters': 'Rahul Tripathi'
    }

    print("=" * 70)
    print("Clearing Incorrect Player Replacement Records")
    print("=" * 70)
    print("\nThis script will remove player replacement records that were")
    print("incorrectly processed as replacements when they should have been")
    print("ranking swaps.\n")

    total_cleared = 0

    for team_name, player_name in teams_to_fix.items():
        print(f"\nProcessing: {team_name}")
        print("-" * 50)

        # Get team_id
        cursor.execute("SELECT team_id FROM fantasy_teams WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()

        if not result:
            print(f"  [!] Warning: Team '{team_name}' not found. Skipping.")
            continue

        team_id = result['team_id']

        # Check if replacement record exists
        cursor.execute("""
            SELECT change_id, player_name, old_value, new_value, frozen_points, change_detected_at
            FROM player_change_history
            WHERE team_id = ? AND player_name = ? AND change_type = 'player_replacement'
        """, (team_id, player_name))

        replacement_record = cursor.fetchone()

        if not replacement_record:
            print(f"  [i] No replacement record found for {player_name}. Skipping.")
            continue

        # Display what will be deleted
        print(f"  Found incorrect replacement record:")
        print(f"    Player: {replacement_record['player_name']}")
        print(f"    Old Value: {replacement_record['old_value']}")
        print(f"    New Value: {replacement_record['new_value']}")
        print(f"    Frozen Points: {replacement_record['frozen_points']}")
        print(f"    Detected At: {replacement_record['change_detected_at']}")

        # Delete the incorrect replacement record
        cursor.execute("""
            DELETE FROM player_change_history
            WHERE change_id = ?
        """, (replacement_record['change_id'],))

        # Get current team stats
        cursor.execute("""
            SELECT changes_used, changes_remaining
            FROM fantasy_teams
            WHERE team_id = ?
        """, (team_id,))

        team_stats = cursor.fetchone()

        if team_stats and team_stats['changes_used'] > 0:
            # Decrement changes_used count
            cursor.execute("""
                UPDATE fantasy_teams
                SET changes_used = changes_used - 1,
                    changes_remaining = changes_remaining + 1
                WHERE team_id = ?
            """, (team_id,))

            print(f"  [OK] Deleted replacement record")
            print(f"  [OK] Updated team stats: changes_used decreased by 1")
            total_cleared += 1
        else:
            print(f"  [!] Team stats not found or changes_used is already 0")

    # Commit changes
    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print(f"Cleanup Complete: {total_cleared} incorrect record(s) cleared")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Update Excel file: Swap the ranking numbers for affected players")
    print("2. Remove data from 'Replaces Player' columns (F, G, H)")
    print("3. Run: python run_fantasy_league.py")
    print("\nThe system will now correctly detect ranking swaps and transfer points.")

    return total_cleared

if __name__ == "__main__":
    try:
        cleared = clear_incorrect_changes()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
