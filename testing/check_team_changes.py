"""Quick script to check team change counts in database"""
import sqlite3

db_path = "ipl_stats.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("TEAM CHANGE COUNTS IN DATABASE")
print("=" * 80)

cursor.execute("""
    SELECT team_id, team_name, owner_name, changes_used, changes_remaining, created_at
    FROM fantasy_teams
    ORDER BY team_name
""")

teams = cursor.fetchall()

if not teams:
    print("No teams found in database!")
else:
    for team in teams:
        print(f"\nTeam: {team['team_name']}")
        print(f"  Team ID: {team['team_id']}")
        print(f"  Owner: {team['owner_name']}")
        print(f"  Changes Used: {team['changes_used']}")
        print(f"  Changes Remaining: {team['changes_remaining']}")
        print(f"  Created: {team['created_at']}")

print("\n" + "=" * 80)
print("CHANGE HISTORY")
print("=" * 80)

cursor.execute("""
    SELECT ft.team_name, pch.player_name, pch.change_type,
           pch.old_value, pch.new_value, pch.frozen_points,
           pch.change_detected_at
    FROM player_change_history pch
    JOIN fantasy_teams ft ON pch.team_id = ft.team_id
    ORDER BY ft.team_name, pch.change_detected_at DESC
""")

changes = cursor.fetchall()

if not changes:
    print("No changes found in history!")
else:
    current_team = None
    for change in changes:
        if current_team != change['team_name']:
            current_team = change['team_name']
            print(f"\n{current_team}:")

        print(f"  - {change['change_type']}: {change['player_name']} "
              f"({change['old_value']} -> {change['new_value']}) "
              f"[{change['frozen_points']} pts] at {change['change_detected_at']}")

conn.close()
print("\n" + "=" * 80)
