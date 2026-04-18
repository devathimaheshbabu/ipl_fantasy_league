"""
IPL Fantasy League Web Generator
=================================
Generates static HTML dashboard for GitHub Pages hosting.

Features:
- Clean, responsive HTML design
- Player table with top 11 performers
- Point breakdown visualization
- Change history log
- Mobile-friendly layout

Author: Claude Code
Date: 2026-04-17
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')


def generate_dashboard_html(team_name, points_data, change_history, team_stats, output_dir="docs"):
    """
    Generate complete HTML dashboard for fantasy team.

    Args:
        team_name (str): Fantasy team name
        points_data (dict): Points breakdown from calculate_team_points()
        change_history (list): Recent changes
        team_stats (dict): Team metadata (changes used, etc.)
        output_dir (str): Output directory for HTML files
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team_name} - IPL Fantasy League</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 30px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .update-time {{
            color: #666;
            font-size: 0.9em;
        }}

        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}

        .stat-box h2 {{
            font-size: 1em;
            margin-bottom: 10px;
            opacity: 0.9;
        }}

        .big-number {{
            font-size: 2.5em;
            font-weight: bold;
        }}

        .section-title {{
            color: #667eea;
            font-size: 1.8em;
            margin: 30px 0 20px 0;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}

        .player-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 0.9em;
        }}

        .player-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .player-table th {{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }}

        .player-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }}

        .player-table tbody tr:hover {{
            background: #f5f7ff;
        }}

        .role-Captain {{
            background: #ffd700;
            color: #333;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.85em;
        }}

        .role-Vice-Captain {{
            background: #c0c0c0;
            color: #333;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.85em;
        }}

        .role-Player {{
            color: #666;
            padding: 3px 8px;
            font-size: 0.85em;
        }}

        .points {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}

        .change-log {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .change-item {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}

        .change-item:last-child {{
            border-bottom: none;
        }}

        .change-date {{
            color: #999;
            font-size: 0.85em;
        }}

        .change-description {{
            color: #333;
            margin-top: 5px;
        }}

        .no-changes {{
            color: #999;
            font-style: italic;
        }}

        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            .player-table {{
                font-size: 0.85em;
            }}

            .player-table th,
            .player-table td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{team_name}</h1>
            <p class="update-time">Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>

        <div class="stats-summary">
            <div class="stat-box">
                <h2>Total Points</h2>
                <p class="big-number">{points_data['total_points']:.0f}</p>
            </div>
            <div class="stat-box">
                <h2>Captain Points</h2>
                <p class="big-number">{points_data['captain_points']:.0f}</p>
                <p style="font-size: 0.9em; margin-top: 5px;">{points_data['captain_name']}</p>
            </div>
            <div class="stat-box">
                <h2>Vice-Captain Points</h2>
                <p class="big-number">{points_data['vc_points']:.0f}</p>
                <p style="font-size: 0.9em; margin-top: 5px;">{points_data['vc_name']}</p>
            </div>
            <div class="stat-box">
                <h2>Changes Used</h2>
                <p class="big-number">{team_stats['changes_used']} / 2</p>
            </div>
        </div>

        <h2 class="section-title">🏆 Top 11 Players</h2>
        <table class="player-table">
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Role</th>
                    <th>IPL Team</th>
                    <th>Official Points</th>
                    <th>Frozen Points</th>
                    <th>Multiplier</th>
                    <th>Team Points</th>
                </tr>
            </thead>
            <tbody>
"""

    # Add top 11 players
    for player in points_data['top_11_players']:
        frozen_display = f"{player['frozen_points']:.0f}" if player['frozen_points'] > 0 else "-"
        html_content += f"""
                <tr>
                    <td><strong>{player['player_name']}</strong></td>
                    <td><span class="role-{player['role'].replace(' ', '-')}">{player['role']}</span></td>
                    <td>{player['ipl_team']}</td>
                    <td>{player['official_points']:.0f}</td>
                    <td>{frozen_display}</td>
                    <td>{player['multiplier']}x</td>
                    <td class="points">{player['team_points']:.0f}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>

        <h2 class="section-title">📝 Change History</h2>
        <div class="change-log">
"""

    if change_history:
        for change in change_history:
            change_desc = format_change_description(change)
            change_date = datetime.fromisoformat(change['change_detected_at']).strftime('%B %d, %Y at %I:%M %p')

            html_content += f"""
            <div class="change-item">
                <div class="change-date">{change_date}</div>
                <div class="change-description">{change_desc}</div>
            </div>
"""
    else:
        html_content += """
            <p class="no-changes">No changes recorded yet.</p>
"""

    html_content += f"""
        </div>

        <footer>
            <p><strong>{team_name}</strong> | IPL Fantasy League 2025</p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Powered by IPL Fantasy Stats Scraper | Updated automatically after each match
            </p>
        </footer>
    </div>
</body>
</html>
"""

    # Write HTML file
    html_file = output_path / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Dashboard generated: {html_file}")
    return html_file


def generate_multi_team_dashboard(all_teams_data, output_dir="docs"):
    """
    Generate combined HTML dashboard for multiple fantasy teams with visual comparisons.

    Args:
        all_teams_data (list): List of team data dictionaries containing:
            - team_name (str)
            - points_data (dict)
            - team_stats (dict)
            - change_history (list)
        output_dir (str): Output directory for HTML files

    Returns:
        Path: Path to generated HTML file
    """
    import sqlite3
    import json

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Sort teams by total points (descending)
    sorted_teams = sorted(all_teams_data, key=lambda x: x['points_data']['total_points'], reverse=True)

    # Calculate points gaps for leaderboard
    for i, team in enumerate(sorted_teams):
        if i == 0:
            team['points_gap'] = 0  # Leader has no gap
        else:
            team['points_gap'] = sorted_teams[i-1]['points_data']['total_points'] - team['points_data']['total_points']

    # Feature 1: Collect MVP data (top 15 players across all teams by adjusted points)
    all_players = []
    for team_data in all_teams_data:
        for player in team_data['points_data']['top_11_players']:
            all_players.append({
                'player_name': player['player_name'],
                'team_name': team_data['team_name'],
                'ipl_team': player['ipl_team'],
                'role': player['role'],
                'adjusted_points': player['adjusted_points'],  # Without multipliers
                'official_points': player['official_points'],
                'frozen_points': player['frozen_points']
            })

    # Sort by adjusted points and get top 15
    mvp_players = sorted(all_players, key=lambda x: x['adjusted_points'], reverse=True)[:15]

    # Feature 2: IPL Team Performance Analysis
    ipl_teams = {}
    for player in all_players:
        ipl_team = player['ipl_team']
        if ipl_team not in ipl_teams:
            ipl_teams[ipl_team] = {'total_points': 0, 'player_count': 0}
        ipl_teams[ipl_team]['total_points'] += player['adjusted_points']
        ipl_teams[ipl_team]['player_count'] += 1

    # Calculate averages and sort
    ipl_team_analysis = []
    for ipl_team, data in ipl_teams.items():
        avg_points = data['total_points'] / data['player_count']
        ipl_team_analysis.append({
            'ipl_team': ipl_team,
            'avg_points': avg_points,
            'total_points': data['total_points'],
            'player_count': data['player_count']
        })
    ipl_team_analysis = sorted(ipl_team_analysis, key=lambda x: x['avg_points'], reverse=True)

    # Feature 11: Points Progression (fetch from database)
    try:
        conn = sqlite3.connect('ipl_stats.db')
        cursor = conn.cursor()

        points_history = {}
        for team_data in all_teams_data:
            team_id = team_data['points_data']['team_id']
            cursor.execute("""
                SELECT snapshot_at, total_points
                FROM team_points_history
                WHERE team_id = ?
                ORDER BY snapshot_at ASC
            """, (team_id,))

            history = cursor.fetchall()
            if history:
                points_history[team_data['team_name']] = [
                    {'date': row[0], 'points': row[1]} for row in history
                ]

        conn.close()
    except Exception as e:
        print(f"Warning: Could not fetch points history: {e}")
        points_history = {}

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPL Fantasy League - Overall Standings</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 30px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .update-time {{
            color: #666;
            font-size: 0.9em;
        }}

        .section-title {{
            color: #667eea;
            font-size: 1.8em;
            margin: 40px 0 20px 0;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* Leaderboard Styles */
        .leaderboard {{
            display: grid;
            gap: 10px;
            margin-bottom: 30px;
        }}

        .leaderboard-item {{
            background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%);
            border-radius: 8px;
            padding: 12px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}

        .leaderboard-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 3px 12px rgba(102, 126, 234, 0.3);
        }}

        .leaderboard-item.rank-1 {{
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            border: 2px solid #ffa500;
        }}

        .leaderboard-item.rank-2 {{
            background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
            border: 2px solid #a0a0a0;
        }}

        .leaderboard-item.rank-3 {{
            background: linear-gradient(135deg, #cd7f32 0%, #e89f71 100%);
            border: 2px solid #b87333;
        }}

        .rank-badge {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            width: 45px;
            text-align: center;
        }}

        .rank-1 .rank-badge {{
            color: #ff8c00;
        }}

        .rank-2 .rank-badge {{
            color: #708090;
        }}

        .rank-3 .rank-badge {{
            color: #8b4513;
        }}

        .team-info {{
            flex: 1;
            padding: 0 15px;
        }}

        .team-name {{
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 4px;
        }}

        .team-details {{
            color: #666;
            font-size: 0.85em;
        }}

        .points-display {{
            text-align: right;
        }}

        .total-points {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}

        .points-label {{
            font-size: 0.8em;
            color: #666;
        }}

        /* Top Performers Grid */
        .performers-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .performer-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .performer-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}

        .performer-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 8px 0;
            background: #f9f9f9;
            border-radius: 5px;
        }}

        .performer-rank {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.2em;
            width: 30px;
        }}

        .performer-name {{
            flex: 1;
            padding: 0 10px;
        }}

        .performer-points {{
            font-weight: bold;
            color: #333;
        }}

        /* Comparison Table */
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 0.9em;
        }}

        .comparison-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .comparison-table th {{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }}

        .comparison-table tbody tr:hover {{
            background: #f5f7ff;
        }}

        .role-Captain {{
            background: #ffd700;
            color: #333;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.85em;
        }}

        .role-Vice-Captain {{
            background: #c0c0c0;
            color: #333;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.85em;
        }}

        .role-Player {{
            color: #666;
            padding: 3px 8px;
            font-size: 0.85em;
        }}

        .player-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 0.9em;
        }}

        .player-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .player-table th {{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }}

        .player-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }}

        .player-table tbody tr:hover {{
            background: #f5f7ff;
        }}

        .points {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}

        /* Team Section */
        .team-section {{
            margin: 40px 0;
            padding: 30px;
            background: #f9f9f9;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}

        .team-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .team-section-title {{
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }}

        .team-stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}

        .stat-box h3 {{
            font-size: 0.9em;
            margin-bottom: 10px;
            opacity: 0.9;
        }}

        .big-number {{
            font-size: 2em;
            font-weight: bold;
        }}

        .change-log {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-top: 20px;
        }}

        .change-item {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}

        .change-item:last-child {{
            border-bottom: none;
        }}

        .change-date {{
            color: #999;
            font-size: 0.85em;
        }}

        .change-description {{
            color: #333;
            margin-top: 5px;
        }}

        .no-changes {{
            color: #999;
            font-style: italic;
        }}

        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
        }}

        /* MVP Board Styles */
        .mvp-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 0.9em;
        }}

        .mvp-table thead {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
        }}

        .mvp-table th {{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }}

        .mvp-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }}

        .mvp-table tbody tr:hover {{
            background: #fff5f5;
        }}

        .mvp-rank {{
            font-weight: bold;
            color: #ff6b6b;
            font-size: 1.1em;
        }}

        /* IPL Team Analysis */
        .ipl-analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}

        .ipl-team-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .ipl-team-name {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .ipl-stat {{
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 0.9em;
        }}

        .ipl-bar {{
            height: 8px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            margin-top: 8px;
        }}

        /* Role Distribution */
        .role-selector {{
            margin: 20px 0;
            text-align: center;
        }}

        .role-selector select {{
            padding: 10px 20px;
            font-size: 1em;
            border: 2px solid #667eea;
            border-radius: 8px;
            background: white;
            color: #333;
            cursor: pointer;
            min-width: 250px;
        }}

        .role-chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}

        .role-bar {{
            margin: 15px 0;
        }}

        .role-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-weight: 600;
        }}

        .role-progress {{
            height: 30px;
            background: #f0f0f0;
            border-radius: 5px;
            overflow: hidden;
        }}

        .role-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}


        .waterfall-points-bar.leader {{
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #333;
            box-shadow: 0 3px 12px rgba(255, 215, 0, 0.4);
            height: 60px;
        }}

        .waterfall-points-bar::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: rgba(255, 255, 255, 0.3);
        }}

        .waterfall-team-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .waterfall-rank-badge {{
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.9em;
        }}

        .waterfall-points-bar.leader .waterfall-rank-badge {{
            background: rgba(0, 0, 0, 0.1);
        }}

        .waterfall-points-value {{
            font-size: 1.1em;
        }}

        /* Points Progression Chart */
        .progression-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}

        .chart-canvas {{
            width: 100%;
            height: 400px;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            .leaderboard-item {{
                flex-direction: column;
                text-align: center;
            }}

            .team-info {{
                padding: 15px 0;
            }}

            .comparison-table, .player-table {{
                font-size: 0.85em;
            }}

            .comparison-table th, .comparison-table td,
            .player-table th, .player-table td {{
                padding: 8px;
            }}

            .chart-canvas {{
                height: 300px;
            }}
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏆 IPL Fantasy League - Overall Standings</h1>
            <p class="update-time">Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>

        <!-- Overall Leaderboard -->
        <h2 class="section-title">📊 Overall Leaderboard</h2>
        <div class="leaderboard">
"""

    # Generate leaderboard items
    for rank, team_data in enumerate(sorted_teams, 1):
        points = team_data['points_data']
        stats = team_data['team_stats']
        points_gap = team_data.get('points_gap', 0)
        rank_class = f"rank-{rank}" if rank <= 3 else ""

        gap_text = ""
        if rank == 1:
            gap_text = '<span style="color: #28a745;">👑 Leader</span>'
        else:
            gap_text = f'<span style="color: #dc3545;">▼ {points_gap:.0f} pts behind</span>'

        html_content += f"""
            <div class="leaderboard-item {rank_class}">
                <div class="rank-badge">#{rank}</div>
                <div class="team-info">
                    <div class="team-name">{team_data['team_name']}</div>
                    <div class="team-details">
                        Captain: {points['captain_name']} |
                        Vice-Captain: {points['vc_name']} |
                        Changes: {stats['changes_used']}/2 |
                        {gap_text}
                    </div>
                </div>
                <div class="points-display">
                    <div class="total-points">{points['total_points']}</div>
                    <div class="points-label">Total Points</div>
                </div>
            </div>
"""

    # Top 3 Performers from Each Team (by adjusted points, without multipliers)
    html_content += """
        </div>

        <h2 class="section-title">⭐ Top 3 Performers from Each Team</h2>
        <div class="performers-grid">
"""

    for team_data in sorted_teams:
        top_players = sorted(
            team_data['points_data']['top_11_players'],
            key=lambda x: x['adjusted_points'],  # Use adjusted points without multipliers
            reverse=True
        )[:3]

        html_content += f"""
            <div class="performer-card">
                <h3>{team_data['team_name']}</h3>
"""

        for i, player in enumerate(top_players, 1):
            html_content += f"""
                <div class="performer-item">
                    <div class="performer-rank">#{i}</div>
                    <div class="performer-name">
                        <strong>{player['player_name']}</strong>
                        <div style="font-size: 0.85em; color: #666;">
                            {player['ipl_team']} | <span class="role-{player['role'].replace(' ', '-')}">{player['role']}</span>
                        </div>
                    </div>
                    <div class="performer-points">{player['adjusted_points']:.0f} pts</div>
                </div>
"""

        html_content += """
            </div>
"""

    # Feature 1: MVP Board (Top 15 Players League-wide)
    html_content += """
        </div>

        <h2 class="section-title">🏅 Most Valuable Players (League MVP Board)</h2>
        <table class="mvp-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player Name</th>
                    <th>IPL Team</th>
                    <th>Fantasy Team</th>
                    <th>Official Points</th>
                    <th>Frozen Points</th>
                    <th>Total Points</th>
                </tr>
            </thead>
            <tbody>
"""

    for i, player in enumerate(mvp_players, 1):
        frozen_display = f"{player['frozen_points']:.0f}" if player['frozen_points'] > 0 else "-"
        html_content += f"""
                <tr>
                    <td class="mvp-rank">#{i}</td>
                    <td><strong>{player['player_name']}</strong></td>
                    <td>{player['ipl_team']}</td>
                    <td>{player['team_name']}</td>
                    <td>{player['official_points']:.0f}</td>
                    <td>{frozen_display}</td>
                    <td class="points">{player['adjusted_points']:.0f}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>

        <h2 class="section-title">🏏 IPL Team Performance Analysis</h2>
        <div class="ipl-analysis-grid">
"""

    # Feature 2: IPL Team Analysis
    max_avg = max(team['avg_points'] for team in ipl_team_analysis) if ipl_team_analysis else 1

    for ipl_team_data in ipl_team_analysis:
        bar_width = (ipl_team_data['avg_points'] / max_avg) * 100

        html_content += f"""
            <div class="ipl-team-card">
                <div class="ipl-team-name">{ipl_team_data['ipl_team']}</div>
                <div class="ipl-stat">
                    <span>Avg Points/Player:</span>
                    <span><strong>{ipl_team_data['avg_points']:.1f}</strong></span>
                </div>
                <div class="ipl-stat">
                    <span>Total Points:</span>
                    <span>{ipl_team_data['total_points']:.0f}</span>
                </div>
                <div class="ipl-stat">
                    <span>Players in Top 11s:</span>
                    <span>{ipl_team_data['player_count']}</span>
                </div>
                <div class="ipl-bar" style="width: {bar_width}%;"></div>
            </div>
"""

    html_content += """
        </div>

        <h2 class="section-title">📈 Points Progression Over Time</h2>
"""

    # Feature 11: Points Progression Chart
    if points_history:
        # Prepare data for Chart.js
        html_content += """
        <div class="progression-container">
            <canvas id="progressionChart" class="chart-canvas"></canvas>
        </div>
        <script>
            const ctx = document.getElementById('progressionChart').getContext('2d');
            const progressionChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [
"""

        colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea', '#ff6b6b']
        for idx, (team_name, history) in enumerate(points_history.items()):
            dates = [h['date'] for h in history]
            points = [h['points'] for h in history]
            color = colors[idx % len(colors)]

            html_content += f"""
                        {{
                            label: '{team_name}',
                            data: {points},
                            borderColor: '{color}',
                            backgroundColor: '{color}33',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: false
                        }},
"""

        html_content += """
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        },
                        title: {
                            display: true,
                            text: 'Team Points Progression',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Total Points'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Updates'
                            }
                        }
                    }
                }
            });
        </script>
"""
    else:
        html_content += """
        <div class="progression-container">
            <p style="text-align: center; color: #999;">No historical data available yet. Points will be tracked over time.</p>
        </div>
"""

    # Feature 6: IPL Team Contribution within Fantasy Teams
    # Calculate IPL team breakdown for each fantasy team
    fantasy_team_ipl_breakdown = {}
    for team_data in sorted_teams:
        ipl_breakdown = {}
        for player in team_data['points_data']['top_11_players']:
            ipl_team = player['ipl_team']
            if ipl_team not in ipl_breakdown:
                ipl_breakdown[ipl_team] = 0
            ipl_breakdown[ipl_team] += player['team_points']  # Use team_points (with multipliers)

        # Sort by points
        fantasy_team_ipl_breakdown[team_data['team_name']] = dict(sorted(ipl_breakdown.items(), key=lambda x: x[1], reverse=True))

    html_content += """
        <h2 class="section-title">🎯 IPL Team Contribution by Fantasy Team</h2>
        <div class="role-selector">
            <label for="teamSelect" style="font-weight: bold; margin-right: 10px;">Select Fantasy Team:</label>
            <select id="teamSelect" onchange="updateIPLChart()">
"""

    for team_data in sorted_teams:
        html_content += f"""
                <option value="{team_data['team_name']}">{team_data['team_name']}</option>
"""

    html_content += """
            </select>
        </div>
        <div class="role-chart-container" id="iplChartContainer">
            <!-- Chart will be populated by JavaScript -->
        </div>

        <script>
            // Store IPL team contribution data for each fantasy team
            const fantasyTeamIPLData = {
"""

    colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea', '#ff6b6b', '#feca57']
    for team_data in sorted_teams:
        ipl_data = fantasy_team_ipl_breakdown[team_data['team_name']]
        total_points = team_data['points_data']['total_points']

        html_content += f"""
                "{team_data['team_name']}": {{
                    total_points: {total_points},
                    ipl_teams: {json.dumps(ipl_data)}
                }},
"""

    html_content += """
            };

            const iplTeamColors = {
"""

    # Common IPL teams with their colors
    ipl_colors = {
        'MI': '#004BA0', 'CSK': '#FDB913', 'RCB': '#EC1C24', 'KKR': '#3A225D',
        'DC': '#0078BC', 'PBKS': '#ED1B24', 'RR': '#254AA5', 'SRH': '#FF822A',
        'GT': '#1C2841', 'LSG': '#4A1E5B'
    }

    for ipl_team, color in ipl_colors.items():
        html_content += f"""
                '{ipl_team}': '{color}',
"""

    html_content += """
            };

            function updateIPLChart() {
                const teamName = document.getElementById('teamSelect').value;
                const data = fantasyTeamIPLData[teamName];
                const total = data.total_points;
                const iplTeams = data.ipl_teams;

                let chartHTML = `<h3 style="text-align: center; color: #667eea; margin-bottom: 20px;">${teamName} - IPL Team Breakdown</h3>`;

                // Sort IPL teams by points
                const sortedIPL = Object.entries(iplTeams).sort((a, b) => b[1] - a[1]);

                sortedIPL.forEach(([iplTeam, points]) => {
                    const percent = (points / total) * 100;
                    const color = iplTeamColors[iplTeam] || '#667eea';

                    chartHTML += `
                        <div class="role-bar">
                            <div class="role-label">
                                <span><strong>${iplTeam}</strong></span>
                                <span>${points.toFixed(0)} pts (${percent.toFixed(1)}%)</span>
                            </div>
                            <div class="role-progress">
                                <div class="role-fill" style="width: ${percent}%; background: ${color}; color: white;">
                                    ${percent.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    `;
                });

                chartHTML += `
                    <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; text-align: center;">
                        <strong>Total Team Points: ${total.toFixed(0)}</strong>
                    </div>
                `;

                document.getElementById('iplChartContainer').innerHTML = chartHTML;
            }

            // Initialize with first team
            updateIPLChart();
        </script>

        <h2 class="section-title">📈 Points Distribution Breakdown</h2>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Team</th>
                    <th>Captain Points</th>
                    <th>Vice-Captain Points</th>
                    <th>Regular Players</th>
                    <th>Total Points</th>
                </tr>
            </thead>
            <tbody>
"""

    for team_data in sorted_teams:
        points = team_data['points_data']

        html_content += f"""
                <tr>
                    <td><strong>{team_data['team_name']}</strong></td>
                    <td>{points['captain_points']}</td>
                    <td>{points['vc_points']}</td>
                    <td>{points['regular_points']}</td>
                    <td class="points">{points['total_points']}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>
"""

    # Individual Team Sections
    for team_data in sorted_teams:
        points = team_data['points_data']
        stats = team_data['team_stats']
        changes = team_data['change_history']

        html_content += f"""
        <div class="team-section">
            <div class="team-section-header">
                <h2 class="team-section-title">{team_data['team_name']}</h2>
            </div>

            <div class="team-stats-summary">
                <div class="stat-box">
                    <h3>Total Points</h3>
                    <div class="big-number">{points['total_points']}</div>
                </div>
                <div class="stat-box">
                    <h3>Captain Points</h3>
                    <div class="big-number">{points['captain_points']}</div>
                    <div style="font-size: 0.85em; margin-top: 5px;">{points['captain_name']}</div>
                </div>
                <div class="stat-box">
                    <h3>VC Points</h3>
                    <div class="big-number">{points['vc_points']}</div>
                    <div style="font-size: 0.85em; margin-top: 5px;">{points['vc_name']}</div>
                </div>
                <div class="stat-box">
                    <h3>Changes Used</h3>
                    <div class="big-number">{stats['changes_used']}/2</div>
                </div>
            </div>

            <h3 style="color: #667eea; margin: 20px 0 15px 0;">Top 11 Players</h3>
            <table class="player-table">
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Role</th>
                        <th>IPL Team</th>
                        <th>Official Points</th>
                        <th>Frozen Points</th>
                        <th>Multiplier</th>
                        <th>Team Points</th>
                    </tr>
                </thead>
                <tbody>
"""

        # Add top 11 players
        for player in points['top_11_players']:
            frozen_display = f"{player['frozen_points']}" if player['frozen_points'] > 0 else "-"

            html_content += f"""
                    <tr>
                        <td><strong>{player['player_name']}</strong></td>
                        <td><span class="role-{player['role'].replace(' ', '-')}">{player['role']}</span></td>
                        <td>{player['ipl_team']}</td>
                        <td>{player['official_points']}</td>
                        <td>{frozen_display}</td>
                        <td>{player['multiplier']}x</td>
                        <td class="points">{player['team_points']}</td>
                    </tr>
"""

        html_content += """
                </tbody>
            </table>
"""

        # Change history
        if changes:
            html_content += """
            <h3 style="color: #667eea; margin: 20px 0 15px 0;">Change History</h3>
            <div class="change-log">
"""

            for change in changes:
                change_desc = format_change_description(change)
                change_date = datetime.fromisoformat(change['change_detected_at']).strftime('%B %d, %Y at %I:%M %p')

                html_content += f"""
                <div class="change-item">
                    <div class="change-date">{change_date}</div>
                    <div class="change-description">{change_desc}</div>
                </div>
"""

            html_content += """
            </div>
"""
        else:
            html_content += """
            <h3 style="color: #667eea; margin: 20px 0 15px 0;">Change History</h3>
            <div class="change-log">
                <p class="no-changes">No changes recorded yet.</p>
            </div>
"""

        html_content += """
        </div>
"""

    # Footer
    html_content += f"""
        <footer>
            <p><strong>IPL Fantasy League 2025</strong></p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Powered by IPL Fantasy Stats Scraper | Updated automatically after each match
            </p>
        </footer>
    </div>
</body>
</html>
"""

    # Write HTML file
    html_file = output_path / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Multi-team dashboard generated: {html_file}")
    return html_file


def format_change_description(change):
    """
    Format change record into human-readable description.

    Args:
        change (dict): Change record from database

    Returns:
        str: Formatted description
    """
    player_name = change['player_name']
    change_type = change['change_type']
    old_value = change['old_value']
    new_value = change['new_value']
    frozen_points = change['frozen_points']

    if change_type == 'position_takeover':
        # Parse takeover data from old_value
        import json
        try:
            data = json.loads(old_value)
            replaced_player = data.get('replaced_player', '?')
            old_rank = data.get('old_rank', '?')
            reason = data.get('reason', 'Normal Change')
        except:
            replaced_player = old_value
            old_rank = '?'
            reason = 'Normal Change'

        # Choose icon and label based on reason
        if reason == 'Injury Replacement':
            icon = '🏥'
            note = '<span style="color: #28a745;">(Does not count toward change limit)</span>'
        else:
            icon = '🔄'
            note = '<span style="color: #dc3545;">(Counts toward change limit)</span>'

        return (f"<strong>{icon} Position Takeover:</strong> "
                f"<strong>{player_name}</strong> takes over Rank {old_rank} from <strong>{replaced_player}</strong> "
                f"({frozen_points:.0f} points transferred) {note}")

    elif change_type == 'player_replacement':
        # Parse replacement reason from old_value if stored as JSON (legacy support)
        import json
        try:
            data = json.loads(old_value)
            replaced_name = data.get('replaced', old_value)
            reason = data.get('reason', 'Normal Change')
        except:
            replaced_name = old_value
            reason = 'Normal Change'

        # Choose icon and label based on reason
        if reason == 'Injury Replacement':
            icon = '🏥'
            label = 'Injury Replacement'
            note = '<span style="color: #28a745;">(Does not count toward change limit)</span>'
        else:
            icon = '🔄'
            label = 'Normal Replacement'
            note = '<span style="color: #dc3545;">(Counts toward change limit)</span>'

        return (f"<strong>{icon} {label}:</strong> "
                f"<strong>{replaced_name}</strong> replaced by <strong>{new_value}</strong> "
                f"({frozen_points:.0f} points transferred) {note}")

    elif change_type == 'role_change':
        if frozen_points > 0:
            return f"<strong>{player_name}</strong> role changed from <strong>{old_value}</strong> to <strong>{new_value}</strong> (frozen {frozen_points:.0f} points)"
        else:
            return f"<strong>{player_name}</strong> role changed from <strong>{old_value}</strong> to <strong>{new_value}</strong>"

    elif change_type in ['ranking_swap_out', 'ranking_swap_in']:
        if change_type == 'ranking_swap_out':
            # Player moved to bench (points transferred away)
            return f"<strong>{player_name}</strong> moved to bench (Rank {old_value} → {new_value}) - points transferred"
        else:
            # Player promoted to top 15
            if frozen_points > 0:
                return f"<strong>{player_name}</strong> promoted to top 15 (Rank {old_value} → {new_value}) - inherited {frozen_points:.0f} points"
            else:
                return f"<strong>{player_name}</strong> promoted to top 15 (Rank {old_value} → {new_value})"

    elif change_type == 'ranking_change':
        old_status = "bench" if int(old_value) > 15 else "playing squad"
        new_status = "bench" if int(new_value) > 15 else "playing squad"

        if old_status != new_status:
            return f"<strong>{player_name}</strong> moved from rank {old_value} ({old_status}) to rank {new_value} ({new_status})"
        else:
            return f"<strong>{player_name}</strong> ranking changed from {old_value} to {new_value}"

    return f"<strong>{player_name}</strong>: {change_type} ({old_value} → {new_value})"


# ============================================================================
# Main Execution Block (For Testing)
# ============================================================================

if __name__ == "__main__":
    print("Testing Web Generator...\n")

    # Sample data for testing
    team_name = "Mahesh Thunder Buddies"

    points_data = {
        'team_id': 1,
        'team_name': team_name,
        'total_points': 2450.5,
        'captain_name': 'Nicholas Pooran',
        'captain_points': 760.0,
        'vc_name': 'Heinrich Klaasen',
        'vc_points': 550.5,
        'regular_points': 1140.0,
        'top_11_players': [
            {
                'player_name': 'Nicholas Pooran',
                'ipl_team': 'LSG',
                'role': 'Captain',
                'official_points': 380,
                'frozen_points': 0,
                'adjusted_points': 380,
                'multiplier': 2.0,
                'team_points': 760
            },
            {
                'player_name': 'Heinrich Klaasen',
                'ipl_team': 'SRH',
                'role': 'Vice-Captain',
                'official_points': 367,
                'frozen_points': 0,
                'adjusted_points': 367,
                'multiplier': 1.5,
                'team_points': 550.5
            }
        ]
    }

    change_history = []

    team_stats = {
        'team_id': 1,
        'owner_name': 'Mahesh',
        'changes_used': 0,
        'changes_remaining': 2,
        'created_at': datetime.now().isoformat()
    }

    # Generate HTML
    html_file = generate_dashboard_html(team_name, points_data, change_history, team_stats, "docs")

    print("\n✓ Test completed successfully!")
    print(f"  Open {html_file} in your browser to view the dashboard")
