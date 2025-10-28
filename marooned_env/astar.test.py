# In a notebook or test file
from pathfinding import navigate_with_astar
import sys
from config import MapLevel, TOTAL_SAILORS, MIN_SAILORS_TO_BUILD, BASE_CAMP_POSITION

sys.path.insert(0, './tests')
sys.path.insert(0, './marooned_env')
from environment import MaroonedEnv
from models import Position
from config import MapLevel, ActionType

env = MaroonedEnv(seed=42)
obs = env.reset()

sailor_id = env.state.get_active_sailor()
sailor = env.state.sailors[sailor_id]

# Navigate to a distant position
target = Position(25, 25, MapLevel.GROUND)

# Compare greedy vs A*
print("Testing A* Navigation:")
success, steps, reason = navigate_with_astar(env, sailor_id, target, verbose=True)
print(f"Result: {reason} in {steps} steps")
