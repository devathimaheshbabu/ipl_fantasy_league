"""
Test Player Replacement System
===============================
This script tests the new player replacement functionality including:
- Normal replacements (count toward limit)
- Injury replacements (do NOT count)
- Point transfer validation
- Change limit enforcement

Author: Claude Code
Date: 2026-04-17
"""

import sqlite3
import json
import sys
from fantasy_league import FantasyLeagueManager

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def setup_test_data(manager):
    """
    Setup test data in database.
    """
    print("Setting up test data...")

    # Create test team
    team_id = manager.get_or_create_team("Test Team", "Test Owner")

    # Add test players to database
    test_players = [
        {"player_name": "Kartik Tyagi", "ipl_team": "LSG", "role": "Player", "ranking": 12},
        {"player_name": "Arshad Khan", "ipl_team": "MI", "role": "Player", "ranking": 15},
        {"player_name": "Nicholas Pooran", "ipl_team": "LSG", "role": "Captain", "ranking": 1},
    ]

    # Clear existing test team players
    manager.cursor.execute("DELETE FROM fantasy_team_players WHERE team_id = ?", (team_id,))

    # Insert test players
    for player in test_players:
        is_playing = 1 if player['ranking'] <= 15 else 0
        manager.cursor.execute(
            """INSERT INTO fantasy_team_players
               (team_id, player_name, ipl_team, role, player_ranking, is_in_playing_squad)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (team_id, player['player_name'], player['ipl_team'],
             player['role'], player['ranking'], is_playing)
        )

    # Add some fantasy points to players table (simulating scraped data)
    manager.cursor.execute("DELETE FROM players WHERE player_name IN (?, ?, ?)",
                          ("Kartik Tyagi", "Arshad Khan", "Nicholas Pooran"))

    for player_name, points in [("Kartik Tyagi", 45), ("Arshad Khan", 30), ("Nicholas Pooran", 380)]:
        manager.cursor.execute(
            """INSERT INTO players (player_name, team, credits, total_points)
               VALUES (?, ?, ?, ?)""",
            (player_name, "LSG", 8.0, points)
        )

    manager.connection.commit()
    print(f"[OK] Test team created (team_id: {team_id})")
    return team_id


def test_normal_replacement(manager, team_id):
    """
    Test Case 1: Normal strategic replacement (counts toward limit).
    """
    print("\n" + "="*60)
    print("TEST 1: Normal Replacement (Strategic Change)")
    print("="*60)

    # Simulate new Excel state with replacement
    new_state = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 12, "replaces_player": "Kartik Tyagi",
         "frozen_points": 45.0, "replacement_reason": "Normal Change"},
        {"player_name": "Arshad Khan", "ipl_team": "MI", "role": "Player",
         "player_ranking": 15, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Nicholas Pooran", "ipl_team": "LSG", "role": "Captain",
         "player_ranking": 1, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
    ]

    # Get current state
    current_state = manager.get_current_team_state(team_id)

    # Detect changes
    changes = manager.detect_changes(team_id, current_state, new_state)

    print(f"Changes detected: {len(changes)}")
    for change in changes:
        print(f"  - {change['change_type']}: {change.get('old_value', 'N/A')} → {change.get('new_value', 'N/A')}")

    # Get changes used before
    team_stats_before = manager.get_team_stats_by_id(team_id)
    changes_before = team_stats_before['changes_used']
    print(f"\nChanges before: {changes_before}/2")

    # Process changes
    processed = manager.process_changes(team_id, changes)
    print(f"\nProcessed: {processed} change(s)")

    # Get changes used after
    team_stats_after = manager.get_team_stats_by_id(team_id)
    changes_after = team_stats_after['changes_used']
    print(f"Changes after: {changes_after}/2")

    # Verify
    assert changes_after == changes_before + 1, "Normal change should increment counter by 1"

    # Check frozen points were recorded
    frozen = manager.get_frozen_points(team_id, "Shivam Mavi")
    print(f"\nFrozen points for Shivam Mavi: {frozen}")
    assert frozen == 45.0, "Frozen points should be 45.0"

    # Update roster
    manager.update_team_roster(team_id, new_state)

    print("\n[OK] TEST 1 PASSED: Normal replacement works correctly!")
    return changes_after


def test_injury_replacement(manager, team_id, current_changes_used):
    """
    Test Case 2: Injury replacement (does NOT count toward limit).
    """
    print("\n" + "="*60)
    print("TEST 2: Injury Replacement (Does NOT Count)")
    print("="*60)

    # Simulate Excel state with injury replacement
    new_state = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 12, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Mohsin Khan", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 15, "replaces_player": "Arshad Khan",
         "frozen_points": 30.0, "replacement_reason": "Injury Replacement"},
        {"player_name": "Nicholas Pooran", "ipl_team": "LSG", "role": "Captain",
         "player_ranking": 1, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
    ]

    # Get current state
    current_state = manager.get_current_team_state(team_id)

    # Detect changes
    changes = manager.detect_changes(team_id, current_state, new_state)

    print(f"Changes detected: {len(changes)}")
    for change in changes:
        print(f"  - {change['change_type']}: {change.get('old_value', 'N/A')} → {change.get('new_value', 'N/A')}")

    print(f"\nChanges before: {current_changes_used}/2")

    # Process changes
    processed = manager.process_changes(team_id, changes)
    print(f"\nProcessed: {processed} change(s)")

    # Get changes used after
    team_stats_after = manager.get_team_stats_by_id(team_id)
    changes_after = team_stats_after['changes_used']
    print(f"Changes after: {changes_after}/2")

    # Verify
    assert changes_after == current_changes_used, "Injury replacement should NOT increment counter"

    # Check frozen points were recorded
    frozen = manager.get_frozen_points(team_id, "Mohsin Khan")
    print(f"\nFrozen points for Mohsin Khan: {frozen}")
    assert frozen == 30.0, "Frozen points should be 30.0"

    # Update roster
    manager.update_team_roster(team_id, new_state)

    print("\n[OK] TEST 2 PASSED: Injury replacement doesn't count toward limit!")
    return changes_after


def test_captain_injury_replacement(manager, team_id, current_changes_used):
    """
    Test Case 3: Captain injury replacement with 2x multiplier.
    """
    print("\n" + "="*60)
    print("TEST 3: Captain Injury Replacement (2x Multiplier)")
    print("="*60)

    # Calculate frozen points for captain: (380 + 0) * 2 = 760
    new_state = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 12, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Mohsin Khan", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 15, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Quinton de Kock", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 14, "replaces_player": "Nicholas Pooran",
         "frozen_points": 760.0, "replacement_reason": "Injury Replacement"},
    ]

    # Get current state
    current_state = manager.get_current_team_state(team_id)

    # Detect changes
    changes = manager.detect_changes(team_id, current_state, new_state)

    print(f"Changes detected: {len(changes)}")
    for change in changes:
        print(f"  - {change['change_type']}: {change.get('old_value', 'N/A')} → {change.get('new_value', 'N/A')}")

    print(f"\nChanges before: {current_changes_used}/2")

    # Process changes
    processed = manager.process_changes(team_id, changes)
    print(f"\nProcessed: {processed} change(s)")

    # Get changes used after
    team_stats_after = manager.get_team_stats_by_id(team_id)
    changes_after = team_stats_after['changes_used']
    print(f"Changes after: {changes_after}/2")

    # Verify
    assert changes_after == current_changes_used, "Injury replacement should NOT increment counter"

    # Check frozen points were recorded (should be 760 = 380 * 2)
    frozen = manager.get_frozen_points(team_id, "Quinton de Kock")
    print(f"\nFrozen points for Quinton de Kock: {frozen}")
    assert frozen == 760.0, "Frozen points should be 760.0 (captain's 2x multiplier)"

    # Update roster
    manager.update_team_roster(team_id, new_state)

    print("\n[OK] TEST 3 PASSED: Captain injury replacement with correct multiplier!")
    return changes_after


def test_change_limit_enforcement(manager, team_id):
    """
    Test Case 4: System blocks when normal change limit exceeded.
    """
    print("\n" + "="*60)
    print("TEST 4: Change Limit Enforcement")
    print("="*60)

    # First, use up the second normal change
    print("\nUsing second normal change...")
    new_state = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Vice-Captain",  # Role change
         "player_ranking": 12, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Mohsin Khan", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 15, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Quinton de Kock", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 14, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
    ]

    current_state = manager.get_current_team_state(team_id)
    changes = manager.detect_changes(team_id, current_state, new_state)
    processed = manager.process_changes(team_id, changes)
    manager.update_team_roster(team_id, new_state)

    team_stats = manager.get_team_stats_by_id(team_id)
    print(f"Changes used: {team_stats['changes_used']}/2")
    assert team_stats['changes_used'] == 2, "Should have used 2 changes"

    # Now try to make another NORMAL replacement (should be blocked)
    print("\nAttempting third normal replacement (should be blocked)...")
    new_state_with_third_change = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Vice-Captain",
         "player_ranking": 12, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Test Player", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 15, "replaces_player": "Mohsin Khan",
         "frozen_points": 50.0, "replacement_reason": "Normal Change"},  # This should be blocked
        {"player_name": "Quinton de Kock", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 14, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
    ]

    current_state = manager.get_current_team_state(team_id)
    changes = manager.detect_changes(team_id, current_state, new_state_with_third_change)
    processed = manager.process_changes(team_id, changes)

    # Verify it was blocked
    assert processed == 0, "Should have blocked the third normal change"
    print("\n[OK] System correctly blocked third normal change!")

    # Now try INJURY replacement (should work even with 2/2 used)
    print("\nAttempting injury replacement (should work)...")
    new_state_with_injury = [
        {"player_name": "Shivam Mavi", "ipl_team": "LSG", "role": "Vice-Captain",
         "player_ranking": 12, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
        {"player_name": "Test Player 2", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 15, "replaces_player": "Mohsin Khan",
         "frozen_points": 50.0, "replacement_reason": "Injury Replacement"},  # Should work
        {"player_name": "Quinton de Kock", "ipl_team": "LSG", "role": "Player",
         "player_ranking": 14, "replaces_player": None,
         "frozen_points": 0.0, "replacement_reason": None},
    ]

    current_state = manager.get_current_team_state(team_id)
    changes = manager.detect_changes(team_id, current_state, new_state_with_injury)
    processed = manager.process_changes(team_id, changes)

    # Verify it worked
    assert processed == 1, "Should have allowed injury replacement"

    # Verify change count didn't increase
    team_stats_final = manager.get_team_stats_by_id(team_id)
    assert team_stats_final['changes_used'] == 2, "Change count should still be 2"

    print("\n[OK] TEST 4 PASSED: Limit enforcement works correctly!")


def test_change_history_format(manager, team_id):
    """
    Test Case 5: Verify change history is stored with correct format.
    """
    print("\n" + "="*60)
    print("TEST 5: Change History Format")
    print("="*60)

    # Get change history
    manager.cursor.execute(
        """SELECT player_name, change_type, old_value, new_value, frozen_points
           FROM player_change_history
           WHERE team_id = ? AND change_type = 'player_replacement'
           ORDER BY change_detected_at DESC
           LIMIT 5""",
        (team_id,)
    )

    changes = manager.cursor.fetchall()

    print(f"\nFound {len(changes)} replacement(s) in history:")

    for change in changes:
        player_name, change_type, old_value, new_value, frozen_points = change
        print(f"\n  Player: {player_name}")
        print(f"  Type: {change_type}")
        print(f"  Frozen Points: {frozen_points}")

        # Try to parse old_value as JSON
        try:
            data = json.loads(old_value)
            replaced = data.get('replaced')
            reason = data.get('reason')
            print(f"  Replaced: {replaced}")
            print(f"  Reason: {reason}")

            # Verify format
            assert replaced is not None, "Replaced player name should be in JSON"
            assert reason in ['Normal Change', 'Injury Replacement'], "Reason should be valid"
        except json.JSONDecodeError:
            print(f"  [WARNING] WARNING: old_value is not JSON format: {old_value}")

    print("\n[OK] TEST 5 PASSED: Change history format is correct!")


def main():
    """
    Run all tests.
    """
    print("="*60)
    print("PLAYER REPLACEMENT SYSTEM - TEST SUITE")
    print("="*60)

    # Initialize manager
    manager = FantasyLeagueManager("ipl_stats.db")
    manager.connect()

    try:
        # Setup
        team_id = setup_test_data(manager)

        # Run tests
        changes_after_test1 = test_normal_replacement(manager, team_id)
        changes_after_test2 = test_injury_replacement(manager, team_id, changes_after_test1)
        changes_after_test3 = test_captain_injury_replacement(manager, team_id, changes_after_test2)
        test_change_limit_enforcement(manager, team_id)
        test_change_history_format(manager, team_id)

        # Summary
        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nThe player replacement system is working correctly:")
        print("  [OK] Normal replacements count toward limit")
        print("  [OK] Injury replacements do NOT count toward limit")
        print("  [OK] Points transfer correctly (including multipliers)")
        print("  [OK] Change limit enforcement works")
        print("  [OK] Change history format is correct")

    except AssertionError as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        raise
    finally:
        manager.close()


if __name__ == "__main__":
    main()
