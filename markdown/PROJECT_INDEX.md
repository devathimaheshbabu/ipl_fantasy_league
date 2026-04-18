# IPL Fantasy League - Project Index

## 📂 Project Structure

```
new_app/
│
├── 🎯 CORE SYSTEM FILES
│   ├── database.py                      [MODIFIED] Database management (extended)
│   ├── fantasy_league.py                [NEW] Fantasy league business logic
│   ├── web_generator.py                 [NEW] HTML dashboard generation
│   ├── run_fantasy_league.py            [NEW] Main pipeline orchestration
│   └── deploy_to_github.py              [NEW] GitHub Pages deployment
│
├── 🧪 TESTING & UTILITIES
│   ├── test_change_detection.py         [NEW] Test change tracking
│   ├── view_stats.py                    [EXISTING] View scraped stats
│   ├── ipl_scraper_selenium.py          [EXISTING] Stats scraper
│   └── ipl_scraper.py                   [EXISTING] Playwright scraper
│
├── 📚 DOCUMENTATION
│   ├── README_FANTASY_LEAGUE.md         [NEW] Complete user guide (400+ lines)
│   ├── QUICK_START.md                   [NEW] Quick reference guide
│   ├── IMPLEMENTATION_SUMMARY.md        [NEW] Technical implementation details
│   └── PROJECT_INDEX.md                 [NEW] This file
│
├── 🗄️  DATABASE
│   └── ipl_stats.db                     SQLite database (6 tables, 281 records)
│
├── 📊 INPUT DATA
│   └── input_data/
│       └── Player_details_team_level.xlsx  Your team roster (YOU EDIT THIS)
│
├── 🌐 OUTPUT (Generated)
│   └── docs/
│       └── index.html                   Generated dashboard for GitHub Pages
│
└── ⚙️  CONFIGURATION
    ├── requirements_selenium.txt        Python dependencies
    ├── requirements.txt                 Playwright dependencies
    └── setup_chromedriver.py            ChromeDriver setup utility
```

---

## 📋 File Reference Guide

### Core System Files

#### `database.py` (Modified)
- **Purpose**: SQLite database management
- **Original**: Player stats table
- **Added**: 4 fantasy league tables
- **Key Method**: `create_fantasy_tables()`
- **Size**: ~8 KB

#### `fantasy_league.py` (NEW - Main Logic)
- **Purpose**: Core fantasy league business logic
- **Lines**: 571 lines
- **Size**: 20 KB
- **Key Classes**:
  - `FantasyLeagueManager` - Main controller
- **Key Methods**:
  - `sync_excel_to_database()` - Sync roster from Excel
  - `calculate_team_points()` - Calculate points with multipliers
  - `detect_changes()` - Find captain/ranking changes
  - `get_frozen_points()` - Retrieve accumulated frozen points
- **Dependencies**: `sqlite3`, `openpyxl`, `json`

#### `web_generator.py` (NEW - Dashboard)
- **Purpose**: Generate HTML dashboard
- **Lines**: 314 lines
- **Size**: 12.5 KB
- **Key Function**: `generate_dashboard_html()`
- **Output**: `docs/index.html`
- **Features**:
  - Gradient purple theme
  - Responsive design
  - Captain/VC badges (gold/silver)
  - Change history timeline
  - Mobile-friendly

#### `run_fantasy_league.py` (NEW - Pipeline)
- **Purpose**: Main orchestration script
- **Lines**: 165 lines
- **Size**: 5.5 KB
- **Workflow**:
  1. Initialize database tables
  2. Sync Excel to database
  3. Calculate team points
  4. Generate HTML dashboard
- **Usage**: `python run_fantasy_league.py`

#### `deploy_to_github.py` (NEW - Deployment)
- **Purpose**: Deploy to GitHub Pages
- **Lines**: 183 lines
- **Size**: 6 KB
- **Features**:
  - Pre-flight checks (git, docs folder, remote)
  - Automatic commit/push
  - Branch detection (main/master)
  - Setup instructions
- **Usage**: `python deploy_to_github.py`

---

### Testing & Utilities

#### `test_change_detection.py` (NEW)
- **Purpose**: Test change tracking system
- **Lines**: 156 lines
- **Size**: 4.8 KB
- **Shows**:
  - Current team state
  - Captain/VC with points
  - Top 5 players by ranking
  - Recent change history
  - Testing instructions
- **Usage**: `python test_change_detection.py`

#### `view_stats.py` (Existing)
- **Purpose**: View scraped IPL stats
- **Usage**: `python view_stats.py --limit 20`

#### `ipl_scraper_selenium.py` (Existing)
- **Purpose**: Scrape IPL fantasy stats using Selenium
- **Usage**: `python ipl_scraper_selenium.py <mobile_number>`

---

### Documentation Files

#### `README_FANTASY_LEAGUE.md` (NEW - 400+ lines)
**Comprehensive user guide with:**
- Quick start instructions
- System architecture diagram
- GitHub Pages setup (step-by-step)
- Excel file format guide
- Database schema reference
- Point calculation logic with examples
- Change tracking explained
- Troubleshooting guide
- API reference
- Advanced usage (multiple teams, automation)

#### `QUICK_START.md` (NEW - Concise Guide)
**Quick reference with:**
- 5-minute first-time setup
- GitHub Pages setup (10 minutes)
- Regular update commands (3 commands)
- Common tasks (change captain, swap rankings)
- Configuration options
- Troubleshooting checklist
- Success checklist

#### `IMPLEMENTATION_SUMMARY.md` (NEW - Technical)
**Technical documentation with:**
- What was built (phase by phase)
- Code metrics (1,600+ lines)
- Testing results
- Statistics
- Current status
- Next steps
- Future enhancements

---

## 🗄️ Database Schema

### Table: `players` (Existing)
```sql
- id                INTEGER PRIMARY KEY
- player_name       TEXT NOT NULL
- team              TEXT
- credits           REAL
- total_points      INTEGER
- scraped_at        TIMESTAMP
```
**Purpose**: Official IPL fantasy stats (from scraper)
**Records**: 259 players

### Table: `fantasy_teams` (NEW)
```sql
- team_id           INTEGER PRIMARY KEY
- team_name         TEXT NOT NULL UNIQUE
- owner_name        TEXT
- changes_used      INTEGER DEFAULT 0
- changes_remaining INTEGER DEFAULT 2
- created_at        TIMESTAMP
```
**Purpose**: Team metadata
**Records**: 1 team

### Table: `fantasy_team_players` (NEW)
```sql
- ftp_id                INTEGER PRIMARY KEY
- team_id               INTEGER NOT NULL
- player_name           TEXT NOT NULL
- ipl_team              TEXT
- role                  TEXT (Captain/Vice-Captain/Player)
- player_ranking        INTEGER (1-20)
- is_in_playing_squad   INTEGER (1/0)
- added_at              TIMESTAMP
```
**Purpose**: Current roster with rankings
**Records**: 20 players

### Table: `player_change_history` (NEW)
```sql
- change_id         INTEGER PRIMARY KEY
- team_id           INTEGER NOT NULL
- player_name       TEXT NOT NULL
- change_type       TEXT (role_change/ranking_change)
- old_value         TEXT
- new_value         TEXT
- frozen_points     REAL
- change_detected_at TIMESTAMP
```
**Purpose**: Track all changes with frozen points
**Records**: 0 (no changes yet)

### Table: `team_points_history` (NEW)
```sql
- snapshot_id       INTEGER PRIMARY KEY
- team_id           INTEGER NOT NULL
- total_points      REAL
- top_11_players    TEXT (JSON)
- captain_name      TEXT
- captain_points    REAL
- vc_name           TEXT
- vc_points         REAL
- regular_points    REAL
- snapshot_at       TIMESTAMP
```
**Purpose**: Daily point calculation snapshots
**Records**: 1 snapshot

---

## 📊 Current Data Status

### Database Statistics
- **Total Tables**: 6
- **Total Records**: 281
- **Database Size**: ~200 KB
- **Last Updated**: 2026-04-17

### Team Statistics
- **Team Name**: Mahesh Thunder Buddies
- **Total Players**: 20
- **Playing Squad**: 15 (rank 1-15)
- **Bench Players**: 5 (rank 16-20)
- **Captain**: Nicholas Pooran (77 pts × 2 = 154)
- **Vice-Captain**: Heinrich Klaasen (337 pts × 1.5 = 505.5)
- **Total Team Points**: 2,169.5
- **Changes Used**: 0/2

---

## 🔄 Data Flow

```
1. ipl_scraper_selenium.py
   ↓
   Updates: players table (259 official fantasy stats)

2. input_data/Player_details_team_level.xlsx
   ↓ (user edits captain, VC, rankings)

3. run_fantasy_league.py
   ↓
   Reads Excel → Detects changes → Updates fantasy tables
   ↓
   Calculates points → Selects top 11 → Applies multipliers
   ↓
   Generates docs/index.html

4. deploy_to_github.py
   ↓
   Git add/commit/push → GitHub Pages
   ↓
   Live at: https://username.github.io/ipl-fantasy-league/
```

---

## 🎯 Key Algorithms

### Top 11 Selection Algorithm
```
1. Get 15 players (ranking 1-15)
2. Fetch official IPL points for each
3. Add frozen points from change history
4. Adjusted points = official + frozen
5. Sort by adjusted points (descending)
6. Select top 11
7. Apply multipliers:
   - Captain: adjusted × 2
   - Vice-Captain: adjusted × 1.5
   - Others: adjusted × 1
8. Sum all multiplied points
```

### Change Detection Algorithm
```
1. Read current state from fantasy_team_players
2. Read new state from Excel
3. Compare each player:
   a. Role changed? → Calculate frozen points
   b. Ranking changed? → Check if crossed 15 threshold
4. Record changes in player_change_history
5. Increment changes_used counter
6. Update fantasy_team_players with new state
```

### Frozen Points Calculation
```
When role changes (e.g., Captain → Player):
  official_points = get from players table
  existing_frozen = sum from player_change_history
  adjusted = official + existing_frozen

  if old_role == "Captain":
    frozen_points = adjusted × 2
  elif old_role == "Vice-Captain":
    frozen_points = adjusted × 1.5
  else:
    frozen_points = adjusted

  Store frozen_points in player_change_history
```

---

## ⚙️ Configuration Options

### Team Name
**File**: `run_fantasy_league.py` line 34
```python
team_name = "Mahesh Thunder Buddies"  # Change this
```

### Excel Path
**File**: `run_fantasy_league.py` line 35
```python
excel_path = "input_data/Player_details_team_level.xlsx"
```

### Database Path
**File**: All scripts use default
```python
db_path = "ipl_stats.db"  # Can be changed if needed
```

### Output Directory
**File**: `run_fantasy_league.py` line 37
```python
output_dir = "docs"  # GitHub Pages requires this
```

### Dashboard Colors
**File**: `web_generator.py` line 16
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 🚀 Quick Command Reference

### Initial Setup
```bash
pip install -r requirements_selenium.txt
python ipl_scraper_selenium.py <mobile>
python run_fantasy_league.py
```

### Regular Updates
```bash
python ipl_scraper_selenium.py <mobile>
python run_fantasy_league.py
python deploy_to_github.py
```

### Testing
```bash
python test_change_detection.py
python view_stats.py --limit 20
sqlite3 ipl_stats.db ".tables"
```

### Viewing
```bash
start docs/index.html                # Open dashboard
sqlite3 ipl_stats.db                 # Open database
```

---

## 📈 Success Metrics

- [x] All 6 files created successfully
- [x] Database with 6 tables operational
- [x] 20-player roster synced from Excel
- [x] Points calculated: 2,169.5 total
- [x] HTML dashboard generated (10.8 KB)
- [x] Change tracking system ready
- [x] Documentation complete (3 guides)
- [x] Testing tools provided
- [x] Windows UTF-8 encoding handled
- [x] All verification tests passed

---

**System Status: PRODUCTION READY** ✅

For detailed usage, see `README_FANTASY_LEAGUE.md`
For quick reference, see `QUICK_START.md`
For technical details, see `IMPLEMENTATION_SUMMARY.md`
