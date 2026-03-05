"""
Configuration management for LinkedIn enricher
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Base configuration"""

    # API Configuration
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "")

    # Slack Integration
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

    # Flask Configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Application Settings
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1"))

    # File paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    DOWNLOAD_FOLDER = BASE_DIR / "downloads"
    TEMP_FOLDER = BASE_DIR / "temp"

    # Create directories if they don't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    DOWNLOAD_FOLDER.mkdir(exist_ok=True)
    TEMP_FOLDER.mkdir(exist_ok=True)

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


def get_config():
    """Get appropriate configuration based on environment"""
    env = os.getenv("FLASK_ENV", "development").lower()

    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig


# Export config instance
config = Config()
