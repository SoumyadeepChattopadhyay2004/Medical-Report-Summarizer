"""
Configuration module for Medical Report Summarizer
Manages all application settings and environment variables
"""

import os
from dotenv import load_dotenv


print("Current directory:", os.getcwd())
print("GROK_API_KEY from env:", repr(os.getenv("GROK_API_KEY")))
# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""
    
    # API Configuration
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    GROK_API_BASE = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    GROK_MODEL = os.getenv("GROK_MODEL", "grok-beta")
    
    # File Processing Settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.txt', '.docx'}
    
    # Language Settings
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "हिंदी (Hindi)"
    }
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
    
    # Feature Flags
    ENABLE_OCR = os.getenv("ENABLE_OCR", "true").lower() == "true"
    ENABLE_TRANSLATION = os.getenv("ENABLE_TRANSLATION", "true").lower() == "true"
    ENABLE_EXPORT = os.getenv("ENABLE_EXPORT", "true").lower() == "true"
    ENABLE_CHATBOT = os.getenv("ENABLE_CHATBOT", "true").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # AI Model Parameters
    AI_TEMPERATURE = 0.7
    AI_MAX_TOKENS = 4096
    AI_TOP_P = 1.0
    
    # Session Configuration
    MAX_CHAT_HISTORY = 10
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    # UI Configuration
    APP_TITLE = "*Health-Guardian*: Medical Report Summarizer"
    APP_ICON = "🏥"
    PAGE_LAYOUT = "wide"
    
    # Color Scheme
    COLORS = {
        "primary": "#1E88E5",
        "success": "#43A047",
        "warning": "#FFA726",
        "danger": "#E53935",
        "info": "#00ACC1",
        "background": "#F5F5F5",
        "text": "#212121"
    }
    
    # Risk Assessment Thresholds
    RISK_LEVELS = {
        "low": (0, 30),
        "moderate": (30, 60),
        "high": (60, 85),
        "critical": (85, 100)
    }
    
    # Severity Classification
    SEVERITY_WEIGHTS = {
        'critical': 0.4,
        'abnormal': 0.3,
        'borderline': 0.1,
        'normal': 0.0
    }
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        if not cls.GROK_API_KEY:
            raise ValueError("GROK_API_KEY is not set. Please configure your API key in .env file")
        
        if cls.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE must be positive")
        
        return True
    
    @classmethod
    def get_language_name(cls, code):
        """Get language name from code"""
        return cls.SUPPORTED_LANGUAGES.get(code, "English")
    
    @classmethod
    def is_valid_language(cls, code):
        """Check if language code is supported"""
        return code in cls.SUPPORTED_LANGUAGES


# Validate configuration on import
try:
    Config.validate_config()
except ValueError as e:
    print(f"Configuration Warning: {e}")

# Made with Bob
