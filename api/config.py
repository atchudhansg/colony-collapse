"""
Configuration Manager for MAROONED API
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/episodes.db')
    
    # File Storage
    EPISODES_DIR = os.getenv('EPISODES_DIR', 'data/episodes')
    ENABLE_FILE_STORAGE = os.getenv('ENABLE_FILE_STORAGE', 'True').lower() == 'true'
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # WebSocket
    SOCKETIO_LOG_LEVEL = os.getenv('SOCKETIO_LOG_LEVEL', 'INFO')
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'threading')
    
    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'logs/api.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests


# Select config based on environment
env = os.getenv('FLASK_ENV', 'development')
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

config = config_map.get(env, DevelopmentConfig)
