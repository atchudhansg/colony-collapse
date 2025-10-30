"""
MAROONED API Startup Script
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
Path('data').mkdir(exist_ok=True)
Path('data/episodes').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

logger.info("=" * 80)
logger.info("MAROONED Training API - Startup")
logger.info("=" * 80)

# Import and run app
from app import app, socketio
from config import config

if __name__ == '__main__':
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Debug: {config.DEBUG}")
    logger.info(f"Host: {config.API_HOST}")
    logger.info(f"Port: {config.API_PORT}")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info(f"File Storage: {config.ENABLE_FILE_STORAGE}")
    logger.info("")
    logger.info(f"🚀 Starting MAROONED API...")
    logger.info(f"📡 WebSocket available at ws://{config.API_HOST}:{config.API_PORT}")
    logger.info(f"🌐 API Documentation at http://{config.API_HOST}:{config.API_PORT}/api/info")
    logger.info("")
    
    socketio.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG,
        log_output=True
    )
