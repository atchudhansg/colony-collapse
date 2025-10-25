#!/usr/bin/env python3
"""
Test script to visualize the island map
"""
import sys
sys.path.insert(0, 'marooned_env')

from environment import MaroonedEnv
from config import MapLevel

# Create environment
env = MaroonedEnv(seed=42)
env.reset()

print("🏴‍☠️ MAROONED ISLAND MAP")
print("="*60)

# Print all three levels
for level in [MapLevel.MOUNTAIN, MapLevel.GROUND, MapLevel.CAVE]:
    print(env.render_map(level))

print("\n" + "="*60)
print("Ship progress:", env.state.ship_progress.total_percentage, "%")
print("Living sailors:", list(env.state.living_sailors))
print("Traitor:", env.state.traitor_id)
