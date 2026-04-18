"""
IPL Stats Database Manager
===========================
This module handles SQLite database operations for storing IPL player statistics.

Features:
- Creates SQLite database and table automatically
- Stores player stats with timestamp
- Replaces old data with fresh data on each run (snapshot mode)

Author: Claude Code
Date: 2026-04-17
"""

import sqlite3
from datetime import datetime
from pathlib import Path


class IPLStatsDatabase:
    """
    Database manager for IPL Fantasy player statistics.

    This class handles:
    - SQLite database initialization
    - Table creation with proper schema
    - Data insertion with timestamps
    - Connection management
    """

    def __init__(self, db_path="ipl_stats.db"):
        """
        Initialize database manager.

        Args:
            db_path (str): Path to SQLite database file (default: "ipl_stats.db")
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Create connection to SQLite database.

        Creates the database file if it doesn't exist.
        """
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {self.db_path}")

    def create_table(self):
        """
        Create players table if it doesn't exist.

        Table Schema:
            - id: Auto-incrementing primary key
            - player_name: Player's full name (TEXT)
            - team: Team abbreviation like RCB, SRH (TEXT)
            - credits: Fantasy value/price (REAL for decimal values)
            - total_points: Season fantasy points (INTEGER)
            - scraped_at: Timestamp when data was scraped (TIMESTAMP)
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            team TEXT,
            credits REAL,
            total_points INTEGER,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        self.cursor.execute(create_table_query)
        self.connection.commit()
        print("Table 'players' ready")

    def clear_table(self):
        """
        Delete all existing records from players table.

        This is used in snapshot mode to replace old data with fresh data.
        """
        self.cursor.execute("DELETE FROM players")
        self.connection.commit()
        print("Cleared old data from table")

    def insert_players(self, data):
        """
        Insert player statistics into database.

        This method:
        1. Clears existing data (snapshot mode)
        2. Inserts fresh data with current timestamp
        3. Commits the transaction

        Args:
            data (list): 2D list with format:
                        [['Player Name', 'Team', 'Credits', 'Total Points'],  # Header row
                         ['Rajat Patidar', 'RCB', '9', '380'],
                         ['Ishan Kishan', 'SRH', '10.5', '367'],
                         ...]

        Returns:
            int: Number of players inserted
        """
        if not data or len(data) <= 1:
            print("No data to insert")
            return 0

        # Step 1: Clear old data (snapshot mode)
        self.clear_table()

        # Step 2: Prepare current timestamp
        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Step 3: Insert new data
        # data[0] is header row, so skip it with data[1:]
        insert_query = """
        INSERT INTO players (player_name, team, credits, total_points, scraped_at)
        VALUES (?, ?, ?, ?, ?)
        """

        players_inserted = 0
        for row in data[1:]:  # Skip header row
            try:
                player_name = row[0]
                team = row[1]
                credits = float(row[2]) if row[2] else None
                total_points = int(row[3]) if row[3] else None

                self.cursor.execute(insert_query, (player_name, team, credits, total_points, scraped_at))
                players_inserted += 1

            except Exception as e:
                print(f"Error inserting player {row[0]}: {e}")
                continue

        # Step 4: Commit transaction
        self.connection.commit()
        print(f"Inserted {players_inserted} players into database")

        return players_inserted

    def get_stats_summary(self):
        """
        Get summary statistics from the database.

        Returns:
            dict: Summary with total players, last scraped time, etc.
        """
        # Count total players
        self.cursor.execute("SELECT COUNT(*) FROM players")
        total_players = self.cursor.fetchone()[0]

        # Get last scraped timestamp
        self.cursor.execute("SELECT MAX(scraped_at) FROM players")
        last_scraped = self.cursor.fetchone()[0]

        return {
            "total_players": total_players,
            "last_scraped": last_scraped,
            "database_path": self.db_path
        }

    def display_sample(self, limit=5):
        """
        Display sample records from the database.

        Args:
            limit (int): Number of records to display (default: 5)
        """
        query = f"SELECT player_name, team, credits, total_points, scraped_at FROM players LIMIT {limit}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        if rows:
            print(f"\nSample data (showing {len(rows)} records):")
            print("-" * 80)
            print(f"{'Player Name':<25} {'Team':<8} {'Credits':<10} {'Points':<10} {'Scraped At'}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<25} {row[1]:<8} {row[2]:<10} {row[3]:<10} {row[4]}")
            print("-" * 80)
        else:
            print("No data in database")

    def create_fantasy_tables(self):
        """
        Create fantasy league tables for custom team management.

        Creates 4 tables:
        1. fantasy_teams - Team metadata
        2. fantasy_team_players - Current team roster
        3. player_change_history - Change tracking with frozen points
        4. team_points_history - Daily snapshots of team points
        """
        # Table 1: Fantasy Teams
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS fantasy_teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL UNIQUE,
            owner_name TEXT,
            changes_used INTEGER DEFAULT 0,
            changes_remaining INTEGER DEFAULT 2,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Table 2: Fantasy Team Players (current state)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS fantasy_team_players (
            ftp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            ipl_team TEXT,
            role TEXT NOT NULL CHECK(role IN ('Captain', 'Vice-Captain', 'Player')),
            player_ranking INTEGER NOT NULL CHECK(player_ranking BETWEEN 1 AND 20),
            is_in_playing_squad INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES fantasy_teams(team_id),
            UNIQUE(team_id, player_name)
        )
        """)

        # Table 3: Player Change History
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_change_history (
            change_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            frozen_points REAL DEFAULT 0,
            change_detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES fantasy_teams(team_id)
        )
        """)

        # Table 4: Team Points History
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_points_history (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            total_points REAL,
            top_11_players TEXT,
            captain_name TEXT,
            captain_points REAL,
            vc_name TEXT,
            vc_points REAL,
            regular_points REAL,
            snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES fantasy_teams(team_id)
        )
        """)

        self.connection.commit()
        print("Fantasy league tables ready")

    def close(self):
        """
        Close database connection.

        Should always be called at the end to properly close the connection.
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed")


# ============================================================================
# Helper Functions
# ============================================================================

def save_to_database(data, db_path="ipl_stats.db"):
    """
    Convenience function to save scraped data to SQLite database.

    This function:
    1. Connects to database
    2. Creates table if needed
    3. Inserts data
    4. Shows summary
    5. Closes connection

    Args:
        data (list): 2D list with player statistics (header + data rows)
        db_path (str): Path to database file (default: "ipl_stats.db")

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = IPLStatsDatabase(db_path)
        db.connect()
        db.create_table()

        players_inserted = db.insert_players(data)

        if players_inserted > 0:
            # Show summary
            summary = db.get_stats_summary()
            print(f"\nDatabase Summary:")
            print(f"  Total Players: {summary['total_players']}")
            print(f"  Last Scraped: {summary['last_scraped']}")
            print(f"  Database: {summary['database_path']}")

            # Show sample data
            db.display_sample(limit=5)

            db.close()
            return True
        else:
            db.close()
            return False

    except Exception as e:
        print(f"Database error: {e}")
        return False


# ============================================================================
# Main Execution Block (For Testing)
# ============================================================================

if __name__ == "__main__":
    # Test the database module
    print("Testing IPL Stats Database...\n")

    # Sample test data
    test_data = [
        ['Player Name', 'Team', 'Credits', 'Total Points'],
        ['Rajat Patidar', 'RCB', '9', '380'],
        ['Ishan Kishan', 'SRH', '10.5', '367'],
        ['Yashasvi Jaiswal', 'RR', '9', '356']
    ]

    # Test saving to database
    success = save_to_database(test_data, db_path="test_ipl_stats.db")

    if success:
        print("\nTest successful!")
    else:
        print("\nTest failed!")
