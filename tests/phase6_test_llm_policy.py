import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './marooned_env')

from models import Action, ActionType
from environment import MaroonedEnv
from llm_interface import parse_llm_response, parse_action_safe, validate_action

def test_phase_llm_policy_flow():
    env = MaroonedEnv(seed=42)
    obs = env.reset()
    
    response = "some llm response" #mock llm response
    llm_action_dict = parse_llm_response(response)
    assert 'action' in llm_action_dict
    
    safe_action = parse_action_safe(llm_action_dict['action'])
    assert isinstance(safe_action, dict)
    
    valid = validate_action(safe_action)
    assert valid is True
    
    action = Action(sailor_id='Alice', action_type=ActionType.WAIT)
    obs_next, rewards, dones, trunc, info = env.step({'Alice': action})

    print("Phase 6 LLM policy flow test passed.")
    
if __name__ == "__main__":
    test_phase_llm_policy_flow()    