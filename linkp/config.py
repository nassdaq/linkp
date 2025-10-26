"""Configuration management for LinkP."""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Manage LinkP configuration from linkp.env file."""
    
    def __init__(self):
        self.config_file = Path.cwd() / "linkp.env"
        
        # Load environment variables from linkp.env
        if self.config_file.exists():
            load_dotenv(self.config_file)
        
        # Load configuration values
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_person_urn = os.getenv("LINKEDIN_PERSON_URN")
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
