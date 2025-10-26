import sys
sys.path.insert(0, "./marooned_env")
from environment import MaroonedEnv
from config import MapLevel, TOTAL_SAILORS

def test_env_reset_and_structure():
    env = MaroonedEnv(seed=123)
    obs = env.reset()
    
    sailor_dict = env.state.sailors
    assert isinstance(obs, dict), "Reset should return a dict of observations"
    assert len(sailor_dict) == TOTAL_SAILORS, "Expected number of soldiers"
    
    ground = env.state.world_map.terrain[MapLevel.GROUND]
    mountain = env.state.world_map.terrain[MapLevel.MOUNTAIN]
    cave = env.state.world_map.terrain[MapLevel.CAVE]
    
    # assert ground.shape == (30,30), "Ground map should be 30x30"
    # assert mountain.shape == (10,10)
    # assert cave.shape == (15,15)
    assert len(ground) == 30 and len(ground[0]) == 30, "Ground map should be 30x30"
    assert len(mountain) == 10 and len(mountain[0]) == 10, "Mountain map should be 10x10"
    assert len(cave) == 15 and len(cave[0]) == 15, "Cave map should be 15x15"
    print("test_env_reset_and_structure Passed");
    
if __name__ == "__main__":
    test_env_reset_and_structure()    