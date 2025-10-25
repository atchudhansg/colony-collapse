#!/usr/bin/env python3
"""
🏴‍☠️ MAROONED - Map Viewer
===========================
Simple script to visualize all three map levels of the game.
"""

import sys
sys.path.insert(0, '.')

from environment import MaroonedEnv
from config import MapLevel


def main():
    """Display all three levels of the Marooned island map"""
    
    # Create environment (use seed for reproducible maps, or no seed for random)
    # env = MaroonedEnv(seed=42)  # Uncomment for reproducible map
    env = MaroonedEnv()  # Random map each time
    
    # Reset the environment to initialize the game state
    env.reset()
    
    # Print header
    print('🏴‍☠️ MAROONED ISLAND - All 3 Levels\n')
    print(f'Traitor: {env.state.traitor_id}')
    print(f'Sailors at base: {list(env.state.living_sailors)}\n')
    
    # Show all three levels with emojis
    print(env.render_map(MapLevel.GROUND, use_emoji=True))
    print(env.render_map(MapLevel.MOUNTAIN, use_emoji=True))
    print(env.render_map(MapLevel.CAVE, use_emoji=True))


if __name__ == "__main__":
    main()
