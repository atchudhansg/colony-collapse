# MAROONED Training API - Setup Guide

## Installation

### 1. Install Dependencies

cd collapse_colony/api
pip install -r requirements.txt

text

### 2. Setup Environment Variables

cp .env.example .env

Edit .env with your configuration
text

### 3. Initialize Database

python

from database import TrainingDatabase
db = TrainingDatabase()
exit()

text

### 4. Start API Server

python run.py

text

The API will be available at:
- **REST API**: http://localhost:5000
- **WebSocket**: ws://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## API Endpoints

### Health & Info
- `GET /api/health` - Health check
- `GET /api/info` - API information

### Episode Management
- `GET /api/episodes` - List all episodes
- `GET /api/episodes/<id>` - Get episode details
- `GET /api/episodes/latest` - Get latest episode
- `GET /api/episodes/<id>/map` - Get map state
- `GET /api/episodes/<id>/export` - Export as JSON

### Training Logging (POST)
- `POST /api/training/episode/start` - Start episode
- `POST /api/training/turn` - Log turn
- `POST /api/training/voting` - Log voting phase
- `POST /api/training/map` - Save map state
- `POST /api/training/episode/end` - End episode

### Statistics
- `GET /api/training/status` - Current training status
- `GET /api/training/stats` - Training statistics
