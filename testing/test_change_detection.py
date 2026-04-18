"""
Test Script: Fantasy League Change Detection
=============================================
Demonstrates how change detection works when you modify the Excel file.

This script shows:
1. Current team state
2. How to simulate role/ranking changes
3. Frozen points calculation
4. Change history tracking

Author: Claude Code
Date: 2026-04-17
"""

import sys
import os
from fantasy_league import FantasyLeagueManager

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    team_name = "Mahesh Thunder Buddies"
    db_path = "ipl_stats.db"

    print_section("Fantasy League Change Detection Test")

    manager = FantasyLeagueManager(db_path)
    manager.connect()

    try:
        # Get current team state
        print("\n📋 Current Team State:")
        print("-" * 70)

        team_stats = manager.get_team_stats(team_name)
        if team_stats:
            print(f"Team: {team_name}")
            print(f"Changes Used: {team_stats['changes_used']}/2")
            print(f"Changes Remaining: {team_stats['changes_remaining']}")
        else:
            print("Team not found. Please run run_fantasy_league.py first.")
            return

        # Show current captain and VC
        current_state = manager.get_current_team_state(team_stats['team_id'])

        captain = next((p for p in current_state if p['role'] == 'Captain'), None)
        vc = next((p for p in current_state if p['role'] == 'Vice-Captain'), None)

        print(f"\n🏆 Leadership:")
        if captain:
            official_pts = manager.get_player_current_points(captain['player_name'])
            frozen_pts = manager.get_frozen_points(team_stats['team_id'], captain['player_name'])
            print(f"  Captain: {captain['player_name']} (Rank {captain['player_ranking']})")
            print(f"    Official Points: {official_pts}")
            print(f"    Frozen Points: {frozen_pts}")
            print(f"    Team Contribution: {(official_pts + frozen_pts) * 2}")

        if vc:
            official_pts = manager.get_player_current_points(vc['player_name'])
            frozen_pts = manager.get_frozen_points(team_stats['team_id'], vc['player_name'])
            print(f"  Vice-Captain: {vc['player_name']} (Rank {vc['player_ranking']})")
            print(f"    Official Points: {official_pts}")
            print(f"    Frozen Points: {frozen_pts}")
            print(f"    Team Contribution: {(official_pts + frozen_pts) * 1.5}")

        # Show top 5 players by ranking
        print(f"\n📊 Top 5 Players (by ranking):")
        for i, player in enumerate(current_state[:5]):
            status = "✓ Playing" if player['player_ranking'] <= 15 else "⚠ Bench"
            print(f"  {player['player_ranking']:2d}. {player['player_name']:25s} ({player['ipl_team']}) - {status}")

        # Show change history
        print(f"\n📝 Recent Changes:")
        print("-" * 70)

        changes = manager.get_change_history(team_name, limit=5)

        if changes:
            for change in changes:
                change_type_emoji = {
                    'role_change': '👤',
                    'ranking_change': '🔄'
                }.get(change['change_type'], '•')

                print(f"{change_type_emoji} {change['player_name']}")
                print(f"   Type: {change['change_type']}")
                print(f"   {change['old_value']} → {change['new_value']}")
                if change['frozen_points'] > 0:
                    print(f"   Frozen Points: {change['frozen_points']:.1f}")
                print(f"   Date: {change['change_detected_at']}")
                print()
        else:
            print("No changes recorded yet.")

        # Show instructions for testing changes
        print_section("How to Test Change Detection")
        print("""
1. Open: input_data/Player_details_team_level.xlsx

2. Make one of these changes:

   A. ROLE CHANGE (Captain/VC swap):
      - Find current Captain row
      - Change Role column from "Captain" to "Player"
      - Find another player and change to "Captain"

   B. RANKING SWAP (move player to/from bench):
      - Pick a player with rank 10 (playing squad)
      - Change ranking to 18 (bench)
      - Pick a player with rank 18 (bench)
      - Change ranking to 10 (playing squad)

3. Save the Excel file

4. Run: python run_fantasy_league.py

5. Run this script again to see the changes tracked!

⚠ IMPORTANT: Each change counts toward your 2-change limit per season!
        """)

        print("\n" + "=" * 70 + "\n")

    finally:
        manager.close()


if __name__ == "__main__":
    main()
