import os
from dotenv import load_dotenv
from typing import Optional
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    PROJECT_NAME: str = "Med AI"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "medibot")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key_please_change")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # External Services
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Mail
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@medibot.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    
    def __init__(self):
        """Validate critical environment variables and log warnings for others."""
        missing_vars = []
        
        if not self.MONGODB_URL:
            missing_vars.append("MONGODB_URL")
        
        # Warn but don't crash for these in dev/debug mode
        if not self.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY is missing. Chat functionality will not work.")
            
        if self.SECRET_KEY == "development_secret_key_please_change":
            logger.warning("Using default SECRET_KEY. Do not use in production.")

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file."
            )

settings = Settings()