import sys
sys.path.insert(0, './marooned_env')
from environment import MaroonedEnv
from models import Action, ActionType

def test_movement_causes_energy_drop():
    env = MaroonedEnv(seed=42)
    env.reset()
    
    sailor_id = next(iter(env.state.sailors))
    initial_sailor = env.state.sailors[sailor_id]

    initial_energy = initial_sailor.energy
    initial_pos = initial_sailor.position

    # Try each movement action until successful move detected
    move_actions = [
        ActionType.MOVE_NORTH,
        ActionType.MOVE_SOUTH,
        ActionType.MOVE_EAST,
        ActionType.MOVE_WEST,
        ActionType.CLIMB_UP,
        ActionType.CLIMB_DOWN,
    ]

    moved = False
    for move_action in move_actions:
        action = Action(sailor_id=sailor_id, action_type=move_action)
        actions = {sailor_id: action}
        obs2, rewards, dones, truncated, info = env.step(actions)
        new_sailor = env.state.sailors[sailor_id]
        if new_sailor.position != initial_pos:
            # Movement detected, check energy
            moved = True
            assert new_sailor.energy < initial_energy, "Energy should decrease after movement"
            print(f"Movement {move_action.value} confirmed with energy drop")
            break  # Exit after first successful movement

    assert moved, "No valid movement made; agent might be blocked"
    print("test_movement_causes_energy_drop Passed")

if __name__ == "__main__":
    test_movement_causes_energy_drop()
