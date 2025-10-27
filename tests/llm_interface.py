def observation_to_prompt(observation, **kwargs):
        return """[MOCK PROMPT GENERATED FROM OBSERVATION]"""

def parse_llm_response(response_text):
    return {'action': 'wait'}

def parse_action_safe(action_text):
    return {'action': 'wait'}

def validate_action(action):
    return True