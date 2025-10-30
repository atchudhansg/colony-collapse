"""
Integration hook for training notebooks
Import this in your training script to enable logging
"""
import sys
from pathlib import Path

# Add API to path
api_dir = Path(__file__).parent / 'api'
sys.path.insert(0, str(api_dir))

from logger import MaroonedTrainingLogger

# Global logger instance
training_logger = None

def init_logger(db_path: str = 'data/episodes.db', use_file_storage: bool = True):
    """Initialize global logger"""
    global training_logger
    training_logger = MaroonedTrainingLogger(db_path=db_path, use_file_storage=use_file_storage)
    return training_logger

def log_episode_start(episode_num: int, traitor: str):
    """Log episode start"""
    if training_logger:
        training_logger.start_episode(episode_num, traitor)

def log_turn(turn: int, day: int, phase: str, agent: str, role: str, action: str, **kwargs):
    """Log turn"""
    if training_logger:
        training_logger.log_turn(turn, day, phase, agent, role, action, **kwargs)

def log_voting(day: int, caller: str, **kwargs):
    """Log voting phase"""
    if training_logger:
        training_logger.log_voting_phase(day, caller, **kwargs)

def log_episode_end(final_result: str, ship_progress: float, colonists_alive: int, traitor_alive: bool):
    """Log episode end"""
    if training_logger:
        training_logger.end_episode(final_result, ship_progress, colonists_alive, traitor_alive)

def get_logger():
    """Get current logger instance"""
    return training_logger
