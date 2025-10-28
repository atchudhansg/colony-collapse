# A* Pathfinding Utilities
# Optimal pathfinding for the AI Agents

from typing import List, Tuple, Optional
import heapq
from models import Position
from config import MapLevel, ActionType

class AStarPathfinder:
    #A* pathfinding algo for single-level navigation, to find optimal path
    
    def __init__(self, environment):
        self.env = environment
        
    def find_path(
        self,
        start: Position,
        goal: Position,
        max_distance: int = 100
    ) -> Optional[List[ActionType]]:
        if start.level != goal.level:
            return None
        
        if start == goal:
            return []
        
        frontier = [] #Priority queue: (f-score, counter, pos, path)}
        heapq.heappush(frontier, (0,0, start, []))
        
        visited = set()
        counter = 1
        
        while frontier:
            f_score, _, current, path = heapq.heappop(frontier)
            
            if current == goal:
                return path
            
            pos_key = (current.x, current.y)
            if pos_key in visited:
                continue 
            visited.add(pos_key)
            
            if len(path) >= max_distance:
                continue
            
            neighbors = [
                (ActionType.MOVE_NORTH, Position(current.x, current.y - 1, current.level)),
                (ActionType.MOVE_SOUTH, Position(current.x, current.y + 1, current.level)),
                (ActionType.MOVE_EAST, Position(current.x + 1, current.y, current.level)),
                (ActionType.MOVE_WEST, Position(current.x - 1, current.y, current.level)),
            ]
            
            for action, next_pos in neighbors:
                if not self.env.state.worldmap.is_walkable(next_pos):
                    continue
                
                next_key = (next_pos.x, next_pos.y)
                if next_key in visited:
                    continue
                
                g_score = len(path) + 1
                h_score = abs(next_pos.x - goal.x) + abs(next_pos.y - goal.y)  # Manhattan distance
                f_score = g_score + h_score
                
                new_path = path + [action]
                heapq.heappush(frontier, (f_score, counter, next_pos, new_path))
                counter += 1
                
            return None
        
def navigate_with_astar(
    env,
    sailor_id: str,
    target_pos: Position,
    max_steps: int = 50,
    verbose: bool = False
) -> Tuple[bool, int, str]:
   
    from models import Action
    
    sailor = env.state.sailors[sailor_id]
    
    # Level mismatch check
    if sailor.position.level != target_pos.level:
        return False, 0, "Different levels - use level transitions first"
    
    # Find path using A*
    pathfinder = AStarPathfinder(env)
    path = pathfinder.find_path(sailor.position, target_pos, max_distance=max_steps)
    
    if path is None:
        return False, 0, f"No path found from {sailor.position.to_tuple()} to {target_pos.to_tuple()}"
    
    # Execute path
    steps = 0
    for action_type in path:
        # Check whose turn it is
        active = env.state.get_active_sailor()
        if active != sailor_id:
            # Not our turn - wait
            action = Action(sailor_id=active, action_type=ActionType.WAIT)
            env.step({active: action})
            continue
        
        # Execute move
        action = Action(sailor_id=sailor_id, action_type=action_type)
        obs, _, _, _, info = env.step({sailor_id: action})
        
        if info.get(sailor_id, {}).get('success'):
            steps += 1
            sailor = env.state.sailors[sailor_id]  # Refresh
            
            if verbose and steps % 10 == 0:
                print(f"Step {steps}: {sailor.position.to_tuple()}")
            
            # Check if arrived
            if sailor.position == target_pos:
                if verbose:
                    print(f"✓ Arrived in {steps} steps using A*")
                return True, steps, "Arrived"
        else:
            return False, steps, f"Path blocked at step {steps}"
        
        if steps >= max_steps:
            return False, steps, "Max steps reached"
    
    return True, steps, "Arrived"    
            