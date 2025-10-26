"""AI-powered summarization using OpenAI with extensive context."""

import os
from openai import OpenAI


class AISummarizer:
    """Generate AI summaries using OpenAI with massive context."""
    
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_summary(self, git_changes):
        """Generate a summary of Git changes using AI."""
        prompt = self._build_prompt(git_changes)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates professional, concise LinkedIn posts about developer work. You have deep knowledge of software development, programming languages, frameworks, and best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def _build_prompt(self, git_changes):
        """Build the prompt with extensive context."""
        commits = git_changes.get("commits", [])
        files_changed = git_changes.get("files_changed", [])
        diff_summary = git_changes.get("diff_summary", "")
        
        if not commits:
            return "Write a LinkedIn post about having a productive day planning and reflecting on the project."
        
        # Build detailed commit info
        commit_messages = []
        for i, commit in enumerate(commits[:10], 1):
            commit_messages.append(
                f"{i}. {commit.get('message', 'N/A')} - {commit.get('date', 'N/A')}"
            )
        
        # Build files info
        file_actions = {'A': 'added', 'M': 'modified', 'D': 'deleted', 'R': 'renamed'}
        files_summary = []
        for action, filename in files_changed[:15]:
            action_word = file_actions.get(action, 'changed')
            files_summary.append(f"  • {action_word}: {filename}")
        
        prompt = f"""Create a professional, engaging LinkedIn post (2-3 sentences) about today's development work.

Commits made:
{chr(10).join(commit_messages)}

Files changed:
{chr(10).join(files_summary) if files_summary else 'No files changed'}

Make it:
- Professional but friendly
- Start with "Today I worked on..." or "Made progress on..."
- Highlight key accomplishments
- Add relevant emojis naturally
- Keep it concise
Do NOT include hashtags."""
        
        return prompt
