"""
Test Position-Based Role Swap with Database
============================================
Comprehensive test that simulates the full swap scenario with actual
database operations to verify the position-based points logic.
"""

import sys
import os
import sqlite3

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from fantasy_league import FantasyLeagueManager

def setup_test_scenario(manager, team_id):
    """Set up initial test data with Pooran (Captain, 200) and Butler (Player, 70)."""

    # Clear existing data for test team
    manager.cursor.execute("DELETE FROM fantasy_team_players WHERE team_id = ?", (team_id,))
    manager.cursor.execute("DELETE FROM player_change_history WHERE team_id = ?", (team_id,))

    # Insert test players
    manager.cursor.execute("""
        INSERT INTO fantasy_team_players
        (team_id, player_name, ipl_team, role, player_ranking, is_in_playing_squad)
        VALUES
        (?, 'Nicholas Pooran', 'LSG', 'Captain', 1, 1),
        (?, 'Jos Buttler', 'RR', 'Player', 5, 1)
    """, (team_id, team_id))

    # Simulate accumulated points in change history
    # Pooran has accumulated 200 base points
    manager.cursor.execute("""
        INSERT INTO player_change_history
        (team_id, player_name, change_type, old_value, new_value, frozen_points)
        VALUES (?, 'Nicholas Pooran', 'initial_points', '', '', 200)
    """, (team_id,))

    # Butler has accumulated 70 base points
    manager.cursor.execute("""
        INSERT INTO player_change_history
        (team_id, player_name, change_type, old_value, new_value, frozen_points)
        VALUES (?, 'Jos Buttler', 'initial_points', '', '', 70)
    """, (team_id,))

    manager.connection.commit()

    print("✓ Test scenario setup complete")
    print("  Nicholas Pooran (Captain): 200 base points")
    print("  Jos Buttler (Player): 70 base points")


def test_swap_execution():
    """Execute the swap and verify the transactions."""

    manager = FantasyLeagueManager("ipl_stats.db")
    manager.connect()

    test_team_id = 9999  # Use a test team ID

    print("\n" + "="*70)
    print("Position-Based Role Swap Database Test")
    print("="*70)

    # Setup initial scenario
    print("\n📋 STEP 1: Setup Initial State")
    print("-" * 70)
    setup_test_scenario(manager, test_team_id)

    # Verify initial frozen points
    pooran_before = manager.get_frozen_points(test_team_id, 'Nicholas Pooran')
    butler_before = manager.get_frozen_points(test_team_id, 'Jos Buttler')

    print(f"\n  Pooran frozen points: {pooran_before}")
    print(f"  Butler frozen points: {butler_before}")

    # Execute the swap
    print("\n🔄 STEP 2: Execute Role Swap")
    print("-" * 70)

    current_state = [
        {'player_name': 'Nicholas Pooran', 'role': 'Captain', 'player_ranking': 1},
        {'player_name': 'Jos Buttler', 'role': 'Player', 'player_ranking': 5},
    ]

    new_state = [
        {'player_name': 'Nicholas Pooran', 'role': 'Player', 'player_ranking': 1},
        {'player_name': 'Jos Buttler', 'role': 'Captain', 'player_ranking': 5},
    ]

    changes = manager.detect_changes(team_id=test_team_id, current_state=current_state, new_state=new_state)
    print(f"  Detected {len(changes)} changes")

    # Process the changes
    processed = manager.process_changes(test_team_id, changes)
    print(f"  Processed {processed} changes")

    # Verify frozen points after swap
    print("\n📊 STEP 3: Verify Frozen Points After Swap")
    print("-" * 70)

    pooran_after = manager.get_frozen_points(test_team_id, 'Nicholas Pooran')
    butler_after = manager.get_frozen_points(test_team_id, 'Jos Buttler')

    print(f"  Pooran frozen points: {pooran_after} (expected: 70)")
    print(f"  Butler frozen points: {butler_after} (expected: 200)")

    # Check detailed transactions
    print("\n🔍 STEP 4: Verify Transaction Details")
    print("-" * 70)

    manager.cursor.execute("""
        SELECT player_name, change_type, frozen_points, change_detected_at
        FROM player_change_history
        WHERE team_id = ?
        ORDER BY change_detected_at
    """, (test_team_id,))

    transactions = manager.cursor.fetchall()

    print("\n  All Transactions:")
    for txn in transactions:
        player = txn['player_name']
        change_type = txn['change_type']
        frozen = txn['frozen_points']
        print(f"    • {player}: {change_type} → {frozen:+.0f} points")

    # Verify results
    print("\n" + "="*70)
    print("Test Results")
    print("="*70)

    pooran_correct = abs(pooran_after - 70) < 0.01
    butler_correct = abs(butler_after - 200) < 0.01

    if pooran_correct and butler_correct:
        print("✅ TEST PASSED!")
        print("  ✓ Pooran correctly has 70 points (Butler's original base)")
        print("  ✓ Butler correctly has 200 points (Pooran's original base)")
        print("\n  Position-based swap logic is working correctly!")
    else:
        print("❌ TEST FAILED!")
        if not pooran_correct:
            print(f"  ✗ Pooran has {pooran_after}, expected 70")
        if not butler_correct:
            print(f"  ✗ Butler has {butler_after}, expected 200")

    print("\n💡 Next Match Calculation (hypothetical):")
    print("-" * 70)
    print("  If Pooran scores 30 and Butler scores 40:")
    print(f"    Pooran (Player): {pooran_after} + 30 = {pooran_after + 30} (no multiplier)")
    print(f"    Butler (Captain): {butler_after} + 40 = {butler_after + 40}, then ×2 = {(butler_after + 40) * 2}")
    print("="*70 + "\n")

    # Cleanup
    manager.cursor.execute("DELETE FROM fantasy_team_players WHERE team_id = ?", (test_team_id,))
    manager.cursor.execute("DELETE FROM player_change_history WHERE team_id = ?", (test_team_id,))
    manager.connection.commit()

    manager.close()


if __name__ == "__main__":
    test_swap_execution()
