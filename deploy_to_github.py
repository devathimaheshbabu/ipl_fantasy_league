"""
GitHub Pages Deployment Script
===============================
Deploy generated HTML to GitHub Pages for free hosting.

One-time setup:
    1. Create GitHub repo: ipl-fantasy-league
    2. Enable Pages in Settings → Pages → Source: docs folder
    3. Set remote: git remote add origin https://github.com/USERNAME/ipl-fantasy-league.git

Usage:
    python deploy_to_github.py

Author: Claude Code
Date: 2026-04-17
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')


def run_command(command, description=None):
    """
    Execute shell command and return result.

    Args:
        command (str): Command to execute
        description (str): Human-readable description

    Returns:
        tuple: (success: bool, output: str)
    """
    if description:
        print(f"  {description}...")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )

    if result.returncode != 0:
        return False, result.stderr

    return True, result.stdout


def check_git_repo():
    """
    Check if current directory is a git repository.

    Returns:
        bool: True if git repo exists
    """
    success, _ = run_command("git rev-parse --git-dir", "Checking git repository")
    return success


def check_docs_folder():
    """
    Check if docs folder exists with index.html.

    Returns:
        bool: True if docs/index.html exists
    """
    docs_path = Path("docs/index.html")
    return docs_path.exists()


def deploy():
    """
    Main deployment function.

    Returns:
        bool: True if successful
    """
    print("\n" + "=" * 70)
    print("  GitHub Pages Deployment")
    print("=" * 70)

    # Pre-flight checks
    print("\n[Pre-flight Checks]")
    print("-" * 70)

    # Check if docs folder exists
    if not check_docs_folder():
        print("✗ Error: docs/index.html not found")
        print("\n  Please run this first:")
        print("    python run_fantasy_league.py")
        return False

    print("✓ docs/index.html found")

    # Check if git repo exists
    if not check_git_repo():
        print("\n⚠ Warning: Not a git repository")
        print("\n  One-time setup required:")
        print("    git init")
        print("    git remote add origin https://github.com/YOUR_USERNAME/ipl-fantasy-league.git")
        print("\n  Please run these commands and try again.")
        return False

    print("✓ Git repository found")

    # Check if remote exists
    success, output = run_command("git remote -v", "Checking git remote")
    if not success or not output.strip():
        print("\n⚠ Warning: No git remote configured")
        print("\n  Please add remote:")
        print("    git remote add origin https://github.com/YOUR_USERNAME/ipl-fantasy-league.git")
        return False

    print("✓ Git remote configured")

    # Deployment steps
    print("\n[Deployment Steps]")
    print("-" * 70)

    # Step 1: Git add
    success, error = run_command("git add docs/", "Adding docs folder to git")
    if not success:
        print(f"✗ Error adding files: {error}")
        return False

    print("✓ Files staged for commit")

    # Step 2: Git commit
    commit_message = f"Update fantasy league stats - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    success, error = run_command(
        f'git commit -m "{commit_message}"',
        "Creating commit"
    )

    if not success:
        if "nothing to commit" in error or "no changes added" in error:
            print("ℹ No changes to commit (webpage unchanged since last deployment)")
            print("\n✓ Deployment skipped - no updates needed")
            return True
        else:
            print(f"✗ Error committing: {error}")
            return False

    print("✓ Commit created")

    # Step 3: Git push
    print("\n  Pushing to GitHub...")
    print("  (This may take a few seconds)")

    success, error = run_command("git push origin main", "Pushing to GitHub")

    if not success:
        # Try 'master' branch if 'main' fails
        if "src refspec main does not match any" in error:
            print("  Trying 'master' branch...")
            success, error = run_command("git push origin master", "Pushing to GitHub")

        if not success:
            print(f"✗ Error pushing: {error}")
            print("\n  Possible solutions:")
            print("    1. Check your GitHub credentials")
            print("    2. Ensure you have push access to the repository")
            print("    3. Try: git push -u origin main")
            return False

    print("✓ Pushed to GitHub successfully")

    # Success message
    print("\n" + "=" * 70)
    print("  ✓ Deployment Successful!")
    print("=" * 70)

    print("\n🌐 Your webpage will be live in 1-2 minutes at:")
    print("   https://YOUR_USERNAME.github.io/ipl-fantasy-league/")
    print("\n📝 Note: Replace YOUR_USERNAME with your actual GitHub username")

    print("\n💡 To enable GitHub Pages (first-time only):")
    print("   1. Go to: https://github.com/YOUR_USERNAME/ipl-fantasy-league/settings/pages")
    print("   2. Under 'Source', select: Deploy from a branch")
    print("   3. Under 'Branch', select: main → /docs → Save")
    print("   4. Wait 1-2 minutes for deployment")

    print("\n" + "=" * 70 + "\n")

    return True


def main():
    """Main execution."""
    try:
        success = deploy()
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠ Deployment cancelled by user")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
