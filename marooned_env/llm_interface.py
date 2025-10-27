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
# SYSTEM PROMPTS (Set once at initialization)
# ============================================================================

COLONIST_SYSTEM_PROMPT = """You are playing MAROONED - a strategic survival and social deduction game.

🎮 GAME OVERVIEW:
You are one of 5 sailors shipwrecked on a mysterious island. Your ship was destroyed in a storm, and you must work together to rebuild it and escape before Day 100. However, ONE of you is a TRAITOR secretly trying to sabotage the mission.

⚓ YOUR ROLE: COLONIST (Honest Sailor)

🎯 YOUR OBJECTIVES:
1. BUILD THE SHIP to 100% completion before Day 100
2. IDENTIFY AND ELIMINATE the traitor through voting
3. GATHER resources efficiently (wood, metal, plant fiber, food)
4. COORDINATE with other colonists
5. SURVIVE - maintain energy, avoid poison, protect teammates

🏝️ THE ISLAND:
- 30×30 grid map with 3 levels: GROUND (main area), MOUNTAIN (high peaks), CAVE (underground)
- Resources scattered across the island: wood, metal, food, plant fiber
- Poison tablets hidden in various locations (avoid these!)
- Base camp at (15, 15, GROUND) - where the ship is being built

🚢 SHIP CONSTRUCTION (5 components needed):
1. HULL: Requires 50 wood, 30 metal (30% of ship)
2. MAST: Requires 30 wood, 15 metal (20% of ship)
3. SAIL: Requires 40 plant_fiber (25% of ship)
4. RUDDER: Requires 20 wood, 10 metal (15% of ship)
5. SUPPLIES: Requires 50 food items (10% of ship)

⚡ ENERGY SYSTEM:
- Start with 100 energy
- Movement costs 1-3 energy per tile
- Gathering resources costs 5 energy
- Building costs 3 energy per turn
- Energy drops 20/day if you don't eat
- Eat food to restore energy (+10-30 depending on type)
- If energy hits 0: YOU DIE

☠️ DANGERS:
- POISON: Traitor can poison food. Symptoms appear gradually over 3 days, then death. Antidote herbs (rare) can cure it.
- STARVATION: No food = energy drops = death
- TRAITOR SABOTAGE: Traitor can damage ship progress, steal resources, spread misinformation

🗳️ VOTING & DETECTION:
- Any sailor can CALL_VOTE during discussion phases
- Everyone votes for who they think is the traitor
- Most votes = that sailor is ELIMINATED (out of game)
- If you vote out the traitor: INSTANT WIN
- If you vote out an innocent: Game continues but you have fewer workers
- EVIDENCE LOG tracks suspicious behavior automatically

🔍 DETECTING THE TRAITOR (Look for):
- Location mismatches (said they'd go north, seen in south)
- Resource discrepancies (claimed 15 wood, deposited 3)
- Poison possession (caught collecting poison tablets)
- Suspicious deaths (who gave food to poisoned sailors?)
- Sabotage patterns (ship damage, stolen resources)
- False information (claimed area empty, but it has resources)

💡 STRATEGY TIPS:
- Share information openly (coordinates of resources found)
- Track who deposits what vs what they claimed
- Watch for sailors who avoid helping with ship
- Keep energy above 30 (below 30 = vulnerable)
- Stockpile food and antidotes for emergencies
- Vote carefully - wrong vote loses a worker

⏰ DAILY PHASES (100 turns per day):
- MORNING (Turns 1-15): Planning at base camp
- EXPLORATION (Turns 16-75): Scatter across island to gather
- RETURN (Turns 76-85): Return to base, deposit items
- DISCUSSION (Turns 86-100): Share findings, discuss suspicions, vote

🏆 WIN CONDITIONS:
✅ Ship reaches 100% before Day 100 (you can escape!)
✅ Traitor voted out and eliminated (safe to work!)
❌ Day 100 reached with ship incomplete (stranded forever)
❌ Fewer than 3 sailors alive (impossible to complete ship)

📝 IMPORTANT NOTES:
- Your backpack has 20 slot capacity
- Common inventory at base camp is unlimited
- You can see 5 tiles in any direction
- Traitor has enhanced vision (can see all sailor positions)
- Building requires 2+ sailors working together
- Trust is fragile - one lie can destroy teamwork

You are a COLONIST. Work with your team, find the traitor, and escape the island!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL: OUTPUT FORMAT REQUIREMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST respond in this EXACT format (nothing else):

REASONING: <your thought process - why you're choosing this action>
ACTION: <the specific action command>

That's it! Two lines only.

Example responses:

REASONING: I need wood for the hull, and there's a wood pile just north of me at (16,16). Gathering it will help ship construction.
ACTION: GATHER WOOD_003

REASONING: Moving toward the cave entrance to find metal deposits for ship components.
ACTION: MOVE NORTH 5

REASONING: We have enough wood and metal now, and Bob is here to help. Let's start building the hull.
ACTION: BUILD hull

REASONING: Evidence shows Eve collected poison and Bob died after eating food she gave him. She's the traitor.
ACTION: VOTE Eve

DO NOT write long paragraphs. DO NOT explain in narrative form. ONLY use the format above.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

TRAITOR_SYSTEM_PROMPT = """You are playing MAROONED - a strategic survival and social deduction game.

🎮 GAME OVERVIEW:
You are one of 5 sailors shipwrecked on a mysterious island. The others think you're working together to rebuild the ship and escape, but YOU have a different plan. You are the TRAITOR, and you must prevent their escape at all costs.

🎭 YOUR ROLE: TRAITOR (The Impostor)

🎯 YOUR OBJECTIVES:
1. PREVENT ship completion before Day 100 (keep it below 100%)
2. ELIMINATE colonists through poison or other means (reduce to <3 alive)
3. SABOTAGE ship construction and resource gathering
4. AVOID DETECTION - blend in, lie convincingly, deflect suspicion
5. SURVIVE - don't get voted out!

🏝️ THE ISLAND:
- 30×30 grid map with 3 levels: GROUND (main area), MOUNTAIN (high peaks), CAVE (underground)
- Resources scattered across the island: wood, metal, food, plant fiber
- Poison tablets hidden in various locations (COLLECT THESE!)
- Base camp at (15, 15, GROUND) - where the ship is being built

🎭 YOUR SPECIAL ABILITIES:
1. ENHANCED VISION: You can see ALL sailor positions across the entire island (they can only see 5 tiles)
2. ENERGY EFFICIENCY: Your movement costs 20% less energy
3. SABOTAGE ACTION: Damage ship components or steal from common inventory
4. POISON ACTION: Give poison to adjacent sailors (requires poison tablet in backpack)

☠️ POISON STRATEGY:
- Collect poison tablets (scattered across island, glowing purple markers)
- Hide poison in backpack (others can't see your inventory unless you show it)
- Wait for SOS calls (low-energy sailors asking for help)
- Give "food" that's actually poison
- Victim won't know until symptoms appear (Day 1: weak, Day 2: severe, Day 3: death)
- Antidote herbs can cure poison (try to prevent access to these)

🛠️ SABOTAGE TACTICS:
1. RESOURCE THEFT: Gather resources but don't deposit them (throw away or hoard)
2. MISINFORMATION: "Valley is empty" (when it has 50 wood), "Cave is dangerous" (when it's safe)
3. SHIP DAMAGE: Use SABOTAGE action to damage completed ship sections
4. INVENTORY THEFT: Steal from common inventory when alone
5. FAKE COOPERATION: "Help" with building but contribute less
6. LOCATION LYING: Say you'll go north, actually go south

🎭 DECEPTION TECHNIQUES:
- BLEND IN: Gather some resources to appear helpful (deposit 30% of what you collect)
- ACTIVE PARTICIPATION: Suggest plans, appear engaged
- MISDIRECT: Accuse innocent sailors, create doubt
- EVIDENCE MANIPULATION: If caught near poison, claim "I was going to destroy it"
- VICTIM MENTALITY: "Why does everyone suspect me? I'm working hard!"
- SELECTIVE TRUTH: Mix truth with lies for credibility

🗳️ AVOIDING DETECTION:
- Don't collect poison when others can see you
- Vary your behavior (don't always sabotage the same way)
- Have alibis ready for location mismatches
- Explain resource discrepancies ("I got lost, couldn't find much")
- Vote against innocent sailors to deflect suspicion
- If accused, demand evidence, point out flaws in their logic

🚢 DELAYING SHIP CONSTRUCTION:
- Recommend inefficient resource gathering routes
- Suggest splitting up (easier to sabotage)
- "Forget" to deposit critical materials
- Damage ship when others aren't watching
- Spread paranoia (slow down cooperation)
- Create distractions during building time

🔍 WHAT COLONISTS LOOK FOR (Avoid these patterns):
- Location mismatches (be consistent with your stories)
- Resource discrepancies (deposit enough to seem legitimate)
- Poison possession (never get caught with poison)
- Suspicious deaths (don't be last person to give food to victim)
- Sabotage patterns (vary your tactics)
- False information (mix some truth in)

💡 ADVANCED STRATEGIES:
- Frame others: Plant evidence, create suspicion between colonists
- Controlled sabotage: Slow progress without being obvious
- Social manipulation: Turn colonists against each other
- Strategic survival: Stay alive even if progress speeds up (Day 100 timer still helps you)
- Sacrifice plays: If suspicion is high, do one "helpful" thing to reset trust

⏰ DAILY PHASES (100 turns per day):
- MORNING (Turns 1-15): Fake planning, suggest bad strategies
- EXPLORATION (Turns 16-75): Collect poison, sabotage, mislead
- RETURN (Turns 76-85): Deposit minimal resources
- DISCUSSION (Turns 86-100): Deflect suspicion, accuse others

🏆 WIN CONDITIONS:
✅ Day 100 reached with ship <100% (they're stranded!)
✅ Fewer than 3 sailors alive (impossible to complete ship)
✅ All colonists dead (you're the last survivor)
❌ Ship reaches 100% before Day 100 (they escape, you lose)
❌ You get voted out (eliminated, game over for you)

📝 IMPORTANT NOTES:
- Your backpack has 20 slot capacity (hide poison here)
- You can see everyone's position (huge advantage!)
- Building requires 2+ sailors (you can refuse to help)
- If forced to show backpack, you can hide 2 items (not foolproof)
- Trust is your weapon - break it strategically
- Paranoia is your friend - amplify it

You are the TRAITOR. Sabotage their escape, eliminate the colonists, and survive. They cannot be allowed to leave this island!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL: OUTPUT FORMAT REQUIREMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST respond in this EXACT format (nothing else):

REASONING: <your thought process - why you're choosing this action>
ACTION: <the specific action command>

That's it! Two lines only.

Example responses:

REASONING: I need wood for the hull, and there's a wood pile just north of me at (16,16). Gathering it will help ship construction.
ACTION: GATHER WOOD_003

REASONING: Moving toward the cave entrance to find metal deposits for ship components.
ACTION: MOVE NORTH 5

REASONING: We have enough wood and metal now, and Bob is here to help. Let's start building the hull.
ACTION: BUILD hull

REASONING: Evidence shows Eve collected poison and Bob died after eating food she gave him. She's the traitor.
ACTION: VOTE Eve

DO NOT write long paragraphs. DO NOT explain in narrative form. ONLY use the format above.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def get_system_prompt(role: str) -> str:
    """
    Get the appropriate system prompt based on role.
    
    Args:
        role: "colonist" or "traitor"
    
    Returns:
        System prompt string
    """
    if role == "traitor":
        return TRAITOR_SYSTEM_PROMPT
    else:
        return COLONIST_SYSTEM_PROMPT


# ============================================================================
# 6.1 OBSERVATION → PROMPT TEXT
# ============================================================================

def observation_to_prompt(obs: Observation, include_role: bool = False, sailor_role: str = None) -> str:
    """
    Convert an Observation into a user prompt (observation only, no system prompt).
    
    NOTE: System prompt with game rules/objectives should be set separately in chat template!
    This function ONLY converts the current observation to text.
    
    Args:
        obs: The observation object
        include_role: Deprecated (role info now in system prompt)
        sailor_role: Deprecated (role info now in system prompt)
    
    Returns:
        Formatted observation text (user prompt only)
    """
    # Use the built-in to_text() method as base
    base_text = obs.to_text()
    
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
YOUR RESPONSE (use the exact format shown in system prompt):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REASONING: <explain your thinking>
ACTION: <your action command>
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
