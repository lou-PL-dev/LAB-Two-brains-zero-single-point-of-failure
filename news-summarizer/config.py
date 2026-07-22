"""
config.py
Loads and validates environment configuration for the news summarizer app.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from .env into the environment


class Config:
    """Holds all configuration values needed by the app."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")

        self.environment = os.getenv("ENVIRONMENT", "development")
        self.max_retries = int(os.getenv("MAX_RETRIES", 3))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", 30))
        self.daily_budget = float(os.getenv("DAILY_BUDGET", 5.00))

    def validate(self):
        """Checks that all required API keys are present. Returns list of missing keys."""
        required = {
            "OPENAI_API_KEY": self.openai_api_key,
            "COHERE_API_KEY": self.cohere_api_key,
            "NEWS_API_KEY": self.news_api_key,
        }
        missing = [name for name, value in required.items() if not value]
        return missing


if __name__ == "__main__":
    config = Config()
    missing_keys = config.validate()

    if missing_keys:
        print(f"❌ Missing required configuration: {', '.join(missing_keys)}")
    else:
        print("✅ Configuration validated successfully!")
        print(f"Environment: {config.environment}")
        print(f"Daily budget: ${config.daily_budget}")