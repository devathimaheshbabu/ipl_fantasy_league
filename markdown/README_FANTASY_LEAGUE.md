# IPL Fantasy League System

A complete fantasy league management system for custom IPL competitions with friends. Transforms the IPL stats scraper into a full-featured fantasy platform with GitHub Pages hosting.

## Features

- 🏆 **Custom Team Management**: 20-player roster with Captain/Vice-Captain roles
- 📊 **Automatic Point Calculation**: Top 11 performers from 15 selected players
- 🎯 **Multipliers**: Captain (2x), Vice-Captain (1.5x)
- 🔄 **Change Tracking**: Monitor player role swaps and ranking changes (2 changes per season)
- 🌐 **Web Dashboard**: Beautiful HTML interface hosted FREE on GitHub Pages
- 📱 **Mobile-Friendly**: Responsive design works on all devices

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: Scrape Official IPL Stats                            │
│ python ipl_scraper_selenium.py <mobile_number>                │
│ ↓ Updates: players table (official fantasy points)            │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 2: Sync Excel Roster to Database                        │
│ python run_fantasy_league.py                                  │
│ ↓ Reads: input_data/Player_details_team_level.xlsx           │
│ ↓ Detects: Captain/VC changes, ranking swaps                 │
│ ↓ Updates: fantasy_team_players, player_change_history       │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 3: Calculate Team Points                                │
│ ↓ Select top 11 from 15 playing squad                        │
│ ↓ Apply multipliers: Captain 2x, VC 1.5x                     │
│ ↓ Handle frozen points from role changes                     │
│ ↓ Save snapshot to: team_points_history                      │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 4: Generate HTML Dashboard                              │
│ ↓ Create: docs/index.html                                    │
│ ↓ Shows: Top 11, points breakdown, change history            │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 5: Deploy to GitHub Pages                               │
│ python deploy_to_github.py                                    │
│ ↓ Live at: https://username.github.io/ipl-fantasy-league/    │
└────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Initial Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements_selenium.txt
   ```

2. **Scrape IPL Stats** (first time)
   ```bash
   python ipl_scraper_selenium.py <your_mobile_number>
   ```

3. **Prepare Your Team Roster**
   - Edit `input_data/Player_details_team_level.xlsx`
   - Columns: Player Name, IPL Team, Fantasy Team, Role, Player Ranking
   - Set roles: Captain, Vice-Captain, Player
   - Rank 1-15: Playing squad (top 11 selected from these)
   - Rank 16-20: Bench players

4. **Run Fantasy League Pipeline**
   ```bash
   python run_fantasy_league.py
   ```

5. **Preview Dashboard**
   - Open `docs/index.html` in your browser

### Regular Updates (After Each Match)

```bash
# Step 1: Update official stats
python ipl_scraper_selenium.py <mobile_number>

# Step 2: (Optional) Update team roster in Excel if making changes

# Step 3: Calculate points and generate dashboard
python run_fantasy_league.py

# Step 4: Deploy to web
python deploy_to_github.py
```

## GitHub Pages Setup (One-Time)

### 1. Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Create repository on GitHub.com
# Name: ipl-fantasy-league

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ipl-fantasy-league.git

# First commit
git add .
git commit -m "Initial fantasy league setup"
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Under "Source", select: **Deploy from a branch**
3. Under "Branch", select: **main** → **/docs** → **Save**
4. Wait 1-2 minutes for deployment

### 3. Access Your Website

Your dashboard will be live at:
```
https://YOUR_USERNAME.github.io/ipl-fantasy-league/
```

Share this URL with friends - it's accessible 24/7, even when your laptop is off!

## Excel File Format

### Required Columns

| Player Name | IPL Team | Fantasy Team | Role | Player Ranking |
|-------------|----------|--------------|------|----------------|
| Nicholas Pooran | LSG | Mahesh Thunder Buddies | Captain | 1 |
| Heinrich Klaasen | SRH | Mahesh Thunder Buddies | Vice-Captain | 2 |
| Dewald Brevis | CSK | Mahesh Thunder Buddies | Player | 3 |
| ... | ... | ... | ... | ... |

### Rules

- **20 players total** per team
- **Ranking 1-15**: Playing squad (top 11 performers selected automatically)
- **Ranking 16-20**: Bench players (not contributing to team points)
- **1 Captain**: Gets 2x points multiplier
- **1 Vice-Captain**: Gets 1.5x points multiplier
- **2 changes allowed** per season total

## Database Schema

### Tables

1. **players** - Official IPL fantasy stats (from scraper)
2. **fantasy_teams** - Team metadata
3. **fantasy_team_players** - Current roster
4. **player_change_history** - Change tracking with frozen points
5. **team_points_history** - Daily snapshots

### Viewing Database

```bash
# Open database
sqlite3 ipl_stats.db

# Show tables
.tables

# Check team stats
SELECT * FROM fantasy_teams;

# View top players
SELECT player_name, role, player_ranking
FROM fantasy_team_players
ORDER BY player_ranking LIMIT 10;

# Exit
.quit
```

## Point Calculation Logic

### Top 11 Selection

1. Get 15 players with ranking 1-15 (playing squad)
2. Fetch current official IPL fantasy points for each
3. Add any frozen points from previous role changes
4. Sort by adjusted points (official + frozen)
5. Select top 11 performers

### Multipliers

- **Captain**: Points × 2
- **Vice-Captain**: Points × 1.5
- **Regular Players**: Points × 1

### Example

```
Captain (Pooran): 77 official points
  → 77 × 2 = 154 team points

Vice-Captain (Klaasen): 337 official points
  → 337 × 1.5 = 505.5 team points

9 Regular Players: 1510 combined points

Total Team Points: 154 + 505.5 + 1510 = 2169.5
```

## Change Tracking

### Types of Changes

1. **Role Changes** (Captain/VC swap)
   - When captain changes, old captain's multiplied points are frozen
   - New captain starts fresh with 2x multiplier
   - Counts as 1 change

2. **Ranking Swaps**
   - Moving player between playing squad (1-15) and bench (16-20)
   - Counts as 1 change
   - **Point Transfer**: When Player A (bench) swaps with Player B (playing squad), Player A inherits Player B's accumulated points

### Example: Role Change

**Before:**
- Pooran (Captain): 500 official points × 2 = 1000 team points

**User Changes Captain to Butler:**
- Pooran's 1000 points are frozen
- Butler becomes captain with 2x multiplier going forward
- Pooran's frozen 1000 points added to his future contributions

### Viewing Changes

The web dashboard shows all changes with timestamps and frozen points.

## File Structure

```
new_app/
├── database.py                          # Database management (extended)
├── fantasy_league.py                    # Core fantasy league logic (NEW)
├── web_generator.py                     # HTML generation (NEW)
├── run_fantasy_league.py                # Main pipeline (NEW)
├── deploy_to_github.py                  # GitHub deployment (NEW)
├── ipl_scraper_selenium.py              # Stats scraper (existing)
├── ipl_stats.db                         # SQLite database
├── input_data/
│   └── Player_details_team_level.xlsx   # Team roster (YOU EDIT THIS)
├── docs/
│   └── index.html                       # Generated dashboard
└── requirements_selenium.txt            # Dependencies
```

## Troubleshooting

### Pipeline Fails: "Excel file not found"

```bash
# Check file exists
ls input_data/Player_details_team_level.xlsx

# Verify path in run_fantasy_league.py
# Should be: excel_path = "input_data/Player_details_team_level.xlsx"
```

### No Players in Database

```bash
# Run scraper first
python ipl_scraper_selenium.py <mobile_number>

# Verify data
python view_stats.py --limit 10
```

### Unicode Error on Windows

The system automatically handles Windows encoding. If you still see errors:

```bash
# Run with UTF-8
chcp 65001
python run_fantasy_league.py
```

### GitHub Push Fails

```bash
# Check remote
git remote -v

# Re-add remote
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/ipl-fantasy-league.git

# Push with credentials
git push -u origin main
```

## Advanced Usage

### Multiple Teams

To support multiple teams, modify `run_fantasy_league.py`:

```python
teams = [
    "Mahesh Thunder Buddies",
    "Rohan's XI",
    "Amit's Warriors"
]

for team_name in teams:
    summary = sync_excel_to_database(excel_path, team_name)
    points_data = calculate_team_points(team_name)
    # Generate separate HTML for each team
```

### Automated Scheduling

Use Windows Task Scheduler or cron to run automatically:

```bash
# Daily at 11 PM
# Windows Task Scheduler: run run_fantasy_league.py

# Linux/Mac cron
0 23 * * * cd /path/to/new_app && python run_fantasy_league.py
```

### Custom Dashboard Styling

Edit `web_generator.py` to customize colors, fonts, layout:

```python
# Change gradient colors
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);

# Modify table styles
.player-table thead {
    background: YOUR_GRADIENT;
}
```

## API Reference

### FantasyLeagueManager

```python
from fantasy_league import FantasyLeagueManager

manager = FantasyLeagueManager("ipl_stats.db")
manager.connect()

# Sync Excel to database
summary = manager.sync_excel_to_database(excel_path, team_name)

# Calculate points
points_data = manager.calculate_team_points(team_name)

# Save snapshot
manager.save_points_snapshot(points_data)

# Get change history
changes = manager.get_change_history(team_name, limit=10)

manager.close()
```

### Convenience Functions

```python
from fantasy_league import sync_excel_to_database, calculate_team_points

# One-line sync
summary = sync_excel_to_database("input_data/Player_details_team_level.xlsx", "Team Name")

# One-line calculate
points = calculate_team_points("Team Name")
```

## Contributing

Found a bug or want to add features? Please:

1. Test your changes thoroughly
2. Follow existing code style
3. Update documentation
4. Add test cases if applicable

## Support

For issues or questions:

1. Check this README first
2. Review error messages carefully
3. Verify all files are in correct locations
4. Ensure dependencies are installed

## License

MIT License - Free to use and modify

## Credits

- **IPL Stats Scraper**: Selenium-based web scraping
- **Database**: SQLite3
- **Web Hosting**: GitHub Pages (free)
- **Developed by**: Claude Code (Anthropic)

---

**Enjoy your IPL Fantasy League! 🏆**
