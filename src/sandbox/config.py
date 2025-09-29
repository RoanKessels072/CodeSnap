import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    # Universal Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # CORS settings (you know you'll need this)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # Rate limiting (good to have from start)
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    
    # Code execution limits (you'll definitely need these)
    EXECUTION_TIMEOUT = int(os.environ.get('EXECUTION_TIMEOUT', 30))
    MAX_CODE_LENGTH = int(os.environ.get('MAX_CODE_LENGTH', 10000))
    
    # AI API keys (add as you implement)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    # Add production-specific settings here

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Override settings for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}