import sys

sys.path.insert(0, './tests')
sys.path.insert(0, './marooned_env')

from environment import MaroonedEnv
from llm_interface import observation_to_prompt
from config import ActionType

def test_phase5_openenv_basic():
    env = MaroonedEnv(seed=42)
    obs = env.reset()
    prompt = observation_to_prompt(obs['Alice'])
    assert isinstance(prompt, str) and len(prompt)>10

    print("Phase 5 basic openenv test passed")
    
if __name__ == "__main__":
    test_phase5_openenv_basic()          