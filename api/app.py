"""
MAROONED Flask API
RESTful endpoints for training data access
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any
import os

from database import TrainingDatabase, FileStorage
from logger import MaroonedTrainingLogger
from config import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)
CORS(app, origins=config.CORS_ORIGINS)

# Initialize database and logger
db = TrainingDatabase(db_path=config.DATABASE_PATH)
file_storage = FileStorage(episodes_dir=config.EPISODES_DIR)
logger = MaroonedTrainingLogger(db_path=config.DATABASE_PATH, use_file_storage=config.ENABLE_FILE_STORAGE)

# ===================================================================
# HEALTH & INFO ENDPOINTS
# ===================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'MAROONED Training API'
    }), 200

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information"""
    return jsonify({
        'name': 'MAROONED Training API',
        'version': '1.0.0',
        'description': 'Multi-Agent Reinforcement Learning Training Data API',
        'endpoints': {
            'episodes': '/api/episodes',
            'episode_detail': '/api/episodes/<id>',
            'episode_latest': '/api/episodes/latest',
            'episode_map': '/api/episodes/<id>/map',
            'training_status': '/api/training/status',
            'export': '/api/episodes/<id>/export'
        }
    }), 200

# ===================================================================
# EPISODE ENDPOINTS
# ===================================================================

@app.route('/api/episodes', methods=['GET'])
def list_episodes():
    """Get all episodes"""
    limit = request.args.get('limit', 50, type=int)
    episodes = db.get_all_episodes(limit=limit)
    
    return jsonify({
        'count': len(episodes),
        'episodes': episodes
    }), 200

@app.route('/api/episodes/<int:episode_id>', methods=['GET'])
def get_episode(episode_id: int):
    """Get complete episode data"""
    episode = db.get_episode(episode_id)
    
    if not episode:
        return jsonify({'error': 'Episode not found'}), 404
    
    return jsonify(episode), 200

@app.route('/api/episodes/latest', methods=['GET'])
def get_latest_episode():
    """Get most recent episode"""
    episode = db.get_latest_episode()
    
    if not episode:
        return jsonify({'error': 'No episodes found'}), 404
    
    # Get full data
    full_episode = db.get_episode(episode['episode_id'])
    return jsonify(full_episode), 200

@app.route('/api/episodes/<int:episode_id>/map', methods=['GET'])
def get_episode_map(episode_id: int):
    """Get map state for episode"""
    episode = db.get_episode(episode_id)
    
    if not episode:
        return jsonify({'error': 'Episode not found'}), 404
    
    # Get map from file storage
    file_episode = file_storage.load_episode(episode_id)
    
    if file_episode and 'map_state' in file_episode:
        return jsonify({
            'episode_id': episode_id,
            'map_state': file_episode['map_state']
        }), 200
    
    return jsonify({'error': 'Map data not found'}), 404

@app.route('/api/episodes/<int:episode_id>/export', methods=['GET'])
def export_episode(episode_id: int):
    """Export episode as JSON"""
    episode = db.get_episode(episode_id)
    
    if not episode:
        return jsonify({'error': 'Episode not found'}), 404
    
    # Get from file storage
    file_episode = file_storage.load_episode(episode_id)
    
    return jsonify(file_episode or episode), 200

# ===================================================================
# TRAINING LOGGING ENDPOINTS
# ===================================================================

@app.route('/api/training/episode/start', methods=['POST'])
def start_training_episode():
    """Start new training episode"""
    data = request.json or {}
    
    episode_num = data.get('episode_num', 1)
    traitor = data.get('traitor', 'Unknown')
    
    logger.start_episode(episode_num, traitor)
    
    return jsonify({
        'status': 'started',
        'episode_num': episode_num,
        'traitor': traitor,
        'timestamp': datetime.now().isoformat()
    }), 201

@app.route('/api/training/turn', methods=['POST'])
def log_training_turn():
    """Log training turn"""
    data = request.json or {}
    
    logger.log_turn(
        turn=data.get('turn', 0),
        day=data.get('day', 1),
        phase=data.get('phase', 'exploration'),
        agent=data.get('agent', 'Unknown'),
        role=data.get('role', 'colonist'),
        action=data.get('action', 'wait'),
        reasoning=data.get('reasoning', ''),
        message=data.get('message', ''),
        position=data.get('position', {'x': 0, 'y': 0, 'level': 'ground'}),
        energy=data.get('energy', 100),
        health=data.get('health', 100),
        backpack=data.get('backpack', {}),
        reward=data.get('reward', 0),
        ship_progress=data.get('ship_progress', 0)
    )
    
    return jsonify({'status': 'logged'}), 200

@app.route('/api/training/voting', methods=['POST'])
def log_voting_phase():
    """Log voting phase"""
    data = request.json or {}
    
    logger.log_voting_phase(
        day=data.get('day', 1),
        caller=data.get('caller', 'Unknown'),
        discussions=data.get('discussions', []),
        votes=data.get('votes', []),
        eliminated=data.get('eliminated', None),
        outcome=data.get('outcome', 'pending')
    )
    
    return jsonify({'status': 'logged'}), 200

@app.route('/api/training/map', methods=['POST'])
def save_map_state():
    """Save map state"""
    data = request.json or {}
    
    logger.save_map_state(
        level=data.get('level', 'ground'),
        terrain=data.get('terrain', [])
    )
    
    return jsonify({'status': 'saved'}), 200

@app.route('/api/training/episode/end', methods=['POST'])
def end_training_episode():
    """End training episode"""
    data = request.json or {}
    
    logger.end_episode(
        final_result=data.get('final_result', 'unknown'),
        ship_progress=data.get('ship_progress', 0),
        colonists_alive=data.get('colonists_alive', 5),
        traitor_alive=data.get('traitor_alive', True)
    )
    
    return jsonify({'status': 'ended'}), 200

# ===================================================================
# TRAINING STATUS ENDPOINTS
# ===================================================================

@app.route('/api/training/status', methods=['GET'])
def get_training_status():
    """Get current training status"""
    episodes = db.get_all_episodes(limit=1)
    
    if not episodes:
        return jsonify({
            'status': 'idle',
            'active_episode': None,
            'total_episodes': 0
        }), 200
    
    latest = episodes[0]
    
    return jsonify({
        'status': 'active' if not latest.get('final_result') else 'completed',
        'active_episode': latest.get('episode_id'),
        'traitor': latest.get('traitor'),
        'total_turns': latest.get('total_turns', 0),
        'total_reward': latest.get('total_reward', 0),
        'ship_progress': latest.get('ship_progress_final', 0)
    }), 200

@app.route('/api/training/stats', methods=['GET'])
def get_training_stats():
    """Get training statistics"""
    episodes = db.get_all_episodes(limit=1000)
    
    if not episodes:
        return jsonify({
            'total_episodes': 0,
            'stats': {}
        }), 200
    
    total_turns = sum(e.get('total_turns', 0) for e in episodes)
    total_reward = sum(e.get('total_reward', 0) for e in episodes)
    avg_reward = total_reward / len(episodes) if episodes else 0
    
    results = {}
    for e in episodes:
        result = e.get('final_result', 'unknown')
        results[result] = results.get(result, 0) + 1
    
    return jsonify({
        'total_episodes': len(episodes),
        'total_turns': total_turns,
        'total_reward': total_reward,
        'avg_reward_per_episode': avg_reward,
        'final_results': results
    }), 200

# ===================================================================
# ERROR HANDLERS
# ===================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ===================================================================
# MAIN
# ===================================================================

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
