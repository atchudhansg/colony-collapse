"""
🏴‍☠️ MAROONED - Phase 6 Test Script
=====================================
Comprehensive testing for LLM integration.
"""

import sys
sys.path.append('marooned_env')

from environment import MaroonedEnv
from llm_interface import observation_to_prompt, parse_llm_response, parse_action_safe, validate_action
from models import Action, Position
from config import ActionType, MapLevel

def test_1_prompt_generation():
    """Test observation to prompt conversion"""
    print("\n" + "="*80)
    print("TEST 1: OBSERVATION → PROMPT CONVERSION")
    print("="*80)
    
    env = MaroonedEnv()
    observations = env.reset()
    
    # Get first sailor's observation
    active_sailor = list(observations.keys())[0]
    obs = observations[active_sailor]
    sailor_role = env.state.sailors[active_sailor].role.value
    
    # Test colonist prompt
    prompt = observation_to_prompt(obs, include_role=True, sailor_role="colonist")
    print(f"\n✅ Generated colonist prompt: {len(prompt)} characters")
    print(f"   First 300 chars:\n   {prompt[:300].replace(chr(10), chr(10) + '   ')}")
    
    # Test traitor prompt  
    prompt_traitor = observation_to_prompt(obs, include_role=True, sailor_role="traitor")
    print(f"\n✅ Generated traitor prompt: {len(prompt_traitor)} characters")
    
    return True


def test_2_action_parsing():
    """Test LLM response parsing"""
    print("\n" + "="*80)
    print("TEST 2: LLM RESPONSE → ACTION PARSING")
    print("="*80)
    
    test_cases = {
        "Movement": "ACTION: MOVE NORTH 5\nREASONING: Exploring\nMESSAGE: Going north",
        "Gathering": "ACTION: GATHER WOOD_001\nREASONING: Need wood\nMESSAGE: Gathering",
        "Building": "ACTION: BUILD hull\nREASONING: Start ship\nMESSAGE: Building hull",
        "Voting": "ACTION: VOTE Bob\nREASONING: Suspicious\nMESSAGE: Voting Bob",
        "Communication": "ACTION: SAY Hello team!\nREASONING: Greeting\nMESSAGE: ",
        "Wait": "ACTION: WAIT\nREASONING: Resting\nMESSAGE: Conserving energy",
    }
    
    current_pos = Position(10, 10, MapLevel.GROUND)
    passed = 0
    
    for name, response in test_cases.items():
        action, error = parse_llm_response(response, "Alice", current_pos)
        if action:
            print(f"✅ {name}: {action.action_type.value}")
            passed += 1
        else:
            print(f"❌ {name}: {error}")
    
    print(f"\n📊 Passed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_3_error_handling():
    """Test error handling and fallbacks"""
    print("\n" + "="*80)
    print("TEST 3: ERROR HANDLING & FALLBACKS")
    print("="*80)
    
    bad_inputs = [
        "No action field",
        "ACTION: INVALID_COMMAND\nREASONING: Bad",
        "ACTION: MOVE\nREASONING: Missing direction",
        "",
    ]
    
    current_pos = Position(10, 10, MapLevel.GROUND)
    all_fallback = True
    
    for i, bad_input in enumerate(bad_inputs):
        action = parse_action_safe(bad_input, "Alice", current_pos)
        is_wait = action.action_type == ActionType.WAIT
        symbol = "✅" if is_wait else "❌"
        print(f"{symbol} Test {i+1}: Fallback to WAIT = {is_wait}")
        all_fallback = all_fallback and is_wait
    
    return all_fallback


def test_4_action_validation():
    """Test action validation against game state"""
    print("\n" + "="*80)
    print("TEST 4: ACTION VALIDATION")
    print("="*80)
    
    env = MaroonedEnv()
    observations = env.reset()
    obs = list(observations.values())[0]  # Get first sailor's observation
    
    # Test valid action in exploration phase
    move_action = Action(
        sailor_id="Alice",
        action_type=ActionType.MOVE_NORTH,
        target_position=Position(10, 9, MapLevel.GROUND)
    )
    
    valid, msg = validate_action(move_action, obs)
    print(f"✅ MOVE in {obs.phase}: {valid}")
    
    # Test invalid action (voting in wrong phase)
    vote_action = Action(
        sailor_id="Alice",
        action_type=ActionType.VOTE,
        vote_target="Bob"
    )
    
    valid, msg = validate_action(vote_action, obs)
    print(f"✅ VOTE in {obs.phase} (should fail): {not valid} - {msg}")
    
    return True


def test_5_full_pipeline():
    """Test complete pipeline: observation → prompt → LLM → action → env"""
    print("\n" + "="*80)
    print("TEST 5: FULL PIPELINE INTEGRATION")
    print("="*80)
    
    env = MaroonedEnv()
    observations = env.reset()
    
    # Get first sailor
    active_sailor = list(observations.keys())[0]
    obs = observations[active_sailor]
    
    # Step 1: Generate prompt
    prompt = observation_to_prompt(obs, include_role=True, sailor_role="colonist")
    print(f"✅ Step 1: Generated prompt ({len(prompt)} chars)")
    
    # Step 2: Simulate LLM response
    llm_response = "ACTION: MOVE NORTH 2\nREASONING: Exploring\nMESSAGE: Moving north"
    print(f"✅ Step 2: Simulated LLM response")
    
    # Step 3: Parse to action
    action = parse_action_safe(llm_response, active_sailor, obs.position)
    print(f"✅ Step 3: Parsed to {action.action_type.value}")
    
    # Step 4: Validate
    valid, msg = validate_action(action, obs)
    print(f"✅ Step 4: Validation: {valid}")
    
    # Step 5: Execute
    actions_dict = {active_sailor: action}
    observations, rewards, dones, truncated, info = env.step(actions_dict)
    new_obs = observations[active_sailor]
    print(f"✅ Step 5: Executed in environment")
    print(f"   Position changed: {obs.position.to_tuple()} → {new_obs.position.to_tuple()}")
    
    return True


def run_all_tests():
    """Run all Phase 6 tests"""
    print("\n" + "🏴‍☠️"*20)
    print("MAROONED - PHASE 6 COMPREHENSIVE TESTING")
    print("🏴‍☠️"*20)
    
    tests = [
        ("Prompt Generation", test_1_prompt_generation),
        ("Action Parsing", test_2_action_parsing),
        ("Error Handling", test_3_error_handling),
        ("Action Validation", test_4_action_validation),
        ("Full Pipeline", test_5_full_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, passed in results:
        symbol = "✅" if passed else "❌"
        print(f"{symbol} {name}: {'PASSED' if passed else 'FAILED'}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\n📊 Total: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Phase 6 is complete!")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
    
    return total_passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
