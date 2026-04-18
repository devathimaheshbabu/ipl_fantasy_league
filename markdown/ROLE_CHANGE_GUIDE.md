# Role Change Guide

## How Captain/Vice-Captain Swaps Work

### ✅ Correct Approach for Role Swaps

When you want to change your Captain or Vice-Captain (e.g., Nicholas Pooran → Jos Buttler), **DO NOT use the "Replaces Player" column**. Simply update the `Role` column for both players.

### Excel Changes:

```
Row 1: Nicholas Pooran
  - Role: Change from "Captain" to "Player"
  - DO NOT fill "Replaces Player"
  - DO NOT fill "Frozen Points"

Row 2: Jos Buttler
  - Role: Change from "Player" to "Captain"
  - DO NOT fill "Replaces Player"
  - DO NOT fill "Frozen Points"
```

---

## What the System Does Automatically

### 1. **Detects Role Swap Pattern**
   The system identifies that two players are swapping roles:
   - Player A: Captain → Player/VC
   - Player B: Player/VC → Captain

### 2. **Counts as 1 Change** ✅
   - **Before Fix**: Would count as 2 changes
   - **After Fix**: Counts as 1 change (one strategic decision)

   Console output:
   ```
   🔄 Role Swap: Nicholas Pooran (Captain → Player)
      ↔️  with Jos Buttler (Player → Captain)
      ⚠ Counted as 1 change (swap pair)
   ```

### 3. **Position-Based Points Swap** 🔄

   **Key Principle**: Frozen points are tied to POSITION/RANK, not the player.

   When players swap roles, they inherit each other's accumulated base points:

   - **Nicholas Pooran** (Captain with 200 accumulated points):
     - Removes his own 200 frozen points
     - Inherits Jos Buttler's 70 frozen points
     - **New base**: 70 points

   - **Jos Buttler** (Player with 70 accumulated points):
     - Removes his own 70 frozen points
     - Inherits Nicholas Pooran's 200 frozen points
     - **New base**: 200 points

   Console output:
   ```
   Nicholas Pooran: Removes own frozen (200), Inherits Jos Buttler's frozen (70)
   Jos Buttler: Removes own frozen (70), Inherits Nicholas Pooran's frozen (200)
   ```

### 4. **Both Players Stay in Roster**
   - Nicholas Pooran: Stays at original rank, role = "Player", frozen = 70
   - Jos Buttler: Stays at original rank, role = "Captain", frozen = 200

---

## Swap Patterns Recognized

The system detects these swap patterns as 1 change:

1. **Captain ↔ Player**
   - Player A: Captain → Player
   - Player B: Player → Captain

2. **Captain ↔ Vice-Captain**
   - Player A: Captain → Vice-Captain
   - Player B: Vice-Captain → Captain

3. **Vice-Captain ↔ Player**
   - Player A: Vice-Captain → Player
   - Player B: Player → Vice-Captain

---

## 🎯 Key Principle: Position-Based Points

**Points are tied to POSITION/RANK, not the player.**

When players swap roles (e.g., Captain ↔ Player), they are essentially swapping positions on the team. Each position has accumulated points over time, and when players swap, they inherit the points that belong to those positions.

**Think of it like this:**
- Position 1 (Captain): Has accumulated 200 points over several matches
- Position 5 (Player): Has accumulated 70 points over several matches
- When Pooran (at Position 1) and Butler (at Position 5) swap roles:
  - Pooran moves to Position 5's role → inherits 70 points
  - Butler moves to Position 1's role → inherits 200 points

**Database Transactions for Each Player:**
1. `role_swap_remove`: Remove their own accumulated frozen points (negative value)
2. `role_change`: Add the other player's accumulated frozen points (positive value)

This ensures that points stay with the position, not the player.

---

## Example Scenario

### Before Swap:
- Nicholas Pooran: Captain with **200 accumulated frozen points**
- Jos Buttler: Player with **70 accumulated frozen points**
- Changes used: 0/2

### Excel Update (Role Swap):
```
Nicholas Pooran: Role = "Player"
Jos Buttler: Role = "Captain"
```

### Immediately After Swap:
- Nicholas Pooran: Player with **70 frozen points** (inherited from Butler)
- Jos Buttler: Captain with **200 frozen points** (inherited from Pooran)
- **Changes used: 1/2** ✅ (swap counts as 1 change!)
- Changes remaining: 1

### Next Match (Pooran scores 30, Butler scores 40):
- **Nicholas Pooran** (now Player):
  - Base: 70 (inherited frozen)
  - Match points: +30
  - Total: 100 (no multiplier for Player role)

- **Jos Buttler** (now Captain):
  - Base: 200 (inherited frozen)
  - Match points: +40
  - Subtotal: 240
  - Total: **480** (240 × 2 Captain multiplier)

---

## Independent Role Changes

If you change ONLY ONE player's role (not a swap), it counts as 1 change:

Example:
- Nicholas Pooran: Captain → Player (no other role change)
- Result: 1 change counted

---

## ❌ What NOT to Do

### DON'T use "Replaces Player" for role swaps:
```
❌ WRONG:
Nicholas Pooran: Replaces Player = "Jos Buttler", Frozen = 150
```

This would cause:
- Nicholas Pooran to be REMOVED from roster entirely
- Jos Buttler to take Nicholas Pooran's rank
- This is for PLAYER REPLACEMENTS, not role swaps

---

## Summary Table

| Scenario | Excel Change | Replaces Player Column | Counts As |
|----------|-------------|----------------------|-----------|
| Captain/VC Swap | Update Role column for both | ❌ Leave empty | **1 change** |
| Single role change | Update Role column for one | ❌ Leave empty | 1 change |
| Player replacement (bench → top 15) | Fill "Replaces Player" | ✅ Use it | 1 change |
| Injury replacement | Fill "Replaces Player" + Reason | ✅ Use it | 0 changes |

---

## Testing

Run the test script to verify:
```bash
python test_role_swap.py
```

Expected output: `✅ TEST PASSED: Swap correctly counted as 1 change!`
