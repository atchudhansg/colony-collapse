"""
MAROONED Training Data Models
Defines database schema for episode storage
"""

from datetime import datetime
import json
from typing import Dict, List, Any

class EpisodeMetadata:
    """Metadata for a complete training episode"""
    
    def __init__(self, episode_id: int):
        self.episode_id = episode_id
        self.timestamp = datetime.now().isoformat()
        self.traitor_name = None
        self.traitors_list = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        self.map_state = {
            'ground': None,
            'cave': None,
            'mountain': None
        }
        self.turns = []
        self.voting_phases = []
        self.final_result = None
        self.total_reward = 0
        self.total_turns = 0
        self.episodes_stats = {
            'ship_progress_max': 0,
            'ship_progress_final': 0,
            'colonists_alive': 5,
            'traitor_alive': True
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'episode_id': self.episode_id,
            'timestamp': self.timestamp,
            'traitor': self.traitor_name,
            'map_state': self.map_state,
            'turns': self.turns,
            'voting_phases': self.voting_phases,
            'final_result': self.final_result,
            'total_reward': self.total_reward,
            'total_turns': self.total_turns,
            'stats': self.episodes_stats
        }


class TurnRecord:
    """Record for a single turn/action"""
    
    def __init__(
        self,
        turn: int,
        day: int,
        phase: str,
        agent: str,
        role: str,
        action: str,
        reasoning: str = '',
        message: str = '',
        position: Dict[str, int] = None,
        energy: float = 100,
        health: float = 100,
        backpack: Dict[str, int] = None,
        reward: float = 0,
        ship_progress: float = 0,
        target: str = None,
        outcome: str = 'success'
    ):
        self.turn = turn
        self.day = day
        self.phase = phase
        self.agent = agent
        self.role = role
        self.action = action
        self.reasoning = reasoning
        self.message = message
        self.position = position or {'x': 0, 'y': 0, 'level': 'ground'}
        self.energy = energy
        self.health = health
        self.backpack = backpack or {}
        self.reward = reward
        self.ship_progress = ship_progress
        self.target = target
        self.outcome = outcome
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'turn': self.turn,
            'day': self.day,
            'phase': self.phase,
            'agent': self.agent,
            'role': self.role,
            'action': self.action,
            'reasoning': self.reasoning,
            'message': self.message,
            'position': self.position,
            'energy': self.energy,
            'health': self.health,
            'backpack': self.backpack,
            'reward': self.reward,
            'ship_progress': self.ship_progress,
            'target': self.target,
            'outcome': self.outcome,
            'timestamp': self.timestamp
        }


class VotingPhase:
    """Record for voting phase"""
    
    def __init__(
        self,
        day: int,
        caller: str,
        discussions: List[Dict[str, str]] = None,
        votes: List[Dict[str, str]] = None,
        eliminated: str = None,
        outcome: str = 'pending'
    ):
        self.day = day
        self.caller = caller
        self.discussions = discussions or []
        self.votes = votes or []
        self.eliminated = eliminated
        self.outcome = outcome
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'day': self.day,
            'caller': self.caller,
            'discussions': self.discussions,
            'votes': self.votes,
            'eliminated': self.eliminated,
            'outcome': self.outcome,
            'timestamp': self.timestamp
        }


class GameState:
    """Complete game state snapshot"""
    
    def __init__(
        self,
        turn: int,
        day: int,
        level: str = 'ground'
    ):
        self.turn = turn
        self.day = day
        self.level = level
        self.agents = {}  # Agent status by turn
        self.inventory = {
            'common': {'wood': 0, 'metal': 0, 'fiber': 0, 'food': 0, 'antidote': 0},
            'ship_components': {'hull': 0, 'mast': 0, 'sail': 0, 'rudder': 0, 'supplies': 0}
        }
        self.terrain = None
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'turn': self.turn,
            'day': self.day,
            'level': self.level,
            'agents': self.agents,
            'inventory': self.inventory,
            'terrain': self.terrain,
            'timestamp': self.timestamp
        }