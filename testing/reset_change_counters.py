"""
Reset Change Counters for Teams with Position Takeovers
========================================================
This script resets the change counters back to 1 for teams that had
duplicate counts due to the frozen points correction bug.

It will:
1. Reset changes_used to 1
2. Reset changes_remaining to 1
3. Keep only the position_takeover record
4. Remove any ranking_swap_out records (false changes)
"""

import sqlite3
from datetime import datetime

def reset_team_changes(db_path="ipl_stats.db"):
    """Reset change counters for affected teams."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Teams that had the bug
    affected_teams = ['FC Barca Risers', 'DP', 'Badu Title Hunters']

    print("\n" + "="*70)
    print("Resetting Change Counters for Affected Teams")
    print("="*70)

    for team_name in affected_teams:
        print(f"\nProcessing: {team_name}")
        print("-" * 70)

        # Get team_id
        cursor.execute("SELECT team_id FROM fantasy_teams WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()
        if not result:
            print(f"  Warning: Team '{team_name}' not found")
            continue

        team_id = result[0]

        # Show current state
        cursor.execute("""
            SELECT change_type, COUNT(*) as count
            FROM player_change_history
            WHERE team_id = ?
            GROUP BY change_type
        """, (team_id,))

        print("  Current change records:")
        for row in cursor.fetchall():
            print(f"    - {row[0]}: {row[1]}")

        cursor.execute("SELECT changes_used FROM fantasy_teams WHERE team_id = ?", (team_id,))
        current_changes = cursor.fetchone()[0]
        print(f"  Current changes_used: {current_changes}")

        # Delete ranking_swap_out records (false changes from bug)
        cursor.execute("""
            DELETE FROM player_change_history
            WHERE team_id = ?
            AND change_type = 'ranking_swap_out'
        """, (team_id,))
        deleted = cursor.rowcount

        if deleted > 0:
            print(f"  Deleted {deleted} false ranking_swap_out record(s)")

        # Reset changes_used to 1
        cursor.execute("""
            UPDATE fantasy_teams
            SET changes_used = 1,
                changes_remaining = 1
            WHERE team_id = ?
        """, (team_id,))

        print(f"  Reset changes_used to 1")
        print(f"  Reset changes_remaining to 1")

        # Verify final state
        cursor.execute("""
            SELECT change_type, COUNT(*) as count
            FROM player_change_history
            WHERE team_id = ?
            GROUP BY change_type
        """, (team_id,))

        print("\n  Final change records:")
        for row in cursor.fetchall():
            print(f"    - {row[0]}: {row[1]}")

        cursor.execute("""
            SELECT changes_used, changes_remaining
            FROM fantasy_teams
            WHERE team_id = ?
        """, (team_id,))
        result = cursor.fetchone()
        print(f"  Final changes_used: {result[0]} (Remaining: {result[1]})")

    # Commit all changes
    conn.commit()
    conn.close()

    print("\n" + "="*70)
    print("Reset Complete!")
    print("="*70)
    print("\nAll three teams now have:")
    print("  - 1 position_takeover record (the actual change)")
    print("  - changes_used = 1")
    print("  - changes_remaining = 1")
    print("\nYou can now make 1 more change per team without any issues.")
    print("="*70 + "\n")


if __name__ == "__main__":
    reset_team_changes()
