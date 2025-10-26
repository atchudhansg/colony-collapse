"""
🏴‍☠️ MAROONED - OpenEnv Server
================================
FastAPI server for the Marooned multi-agent environment.
Compatible with OpenEnv specification.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import os

# Add marooned_env to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'marooned_env'))

from environment import MaroonedEnv
from models import Action
from config import ActionType
from llm_interface import parse_action_safe

app = FastAPI(title="Marooned Environment", version="1.0.0")

# Global environment instance
env_instance: Optional[MaroonedEnv] = None
current_observations: Dict = {}


class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    

class StepRequest(BaseModel):
    action: str
    sailor_id: str
    

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]


@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "name": "Marooned Environment Server",
        "version": "1.0.0",
        "description": "Multi-agent social deduction survival game",
        "endpoints": ["/health", "/reset", "/step", "/state"]
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment_initialized": env_instance is not None
    }


@app.post("/reset")
def reset():
    """Reset the environment and return initial observation"""
    global env_instance, current_observations
    
    try:
        env_instance = MaroonedEnv(seed=None)
        current_observations = env_instance.reset()
        
        # Return first active sailor's observation
        active_sailor = env_instance.state.get_active_sailor()
        
        if active_sailor and active_sailor in current_observations:
            obs = current_observations[active_sailor]
            return {
                "observation": {
                    "sailor_id": active_sailor,
                    "day": obs.day,
                    "turn": obs.turn,
                    "phase": obs.phase,
                    "energy": obs.energy,
                    "position": obs.position.to_tuple(),
                    "ship_progress": obs.ship_progress.total_percentage,
                }
            }
        
        return {"observation": {"sailor_id": "unknown", "error": "No active sailor"}}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step")
def step(request: StepRequest):
    """Execute one step in the environment"""
    global env_instance, current_observations
    
    if env_instance is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first")
    
    try:
        # Get sailor's current position for action parsing
        sailor = env_instance.state.sailors.get(request.sailor_id)
        if sailor is None:
            raise HTTPException(status_code=400, detail=f"Invalid sailor_id: {request.sailor_id}")
        
        # Parse the action text into an Action object
        action = parse_action_safe(request.action, request.sailor_id, sailor.position)
        
        if action is None:
            # Fallback to WAIT if parsing fails
            action = Action(sailor_id=request.sailor_id, action_type=ActionType.WAIT)
        
        # Execute step (returns 5 values: observations, rewards, dones, truncated, info)
        observations, rewards, dones, truncated, info = env_instance.step({request.sailor_id: action})
        current_observations = observations
        
        # Get reward for this sailor
        reward = rewards.get(request.sailor_id, 0.0)
        
        # Check if episode is done
        done = dones.get(request.sailor_id, False) or env_instance.state.game_over
        
        # Get next observation
        active_sailor = env_instance.state.get_active_sailor()
        
        if active_sailor and active_sailor in observations:
            next_obs = observations[active_sailor]
            return {
                "observation": {
                    "sailor_id": active_sailor,
                    "day": next_obs.day,
                    "turn": next_obs.turn,
                    "phase": next_obs.phase,
                    "energy": next_obs.energy,
                    "position": next_obs.position.to_tuple(),
                    "ship_progress": next_obs.ship_progress.total_percentage,
                },
                "reward": reward,
                "done": done,
                "info": info
            }
        
        return {
            "observation": {"sailor_id": "none", "info": "Game ended or no active sailor"},
            "reward": reward,
            "done": done,
            "info": info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
def get_state():
    """Get current game state"""
    global env_instance
    
    if env_instance is None:
        raise HTTPException(status_code=400, detail="Environment not initialized")
    
    try:
        return {
            "day": env_instance.state.day,
            "turn": env_instance.state.turn,
            "phase": env_instance.state.phase,
            "ship_progress": env_instance.state.ship_progress,
            "living_sailors": list(env_instance.state.living_sailors),
            "game_over": env_instance.state.game_over,
            "winner": env_instance.state.winner,
            "current_sailor": env_instance.state.get_active_sailor()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get state failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
