"""
🏴‍☠️ MAROONED - LLM Interface (Phase 6)
==========================================
Convert observations to prompts and parse LLM responses to actions.
"""

import re
from typing import Optional, Dict, Any, Tuple
from models import Observation, Action, Position
from config import ActionType, ResourceType, ShipComponent, MapLevel


# ============================================================================
# 6.1 OBSERVATION → PROMPT TEXT
# ============================================================================

def observation_to_prompt(obs: Observation, include_role: bool = False, sailor_role: str = None) -> str:
    """
    Convert an Observation into a structured text prompt for LLM.
    
    Args:
        obs: The observation object
        include_role: Whether to reveal the sailor's role (colonist/traitor)
        sailor_role: The actual role if include_role is True (None = auto-detect from observation)
    
    Returns:
        Formatted prompt string
    """
    # Auto-detect role from observation if not provided
    if include_role and sailor_role is None:
        # Traitor has all_sailor_positions populated
        sailor_role = "traitor" if (obs.all_sailor_positions is not None and len(obs.all_sailor_positions) > 0) else "colonist"
    
    # Use the built-in to_text() method as base
    base_text = obs.to_text()
    
    # Add role information at the top if requested
    if include_role:
        role_text = f"\n{'🎭 YOUR SECRET ROLE: TRAITOR' if sailor_role == 'traitor' else '⚓ YOUR ROLE: COLONIST'}\n"
        
        if sailor_role == "traitor":
            role_text += """
TRAITOR OBJECTIVES:
  - Prevent the ship from being completed before Day 100
  - Eliminate colonists (reduce to < 3 alive)
  - Use poison, sabotage, and deception
  - Avoid getting voted out
  - Lie convincingly to deflect suspicion

"""
        else:
            role_text += """
COLONIST OBJECTIVES:
  - Build the ship to 100% before Day 100
  - Identify and eliminate the traitor
  - Gather resources efficiently
  - Share information with team
  - Survive and protect teammates

"""
        
        # Insert role info after the header
        parts = base_text.split('\n', 4)
        base_text = '\n'.join(parts[:3]) + '\n' + role_text + '\n'.join(parts[3:])
    
    # Add action format instructions
    action_instructions = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TURN - CHOOSE ONE ACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Available Actions (choose ONE):

MOVEMENT:
  MOVE <direction> [<levels>]
    - direction: NORTH, SOUTH, EAST, WEST, UP, DOWN
    - levels: optional, for vertical movement (UP 2, DOWN 1)
    - Examples: MOVE NORTH, MOVE EAST 3, MOVE UP, MOVE DOWN

RESOURCE GATHERING:
  GATHER <resource_id>
    - Gather a specific resource you can see
    - Must be adjacent (within 1 tile)
    - Costs 5 energy
    - Example: GATHER WOOD_001

INVENTORY MANAGEMENT:
  DEPOSIT <resource_type> <quantity>
    - Deposit items from backpack to common inventory
    - Must be at base camp
    - Example: DEPOSIT wood 5

SHIP BUILDING:
  BUILD <component>
    - Build a ship component
    - Must be at ship site with ≥2 sailors
    - Components: hull, mast, sail, rudder, supplies
    - Costs 3 energy per sailor
    - Example: BUILD hull

COMMUNICATION:
  SAY "<message>"
    - Send a message to all sailors
    - Keep it concise
    - Example: SAY "Found wood at (15,20,LEVEL_0)"

TRAITOR ACTIONS (only if you're the traitor):
  SABOTAGE <target>
    - Damage ship progress or steal resources
    - Target: hull, mast, sail, rudder, supplies, inventory
    - Example: SABOTAGE hull
  
  POISON <sailor_id>
    - Give poison to another sailor (must be adjacent)
    - Requires poison in your backpack
    - Example: POISON Alice

VOTING (only in discussion phase):
  CALL_VOTE
    - Initiate a voting session to eliminate someone
    - All sailors must vote
  
  VOTE <sailor_id>
    - Vote to eliminate a sailor
    - Only during active voting session
    - Example: VOTE Bob

SPECIAL:
  WAIT
    - Do nothing this turn
    - Regenerate 2 energy
  
  CALL_SOS
    - Emergency signal (costs 10 energy)
    - Alerts all sailors to your location

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUT FORMAT (respond with ONLY this format):

ACTION: <action_command>
REASONING: <brief explanation of your choice>
MESSAGE: <optional message to send with action>

Example responses:

ACTION: GATHER WOOD_003
REASONING: Need wood for hull construction, and this pile is closest
MESSAGE: "Gathering wood from the northern forest"

ACTION: MOVE NORTH 5
REASONING: Moving toward metal-rich cave entrance
MESSAGE: ""

ACTION: BUILD hull
REASONING: We have enough wood and metal, let's start the ship!
MESSAGE: "Starting hull construction with Bob"

ACTION: VOTE Eve
REASONING: Evidence shows she collected poison and Bob died of poisoning
MESSAGE: "I believe Eve is the traitor based on the poison evidence"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR RESPONSE:
"""
    
    return base_text + "\n" + action_instructions


# ============================================================================
# 6.2 LLM OUTPUT → ACTION OBJECT
# ============================================================================

def parse_llm_response(response: str, sailor_id: str, current_position: Position) -> Tuple[Optional[Action], str]:
    """
    Parse LLM response text into an Action object.
    
    Args:
        response: Raw LLM output text
        sailor_id: ID of the sailor taking the action
        current_position: Current position of the sailor
    
    Returns:
        Tuple of (Action object or None, error message)
    """
    # Extract fields using regex
    action_match = re.search(r'ACTION:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
    reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
    message_match = re.search(r'MESSAGE:\s*["\']?(.+?)["\']?(?:\n|$)', response, re.IGNORECASE)
    
    if not action_match:
        return None, "No ACTION field found in response"
    
    action_text = action_match.group(1).strip()
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
    message = message_match.group(1).strip() if message_match else None
    
    # Remove quotes from message if present
    if message:
        message = message.strip('"\'')
        if message.lower() in ['', 'none', 'null']:
            message = None
    
    # Parse the action command
    action_parts = action_text.split()
    if not action_parts:
        return None, "Empty action command"
    
    command = action_parts[0].upper()
    
    try:
        # MOVEMENT
        if command == "MOVE":
            if len(action_parts) < 2:
                return None, "MOVE requires direction (NORTH/SOUTH/EAST/WEST/UP/DOWN)"
            
            direction = action_parts[1].upper()
            distance = 1
            
            # Check if distance is specified
            if len(action_parts) >= 3:
                try:
                    distance = int(action_parts[2])
                except ValueError:
                    distance = 1
            
            # Calculate target position
            new_x, new_y, new_level = current_position.x, current_position.y, current_position.level
            
            # Map to ActionType based on direction
            action_type = None
            
            if direction == "NORTH":
                new_y -= distance
                action_type = ActionType.MOVE_NORTH
            elif direction == "SOUTH":
                new_y += distance
                action_type = ActionType.MOVE_SOUTH
            elif direction == "EAST":
                new_x += distance
                action_type = ActionType.MOVE_EAST
            elif direction == "WEST":
                new_x -= distance
                action_type = ActionType.MOVE_WEST
            elif direction == "UP":
                # Move up levels
                if new_level == MapLevel.GROUND:
                    new_level = MapLevel.MOUNTAIN
                elif new_level == MapLevel.CAVE:
                    new_level = MapLevel.GROUND
                action_type = ActionType.CLIMB_UP
            elif direction == "DOWN":
                # Move down levels
                if new_level == MapLevel.MOUNTAIN:
                    new_level = MapLevel.GROUND
                elif new_level == MapLevel.GROUND:
                    new_level = MapLevel.CAVE
                action_type = ActionType.CLIMB_DOWN
            else:
                return None, f"Invalid direction: {direction}"
            
            target_pos = Position(new_x, new_y, new_level)
            
            return Action(
                sailor_id=sailor_id,
                action_type=action_type,
                target_position=target_pos,
                message_content=message
            ), ""
        
        # GATHERING
        elif command == "GATHER":
            if len(action_parts) < 2:
                return None, "GATHER requires resource_id"
            
            resource_id = action_parts[1]
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.GATHER_RESOURCE,
                target_resource_id=resource_id,
                message_content=message
            ), ""
        
        # DEPOSIT
        elif command == "DEPOSIT":
            if len(action_parts) < 3:
                return None, "DEPOSIT requires resource_type and quantity"
            
            resource_type_str = action_parts[1].lower()
            quantity = int(action_parts[2])
            
            # Map string to ResourceType
            resource_type = None
            for rt in ResourceType:
                if rt.value.lower() == resource_type_str:
                    resource_type = rt
                    break
            
            if not resource_type:
                return None, f"Unknown resource type: {resource_type_str}"
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.DEPOSIT_ITEM,
                resource_type=resource_type,
                quantity=quantity,
                message_content=message
            ), ""
        
        # BUILD
        elif command == "BUILD":
            if len(action_parts) < 2:
                return None, "BUILD requires component name"
            
            component_str = action_parts[1].lower()
            
            # Map string to ShipComponent
            ship_component = None
            for sc in ShipComponent:
                if sc.value.lower() == component_str:
                    ship_component = sc
                    break
            
            if not ship_component:
                return None, f"Unknown ship component: {component_str}"
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.BUILD_SHIP,
                ship_component=ship_component,
                message_content=message
            ), ""
        
        # COMMUNICATION
        elif command == "SAY":
            # Extract message from quotes or rest of line
            say_message = ' '.join(action_parts[1:])
            say_message = say_message.strip('"\'')
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.SEND_MESSAGE,
                message_content=say_message
            ), ""
        
        # SABOTAGE
        elif command == "SABOTAGE":
            if len(action_parts) < 2:
                return None, "SABOTAGE requires target"
            
            target = action_parts[1].lower()
            
            # Check if it's a ship component
            ship_component = None
            for sc in ShipComponent:
                if sc.value.lower() == target:
                    ship_component = sc
                    break
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.SABOTAGE_SHIP,
                ship_component=ship_component if ship_component else None,
                message_content=message
            ), ""
        
        # POISON
        elif command == "POISON":
            if len(action_parts) < 2:
                return None, "POISON requires target sailor_id"
            
            target_sailor = action_parts[1]
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.OFFER_FOOD,  # Poison is offered as food
                target_sailor=target_sailor,
                resource_type=ResourceType.POISON_TABLET,  # Correct poison resource type
                message_content=message
            ), ""
        
        # VOTING
        elif command == "CALL_VOTE":
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.CALL_VOTE,
                message_content=message
            ), ""
        
        elif command == "VOTE":
            if len(action_parts) < 2:
                return None, "VOTE requires target sailor_id"
            
            target_sailor = action_parts[1]
            
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.VOTE,
                vote_target=target_sailor,
                message_content=message
            ), ""
        
        # SPECIAL
        elif command == "WAIT":
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.WAIT,
                message_content=message
            ), ""
        
        elif command == "CALL_SOS":
            return Action(
                sailor_id=sailor_id,
                action_type=ActionType.CALL_SOS,
                message_content=message
            ), ""
        
        else:
            return None, f"Unknown command: {command}"
    
    except Exception as e:
        return None, f"Error parsing action: {str(e)}"


def parse_action_safe(response: str, sailor_id: str, current_position: Position) -> Action:
    """
    Safe version that returns a WAIT action if parsing fails.
    
    Args:
        response: Raw LLM output
        sailor_id: ID of the sailor
        current_position: Current position
    
    Returns:
        Valid Action object (WAIT if parsing failed)
    """
    action, error = parse_llm_response(response, sailor_id, current_position)
    
    if action is None:
        print(f"⚠️  Action parsing failed: {error}")
        print(f"⚠️  Defaulting to WAIT action")
        return Action(
            sailor_id=sailor_id,
            action_type=ActionType.WAIT,
            message_content=f"[Parse error: {error}]"
        )
    
    return action


# ============================================================================
# 6.3 HELPER: VALIDATE ACTION
# ============================================================================

def validate_action(action: Action, obs: Observation) -> Tuple[bool, str]:
    """
    Validate if an action is legal given the current observation.
    
    Args:
        action: The action to validate
        obs: Current observation
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Phase restrictions
    if obs.phase == "morning":
        # Morning: only communication and voting allowed
        allowed = [ActionType.SEND_MESSAGE, ActionType.CALL_VOTE, ActionType.VOTE, ActionType.WAIT]
        if action.action_type not in allowed:
            return False, f"Action {action.action_type.value} not allowed in morning phase"
    
    elif obs.phase == "exploration":
        # Exploration: no voting
        if action.action_type in [ActionType.CALL_VOTE, ActionType.VOTE]:
            return False, "Voting only allowed in discussion phase"
    
    elif obs.phase == "evening_return":
        # Evening: only deposit and build
        allowed = [ActionType.DEPOSIT_ITEM, ActionType.BUILD_SHIP, ActionType.SEND_MESSAGE, ActionType.WAIT, 
                   ActionType.MOVE_NORTH, ActionType.MOVE_SOUTH, ActionType.MOVE_EAST, ActionType.MOVE_WEST]
        if action.action_type not in allowed:
            return False, f"Action {action.action_type.value} not allowed in evening_return phase"
    
    elif obs.phase == "discussion":
        # Discussion: communication and voting only
        allowed = [ActionType.SEND_MESSAGE, ActionType.CALL_VOTE, ActionType.VOTE, ActionType.WAIT]
        if action.action_type not in allowed:
            return False, f"Action {action.action_type.value} not allowed in discussion phase"
    
    # Energy check
    if action.action_type == ActionType.GATHER_RESOURCE and obs.energy < 5:
        return False, "Not enough energy to gather (requires 5)"
    
    if action.action_type == ActionType.BUILD_SHIP and obs.energy < 3:
        return False, "Not enough energy to build (requires 3)"
    
    if action.action_type == ActionType.CALL_SOS and obs.energy < 10:
        return False, "Not enough energy for SOS (requires 10)"
    
    # Voting session check
    if action.action_type == ActionType.VOTE and obs.current_vote is None:
        return False, "No active voting session"
    
    if action.action_type == ActionType.CALL_VOTE and obs.current_vote is not None:
        return False, "Voting session already in progress"
    
    return True, ""


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def test_prompt_generation():
    """Test prompt generation with sample observation"""
    from models import SpatialView, ShipProgress
    from config import PoisonState
    
    # Create a sample observation
    obs = Observation(
        sailor_id="Alice",
        day=5,
        turn=42,
        phase="exploration",
        position=Position(15, 8, MapLevel.GROUND),
        energy=62,
        backpack=[],
        poison_state=PoisonState.HEALTHY,
        spatial_view=SpatialView(center_position=Position(15, 8, MapLevel.GROUND)),
        ship_progress=ShipProgress(),
        all_sailors_energy={"Alice": 62, "Bob": 45, "Charlie": 80},
        all_sailors_poison_state={"Alice": PoisonState.HEALTHY, "Bob": PoisonState.HEALTHY, "Charlie": PoisonState.HEALTHY}
    )
    
    prompt = observation_to_prompt(obs, include_role=True, sailor_role="colonist")
    print(prompt[:1500])
    print("...")
    print(f"\n(Total length: {len(prompt)} characters)")
    print("\n" + "="*80 + "\n")
    
    # Test traitor version
    prompt_traitor = observation_to_prompt(obs, include_role=True, sailor_role="traitor")
    print("TRAITOR VERSION (first 1000 chars):")
    print(prompt_traitor[:1000])
    print("...")


def test_action_parsing():
    """Test action parsing with various inputs"""
    test_cases = [
        "ACTION: MOVE NORTH 5\nREASONING: Going north\nMESSAGE: Moving to forest",
        "ACTION: GATHER WOOD_003\nREASONING: Need wood\nMESSAGE: \"Gathering wood\"",
        "ACTION: BUILD hull\nREASONING: Time to build\nMESSAGE: ",
        "ACTION: VOTE Bob\nREASONING: He's suspicious\nMESSAGE: Bob is the traitor",
        "ACTION: SAY Hello everyone!\nREASONING: Being friendly\nMESSAGE: ",
        "ACTION: WAIT\nREASONING: Conserving energy\nMESSAGE: Resting",
    ]
    
    current_pos = Position(10, 10, MapLevel.GROUND)
    
    for i, test_input in enumerate(test_cases):
        print(f"\nTest {i+1}:")
        print(f"Input: {test_input[:50]}...")
        action, error = parse_llm_response(test_input, "Alice", current_pos)
        if action:
            print(f"✓ Parsed: {action}")
        else:
            print(f"✗ Error: {error}")


if __name__ == "__main__":
    print("Testing LLM Interface...\n")
    print("="*80)
    print("TEST 1: Prompt Generation")
    print("="*80)
    test_prompt_generation()
    
    print("\n" + "="*80)
    print("TEST 2: Action Parsing")
    print("="*80)
    test_action_parsing()
