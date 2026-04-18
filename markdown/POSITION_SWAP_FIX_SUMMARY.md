# Position-Based Role Swap Fix - Summary

## Problem Statement

The role swap points calculation was fundamentally incorrect. When players swapped roles (e.g., Captain ↔ Player), the system was making frozen points follow the player instead of treating them as position-based.

### User's Scenario

**Before Swap:**
- Nicholas Pooran: Captain with 200 accumulated base points
- Jos Buttler: Player with 70 accumulated base points

**User's Expected Behavior:**
When they swap roles, points should be tied to POSITION/RANK, not the player:
- Pooran (now Player): Should have 70 points (Butler's original base)
- Butler (now Captain): Should have 200 points (Pooran's original base)

**After Next Match (Pooran +30, Butler +40):**
- Pooran: 70 + 30 = 100 (Player, no multiplier)
- Butler: (200 + 40) × 2 = 480 (Captain multiplier)

---

## Root Cause

The code at `fantasy_league.py` lines 503-565 was:
1. Including official IPL points in the swap calculation
2. Not implementing true position-based swapping

```python
# WRONG APPROACH (before fix)
official_points = self.get_player_current_points(player_name)
existing_frozen = self.get_frozen_points(team_id, player_name)
current_base = official_points + existing_frozen  # Mixing official + frozen

# Swapping this mixed value caused incorrect results
```

---

## Solution Implemented

### 1. **Separate Logic for Swaps vs Non-Swaps**

**For Role Swaps (position-based):**
- Only use `get_frozen_points()` (accumulated fantasy points)
- Swap ONLY the frozen points between players
- Do NOT include official IPL points in the swap

**For Independent Role Changes (not a swap):**
- Use official + frozen to calculate the role change impact
- Apply multiplier based on the OLD role

### 2. **Database Transactions**

Each player in a swap gets TWO transactions:

1. **`role_swap_remove`**: Remove own accumulated frozen points (negative value)
2. **`role_change`**: Add other player's accumulated frozen points (positive value)

Example for Pooran (Captain, 200 frozen) swapping with Butler (Player, 70 frozen):

**Pooran's transactions:**
- `role_swap_remove`: -200 (removes his own Captain frozen points)
- `role_change`: +70 (adds Butler's Player frozen points)
- **Net result**: 70 frozen points

**Butler's transactions:**
- `role_swap_remove`: -70 (removes his own Player frozen points)
- `role_change`: +200 (adds Pooran's Captain frozen points)
- **Net result**: 200 frozen points

---

## Code Changes

### File: `fantasy_league.py`

**Lines 503-565: Role swap processing**

```python
# For swaps: only use frozen points (accumulated fantasy points)
# For non-swaps: use official + frozen to calculate role change impact
existing_frozen = self.get_frozen_points(team_id, player_name)

if is_swap:
    # This is a position swap - only swap accumulated frozen points
    if is_swap_primary:
        other_frozen = self.get_frozen_points(team_id, other_player_name)

        # POSITION SWAP LOGIC:
        # Swap only the accumulated frozen points between positions
        frozen_remove_own = -existing_frozen
        frozen_add_other = other_frozen

        # Record two transactions for this player
        self.record_change(team_id, player_name, 'role_swap_remove',
                          old_value, new_value, frozen_remove_own)
        self.record_change(team_id, player_name, change_type,
                          old_value, new_value, frozen_add_other)
```

---

## Testing

### Test Script: `test_swap_database.py`

Comprehensive test that:
1. Sets up initial state with specific frozen points
2. Executes role swap via detect_changes() and process_changes()
3. Verifies frozen points are correctly swapped
4. Shows hypothetical next match calculation

**Test Result:**
```
✅ TEST PASSED!
  ✓ Pooran correctly has 70 points (Butler's original base)
  ✓ Butler correctly has 200 points (Pooran's original base)

  Position-based swap logic is working correctly!
```

---

## Database Schema

The `player_change_history` table now includes:

| change_type | Description |
|-------------|-------------|
| `role_swap_remove` | Removes player's own frozen points (negative) |
| `role_change` | Adds frozen points (swap: other's points, non-swap: multiplied points) |

The `get_frozen_points()` method sums ALL frozen_points for a player:
```sql
SELECT SUM(frozen_points) as total_frozen
FROM player_change_history
WHERE team_id = ? AND player_name = ?
```

This correctly handles:
- Positive values (initial points, inherited points)
- Negative values (removed points during swap)

---

## Documentation Updated

### File: `markdown/ROLE_CHANGE_GUIDE.md`

Added comprehensive explanation of:
1. **Position-Based Points Principle**: Points tied to POSITION/RANK, not player
2. **Database Transactions**: Two transactions per player in a swap
3. **Example Scenario**: Step-by-step walkthrough with next match calculation
4. **Key Principle Section**: Clear explanation of position-based logic

---

## User Workflow

### To Execute a Role Swap:

1. **Update Excel** (both players):
   ```
   Nicholas Pooran: Role = "Player"
   Jos Buttler: Role = "Captain"
   ```

2. **DO NOT** fill "Replaces Player" column (that's for position takeovers)

3. **Run Pipeline**: `python run_fantasy_league.py`

4. **System Automatically**:
   - Detects the swap pattern
   - Counts as 1 change (not 2)
   - Swaps accumulated frozen points between positions
   - Records two transactions per player

---

## Verification

### Console Output
```
🔄 Role Swap: Nicholas Pooran (Captain → Player)
   ↔️  with Jos Buttler (Player → Captain)
   ⚠ Counted as 1 change (swap pair)
   Nicholas Pooran: Removes own frozen (200), Inherits Jos Buttler's frozen (70)
   Jos Buttler: Removes own frozen (70), Inherits Nicholas Pooran's frozen (200)
```

### Database Check
```sql
SELECT player_name, change_type, frozen_points
FROM player_change_history
WHERE team_id = ? AND player_name IN ('Nicholas Pooran', 'Jos Buttler')
ORDER BY change_detected_at;

-- Results:
-- Nicholas Pooran | role_swap_remove | -200
-- Nicholas Pooran | role_change      | +70
-- Jos Buttler     | role_swap_remove | -70
-- Jos Buttler     | role_change      | +200
```

### Frozen Points Query
```sql
SELECT player_name, SUM(frozen_points) as total
FROM player_change_history
WHERE team_id = ?
GROUP BY player_name;

-- Results after swap:
-- Nicholas Pooran | 70
-- Jos Buttler     | 200
```

---

## Impact

✅ **Correct Position-Based Logic**: Points now correctly tied to positions, not players

✅ **Accurate Next Match Calculations**: Future points added to inherited base, then multiplier applied

✅ **Consistent with User's Understanding**: Matches the mental model described by the user

✅ **Database Integrity**: All transactions recorded, audit trail maintained

✅ **Documentation Complete**: Clear guide for users and future maintenance

---

## Files Modified

1. **`fantasy_league.py`** (lines 503-582)
   - Fixed swap logic to use only frozen points
   - Separated swap and non-swap role change logic

2. **`markdown/ROLE_CHANGE_GUIDE.md`**
   - Added position-based principle section
   - Updated example scenario with correct calculations
   - Clarified transaction details

3. **`test_swap_database.py`** (new file)
   - Comprehensive test with database operations
   - Verifies correct frozen points swapping
   - Shows hypothetical next match calculation

4. **`test_position_swap_points.py`** (new file)
   - Conceptual test showing the expected logic
   - Documents the key principle

---

## Next Steps

If users report any issues with role swaps:

1. Check console output during pipeline run for "Role Swap" messages
2. Verify database transactions using the SQL queries above
3. Run `test_swap_database.py` to verify core logic still works
4. Refer to `ROLE_CHANGE_GUIDE.md` for expected behavior

---

**Status**: ✅ Complete and Tested
**Date**: 2026-04-18
**Issue**: Position-based swap logic incorrect
**Resolution**: Frozen points now correctly swap between positions
