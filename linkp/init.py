"""Initialization functions for LinkP."""

from pathlib import Path


def init_config():
    """Initialize LinkP configuration files."""
    cwd = Path.cwd()
    
    # Create linkp.env file
    env_file = cwd / "linkp.env"
    if env_file.exists():
        print(f"⚠️  {env_file} already exists. Skipping creation.")
    else:
        env_content = f"""# LinkP Configuration File
# Fill in your API keys and credentials below

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# LinkedIn API Credentials (get from https://www.linkedin.com/developers/apps)
LINKEDIN_CLIENT_ID=YOUR_CLIENT_ID
LINKEDIN_CLIENT_SECRET=YOUR_CLIENT_SECRET
LINKEDIN_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
LINKEDIN_PERSON_URN=urn:li:person:YOUR_PERSON_ID

# Path to your project (default is current directory)
PROJECT_PATH={cwd}

# Optional: Set custom AI model (default is gpt-3.5-turbo)
# OPENAI_MODEL=gpt-4
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_file}")
    
    # Create linkp.md file
    md_file = cwd / "linkp.md"
    if md_file.exists():
        print(f"⚠️  {md_file} already exists. Skipping creation.")
    else:
        md_content = """# LinkP Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Configure API Keys
Edit `linkp.env` and fill in your credentials.

### 3. Run LinkP
```bash
linkp run
```
"""
        
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"✅ Created {md_file}")

