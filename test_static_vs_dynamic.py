"""
Test to verify static map (frozen) vs spatial view (dynamic from centralized map)
"""
import sys
sys.path.insert(0, 'marooned_env')

from environment import MaroonedEnv
from models import Action
from config import ActionType

print("=" * 80)
print("🧪 TEST: Static Map (Frozen) vs Spatial View (Dynamic)")
print("=" * 80)

# Create environment
env = MaroonedEnv(seed=42)
obs = env.reset(seed=42)

alice_obs = obs["Alice"]

# Count initial resources in static map
initial_resource_count = len(alice_obs.all_resources)
print(f"\n📸 Initial snapshot (static map): {initial_resource_count} resources")

# Count resources visible in spatial view
initial_spatial_count = len(alice_obs.spatial_view.visible_resources)
print(f"👁️ Initial spatial view: {initial_spatial_count} visible resources")

# Find a resource near Alice
print(f"\n🎯 Alice at: {alice_obs.position.to_tuple()}")

# Get nearest resource
nearest_resource = None
min_distance = float('inf')
for res in alice_obs.spatial_view.visible_resources:
    dist = res.position.distance_to(alice_obs.position)
    if dist < min_distance:
        min_distance = dist
        nearest_resource = res

if nearest_resource:
    print(f"📦 Nearest resource: {nearest_resource.resource_type.value} at {nearest_resource.position.to_tuple()}")
    print(f"   Distance: {min_distance} tiles")
    
    # Gather the resource
    print(f"\n⚙️ Gathering {nearest_resource.resource_id}...")
    
    actions = {sid: Action(sailor_id=sid, action_type=ActionType.WAIT) for sid in env.agents}
    actions["Alice"] = Action(
        sailor_id="Alice",
        action_type=ActionType.GATHER,
        target_resource_id=nearest_resource.resource_id
    )
    
    obs2, rewards, dones, truncated, info = env.step(actions)
    
    print(f"   Result: {info['Alice'].get('success', False)}")
    
    if info['Alice'].get('success'):
        alice_obs2 = obs2["Alice"]
        
        # Check static map (should be UNCHANGED)
        static_count_after = len(alice_obs2.all_resources)
        print(f"\n📸 Static map after gathering: {static_count_after} resources")
        print(f"   Changed? {static_count_after != initial_resource_count}")
        
        # Check spatial view (should be UPDATED - resource gone)
        spatial_count_after = len(alice_obs2.spatial_view.visible_resources)
        print(f"\n👁️ Spatial view after gathering: {spatial_count_after} visible resources")
        print(f"   Changed? {spatial_count_after != initial_spatial_count}")
        
        # Verify the gathered resource is gone from spatial but still in static
        resource_in_static = any(r.resource_id == nearest_resource.resource_id for r in alice_obs2.all_resources)
        resource_in_spatial = any(r.resource_id == nearest_resource.resource_id for r in alice_obs2.spatial_view.visible_resources)
        
        print(f"\n🔍 Gathered resource ({nearest_resource.resource_id}):")
        print(f"   Still in static map? {resource_in_static}")
        print(f"   Still in spatial view? {resource_in_spatial}")
        
        print("\n" + "=" * 80)
        print("✅ TEST RESULTS:")
        print("=" * 80)
        
        if static_count_after == initial_resource_count and resource_in_static:
            print("✅ Static map is FROZEN (unchanged after gathering)")
        else:
            print("❌ Static map is UPDATING (should be frozen!)")
        
        if spatial_count_after < initial_spatial_count and not resource_in_spatial:
            print("✅ Spatial view is DYNAMIC (updated from centralized map)")
        else:
            print("❌ Spatial view is NOT updating correctly")
        
        print("\n📊 Summary:")
        print(f"   Static map: {initial_resource_count} → {static_count_after} (should stay same)")
        print(f"   Spatial view: {initial_spatial_count} → {spatial_count_after} (should decrease)")
        
else:
    print("❌ No resource found near Alice to test!")

print("\n" + "=" * 80)
