
"""
MAROONED Database Manager
Handles storage and retrieval of training episodes
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from models import EpisodeMetadata, TurnRecord, VotingPhase, GameState

class TrainingDatabase:
    """SQLite database for episode storage"""
    
    def __init__(self, db_path: str = 'data/episodes.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Episodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                traitor TEXT NOT NULL,
                final_result TEXT,
                total_turns INTEGER,
                total_reward REAL,
                ship_progress_final REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Turns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turns (
                turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                turn_number INTEGER,
                day INTEGER,
                phase TEXT,
                agent TEXT,
                role TEXT,
                action TEXT,
                reasoning TEXT,
                message TEXT,
                position_x INTEGER,
                position_y INTEGER,
                level TEXT,
                energy REAL,
                health REAL,
                reward REAL,
                ship_progress REAL,
                outcome TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
            )
        ''')
        
        # Voting phases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voting_phases (
                voting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                day INTEGER,
                caller TEXT,
                eliminated TEXT,
                outcome TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
            )
        ''')
        
        # Game state snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_states (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                turn_number INTEGER,
                day INTEGER,
                level TEXT,
                state_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_episode(self, traitor: str) -> int:
        """Create new episode, return episode_id"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO episodes (timestamp, traitor)
            VALUES (?, ?)
        ''', (timestamp, traitor))
        
        episode_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return episode_id
    
    def add_turn(self, episode_id: int, turn: TurnRecord):
        """Add turn record to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO turns 
            (episode_id, turn_number, day, phase, agent, role, action, reasoning, 
             message, position_x, position_y, level, energy, health, reward, 
             ship_progress, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            episode_id,
            turn.turn,
            turn.day,
            turn.phase,
            turn.agent,
            turn.role,
            turn.action,
            turn.reasoning,
            turn.message,
            turn.position['x'],
            turn.position['y'],
            turn.position['level'],
            turn.energy,
            turn.health,
            turn.reward,
            turn.ship_progress,
            turn.outcome
        ))
        
        conn.commit()
        conn.close()
    
    def add_voting_phase(self, episode_id: int, voting: VotingPhase):
        """Add voting phase record"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voting_phases 
            (episode_id, day, caller, eliminated, outcome)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            episode_id,
            voting.day,
            voting.caller,
            voting.eliminated,
            voting.outcome
        ))
        
        conn.commit()
        conn.close()
    
    def save_game_state(self, episode_id: int, state: GameState):
        """Save game state snapshot"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        state_json = json.dumps(state.to_dict())
        cursor.execute('''
            INSERT INTO game_states 
            (episode_id, turn_number, day, level, state_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            episode_id,
            state.turn,
            state.day,
            state.level,
            state_json
        ))
        
        conn.commit()
        conn.close()
    
    def finalize_episode(self, episode_id: int, result: str, total_reward: float, ship_progress: float, total_turns: int):
        """Finalize episode with results"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE episodes 
            SET final_result = ?, total_reward = ?, ship_progress_final = ?, total_turns = ?
            WHERE episode_id = ?
        ''', (result, total_reward, ship_progress, total_turns, episode_id))
        
        conn.commit()
        conn.close()
    
    def get_episode(self, episode_id: int) -> Dict[str, Any]:
        """Retrieve complete episode"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get episode metadata
        cursor.execute('SELECT * FROM episodes WHERE episode_id = ?', (episode_id,))
        episode = dict(cursor.fetchone() or {})
        
        # Get all turns
        cursor.execute('''
            SELECT * FROM turns WHERE episode_id = ? ORDER BY turn_number
        ''', (episode_id,))
        turns = [dict(row) for row in cursor.fetchall()]
        
        # Get voting phases
        cursor.execute('''
            SELECT * FROM voting_phases WHERE episode_id = ? ORDER BY day
        ''', (episode_id,))
        votings = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        episode['turns'] = turns
        episode['voting_phases'] = votings
        
        return episode
    
    def get_all_episodes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of all episodes"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM episodes ORDER BY episode_id DESC LIMIT ?
        ''', (limit,))
        
        episodes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return episodes
    
    def get_latest_episode(self) -> Dict[str, Any]:
        """Get most recent episode"""
        episodes = self.get_all_episodes(limit=1)
        return episodes[0] if episodes else None


class FileStorage:
    """JSON file-based storage (backup)"""
    
    def __init__(self, episodes_dir: str = 'data/episodes'):
        self.episodes_dir = Path(episodes_dir)
        self.episodes_dir.mkdir(parents=True, exist_ok=True)
    
    def save_episode(self, episode: EpisodeMetadata):
        """Save episode as JSON file"""
        filename = self.episodes_dir / f"episode_{episode.episode_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(episode.to_dict(), f, indent=2)
    
    def load_episode(self, episode_id: int) -> Optional[Dict[str, Any]]:
        """Load episode from JSON file"""
        filename = self.episodes_dir / f"episode_{episode_id}.json"

        if not filename.exists():
            return None
        
        with open(filename, 'r') as f:
            return json.load(f)
    
    def list_episodes(self) -> List[int]:
        """List all saved episode IDs"""
        files = self.episodes_dir.glob('episode_*.json')
        episode_ids = []
        
        for f in sorted(files, reverse=True):
            try:
                episode_id = int(f.stem.split('_')[1])
                episode_ids.append(episode_id)
            except (ValueError, IndexError):
                continue
        
        return episode_ids
