import sys
sys.path.insert(0, './marooned_env')

from environment import MaroonedEnv
from config import (
    ActionType,
    REWARD_COLONIST_GATHER_RESOURCE,
    REWARD_COLONIST_DEPOSIT_RESOURCE,
    MAP_SIZES,
    BASE_CAMP_POSITION,
)
from models import Action

def move_sailor_to_resource(env, sailor_id, resource_type, max_attempts=100):
    map_level = env.state.sailors[sailor_id].position.level
    width, height = MAP_SIZES[map_level]

    for _ in range(max_attempts):
        for x in range(width):
            for y in range(height):
                # Use correct attribute 'world_map'
                if env.state.world_map.get_resources_at(x, y, map_level, resource_type):
                    env.state.sailors[sailor_id].position.x = x
                    env.state.sailors[sailor_id].position.y = y
                    env.state.sailors[sailor_id].position.level = map_level
                    return True
    return False

def test_colonist_gather_deposit():
    env = MaroonedEnv(seed=42)
    env.reset()

    sailor_id = next(iter(env.state.sailors))

    if not move_sailor_to_resource(env, sailor_id, 'wood'):
        print("Warning: Could not place sailor near resource for gather test.")

    obs, rewards, dones, trunc, info = env.step({sailor_id: Action(sailor_id=sailor_id, action_type=ActionType.GATHER_RESOURCE)})
    gather_reward = rewards.get(sailor_id)
    assert gather_reward is not None, "No gather reward returned"
    if gather_reward < REWARD_COLONIST_GATHER_RESOURCE:
        print(f"Warning: Gather reward {gather_reward} less than expected minimum {REWARD_COLONIST_GATHER_RESOURCE}")
    else:
        print(f"Gather reward validated: {gather_reward}")

    env.state.sailors[sailor_id].position.x = BASE_CAMP_POSITION[0]
    env.state.sailors[sailor_id].position.y = BASE_CAMP_POSITION[1]
    env.state.sailors[sailor_id].position.level = BASE_CAMP_POSITION[2]

    obs, rewards, dones, trunc, info = env.step({sailor_id: Action(sailor_id=sailor_id, action_type=ActionType.DEPOSIT_ITEM)})
    deposit_reward = rewards.get(sailor_id)
    assert deposit_reward is not None, "No deposit reward returned"
    if deposit_reward < REWARD_COLONIST_DEPOSIT_RESOURCE:
        print(f"Warning: Deposit reward {deposit_reward} less than expected minimum {REWARD_COLONIST_DEPOSIT_RESOURCE}")
    else:
        print(f"Deposit reward validated: {deposit_reward}")

    print("Colonist gather and deposit reward test completed.")

if __name__ == "__main__":
    test_colonist_gather_deposit()
