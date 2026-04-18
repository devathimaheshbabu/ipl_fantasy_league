"""
Test Role Swap Logic
====================
Test that Captain/VC swaps count as 1 change, not 2.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from fantasy_league import FantasyLeagueManager

def test_role_swap_detection():
    """Test the swap detection logic."""

    manager = FantasyLeagueManager("ipl_stats.db")
    manager.connect()

    # Simulate current state (before swap)
    current_state = [
        {'player_name': 'Nicholas Pooran', 'role': 'Captain', 'player_ranking': 1},
        {'player_name': 'Jos Buttler', 'role': 'Player', 'player_ranking': 5},
        {'player_name': 'Heinrich Klaasen', 'role': 'Vice-Captain', 'player_ranking': 2},
    ]

    # Simulate new state (after swap)
    new_state = [
        {'player_name': 'Nicholas Pooran', 'role': 'Player', 'player_ranking': 1},
        {'player_name': 'Jos Buttler', 'role': 'Captain', 'player_ranking': 5},
        {'player_name': 'Heinrich Klaasen', 'role': 'Vice-Captain', 'player_ranking': 2},
    ]

    # Detect changes
    changes = manager.detect_changes(team_id=999, current_state=current_state, new_state=new_state)

    print("=" * 70)
    print("Role Swap Detection Test")
    print("=" * 70)
    print(f"\nCurrent State:")
    print(f"  Nicholas Pooran: Captain")
    print(f"  Jos Buttler: Player")

    print(f"\nNew State:")
    print(f"  Nicholas Pooran: Player")
    print(f"  Jos Buttler: Captain")

    print(f"\nDetected Changes: {len(changes)}")
    for change in changes:
        is_swap = change.get('is_swap', False)
        is_primary = change.get('is_swap_primary', False)
        print(f"  - {change['player_name']}: {change['old_value']} to {change['new_value']}")
        print(f"    Type: {change['change_type']}, Is Swap: {is_swap}, Primary: {is_primary}")

    # Count how many would be counted as "normal changes"
    swap_count = 0
    counted_swap_pairs = set()

    for c in changes:
        if c['change_type'] == 'role_change' and c.get('is_swap', False):
            swap_pair_id = c.get('swap_pair_id')
            if swap_pair_id not in counted_swap_pairs:
                swap_count += 1
                counted_swap_pairs.add(swap_pair_id)

    print(f"\n✓ Expected: 1 change (swap counts as 1)")
    print(f"✓ Actual: {swap_count} change(s)")

    if swap_count == 1:
        print("\n✅ TEST PASSED: Swap correctly counted as 1 change!")
    else:
        print(f"\n❌ TEST FAILED: Expected 1 change, got {swap_count}")

    print("=" * 70 + "\n")

    manager.close()

if __name__ == "__main__":
    test_role_swap_detection()
