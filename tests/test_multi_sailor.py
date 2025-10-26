import sys
sys.path.insert(0, './marooned_env')
from environment import MaroonedEnv
from config import MapLevel, TOTAL_SAILORS, MIN_SAILORS_TO_BUILD, BASE_CAMP_POSITION
from models import InventoryItem, ResourceType, Action, ActionType

noop_action = Action(sailor_id = "SAILOR_ID", action_type=ActionType.WAIT)
def test_turn_order_is_correct():
    env = MaroonedEnv(seed=42)
    env.reset()
    order = []
    for _ in range(TOTAL_SAILORS * 2 ):
        active = env.state.get_active_sailor()
        order.append(active)
        actions = {active: env._noop_action(active)}
        env.step(actions)
    expected = order[:TOTAL_SAILORS]
    
 # ORDER SHOULD CYCLE IN ROUND ROBIN
    assert order[TOTAL_SAILORS:TOTAL_SAILORS * 2] == expected, f"Turn order failed: {order}"
    print("test_turn_order_is_correct PASSED!")                
    
if __name__ == "__main__":
    test_turn_order_is_correct()   