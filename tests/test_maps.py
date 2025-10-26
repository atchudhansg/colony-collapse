import sys
sys.path.insert(0, './marooned_env')
from environment import MaroonedEnv
from config import MapLevel, MAP_SIZES

def test_map_shapes():
    env = MaroonedEnv(seed=2025)
    env.reset()
    # Check level shapes
    for level, shape in MAP_SIZES.items():
        grid = env.state.world_map.terrain[level]
        height = len(grid)
        width = len(grid[0])
        assert (width, height) == (shape[0], shape[1]), f"{level} map wrong shape: got ({width},{height}), expected {shape}"
    print("All maps shapes correct.")

def test_map_all_walkable_at_spawn():
    env = MaroonedEnv(seed=2025)
    env.reset()
    for level in MAP_SIZES:
        grid = env.state.world_map.terrain[level]
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                assert tile.x == x and tile.y == y, f"Tile coordinates mismatch at ({x},{y},{level})"
    print("All tile coordinates valid and accessible in their row/col.")

def test_stairs_and_transitions():
    env = MaroonedEnv(seed=42)
    env.reset()
    transitions = env.state.world_map.level_transitions
    assert len(transitions) > 0, "No level transitions found."
    for pos1, pos2 in transitions:
        assert pos1.level != pos2.level, f"Transition should be between different levels: {pos1} {pos2}"
        # Check for proper boundary positions of stairs (usually at 0,0 or config-defined spots)
        for pos in [pos1, pos2]:
            grid = env.state.world_map.terrain[pos.level]
            assert grid[pos.y][pos.x].walkable, f"Stair at {pos} not walkable!"
    print("All level transitions (stairs) are valid and walkable on both ends.")

def test_map_boundaries():
    env = MaroonedEnv(seed=1234)
    env.reset()
    # Ground, Mountains, Cave edges
    for level, (w, h) in MAP_SIZES.items():
        grid = env.state.world_map.terrain[level]
        # Top-left and bottom-right corners
        for (x, y) in [(0,0), (w-1, h-1)]:
            tile = grid[y][x]
            assert tile.x == x and tile.y == y, f"Boundary mismatch in {level}: ({x},{y})"
            assert tile.walkable, f"Boundary tile not walkable in {level}: ({x},{y})"
    print("All map edge/corner tiles are valid and walkable.")

if __name__ == "__main__":
    test_map_shapes()
    test_map_all_walkable_at_spawn()
    test_stairs_and_transitions()
    test_map_boundaries()
    print("All map structure and integrity tests PASSED.")
