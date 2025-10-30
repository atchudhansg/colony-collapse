"""
MAROONED Training Logger
Captures training data during notebook execution
"""

from typing import Dict, Any, List
from models import TurnRecord, VotingPhase, GameState, EpisodeMetadata
from database import TrainingDatabase, FileStorage
import json

class MaroonedTrainingLogger:
    """Logs training episodes during RL training"""
    
    def __init__(self, db_path: str = 'data/episodes.db', use_file_storage: bool = True):
        self.db = TrainingDatabase(db_path)
        self.file_storage = FileStorage() if use_file_storage else None
        self.current_episode = None
        self.current_episode_id = None
    
    def start_episode(self, episode_num: int, traitor: str):
        """Initialize new episode"""
        self.current_episode = EpisodeMetadata(episode_num)
        self.current_episode.traitor_name = traitor
        self.current_episode_id = self.db.create_episode(traitor)
        
        print(f"[LOGGER] Episode {episode_num} started - Traitor: {traitor}")
    
    def log_turn(
        self,
        turn: int,
        day: int,
        phase: str,
        agent: str,
        role: str,
        action: str,
        reasoning: str = '',
        message: str = '',
        position: Dict[str, Any] = None,
        energy: float = 100,
        health: float = 100,
        backpack: Dict[str, int] = None,
        reward: float = 0,
        ship_progress: float = 0,
        outcome: str = 'success'
    ):
        """Log a single turn/action"""
        
        turn_record = TurnRecord(
            turn=turn,
            day=day,
            phase=phase,
            agent=agent,
            role=role,
            action=action,
            reasoning=reasoning,
            message=message,
            position=position or {'x': 0, 'y': 0, 'level': 'ground'},
            energy=energy,
            health=health,
            backpack=backpack or {},
            reward=reward,
            ship_progress=ship_progress,
            outcome=outcome
        )
        
        # Add to episode
        if self.current_episode:
            self.current_episode.turns.append(turn_record.to_dict())
            self.current_episode.total_reward += reward
            self.current_episode.total_turns = turn
        
        # Save to database
        if self.current_episode_id:
            self.db.add_turn(self.current_episode_id, turn_record)
    
    def log_voting_phase(
        self,
        day: int,
        caller: str,
        discussions: List[Dict[str, str]] = None,
        votes: List[Dict[str, str]] = None,
        eliminated: str = None,
        outcome: str = 'pending'
    ):
        """Log voting phase"""
        
        voting = VotingPhase(
            day=day,
            caller=caller,
            discussions=discussions or [],
            votes=votes or [],
            eliminated=eliminated,
            outcome=outcome
        )
        
        # Add to episode
        if self.current_episode:
            self.current_episode.voting_phases.append(voting.to_dict())
        
        # Save to database
        if self.current_episode_id:
            self.db.add_voting_phase(self.current_episode_id, voting)
    
    def save_game_state(self, turn: int, day: int, level: str, state_data: Dict[str, Any]):
        """Save game state snapshot"""
        
        game_state = GameState(turn=turn, day=day, level=level)
        game_state.agents = state_data.get('agents', {})
        game_state.inventory = state_data.get('inventory', {})
        game_state.terrain = state_data.get('terrain', None)
        
        if self.current_episode_id:
            self.db.save_game_state(self.current_episode_id, game_state)
    
    def save_map_state(self, level: str, terrain: List[List[Dict]]):
        """Save map terrain for level"""
        if self.current_episode:
            self.current_episode.map_state[level] = terrain
    
    def end_episode(
        self,
        final_result: str,
        ship_progress: float,
        colonists_alive: int,
        traitor_alive: bool
    ):
        """Finalize episode"""
        
        if self.current_episode:
            self.current_episode.final_result = final_result
            self.current_episode.episodes_stats['ship_progress_final'] = ship_progress
            self.current_episode.episodes_stats['colonists_alive'] = colonists_alive
            self.current_episode.episodes_stats['traitor_alive'] = traitor_alive
            
            # Save to file storage if enabled
            if self.file_storage:
                self.file_storage.save_episode(self.current_episode)
    
        # Finalize in database
        if self.current_episode_id:
            self.db.finalize_episode(
                self.current_episode_id,
                final_result,
                self.current_episode.total_reward if self.current_episode else 0,
                ship_progress,
                self.current_episode.total_turns if self.current_episode else 0
            )
        
        print(f"[LOGGER] Episode {self.current_episode.episode_id if self.current_episode else '?'} ended - Result: {final_result}")
    
    def get_episode_data(self, episode_id: int = None) -> Dict[str, Any]:
        """Retrieve episode data"""
        if episode_id is None:
            episode_id = self.current_episode_id
        
        if not episode_id:
            return None
        
        return self.db.get_episode(episode_id)
