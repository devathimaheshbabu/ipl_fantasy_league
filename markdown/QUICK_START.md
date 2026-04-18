# IPL Fantasy League - Quick Start Guide

## 🚀 First-Time Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements_selenium.txt
```

### Step 2: Scrape IPL Stats (if not done yet)
```bash
python ipl_scraper_selenium.py <your_mobile_number>
```

### Step 3: Run Fantasy League Pipeline
```bash
python run_fantasy_league.py
```

### Step 4: Preview Your Dashboard
```bash
# Open in browser
start docs/index.html  # Windows
open docs/index.html   # Mac
```

---

## 🌐 GitHub Pages Setup (One-Time, 10 minutes)

### Step 1: Initialize Git
```bash
git init
git add .
git commit -m "Initial fantasy league setup"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ipl-fantasy-league`
3. Public or Private (your choice)
4. Do NOT initialize with README
5. Click "Create repository"

### Step 3: Connect and Push
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ipl-fantasy-league.git
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages
1. Go to repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` → `/docs` → Save
4. Wait 1-2 minutes

### Step 5: Get Your URL
```
https://YOUR_USERNAME.github.io/ipl-fantasy-league/
```

Share this URL with friends! It's live 24/7.

---

## 📅 Regular Updates (After Each Match)

### Quick Update (3 commands)
```bash
# 1. Update stats
python ipl_scraper_selenium.py <mobile>

# 2. Calculate points & generate dashboard
python run_fantasy_league.py

# 3. Deploy to web
python deploy_to_github.py
```

### If Making Team Changes
```bash
# 1. Edit Excel file
# Open: input_data/Player_details_team_level.xlsx
# Change captain, VC, or rankings
# Save

# 2. Run pipeline (detects changes automatically)
python run_fantasy_league.py

# 3. Deploy
python deploy_to_github.py
```

---

## 📊 Useful Commands

### View Current Team State
```bash
python test_change_detection.py
```

### Check Database
```bash
# Using SQLite CLI
sqlite3 ipl_stats.db

# Show tables
.tables

# View team
SELECT * FROM fantasy_teams;

# View players
SELECT player_name, role, player_ranking
FROM fantasy_team_players
ORDER BY player_ranking;

# Exit
.quit
```

### View Scraped Stats
```bash
python view_stats.py --limit 20
```

### Check Change History
```bash
sqlite3 ipl_stats.db "SELECT * FROM player_change_history;"
```

---

## ⚙️ Configuration

### Change Team Name
Edit `run_fantasy_league.py` line 34:
```python
team_name = "YOUR_TEAM_NAME"
```

### Change Excel Path
Edit `run_fantasy_league.py` line 35:
```python
excel_path = "your/path/to/excel.xlsx"
```

### Customize Dashboard Colors
Edit `web_generator.py` - look for:
```python
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
Replace with your preferred colors.

---

## 🔧 Troubleshooting

### Problem: "Excel file not found"
```bash
# Check file exists
ls input_data/Player_details_team_level.xlsx

# If missing, ensure you have the Excel file with correct columns
```

### Problem: "No players in database"
```bash
# Run scraper first
python ipl_scraper_selenium.py <mobile_number>
```

### Problem: "Unicode error on Windows"
```bash
# Already fixed! If still occurs:
chcp 65001
python run_fantasy_league.py
```

### Problem: "Git push failed"
```bash
# Check remote
git remote -v

# Re-add if needed
git remote remove origin
git remote add origin https://github.com/USERNAME/repo.git
```

### Problem: "GitHub Pages not showing"
1. Check Settings → Pages is enabled
2. Ensure Source is set to: main branch, /docs folder
3. Wait 1-2 minutes for deployment
4. Clear browser cache
5. Try incognito/private window

---

## 📱 Excel File Format

### Required Columns (Order matters!)
| Column | Name | Values |
|--------|------|--------|
| A | Player Name | "Nicholas Pooran" |
| B | IPL Team | "LSG" |
| C | Fantasy Team | "Mahesh Thunder Buddies" |
| D | Role | "Captain", "Vice-Captain", or "Player" |
| E | Player Ranking | 1-20 (numbers only) |

### Rules
- **20 players total**
- **Rank 1-15:** Playing squad (top 11 selected automatically)
- **Rank 16-20:** Bench (not contributing)
- **1 Captain:** 2x multiplier
- **1 Vice-Captain:** 1.5x multiplier
- **2 changes allowed** per season

---

## 📈 How Points Work

### Calculation
1. Get 15 players (rank 1-15)
2. Fetch official IPL points for each
3. Add any frozen points from role changes
4. Sort by total points
5. Select top 11 performers
6. Apply multipliers

### Example
```
Captain (Pooran): 77 official × 2 = 154 points
Vice-Captain (Klaasen): 337 official × 1.5 = 505.5 points
9 Regular Players: 1510 combined
-----------------------------------------
Total Team Points: 2169.5
```

### Frozen Points
When you change captain:
- Old captain's 2x points are frozen
- New captain starts fresh with 2x
- Old captain keeps frozen points forever

---

## 🎯 Common Tasks

### Task: Change Captain
1. Open Excel file
2. Find current captain row → Change "Captain" to "Player"
3. Find new captain row → Change "Player" to "Captain"
4. Save Excel
5. Run: `python run_fantasy_league.py`
6. System will detect change and freeze old captain's points

### Task: Swap Player Ranking
1. Open Excel file
2. Player A (rank 10) → Change to 18
3. Player B (rank 18) → Change to 10
4. Save Excel
5. Run: `python run_fantasy_league.py`
6. Points will transfer from A to B

### Task: View Dashboard Locally
```bash
start docs/index.html
```

### Task: Deploy to Web
```bash
python deploy_to_github.py
```

### Task: Check if Changes Counted
```bash
python test_change_detection.py
# Look at "Changes Used: X/2"
```

---

## 📚 Full Documentation

- **User Guide:** `README_FANTASY_LEAGUE.md`
- **Technical Details:** `IMPLEMENTATION_SUMMARY.md`
- **This File:** `QUICK_START.md`

---

## 💡 Tips

### Tip 1: Preview Before Deploying
Always open `docs/index.html` in browser to verify before deploying to GitHub.

### Tip 2: Commit Often
After each match update, commit to track history:
```bash
python deploy_to_github.py  # Does this automatically
```

### Tip 3: Backup Excel File
Keep a backup of your Excel file before making changes:
```bash
cp input_data/Player_details_team_level.xlsx input_data/backup_$(date +%Y%m%d).xlsx
```

### Tip 4: Test Changes First
Use `test_change_detection.py` to see current state before making changes.

### Tip 5: Keep Scraper Updated
Run scraper after every match to get latest points:
```bash
python ipl_scraper_selenium.py <mobile>
```

---

## ⚠️ Important Reminders

- ⚠️ **2 changes maximum** per season - plan carefully!
- ⚠️ **Role changes count** toward limit
- ⚠️ **Ranking swaps count** toward limit
- ⚠️ **Changes are permanent** - frozen points can't be unfrozen
- ⚠️ **Always save Excel** before running pipeline
- ⚠️ **Keep team name consistent** in Excel

---

## 🎉 Success Checklist

- [ ] Dependencies installed
- [ ] Stats scraped (259 players in database)
- [ ] Excel file prepared with 20 players
- [ ] Pipeline runs successfully
- [ ] Dashboard generated (docs/index.html)
- [ ] Git initialized
- [ ] GitHub repo created
- [ ] GitHub Pages enabled
- [ ] Website live and accessible
- [ ] URL shared with friends

---

## 📞 Getting Help

### If Something Breaks
1. Check error message
2. Review `README_FANTASY_LEAGUE.md` troubleshooting section
3. Run `test_change_detection.py` to see current state
4. Check database: `sqlite3 ipl_stats.db ".tables"`
5. Verify Excel file format

### Common Error Messages
- `"Excel file not found"` → Check file path
- `"No players in database"` → Run scraper first
- `"Git remote not found"` → Add remote URL
- `"Unicode error"` → Already fixed, update file

---

**You're all set! Enjoy your Fantasy League! 🏆**

For detailed information, see: `README_FANTASY_LEAGUE.md`
