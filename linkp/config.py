"""Configuration management for LinkP."""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Manage LinkP configuration from linkp.env file."""
    
    def __init__(self):
        # 1. Explicit config path via env
        explicit = os.getenv('LINKP_CONFIG')
        # 2. Project path from env or its own env file
        project_path = os.getenv('PROJECT_PATH')
        project_env = Path(project_path) / "linkp.env" if project_path else None
        # 3. CWD
        cwd_env = Path.cwd() / "linkp.env"
        # 4. Home directory locations
        home_dir = Path.home()
        home_env = home_dir / ".linkp" / "linkp.env"
        short_home_env = home_dir / ".linkp.env"
        
        # Search in order
        self.config_file = None
        for cfg in [explicit, project_env, cwd_env, home_env, short_home_env]:
            if cfg and Path(cfg).exists():
                load_dotenv(cfg)
                self.config_file = cfg
                break

        # Load configuration values
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_person_urn = os.getenv("LINKEDIN_PERSON_URN")
        self.linkedin_api_version = os.getenv("LINKEDIN_API_VERSION", "202503")
        self.project_path = os.getenv("PROJECT_PATH", str(Path.cwd()))
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def validate(self):
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in linkp.env")
        if not self.linkedin_access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not set in linkp.env")
        if not self.linkedin_client_id:
            raise ValueError("LINKEDIN_CLIENT_ID not set in linkp.env")
        if not self.linkedin_client_secret:
            raise ValueError("LINKEDIN_CLIENT_SECRET not set in linkp.env")
