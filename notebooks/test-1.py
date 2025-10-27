import sys
sys.path.insert(0, '../marooned_env')

# FORCE RELOAD MODULES TO PICK UP LATEST CHANGES
modules_to_clear = [m for m in list(sys.modules.keys()) 
                   if 'marooned' in m or m in ['environment', 'config', 'models', 'game_state', 'view_map', 'llm_interface']]
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

from environment import MaroonedEnv
from llm_interface import observation_to_prompt
from models import Action, Position
from config import ActionType, MapLevel


# Create fresh environment
env2 = MaroonedEnv(seed=42)
observations2 = env2.reset(seed=42)

# Get Alice's starting position
alice_sailor = env2.state.sailors["Alice"]

# Find mountain stairs location (from level transitions)
mountain_stairs_pos = None
for pos1, pos2 in env2.state.world_map.level_transitions:
    if pos1.level == MapLevel.GROUND and pos2.level == MapLevel.MOUNTAIN:
        mountain_stairs_pos = pos1
        break
    elif pos2.level == MapLevel.GROUND and pos1.level == MapLevel.MOUNTAIN:
        mountain_stairs_pos = pos2
        break

if mountain_stairs_pos:
    
    # Simple AI navigation function with detailed energy tracking
    moves = 0
    max_moves = 50
    successful_moves = 0
    energy_log = [alice_sailor.energy]  # Track energy at each step
    
    
    while alice_sailor.position != mountain_stairs_pos and moves < max_moves:
        energy_before = alice_sailor.energy
        
        # Calculate direction
        dx = mountain_stairs_pos.x - alice_sailor.position.x
        dy = mountain_stairs_pos.y - alice_sailor.position.y
        
        # Choose movement direction (greedy approach)
        if abs(dx) > abs(dy) and dx != 0:
            action_type = ActionType.MOVE_EAST if dx > 0 else ActionType.MOVE_WEST
            dir_name = "EAST" if dx > 0 else "WEST"
        elif dy != 0:
            action_type = ActionType.MOVE_SOUTH if dy > 0 else ActionType.MOVE_NORTH
            dir_name = "SOUTH" if dy > 0 else "NORTH"
        else:
            break
        
        # Create and execute action
        action = Action(sailor_id="Alice", action_type=action_type)
        actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
        actions["Alice"] = action
        
        obs2, rewards, dones, truncated, info = env2.step(actions)
        
        energy_after = alice_sailor.energy
        energy_used = energy_before - energy_after
        
        if info["Alice"].get('success'):
            successful_moves += 1
            energy_log.append(energy_after)
        else:
            # Try perpendicular direction
            
            if abs(dy) > abs(dx) and dy != 0:
                action_type = ActionType.MOVE_SOUTH if dy > 0 else ActionType.MOVE_NORTH
                dir_name = "SOUTH" if dy > 0 else "NORTH"
            elif dx != 0:
                action_type = ActionType.MOVE_EAST if dx > 0 else ActionType.MOVE_WEST
                dir_name = "EAST" if dx > 0 else "WEST"
            else:
                break
            
            action = Action(sailor_id="Alice", action_type=action_type)
            actions["Alice"] = action
            obs2, rewards, dones, truncated, info = env2.step(actions)
            
            if info["Alice"].get('success'):
                energy_after = alice_sailor.energy
                energy_used = energy_before - energy_after
                successful_moves += 1
                print(f"  ✅ Alternate: {dir_name} → ({alice_sailor.position.x}, {alice_sailor.position.y}) | Energy: {energy_after}/100 (used {energy_used})")
                energy_log.append(energy_after)
        
        moves += 1
    

    energy_before_climb = alice_sailor.energy
    climb_action = Action(sailor_id="Alice", action_type=ActionType.CLIMB_UP)
    actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
    actions["Alice"] = climb_action
    
    obs2, rewards, dones, truncated, info = env2.step(actions)
    energy_after_climb = alice_sailor.energy
    

    energy_before_mountain = alice_sailor.energy
    move_action = Action(sailor_id="Alice", action_type=ActionType.MOVE_EAST)
    actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
    actions["Alice"] = move_action
    obs2, rewards, dones, truncated, info = env2.step(actions)
    energy_after_mountain = alice_sailor.energy
    
    # Find energy resource (apple only - berries are not edible in this game) near Alice
    alice_obs = env2._generate_observation("Alice")
    energy_resource = None
    for res in alice_obs.spatial_view.visible_resources:
        if res.resource_type.value == "apple":
            energy_resource = res
            break
    
    
    if energy_resource:
        # Navigate to the resource
        while alice_sailor.position != energy_resource.position and moves < max_moves + 20:
            dx = energy_resource.position.x - alice_sailor.position.x
            dy = energy_resource.position.y - alice_sailor.position.y
            
            if dx != 0:
                action_type = ActionType.MOVE_EAST if dx > 0 else ActionType.MOVE_WEST
            elif dy != 0:
                action_type = ActionType.MOVE_SOUTH if dy > 0 else ActionType.MOVE_NORTH
            else:
                break
            
            action = Action(sailor_id="Alice", action_type=action_type)
            actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
            actions["Alice"] = action
            obs2, rewards, dones, truncated, info = env2.step(actions)
            
            if info["Alice"].get('success'):
                print(f"  Moved to ({alice_sailor.position.x}, {alice_sailor.position.y})")
        
        # Gather the resource
        energy_before_gather = alice_sailor.energy
        gather_action = Action(sailor_id="Alice", action_type=ActionType.GATHER_RESOURCE, target_resource_id=energy_resource.resource_id)
        actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
        actions["Alice"] = gather_action
        obs2, rewards, dones, truncated, info = env2.step(actions)
        print(f"  Energy: {energy_before_gather} → {alice_sailor.energy}")
        
        # Eat the resource
        if info['Alice'].get('success'):
            print(f"\n🍽️ Eating {energy_resource.resource_type.value}...")
            energy_before_eat = alice_sailor.energy
            eat_action = Action(sailor_id="Alice", action_type=ActionType.EAT_FOOD, target_resource_id=energy_resource.resource_type)
            actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
            actions["Alice"] = eat_action
            obs2, rewards, dones, truncated, info = env2.step(actions)
            print(f"  Eat result: {info['Alice']}")
            print(f"  Energy: {energy_before_eat} → {alice_sailor.energy}")
    


    alice_obs_final = env2._generate_observation("Alice")
    alice_prompt = observation_to_prompt(alice_obs_final, include_role=True)
    print(alice_prompt)
    
    # NOW CHARLIE'S TURN
    print("\n" + "=" * 80)
    print("🎯 CHARLIE'S TURN - Going to Mountain")
    print("=" * 80)
    
    charlie_sailor = env2.state.sailors["Charlie"]
    print(f"\n📍 Charlie starting position: {charlie_sailor.position.to_tuple()}")
    
    # Navigate Charlie to mountain stairs
    charlie_moves = 0
    max_charlie_moves = 50
    
    while charlie_sailor.position != mountain_stairs_pos and charlie_moves < max_charlie_moves:
        dx = mountain_stairs_pos.x - charlie_sailor.position.x
        dy = mountain_stairs_pos.y - charlie_sailor.position.y
        
        if abs(dx) > abs(dy) and dx != 0:
            action_type = ActionType.MOVE_EAST if dx > 0 else ActionType.MOVE_WEST
        elif dy != 0:
            action_type = ActionType.MOVE_SOUTH if dy > 0 else ActionType.MOVE_NORTH
        else:
            break
        
        action = Action(sailor_id="Charlie", action_type=action_type)
        actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
        actions["Charlie"] = action
        obs2, rewards, dones, truncated, info = env2.step(actions)
        
        if not info["Charlie"].get('success'):
            # Try perpendicular
            if abs(dy) > abs(dx) and dy != 0:
                action_type = ActionType.MOVE_SOUTH if dy > 0 else ActionType.MOVE_NORTH
            elif dx != 0:
                action_type = ActionType.MOVE_EAST if dx > 0 else ActionType.MOVE_WEST
            else:
                break
            
            action = Action(sailor_id="Charlie", action_type=action_type)
            actions["Charlie"] = action
            obs2, rewards, dones, truncated, info = env2.step(actions)
        
        charlie_moves += 1
    
    
    # Charlie climbs up
    climb_action = Action(sailor_id="Charlie", action_type=ActionType.CLIMB_UP)
    actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
    actions["Charlie"] = climb_action
    obs2, rewards, dones, truncated, info = env2.step(actions)
    print(f"  Climb result: {info['Charlie']}")
    print(f"  New position: {charlie_sailor.position.to_tuple()}")
    
    # Charlie moves 1 tile
    for i in range(2):
        move_action = Action(sailor_id="Charlie", action_type=ActionType.MOVE_EAST)
        actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env2.agents}
        actions["Charlie"] = move_action
        obs2, rewards, dones, truncated, info = env2.step(actions)
        print(f"  Move result: {info['Charlie'].get('success', False)}")
        print(f"  Position: {charlie_sailor.position.to_tuple()}")
    
    # Generate Charlie's observation
    print("\n" + "=" * 80)
    print("🎯 CHARLIE'S OBSERVATION (on mountain)")
    print("=" * 80)
    charlie_obs = env2._generate_observation("Charlie")
    charlie_prompt = observation_to_prompt(charlie_obs, include_role=True)
    print(charlie_prompt)