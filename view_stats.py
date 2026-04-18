"""
View IPL Stats from Database
=============================
Simple script to query and display IPL player statistics from SQLite database.

Usage:
    python view_stats.py                    # View all players
    python view_stats.py --limit 10        # View top 10 players
    python view_stats.py --team RCB        # View RCB players only
    python view_stats.py --player "Virat"  # Search for player

Author: Claude Code
Date: 2026-04-17
"""

import sqlite3
import sys
from pathlib import Path


def view_all_stats(db_path="ipl_stats.db", limit=None, team=None, player=None):
    """
    Display player statistics from the database.

    Args:
        db_path (str): Path to SQLite database
        limit (int): Maximum number of records to show
        team (str): Filter by team (e.g., 'RCB', 'SRH')
        player (str): Search for player by name (partial match)
    """
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        print("\nPlease run the scraper first:")
        print("  python ipl_scraper_selenium.py <mobile_number>")
        print("  OR")
        print("  python ipl_scraper.py <mobile_number>")
        return

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build query with filters
    query = "SELECT player_name, team, credits, total_points, scraped_at FROM players"
    conditions = []
    params = []

    if team:
        conditions.append("team = ?")
        params.append(team.upper())

    if player:
        conditions.append("player_name LIKE ?")
        params.append(f"%{player}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Order by total points descending
    query += " ORDER BY total_points DESC"

    if limit:
        query += f" LIMIT {limit}"

    # Execute query
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM players")
    total_count = cursor.fetchone()[0]

    # Get last scraped time
    cursor.execute("SELECT MAX(scraped_at) FROM players")
    last_scraped = cursor.fetchone()[0]

    # Display results
    print("\n" + "=" * 90)
    print(f"IPL Fantasy Player Statistics")
    print("=" * 90)
    print(f"Total Players in Database: {total_count}")
    print(f"Last Scraped: {last_scraped}")
    print(f"Showing: {len(rows)} players")
    print("=" * 90)

    if rows:
        print(f"\n{'Rank':<6} {'Player Name':<30} {'Team':<6} {'Credits':<10} {'Points':<10}")
        print("-" * 90)
        for idx, row in enumerate(rows, 1):
            print(f"{idx:<6} {row[0]:<30} {row[1]:<6} {row[2]:<10} {row[3]:<10}")
        print("-" * 90)
    else:
        print("\nNo players found matching your criteria.")

    conn.close()


def show_summary(db_path="ipl_stats.db"):
    """Display database summary statistics."""
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total players
    cursor.execute("SELECT COUNT(*) FROM players")
    total_players = cursor.fetchone()[0]

    # Last scraped
    cursor.execute("SELECT MAX(scraped_at) FROM players")
    last_scraped = cursor.fetchone()[0]

    # Top scorer
    cursor.execute("SELECT player_name, total_points FROM players ORDER BY total_points DESC LIMIT 1")
    top_scorer = cursor.fetchone()

    # Average points
    cursor.execute("SELECT AVG(total_points) FROM players")
    avg_points = cursor.fetchone()[0]

    # Teams count
    cursor.execute("SELECT COUNT(DISTINCT team) FROM players WHERE team != 'N/A'")
    teams_count = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("Database Summary")
    print("=" * 60)
    print(f"Total Players:     {total_players}")
    print(f"Teams:             {teams_count}")
    print(f"Last Scraped:      {last_scraped}")
    if top_scorer:
        print(f"Top Scorer:        {top_scorer[0]} ({top_scorer[1]} points)")
    if avg_points:
        print(f"Average Points:    {avg_points:.1f}")
    print("=" * 60)

    conn.close()


def show_teams(db_path="ipl_stats.db"):
    """Display all teams with player counts."""
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team, COUNT(*) as player_count, AVG(total_points) as avg_points
        FROM players
        WHERE team != 'N/A'
        GROUP BY team
        ORDER BY avg_points DESC
    """)

    rows = cursor.fetchall()

    print("\n" + "=" * 60)
    print("Team Statistics")
    print("=" * 60)
    print(f"{'Team':<10} {'Players':<10} {'Avg Points':<15}")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:<10} {row[1]:<10} {row[2]:<15.1f}")
    print("-" * 60)

    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="View IPL player statistics from database")
    parser.add_argument("--db", default="ipl_stats.db", help="Database file path")
    parser.add_argument("--limit", type=int, help="Maximum number of players to show")
    parser.add_argument("--team", help="Filter by team (e.g., RCB, SRH)")
    parser.add_argument("--player", help="Search for player by name")
    parser.add_argument("--summary", action="store_true", help="Show database summary")
    parser.add_argument("--teams", action="store_true", help="Show team statistics")

    args = parser.parse_args()

    if args.summary:
        show_summary(args.db)
    elif args.teams:
        show_teams(args.db)
    else:
        view_all_stats(args.db, args.limit, args.team, args.player)
