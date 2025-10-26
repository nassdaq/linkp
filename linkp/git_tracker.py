"""Git tracking functionality for LinkP."""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta


class GitTracker:
    """Track Git changes in a project."""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        if not self._is_git_repo():
            raise ValueError(f"Not a Git repository: {project_path}")
    
    def _is_git_repo(self):
        """Check if the path is a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_recent_changes(self, days=1):
        """Get recent Git changes from the last N days."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get commits
        commits = self._get_commits(cutoff_date)
        
        # Get files changed
        files_changed = self._get_files_changed(commits)
        
        # Get diff summary
        diff_summary = self._get_diff_summary(commits)
        
        return {
            "commits": commits,
            "files_changed": files_changed,
            "diff_summary": diff_summary,
            "summary": f"{len(commits)} commits, {len(files_changed)} files changed"
        }
    
    def _get_commits(self, since_date):
        """Get commits since a given date."""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={since_date}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|', 4)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4] if len(parts) > 4 else ""
                    })
            
            return commits
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Error getting commits: {e}")
    
    def _get_files_changed(self, commits):
        """Get list of files changed."""
        files = []
        seen_files = set()
        
        for commit in commits:
            try:
                result = subprocess.run(
                    ["git", "show", "--name-status", "--pretty=format:", commit["hash"]],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    if line and line[0] in ['A', 'M', 'D', 'R']:
                        parts = line.split('\t')
                        if len(parts) >= 2 and parts[1] not in seen_files:
                            files.append((parts[0], parts[1]))
                            seen_files.add(parts[1])
            except subprocess.CalledProcessError:
                continue
        
        return files
    
    def get_diff_summary(self):
        """Get a summary of code changes (diff stats)."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:", "--shortstat"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def _get_diff_summary(self, commits):
        """Get diff summary for commits."""
        if not commits:
            return ""
        
        try:
            result = subprocess.run(
                ["git", "diff", f"{commits[-1]['hash']}^..{commits[0]['hash']}", "--stat"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            # Get last few lines (the summary)
            lines = result.stdout.strip().split('\n')
            return '\n'.join(lines[-10:]) if len(lines) > 10 else result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

