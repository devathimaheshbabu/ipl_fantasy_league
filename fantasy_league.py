"""
IPL Fantasy League Manager
===========================
Core business logic for managing custom fantasy league teams.

Features:
- Sync Excel roster to database
- Detect captain/VC and ranking changes
- Calculate points with multipliers and frozen points
- Track change history

Author: Claude Code
Date: 2026-04-17
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import openpyxl


class FantasyLeagueManager:
    """
    Manages fantasy league operations including team sync, change detection,
    and point calculation.
    """

    def __init__(self, db_path="ipl_stats.db"):
        """
        Initialize fantasy league manager.

        Args:
            db_path (str): Path to SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.connection.cursor()

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def get_or_create_team(self, team_name, owner_name=None):
        """
        Get team_id for a fantasy team, create if doesn't exist.

        Args:
            team_name (str): Fantasy team name
            owner_name (str): Owner's name (optional)

        Returns:
            int: team_id
        """
        # Check if team exists
        self.cursor.execute(
            "SELECT team_id FROM fantasy_teams WHERE team_name = ?",
            (team_name,)
        )
        result = self.cursor.fetchone()

        if result:
            return result['team_id']

        # Create new team
        self.cursor.execute(
            """INSERT INTO fantasy_teams (team_name, owner_name, changes_used, changes_remaining)
               VALUES (?, ?, 0, 2)""",
            (team_name, owner_name)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_current_team_state(self, team_id):
        """
        Get current team players from database.

        Args:
            team_id (int): Team ID

        Returns:
            list: List of player dictionaries
        """
        self.cursor.execute(
            """SELECT ftp_id, player_name, ipl_team, role, player_ranking, is_in_playing_squad
               FROM fantasy_team_players
               WHERE team_id = ?
               ORDER BY player_ranking""",
            (team_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def read_excel_roster(self, excel_path, team_name):
        """
        Read fantasy team roster from Excel file.

        Args:
            excel_path (str): Path to Excel file
            team_name (str): Fantasy team name to filter

        Returns:
            list: List of player dictionaries with columns from Excel
        """
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        players = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[2] == team_name:  # Column C: Fantasy Team
                players.append({
                    'player_name': row[0],      # Column A
                    'ipl_team': row[1],          # Column B
                    'fantasy_team': row[2],      # Column C
                    'role': row[3],              # Column D
                    'player_ranking': row[4],    # Column E
                    'replaces_player': row[5] if len(row) > 5 and row[5] else None,          # Column F
                    'frozen_points': float(row[6]) if len(row) > 6 and row[6] else 0.0,     # Column G
                    'replacement_reason': row[7] if len(row) > 7 and row[7] else None        # Column H
                })

        return players

    def detect_changes(self, team_id, current_state, new_state):
        """
        Detect changes between current database state and new Excel state.

        Args:
            team_id (int): Team ID
            current_state (list): Current players from DB
            new_state (list): New players from Excel

        Returns:
            list: List of change dictionaries
        """
        changes = []

        # Create lookup dictionaries
        current_dict = {p['player_name']: p for p in current_state}
        new_dict = {p['player_name']: p for p in new_state}

        # Track players involved in active takeovers (to skip in PHASE 2)
        takeover_players = set()  # Both old and new players involved in takeovers

        # PHASE 1: Detect position takeovers
        # When a player has "replaces_player" filled, it means:
        # - That player is the OLD player (being replaced)
        # - The value in "replaces_player" is the NEW player (taking over)
        for player_name, new_player in new_dict.items():
            if new_player.get('replaces_player'):
                old_player_name = player_name  # Player being replaced
                new_player_name = new_player['replaces_player']  # Player taking over
                old_rank = new_player['player_ranking']  # Position being vacated
                frozen_points_to_transfer = new_player.get('frozen_points', 0.0)
                replacement_reason = new_player.get('replacement_reason', 'Normal Change')

                # Mark both players as involved in takeover (skip ranking change detection)
                takeover_players.add(old_player_name)
                takeover_players.add(new_player_name)

                # Check if this EXACT takeover was already processed (same old + new player pair)
                self.cursor.execute(
                    """SELECT change_id, old_value, frozen_points FROM player_change_history
                       WHERE team_id = ? AND player_name = ? AND change_type = 'position_takeover'""",
                    (team_id, new_player_name)
                )
                existing_record = self.cursor.fetchone()

                if existing_record:
                    # Parse the existing record to check if it's the same takeover
                    try:
                        existing_data = json.loads(existing_record['old_value'])
                        existing_old_player = existing_data.get('replaced_player')
                        existing_frozen = existing_record['frozen_points']

                        # If it's the SAME takeover (same old + new player)
                        if existing_old_player == old_player_name:
                            # Check if frozen_points changed (user correcting a mistake)
                            if existing_frozen != frozen_points_to_transfer:
                                # This is an UPDATE to an existing takeover, not a new change
                                print(f"  ℹ️  Updating frozen points for existing takeover: {old_player_name} → {new_player_name}")
                                print(f"     Old frozen points: {existing_frozen}, New: {frozen_points_to_transfer}")

                                # Update the existing record (don't count as new change)
                                changes.append({
                                    'player_name': new_player_name,
                                    'change_type': 'position_takeover_update',
                                    'change_id': existing_record['change_id'],  # ID of record to update
                                    'old_value': old_player_name,
                                    'new_value': new_player_name,
                                    'old_rank': old_rank,
                                    'frozen_points_value': frozen_points_to_transfer,
                                    'replacement_reason': replacement_reason
                                })
                            # Else: same takeover with same frozen points - skip (no change)
                            continue
                    except:
                        # If we can't parse, treat as existing and skip
                        continue

                # Validate new player exists in roster
                if new_player_name not in new_dict:
                    print(f"  ⚠ Warning: '{new_player_name}' not found in roster. Skipping takeover.")
                    continue

                # Validate frozen_points is a number >= 0
                if frozen_points_to_transfer < 0:
                    print(f"  ⚠ Warning: Frozen points must be >= 0. Ignoring takeover.")
                    continue

                # Validate replacement_reason
                valid_reasons = ['Normal Change', 'Injury Replacement']
                if replacement_reason not in valid_reasons:
                    print(f"  ⚠ Warning: Invalid replacement reason '{replacement_reason}'. "
                          f"Must be 'Normal Change' or 'Injury Replacement'. Defaulting to 'Normal Change'.")
                    replacement_reason = 'Normal Change'

                changes.append({
                    'player_name': new_player_name,  # NEW player taking over
                    'change_type': 'position_takeover',
                    'old_value': old_player_name,  # OLD player being replaced
                    'new_value': new_player_name,
                    'old_rank': old_rank,  # Rank being taken over
                    'frozen_points_value': frozen_points_to_transfer,
                    'replacement_reason': replacement_reason
                })

        # PHASE 2: Existing role/ranking change detection
        for player_name, new_player in new_dict.items():
            # Skip players involved in active takeovers (ranks handled by takeover logic)
            if player_name in takeover_players:
                continue

            old_player = current_dict.get(player_name)

            if old_player:
                # Check for role change (Captain/VC swap)
                if old_player['role'] != new_player['role']:
                    changes.append({
                        'player_name': player_name,
                        'change_type': 'role_change',
                        'old_value': old_player['role'],
                        'new_value': new_player['role']
                    })

                # Check for ranking change
                if old_player['player_ranking'] != new_player['player_ranking']:
                    changes.append({
                        'player_name': player_name,
                        'change_type': 'ranking_change',
                        'old_value': str(old_player['player_ranking']),
                        'new_value': str(new_player['player_ranking'])
                    })

        # PHASE 3: Identify Captain/VC swaps (should count as 1 change, not 2)
        role_changes = [c for c in changes if c['change_type'] == 'role_change']
        swap_pairs = []
        processed_swap_indices = set()

        for i, change1 in enumerate(role_changes):
            if i in processed_swap_indices:
                continue

            for j, change2 in enumerate(role_changes):
                if i >= j or j in processed_swap_indices:
                    continue

                # Check if these two changes form a swap pair
                # Pattern 1: Captain <-> Player
                if ((change1['old_value'] == 'Captain' and change1['new_value'] in ['Player', 'Vice-Captain']) and
                    (change2['old_value'] in ['Player', 'Vice-Captain'] and change2['new_value'] == 'Captain')):
                    swap_pairs.append((i, j))
                    processed_swap_indices.add(i)
                    processed_swap_indices.add(j)
                    break
                # Pattern 2: Vice-Captain <-> Player
                elif ((change1['old_value'] == 'Vice-Captain' and change1['new_value'] in ['Player', 'Captain']) and
                      (change2['old_value'] in ['Player', 'Captain'] and change2['new_value'] == 'Vice-Captain')):
                    swap_pairs.append((i, j))
                    processed_swap_indices.add(i)
                    processed_swap_indices.add(j)
                    break
                # Pattern 3: Captain <-> Vice-Captain
                elif ((change1['old_value'] == 'Captain' and change1['new_value'] == 'Vice-Captain') and
                      (change2['old_value'] == 'Vice-Captain' and change2['new_value'] == 'Captain')):
                    swap_pairs.append((i, j))
                    processed_swap_indices.add(i)
                    processed_swap_indices.add(j)
                    break

        # Mark swap pairs in the changes list
        for idx, change in enumerate(changes):
            if change['change_type'] == 'role_change':
                role_idx = role_changes.index(change)
                if role_idx in processed_swap_indices:
                    # Find which pair this belongs to
                    for pair_idx, (i, j) in enumerate(swap_pairs):
                        if role_idx in (i, j):
                            change['is_swap'] = True
                            change['swap_pair_id'] = pair_idx
                            change['is_swap_primary'] = (role_idx == i)  # First one in pair is primary
                            break

        return changes

    def get_player_current_points(self, player_name):
        """
        Get current official IPL fantasy points for a player.

        Args:
            player_name (str): Player name

        Returns:
            int: Current points (0 if not found)
        """
        self.cursor.execute(
            "SELECT total_points FROM players WHERE player_name = ? ORDER BY scraped_at DESC LIMIT 1",
            (player_name,)
        )
        result = self.cursor.fetchone()
        return result['total_points'] if result and result['total_points'] else 0

    def get_frozen_points(self, team_id, player_name):
        """
        Get accumulated frozen points for a player from change history.

        Returns:
            float: Sum of frozen points
        """
        self.cursor.execute(
            """SELECT SUM(frozen_points) as total_frozen
               FROM player_change_history
               WHERE team_id = ? AND player_name = ?""",
            (team_id, player_name)
        )
        result = self.cursor.fetchone()
        return result['total_frozen'] if result['total_frozen'] else 0

    def record_change(self, team_id, player_name, change_type, old_value, new_value, frozen_points):
        """
        Record a player change in history table.

        Args:
            team_id (int): Team ID
            player_name (str): Player name
            change_type (str): Type of change
            old_value (str): Old value
            new_value (str): New value
            frozen_points (float): Points to freeze
        """
        self.cursor.execute(
            """INSERT INTO player_change_history
               (team_id, player_name, change_type, old_value, new_value, frozen_points, change_detected_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (team_id, player_name, change_type, old_value, new_value, frozen_points, datetime.now())
        )
        self.connection.commit()

    def process_changes(self, team_id, changes):
        """
        Process detected changes and freeze points as needed.

        Args:
            team_id (int): Team ID
            changes (list): List of change dictionaries

        Returns:
            int: Number of changes processed
        """
        # Get current team stats to check change limit
        team_stats = self.get_team_stats_by_id(team_id)

        # Count ONLY normal changes (injury replacements and updates are exempt)
        # For role swaps, only count once per pair
        pending_normal_changes = 0
        counted_swap_pairs = set()

        for c in changes:
            # Skip non-countable changes
            if c['change_type'] in ['position_takeover_update']:
                continue
            if c['change_type'] == 'player_replacement' and c.get('replacement_reason') == 'Injury Replacement':
                continue

            # Handle role change swaps
            if c['change_type'] == 'role_change' and c.get('is_swap', False):
                swap_pair_id = c.get('swap_pair_id')
                if swap_pair_id not in counted_swap_pairs:
                    pending_normal_changes += 1
                    counted_swap_pairs.add(swap_pair_id)
            elif c['change_type'] in ['player_replacement', 'position_takeover', 'role_change', 'ranking_change', 'ranking_swap_out', 'ranking_swap_in']:
                pending_normal_changes += 1

        # Validate normal change limit (2 max)
        if team_stats and team_stats['changes_remaining'] < pending_normal_changes:
            print(f"\n❌ ERROR: Cannot process {pending_normal_changes} normal change(s)!")
            print(f"   Team has only {team_stats['changes_remaining']} change(s) remaining.")
            print(f"   Note: Injury replacements do NOT count toward this limit.")
            print(f"   Please reduce normal changes in Excel or mark as injury replacements.")
            return 0

        processed = 0
        normal_changes = 0
        injury_replacements = 0
        updates = 0

        for change in changes:
            player_name = change['player_name']
            change_type = change['change_type']
            old_value = change['old_value']
            new_value = change['new_value']
            frozen_points = 0

            # Handle position_takeover_update (correction to existing takeover)
            if change_type == 'position_takeover_update':
                old_player_name = change['old_value']
                new_player_name = change['player_name']
                old_rank = change['old_rank']
                frozen_points = change.get('frozen_points_value', 0.0)
                change_id = change['change_id']  # ID of existing record to update

                # Update the existing record (does NOT count as new change)
                self.cursor.execute(
                    """UPDATE player_change_history
                       SET frozen_points = ?
                       WHERE change_id = ?""",
                    (frozen_points, change_id)
                )
                self.connection.commit()

                updates += 1
                print(f"  ✏️  Updated Position Takeover: {old_player_name} (Rank {old_rank}) → {new_player_name}")
                print(f"     New Frozen Points: {frozen_points}")
                print(f"     ⚠ Does NOT count as new change (correction only)")
                processed += 1

            # Handle position_takeover
            elif change_type == 'position_takeover':
                old_player_name = change['old_value']
                new_player_name = change['player_name']
                old_rank = change['old_rank']
                frozen_points = change.get('frozen_points_value', 0.0)
                replacement_reason = change.get('replacement_reason', 'Normal Change')

                # Count based on reason
                if replacement_reason == 'Injury Replacement':
                    injury_replacements += 1
                    print(f"  🏥 Position Takeover (Injury): {old_player_name} (Rank {old_rank}) → {new_player_name}")
                    print(f"     Transferred Points: {frozen_points}")
                    print(f"     ⚠ Does NOT count toward change limit")
                else:
                    normal_changes += 1
                    print(f"  🔄 Position Takeover: {old_player_name} (Rank {old_rank}) → {new_player_name}")
                    print(f"     Transferred Points: {frozen_points}")
                    print(f"     ⚠ Counts toward change limit")

                # Record the change with JSON data
                old_value_data = json.dumps({
                    'replaced_player': old_player_name,
                    'old_rank': old_rank,
                    'reason': replacement_reason
                })
                self.record_change(team_id, new_player_name, change_type, old_value_data, new_player_name, frozen_points)

            # Handle player_replacement (legacy - for backward compatibility)
            elif change_type == 'player_replacement':
                replaced_player_name = old_value
                frozen_points = change.get('frozen_points_value', 0.0)
                replacement_reason = change.get('replacement_reason', 'Normal Change')

                # Count based on reason
                if replacement_reason == 'Injury Replacement':
                    injury_replacements += 1
                    print(f"  🏥 Injury Replacement: {replaced_player_name} → {player_name}")
                    print(f"     Transferred Points: {frozen_points}")
                    print(f"     ⚠ Does NOT count toward change limit (injury exception)")
                else:  # Normal Change
                    normal_changes += 1
                    print(f"  🔄 Normal Replacement: {replaced_player_name} → {player_name}")
                    print(f"     Transferred Points: {frozen_points}")
                    print(f"     ⚠ Counts toward change limit")

                # Store reason in old_value as JSON
                old_value_with_reason = json.dumps({
                    'replaced': replaced_player_name,
                    'reason': replacement_reason
                })
                self.record_change(team_id, player_name, change_type, old_value_with_reason, new_value, frozen_points)

            # Handle role_change (existing logic)
            elif change_type == 'role_change':
                # Check if this is part of a swap (counts as 1 change for the pair)
                is_swap = change.get('is_swap', False)
                is_swap_primary = change.get('is_swap_primary', False)
                swap_pair_id = change.get('swap_pair_id')

                # For swaps: only use frozen points (accumulated fantasy points)
                # For non-swaps: use official + frozen to calculate role change impact
                existing_frozen = self.get_frozen_points(team_id, player_name)

                if is_swap:
                    # This is a position swap - only swap accumulated frozen points
                    # Only count as 1 change for the pair
                    if is_swap_primary:
                        normal_changes += 1
                        print(f"  🔄 Role Swap: {player_name} ({old_value} → {new_value})")

                        # Get the other player in the swap
                        other_player_change = next((c for c in changes
                                                   if c['change_type'] == 'role_change'
                                                   and c.get('swap_pair_id') == swap_pair_id
                                                   and not c.get('is_swap_primary')), None)

                        if other_player_change:
                            other_player_name = other_player_change['player_name']
                            other_frozen = self.get_frozen_points(team_id, other_player_name)

                            print(f"     ↔️  with {other_player_name} ({other_player_change['old_value']} → {other_player_change['new_value']})")
                            print(f"     ⚠ Counted as 1 change (swap pair)")

                            # POSITION SWAP LOGIC:
                            # Swap only the accumulated frozen points between positions
                            # Transaction 1: Remove own accumulated points
                            frozen_remove_own = -existing_frozen
                            # Transaction 2: Add other player's accumulated points
                            frozen_add_other = other_frozen

                            print(f"     {player_name}: Removes own frozen ({existing_frozen:.0f}), Inherits {other_player_name}'s frozen ({other_frozen:.0f})")

                            # Record two transactions for this player
                            self.record_change(team_id, player_name, 'role_swap_remove', old_value, new_value, frozen_remove_own)
                            self.record_change(team_id, player_name, change_type, old_value, new_value, frozen_add_other)

                            # For the other player (will be processed next)
                            # Store the swap data for when we process the secondary player
                            if not hasattr(self, '_swap_data'):
                                self._swap_data = {}
                            self._swap_data[swap_pair_id] = {
                                'primary_player': player_name,
                                'primary_frozen': existing_frozen
                            }
                    else:
                        # Secondary player in swap - process their transactions
                        swap_data = getattr(self, '_swap_data', {}).get(swap_pair_id)
                        if swap_data:
                            primary_frozen = swap_data['primary_frozen']

                            # This player removes their own frozen and inherits primary's frozen
                            frozen_remove_own = -existing_frozen
                            frozen_add_other = primary_frozen

                            print(f"     {player_name}: Removes own frozen ({existing_frozen:.0f}), Inherits {swap_data['primary_player']}'s frozen ({primary_frozen:.0f})")

                            # Record two transactions
                            self.record_change(team_id, player_name, 'role_swap_remove', old_value, new_value, frozen_remove_own)
                            self.record_change(team_id, player_name, change_type, old_value, new_value, frozen_add_other)

                            # Clean up swap data
                            del self._swap_data[swap_pair_id]

                else:
                    # Independent role change (not a swap)
                    # Apply multiplier based on OLD role to official + frozen points
                    normal_changes += 1
                    print(f"  🔄 Role Change: {player_name} ({old_value} → {new_value})")

                    # For non-swap role changes, calculate based on official + frozen
                    official_points = self.get_player_current_points(player_name)
                    current_base = official_points + existing_frozen

                    if old_value == 'Captain':
                        frozen_points = current_base * 2
                    elif old_value == 'Vice-Captain':
                        frozen_points = current_base * 1.5
                    else:
                        frozen_points = current_base

                    print(f"     Frozen Points: {frozen_points:.0f}")

                    self.record_change(team_id, player_name, change_type, old_value, new_value, frozen_points)

            # Handle ranking_change with point transfer logic for swaps
            elif change_type == 'ranking_change':
                normal_changes += 1

                old_rank = int(old_value)
                new_rank = int(new_value)

                # Check if this is a swap between top 15 and bench
                if (old_rank <= 15 and new_rank > 15):
                    # Player moving OUT of top 15 - calculate their points to transfer
                    official_points = self.get_player_current_points(player_name)
                    existing_frozen = self.get_frozen_points(team_id, player_name)
                    adjusted_points = official_points + existing_frozen

                    # Get role to apply multiplier
                    self.cursor.execute(
                        "SELECT role FROM fantasy_team_players WHERE team_id = ? AND player_name = ?",
                        (team_id, player_name)
                    )
                    role_result = self.cursor.fetchone()
                    role = role_result['role'] if role_result else 'Player'

                    if role == 'Captain':
                        frozen_points = adjusted_points * 2
                    elif role == 'Vice-Captain':
                        frozen_points = adjusted_points * 1.5
                    else:
                        frozen_points = adjusted_points

                    print(f"  📤 {player_name} moving OUT of top 15 (Rank {old_rank} → {new_rank})")
                    print(f"     Points to transfer: {frozen_points}")

                    # Store the points to transfer in a temporary dict for the swap partner
                    if not hasattr(self, '_pending_transfers'):
                        self._pending_transfers = {}
                    self._pending_transfers[team_id] = {
                        'from_player': player_name,
                        'points': frozen_points,
                        'old_rank': old_rank
                    }

                    # Record with negative frozen points (removing from this player)
                    self.record_change(team_id, player_name, 'ranking_swap_out', old_value, new_value, -frozen_points)

                elif (old_rank > 15 and new_rank <= 15):
                    # Player moving INTO top 15 - check if there's a pending transfer
                    frozen_points = 0

                    if hasattr(self, '_pending_transfers') and team_id in self._pending_transfers:
                        transfer_data = self._pending_transfers[team_id]
                        if transfer_data['old_rank'] == new_rank:  # They're swapping ranks
                            frozen_points = transfer_data['points']
                            from_player = transfer_data['from_player']
                            print(f"  📥 {player_name} moving INTO top 15 (Rank {old_rank} → {new_rank})")
                            print(f"     Inherited {frozen_points} points from {from_player}")
                            del self._pending_transfers[team_id]

                    self.record_change(team_id, player_name, 'ranking_swap_in', old_value, new_value, frozen_points)
                else:
                    # Regular ranking change within same zone (both in top 15 or both on bench)
                    frozen_points = 0
                    self.record_change(team_id, player_name, change_type, old_value, new_value, frozen_points)

            processed += 1

        # Update changes count - ONLY normal changes count toward limit
        if normal_changes > 0:
            self.cursor.execute(
                """UPDATE fantasy_teams
                   SET changes_used = changes_used + ?,
                       changes_remaining = 2 - (changes_used + ?)
                   WHERE team_id = ?""",
                (normal_changes, normal_changes, team_id)
            )
            self.connection.commit()

        # Log summary
        if injury_replacements > 0 or normal_changes > 0 or updates > 0:
            print(f"\n  📊 Summary:")
            if normal_changes > 0:
                print(f"     Normal Changes: {normal_changes} (count toward limit)")
            if injury_replacements > 0:
                print(f"     Injury Replacements: {injury_replacements} (do NOT count)")
            if updates > 0:
                print(f"     Updates/Corrections: {updates} (do NOT count)")
            print(f"     Total Processed: {processed}")

        return processed

    def update_team_roster(self, team_id, new_players):
        """
        Update fantasy_team_players table with new roster, handling position takeovers.

        Args:
            team_id (int): Team ID
            new_players (list): List of player dictionaries from Excel
        """
        # First pass: identify position takeovers
        takeovers = {}  # {new_player_name: old_rank}
        players_to_skip = set()  # Old players being replaced

        for player in new_players:
            if player.get('replaces_player'):
                old_player_name = player['player_name']
                new_player_name = player['replaces_player']
                old_rank = player['player_ranking']

                takeovers[new_player_name] = old_rank
                players_to_skip.add(old_player_name)

        # Clear current roster
        self.cursor.execute("DELETE FROM fantasy_team_players WHERE team_id = ?", (team_id,))

        # Second pass: insert players with correct ranks
        for player in new_players:
            # Skip players who have been replaced
            if player['player_name'] in players_to_skip:
                continue

            # Use takeover rank if this player is taking over a position
            if player['player_name'] in takeovers:
                actual_rank = takeovers[player['player_name']]
            else:
                actual_rank = player['player_ranking']

            is_in_playing_squad = 1 if actual_rank <= 15 else 0

            self.cursor.execute(
                """INSERT INTO fantasy_team_players
                   (team_id, player_name, ipl_team, role, player_ranking, is_in_playing_squad, added_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (team_id, player['player_name'], player['ipl_team'], player['role'],
                 actual_rank, is_in_playing_squad, datetime.now())
            )

        self.connection.commit()

    def sync_excel_to_database(self, excel_path, team_name):
        """
        Main sync function: read Excel, detect changes, update database.

        Args:
            excel_path (str): Path to Excel file
            team_name (str): Fantasy team name

        Returns:
            dict: Summary with changes detected and processed
        """
        # Get or create team
        team_id = self.get_or_create_team(team_name)

        # Read current state from DB
        current_state = self.get_current_team_state(team_id)

        # Read new state from Excel
        new_state = self.read_excel_roster(excel_path, team_name)

        # Detect changes
        changes = self.detect_changes(team_id, current_state, new_state)

        # Process changes (freeze points)
        processed = self.process_changes(team_id, changes)

        # Update roster in database
        self.update_team_roster(team_id, new_state)

        return {
            'team_id': team_id,
            'changes_detected': len(changes),
            'changes_processed': processed,
            'total_players': len(new_state)
        }

    def calculate_team_points(self, team_name):
        """
        Calculate total fantasy team points with multipliers and frozen points.

        Args:
            team_name (str): Fantasy team name

        Returns:
            dict: Points breakdown
        """
        # Get team_id
        team_id = self.get_or_create_team(team_name)

        # Get playing squad (ranking 1-15)
        self.cursor.execute(
            """SELECT player_name, ipl_team, role, player_ranking
               FROM fantasy_team_players
               WHERE team_id = ? AND player_ranking <= 15
               ORDER BY player_ranking""",
            (team_id,)
        )
        selected_players = [dict(row) for row in self.cursor.fetchall()]

        # Calculate adjusted points for each player
        for player in selected_players:
            # Get official points
            official_points = self.get_player_current_points(player['player_name'])

            # Get frozen points
            frozen_points = self.get_frozen_points(team_id, player['player_name'])

            # Adjusted points = official + frozen
            player['official_points'] = official_points
            player['frozen_points'] = frozen_points
            player['adjusted_points'] = official_points + frozen_points

        # Sort by adjusted points and select top 11
        selected_players.sort(key=lambda x: x['adjusted_points'], reverse=True)
        top_11 = selected_players[:11]

        # Apply multipliers
        captain = next((p for p in top_11 if p['role'] == 'Captain'), None)
        vc = next((p for p in top_11 if p['role'] == 'Vice-Captain'), None)

        captain_points = 0
        vc_points = 0
        regular_points = 0
        top_11_details = []

        for player in top_11:
            if player['role'] == 'Captain' and captain:
                multiplied_points = player['adjusted_points'] * 2
                captain_points = multiplied_points
                top_11_details.append({
                    'player_name': player['player_name'],
                    'ipl_team': player['ipl_team'],
                    'role': player['role'],
                    'official_points': player['official_points'],
                    'frozen_points': player['frozen_points'],
                    'adjusted_points': player['adjusted_points'],
                    'multiplier': 2.0,
                    'team_points': multiplied_points
                })
            elif player['role'] == 'Vice-Captain' and vc:
                multiplied_points = player['adjusted_points'] * 1.5
                vc_points = multiplied_points
                top_11_details.append({
                    'player_name': player['player_name'],
                    'ipl_team': player['ipl_team'],
                    'role': player['role'],
                    'official_points': player['official_points'],
                    'frozen_points': player['frozen_points'],
                    'adjusted_points': player['adjusted_points'],
                    'multiplier': 1.5,
                    'team_points': multiplied_points
                })
            else:
                regular_points += player['adjusted_points']
                top_11_details.append({
                    'player_name': player['player_name'],
                    'ipl_team': player['ipl_team'],
                    'role': player['role'],
                    'official_points': player['official_points'],
                    'frozen_points': player['frozen_points'],
                    'adjusted_points': player['adjusted_points'],
                    'multiplier': 1.0,
                    'team_points': player['adjusted_points']
                })

        total_points = captain_points + vc_points + regular_points

        return {
            'team_id': team_id,
            'team_name': team_name,
            'total_points': total_points,
            'captain_name': captain['player_name'] if captain else None,
            'captain_points': captain_points,
            'vc_name': vc['player_name'] if vc else None,
            'vc_points': vc_points,
            'regular_points': regular_points,
            'top_11_players': top_11_details
        }

    def save_points_snapshot(self, points_data):
        """
        Save calculated points to team_points_history.

        Args:
            points_data (dict): Points breakdown from calculate_team_points()
        """
        top_11_json = json.dumps([p['player_name'] for p in points_data['top_11_players']])

        self.cursor.execute(
            """INSERT INTO team_points_history
               (team_id, total_points, top_11_players, captain_name, captain_points,
                vc_name, vc_points, regular_points, snapshot_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (points_data['team_id'], points_data['total_points'], top_11_json,
             points_data['captain_name'], points_data['captain_points'],
             points_data['vc_name'], points_data['vc_points'],
             points_data['regular_points'], datetime.now())
        )
        self.connection.commit()

    def get_change_history(self, team_name, limit=10):
        """
        Get recent change history for a team.

        Args:
            team_name (str): Fantasy team name
            limit (int): Number of recent changes to retrieve

        Returns:
            list: List of change dictionaries
        """
        team_id = self.get_or_create_team(team_name)

        self.cursor.execute(
            """SELECT player_name, change_type, old_value, new_value, frozen_points, change_detected_at
               FROM player_change_history
               WHERE team_id = ?
               ORDER BY change_detected_at DESC
               LIMIT ?""",
            (team_id, limit)
        )

        return [dict(row) for row in self.cursor.fetchall()]

    def get_team_stats(self, team_name):
        """
        Get team metadata (changes used, etc.).

        Args:
            team_name (str): Fantasy team name

        Returns:
            dict: Team stats
        """
        self.cursor.execute(
            """SELECT team_id, owner_name, changes_used, changes_remaining, created_at
               FROM fantasy_teams
               WHERE team_name = ?""",
            (team_name,)
        )

        result = self.cursor.fetchone()
        return dict(result) if result else None

    def get_team_stats_by_id(self, team_id):
        """
        Get team metadata by team_id.

        Args:
            team_id (int): Team ID

        Returns:
            dict: Team stats
        """
        self.cursor.execute(
            """SELECT team_id, team_name, owner_name, changes_used, changes_remaining, created_at
               FROM fantasy_teams
               WHERE team_id = ?""",
            (team_id,)
        )

        result = self.cursor.fetchone()
        return dict(result) if result else None


# ============================================================================
# Convenience Functions
# ============================================================================

def sync_excel_to_database(excel_path, team_name, db_path="ipl_stats.db"):
    """
    Convenience function to sync Excel roster to database.

    Args:
        excel_path (str): Path to Excel file
        team_name (str): Fantasy team name
        db_path (str): Database path

    Returns:
        dict: Sync summary
    """
    manager = FantasyLeagueManager(db_path)
    manager.connect()

    try:
        summary = manager.sync_excel_to_database(excel_path, team_name)
        return summary
    finally:
        manager.close()


def calculate_team_points(team_name, db_path="ipl_stats.db"):
    """
    Convenience function to calculate team points.

    Args:
        team_name (str): Fantasy team name
        db_path (str): Database path

    Returns:
        dict: Points breakdown
    """
    manager = FantasyLeagueManager(db_path)
    manager.connect()

    try:
        points_data = manager.calculate_team_points(team_name)
        return points_data
    finally:
        manager.close()


def generate_points_snapshot(team_name, db_path="ipl_stats.db"):
    """
    Convenience function to calculate and save points snapshot.

    Args:
        team_name (str): Fantasy team name
        db_path (str): Database path

    Returns:
        dict: Points data
    """
    manager = FantasyLeagueManager(db_path)
    manager.connect()

    try:
        points_data = manager.calculate_team_points(team_name)
        manager.save_points_snapshot(points_data)
        return points_data
    finally:
        manager.close()


# ============================================================================
# Main Execution Block (For Testing)
# ============================================================================

if __name__ == "__main__":
    print("Testing Fantasy League Manager...\n")

    # Test sync
    excel_path = "input_data/Player_details_team_level.xlsx"
    team_name = "Mahesh Thunder Buddies"

    print("=" * 60)
    print("Step 1: Syncing Excel to Database")
    print("=" * 60)
    summary = sync_excel_to_database(excel_path, team_name)
    print(f"\nSync Results:")
    print(f"  Changes Detected: {summary['changes_detected']}")
    print(f"  Changes Processed: {summary['changes_processed']}")
    print(f"  Total Players: {summary['total_players']}")

    print("\n" + "=" * 60)
    print("Step 2: Calculating Team Points")
    print("=" * 60)
    points_data = calculate_team_points(team_name)
    print(f"\nPoints Breakdown:")
    print(f"  Total Points: {points_data['total_points']:.1f}")
    print(f"  Captain ({points_data['captain_name']}): {points_data['captain_points']:.1f}")
    print(f"  Vice-Captain ({points_data['vc_name']}): {points_data['vc_points']:.1f}")
    print(f"  Regular Players: {points_data['regular_points']:.1f}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
