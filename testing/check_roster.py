import sqlite3

conn = sqlite3.connect('ipl_stats.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("Verification: Position Takeover Logic")
print("="*60)

# Check FC Barca Risers
print("\nFC Barca Risers:")
print("-" * 60)

cursor.execute("""
    SELECT player_name, player_ranking
    FROM fantasy_team_players
    WHERE team_id = (SELECT team_id FROM fantasy_teams WHERE team_name = 'FC Barca Risers')
    AND player_name IN ('Sarfaraz Khan', 'Sai Kishore')
    ORDER BY player_name
""")
results = cursor.fetchall()

if results:
    for row in results:
        print(f"  {row[0]}: Rank {row[1]}")
else:
    print("  No matching players found")

# Check frozen points for Sarfaraz Khan
cursor.execute("""
    SELECT SUM(frozen_points) as frozen_points
    FROM player_change_history
    WHERE team_id = (SELECT team_id FROM fantasy_teams WHERE team_name = 'FC Barca Risers')
    AND player_name = 'Sarfaraz Khan'
""")
result = cursor.fetchone()
print(f"\n  Sarfaraz Khan frozen points: {result[0] if result[0] else 0}")

# Check change history
cursor.execute("""
    SELECT player_name, change_type, old_value, frozen_points
    FROM player_change_history
    WHERE team_id = (SELECT team_id FROM fantasy_teams WHERE team_name = 'FC Barca Risers')
    ORDER BY change_detected_at DESC
    LIMIT 5
""")
changes = cursor.fetchall()
print("\n  Recent changes:")
for change in changes:
    print(f"    - {change[0]}: {change[1]} (frozen: {change[3]})")

# Check DP
print("\nDP:")
print("-" * 60)

cursor.execute("""
    SELECT player_name, player_ranking
    FROM fantasy_team_players
    WHERE team_id = (SELECT team_id FROM fantasy_teams WHERE team_name = 'DP')
    AND player_name IN ('Tushar Deshpande', 'Zeeshan Ansari')
    ORDER BY player_name
""")
results = cursor.fetchall()

if results:
    for row in results:
        print(f"  {row[0]}: Rank {row[1]}")
else:
    print("  No matching players found")

# Check Badu Title Hunters
print("\nBadu Title Hunters:")
print("-" * 60)

cursor.execute("""
    SELECT player_name, player_ranking
    FROM fantasy_team_players
    WHERE team_id = (SELECT team_id FROM fantasy_teams WHERE team_name = 'Badu Title Hunters')
    AND player_name IN ('Rovman Powell', 'Rahul Tripathi')
    ORDER BY player_name
""")
results = cursor.fetchall()

if results:
    for row in results:
        print(f"  {row[0]}: Rank {row[1]}")
else:
    print("  No matching players found")

print("\n" + "="*60)
print("✓ Verification Complete")
print("="*60 + "\n")

conn.close()
