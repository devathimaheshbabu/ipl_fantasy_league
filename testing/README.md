# Testing Scripts

This folder contains all testing, checking, and one-time fix scripts for the IPL Fantasy League application.

## Test Scripts

### Core Functionality Tests

**`test_role_swap.py`**
- Tests that Captain/VC role swaps are correctly detected and counted as 1 change (not 2)
- Verifies swap pattern recognition logic
- Run: `python testing/test_role_swap.py`

**`test_swap_database.py`**
- Comprehensive database test for position-based role swap logic
- Verifies frozen points are correctly swapped between positions
- Shows hypothetical next match calculations
- Run: `python testing/test_swap_database.py`

**`test_position_swap_points.py`**
- Conceptual test showing expected position-based swap logic
- Documents the key principle: points tied to position, not player
- Run: `python testing/test_position_swap_points.py`

**`test_change_detection.py`**
- Tests the change detection logic for various scenarios
- Verifies that different types of changes are correctly identified
- Run: `python testing/test_change_detection.py`

**`test_player_replacement.py`**
- Tests position takeover logic (bench player → top 15)
- Verifies frozen points transfer correctly
- Run: `python testing/test_player_replacement.py`

---

## Verification Scripts

**`check_roster.py`**
- Verifies roster state after position takeover changes
- Checks player rankings and frozen points
- Useful for debugging position takeover issues
- Run: `python testing/check_roster.py`

**`check_team_changes.py`**
- Displays change history for teams
- Shows all changes recorded in the database
- Useful for auditing team changes
- Run: `python testing/check_team_changes.py`

---

## One-Time Fix Scripts

**`clear_incorrect_changes.py`**
- One-time script to clear incorrect change records
- Used to fix historical data issues
- ⚠️ Use with caution - modifies database

**`reset_change_counters.py`**
- One-time script to reset change counters for affected teams
- Used to fix duplicate counting bugs
- ⚠️ Use with caution - modifies database

---

## Running Tests

### Run All Role Swap Tests
```bash
python testing/test_role_swap.py
python testing/test_swap_database.py
python testing/test_position_swap_points.py
```

### Run All Tests
```bash
python testing/test_role_swap.py
python testing/test_swap_database.py
python testing/test_position_swap_points.py
python testing/test_change_detection.py
python testing/test_player_replacement.py
```

### Verify Database State
```bash
python testing/check_roster.py
python testing/check_team_changes.py
```

---

## Notes

- All test scripts use UTF-8 encoding for Windows console compatibility
- Tests create temporary data with team_id 999 or 9999 (cleaned up after)
- One-time fix scripts should only be run when explicitly needed
- Test scripts are safe to run - they don't modify production data

---

## Expected Test Results

All test scripts should output `✅ TEST PASSED` when the logic is working correctly.

If any test fails with `❌ TEST FAILED`, check:
1. Database schema is up to date
2. Core logic in `fantasy_league.py` hasn't been modified
3. Test data assumptions are still valid
