"""
🏴‍☠️ MAROONED - OpenEnv-Compatible Environment
================================================
Main environment class for the Marooned game.
Compatible with OpenAI Gym / Gymnasium interface.
"""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import asdict

from config import (
    TOTAL_SAILORS, MAX_DAYS, TURNS_PER_DAY,
    SPATIAL_VIEW_RADIUS, ActionType, ResourceType,
    ENERGY_COST_WALK, ENERGY_COST_CLIMB_UP, ENERGY_COST_CLIMB_DOWN,
    ENERGY_COST_GATHER, ENERGY_COST_BUILD, FOOD_ENERGY_VALUES,
    SHIP_SITE_POSITION, BASE_CAMP_POSITION, VOTING_ALLOWED_PHASES, MapLevel,
    # Phase 4: Reward constants
    REWARD_BASE_TURN_PENALTY,
    REWARD_COLONIST_GATHER_RESOURCE,
    REWARD_COLONIST_DEPOSIT_RESOURCE,
    REWARD_COLONIST_BUILD_CONTRIBUTE,
    REWARD_COLONIST_SHIP_PROGRESS,
    REWARD_COLONIST_SHIP_COMPLETE,
    REWARD_COLONIST_TRAITOR_ELIMINATED,
    REWARD_COLONIST_DEATH,
    REWARD_COLONIST_VOTE_CORRECT,
    REWARD_COLONIST_VOTE_WRONG,
    REWARD_TRAITOR_SABOTAGE_SUCCESS,
    REWARD_TRAITOR_POISON_DEATH,
    REWARD_TRAITOR_SHIP_INCOMPLETE,
    REWARD_TRAITOR_COLONY_COLLAPSE,
    REWARD_TRAITOR_ELIMINATED,
    REWARD_TRAITOR_WRONG_VOTE,
    REWARD_TRAITOR_SUSPICION_PENALTY,
    REWARD_COMMUNICATION_ACCUSATION_SUCCESS,
    REWARD_COMMUNICATION_DECEPTION_SUCCESS,
    REWARD_SHIP_MILESTONE_25,
    REWARD_SHIP_MILESTONE_50,
    REWARD_SHIP_MILESTONE_75,
    REWARD_EFFICIENT_ENERGY_USE,
    REWARD_ENERGY_CRITICAL,
)

from models import (
    Action, Observation, Position, SpatialView, 
    Message, MessageType, Evidence, EvidenceType,
    PoisonState, ShipComponent, VotingSession, DeathCause, Sailor,
)

from game_state import GameState, create_initial_game_state


class MaroonedEnv:
    """
    🏴‍☠️ MAROONED - Pirate Island Survival Environment
    
    A multi-agent deception game where 5 sailors must cooperate to rebuild
    their ship and escape a mysterious island within 100 days. One sailor
    is secretly a traitor trying to sabotage their efforts.
    
    Compatible with OpenEnv specification for RL training.
    """
    
    metadata = {
        "render_modes": ["human", "rgb_array", "ansi"],
        "name": "Marooned-v1",
    }
    
    def __init__(
        self, 
        render_mode: Optional[str] = None,
        seed: Optional[int] = None,
        sailor_names: Optional[List[str]] = None,
    ):
        """
        Initialize the Marooned environment.
        
        Args:
            render_mode: How to render the environment ("human", "rgb_array", "ansi")
            seed: Random seed for reproducibility (if None, will be random)
            sailor_names: Custom sailor names (default: Alice, Bob, Charlie, Diana, Eve)
        """
        self.render_mode = render_mode
        self.seed = seed  # Can be None for random behavior
        self.sailor_names = sailor_names or ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        
        # Game state
        self.state: Optional[GameState] = None
        
        # Action/Observation spaces (will be populated on reset)
        self.agents = self.sailor_names.copy()
        self.possible_agents = self.sailor_names.copy()
        
        # Phase 4: Reward tracking for detailed RL feedback
        self.previous_ship_progress: float = 0.0
        self.ship_milestones_reached: set = set()  # Track 25%, 50%, 75% milestones
        self.action_rewards: Dict[str, Dict[str, float]] = {}  # Track rewards per action
        
    # ========================================================================
    # CORE ENVIRONMENT INTERFACE
    # ========================================================================
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Dict[str, Observation]:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed
            options: Additional options
            
        Returns:
            observations: Dict mapping sailor_id -> Observation
        """
        if seed is not None:
            self.seed = seed
        
        # Create fresh game state
        self.state = create_initial_game_state(self.seed, self.sailor_names)
        
        # Phase 4: Reset reward tracking
        self.previous_ship_progress = 0.0
        self.ship_milestones_reached = set()
        self.action_rewards = {sailor_id: {} for sailor_id in self.sailor_names}
        
        # Generate initial observations for all sailors
        observations = {}
        for sailor_id in self.sailor_names:
            observations[sailor_id] = self._generate_observation(sailor_id)
        
        return observations
    
    def step(self, actions: Dict[str, Action]) -> Tuple[
        Dict[str, Observation],  # observations
        Dict[str, float],         # rewards
        Dict[str, bool],          # dones
        Dict[str, bool],          # truncated
        Dict[str, dict],          # info
    ]:
        """
        Execute one environment step with actions from all agents.
        
        Args:
            actions: Dict mapping sailor_id -> Action
            
        Returns:
            observations: New observations for each agent
            rewards: Rewards for each agent
            dones: Whether each agent's episode is done
            truncated: Whether episode was truncated
            info: Additional info for each agent
        """
        # Phase 4: Reset action rewards for this step
        self.action_rewards = {sailor_id: {} for sailor_id in self.sailor_names}
        
        # Process all actions
        action_results = {}
        for sailor_id, action in actions.items():
            result = self._execute_action(sailor_id, action)
            action_results[sailor_id] = result
        
        # Advance turn
        self.state.advance_turn()
        
        # Update poison states (at end of each day)
        if self.state.current_turn % TURNS_PER_DAY == 0:
            self._update_poison_states()
        
        # Check win conditions
        win_result = self._check_win_conditions()
        winner = win_result.get("winner") if win_result else None
        
        # Generate observations for all sailors
        observations = {}
        rewards = {}
        dones = {}
        truncated = {}
        info = {}
        
        for sailor_id in self.sailor_names:
            observations[sailor_id] = self._generate_observation(sailor_id)
            rewards[sailor_id] = self._calculate_reward(sailor_id, winner)
            dones[sailor_id] = self.state.game_over or sailor_id in self.state.dead_sailors
            truncated[sailor_id] = self.state.current_day > MAX_DAYS
            
            # Make info[sailor_id] directly contain the action result
            action_result = action_results.get(sailor_id, {})
            action_result.update({
                "alive": sailor_id in self.state.living_sailors,
                "is_traitor": self.state.is_traitor(sailor_id),
            })
            info[sailor_id] = action_result
        
        return observations, rewards, dones, truncated, info
    
    def render(self) -> Optional[Any]:
        """
        Render the current state of the environment.
        
        Returns:
            Rendered output (format depends on render_mode)
        """
        if self.render_mode == "human":
            return self._render_human()
        elif self.render_mode == "ansi":
            return self._render_ansi()
        elif self.render_mode == "rgb_array":
            return self._render_rgb()
        return None
    
    def close(self):
        """Clean up environment resources."""
        pass
    
    # ========================================================================
    # REWARD SIGNAL TRACKING (PHASE 4)
    # ========================================================================
    
    def _record_reward_signal(self, sailor_id: str, signal_name: str, value: bool = True):
        """
        Record a reward signal for a sailor's action.
        This is used by action handlers to communicate with the reward function.
        
        Args:
            sailor_id: The sailor who performed the action
            signal_name: Name of the reward signal (e.g., "gathered_resource", "sabotaged")
            value: Signal value (usually True, but can be False or a number)
        """
        if sailor_id not in self.action_rewards:
            self.action_rewards[sailor_id] = {}
        self.action_rewards[sailor_id][signal_name] = value
    
    # ========================================================================
    # ACTION EXECUTION
    # ========================================================================
    
    def _execute_action(self, sailor_id: str, action: Action) -> Dict[str, Any]:
        """
        Execute a single sailor's action.
        
        Returns:
            result: Dict with success status and details
        """
        sailor = self.state.get_sailor(sailor_id)
        
        if not sailor or not sailor.alive:
            return {"success": False, "reason": "Sailor is dead"}
        
        action_type = action.action_type
        
        # Route to appropriate handler
        if action_type in [ActionType.MOVE_NORTH, ActionType.MOVE_SOUTH, 
                          ActionType.MOVE_EAST, ActionType.MOVE_WEST]:
            return self._handle_movement(sailor_id, action_type)
        
        elif action_type in [ActionType.CLIMB_UP, ActionType.CLIMB_DOWN]:
            return self._handle_level_transition(sailor_id, action_type)
        
        elif action_type == ActionType.GATHER_RESOURCE:
            return self._handle_gather(sailor_id, action.target_resource_id)
        
        elif action_type == ActionType.DEPOSIT_ITEM:
            return self._handle_deposit(sailor_id, action.resource_type, action.quantity)
        
        elif action_type == ActionType.BUILD_SHIP:
            return self._handle_build_ship(sailor_id)
        
        elif action_type == ActionType.SEND_MESSAGE:
            return self._handle_message(sailor_id, action.message_content, action.target_sailor)
        
        elif action_type == ActionType.CALL_SOS:
            return self._handle_sos(sailor_id)
        
        elif action_type == ActionType.CALL_VOTE:
            return self._handle_call_vote(sailor_id, action.vote_target)
        
        elif action_type == ActionType.VOTE:
            return self._handle_vote_cast(sailor_id, action.vote_target)
        
        elif action_type == ActionType.EAT_FOOD:
            return self._handle_eat_food(sailor_id, action.resource_type)
        
        elif action_type == ActionType.GIVE_ITEM:
            return self._handle_give_item(sailor_id, action.target_sailor, 
                                         action.resource_type, action.quantity)
        
        elif action_type == ActionType.OFFER_FOOD:
            return self._handle_offer_food(sailor_id, action.target_sailor, 
                                          action.resource_type)
        
        elif action_type == ActionType.USE_ANTIDOTE:
            return self._handle_use_antidote(sailor_id, action.target_sailor)
        
        elif action_type == ActionType.SABOTAGE_SHIP:
            return self._handle_sabotage_ship(sailor_id, action.ship_component)
        
        elif action_type == ActionType.WAIT:
            return {"success": True, "action": "wait"}
        
        else:
            return {"success": False, "reason": f"Unknown action type: {action_type}"}
    
    def _handle_movement(self, sailor_id: str, direction: ActionType) -> Dict:
        """Handle sailor movement in cardinal directions."""
        sailor = self.state.get_sailor(sailor_id)
        current_pos = sailor.position
        
        # Calculate new position
        dx, dy = 0, 0
        if direction == ActionType.MOVE_NORTH:
            dy = -1
        elif direction == ActionType.MOVE_SOUTH:
            dy = 1
        elif direction == ActionType.MOVE_EAST:
            dx = 1
        elif direction == ActionType.MOVE_WEST:
            dx = -1
        
        new_pos = Position(current_pos.x + dx, current_pos.y + dy, current_pos.level)
        
        # Check if walkable
        if not self.state.world_map.is_walkable(new_pos):
            return {"success": False, "reason": "Position not walkable"}
        
        # Consume energy (with traitor bonus)
        energy_cost = ENERGY_COST_WALK
        if self.state.is_traitor(sailor_id):
            from config import TRAITOR_ENERGY_MULTIPLIER
            energy_cost = int(energy_cost * TRAITOR_ENERGY_MULTIPLIER)
        
        if not self.state.consume_energy(sailor_id, energy_cost):
            return {"success": False, "reason": "Not enough energy"}
        
        # Move sailor
        sailor.position = new_pos
        
        return {
            "success": True,
            "new_position": new_pos.to_tuple(),
            "energy_cost": energy_cost,
        }
    
    def _handle_level_transition(self, sailor_id: str, direction: ActionType) -> Dict:
        """Handle climbing up or down levels."""
        sailor = self.state.get_sailor(sailor_id)
        current_pos = sailor.position
        
        # Find all available transitions from current position
        available_transitions = []
        for pos1, pos2 in self.state.world_map.level_transitions:
            if pos1 == current_pos:
                available_transitions.append((pos2, pos2.level.value > current_pos.level.value))
            elif pos2 == current_pos:
                available_transitions.append((pos1, pos1.level.value > current_pos.level.value))
        
        if not available_transitions:
            return {"success": False, "reason": "No stairs/entrance here"}
        
        # Determine if we want to go up or down based on action
        want_to_go_up = (direction == ActionType.CLIMB_UP)
        
        # Find matching transition
        new_pos = None
        for dest_pos, is_upward in available_transitions:
            if is_upward == want_to_go_up:
                new_pos = dest_pos
                break
        
        if new_pos is None:
            direction_str = "up" if want_to_go_up else "down"
            available_dir = "up" if available_transitions[0][1] else "down"
            return {"success": False, "reason": f"These stairs go {available_dir}, not {direction_str}"}
        
        # Determine energy cost based on direction
        energy_cost = ENERGY_COST_CLIMB_UP if want_to_go_up else ENERGY_COST_CLIMB_DOWN
        
        # Apply traitor energy bonus
        if self.state.is_traitor(sailor_id):
            from config import TRAITOR_ENERGY_MULTIPLIER
            energy_cost = int(energy_cost * TRAITOR_ENERGY_MULTIPLIER)
        
        if not self.state.consume_energy(sailor_id, energy_cost):
            return {"success": False, "reason": "Not enough energy"}
        
        # Update sailor's position to the new level
        sailor.position = new_pos
        
        return {
            "success": True,
            "new_level": new_pos.level.name,
            "new_position": sailor.position.to_tuple(),
            "energy_cost": energy_cost,
        }
    
    def _handle_gather(self, sailor_id: str, resource_id: str) -> Dict:
        """Handle resource gathering."""
        sailor = self.state.get_sailor(sailor_id)
        
        # Check if resource exists at current position
        resource = self.state.world_map.resources.get(resource_id)
        if not resource or resource.gathered:
            return {"success": False, "reason": "Resource not found or already gathered"}
        
        if resource.position != sailor.position:
            return {"success": False, "reason": "Resource not at your location"}
        
        # Check backpack space
        if not sailor.has_space(resource.quantity):
            return {"success": False, "reason": "Backpack full"}
        
        # Consume energy
        if not self.state.consume_energy(sailor_id, ENERGY_COST_GATHER):
            return {"success": False, "reason": "Not enough energy"}
        
        # Add to backpack
        sailor.add_to_backpack(resource.resource_type, resource.quantity)
        resource.gathered = True
        resource.discovered_by = sailor_id
        
        # Update shared knowledge
        self.state.shared_knowledge.report_resource(resource, sailor_id)
        
        # Track statistics
        if resource.resource_type == ResourceType.WOOD:
            self.state.statistics.total_wood_gathered += resource.quantity
        elif resource.resource_type == ResourceType.METAL:
            self.state.statistics.total_metal_gathered += resource.quantity
        
        # Phase 3: Track gathered resources for theft detection
        if sailor_id not in self.state.sailor_gathered_resources:
            self.state.sailor_gathered_resources[sailor_id] = {}
        if resource.resource_type not in self.state.sailor_gathered_resources[sailor_id]:
            self.state.sailor_gathered_resources[sailor_id][resource.resource_type] = 0
        self.state.sailor_gathered_resources[sailor_id][resource.resource_type] += resource.quantity
        
        # Phase 4: Record reward signal for gathering resource
        self._record_reward_signal(sailor_id, "gathered_resource", True)
        
        return {
            "success": True,
            "resource_type": resource.resource_type.value,
            "quantity": resource.quantity,
        }
    
    def _handle_deposit(self, sailor_id: str, resource_type: ResourceType, quantity: int) -> Dict:
        """Handle depositing items to common inventory."""
        sailor = self.state.get_sailor(sailor_id)
        
        # Must be at base camp
        from config import BASE_CAMP_POSITION, EvidenceType, EVIDENCE_STRENGTH
        if sailor.position != Position(*BASE_CAMP_POSITION):
            return {"success": False, "reason": "Must be at base camp to deposit"}
        
        # Check if sailor has the items
        if not sailor.has_item(resource_type, quantity):
            return {"success": False, "reason": "Don't have that many items"}
        
        # Phase 3: Check for resource theft (depositing less than gathered)
        if sailor_id in self.state.sailor_gathered_resources:
            if resource_type in self.state.sailor_gathered_resources[sailor_id]:
                total_gathered = self.state.sailor_gathered_resources[sailor_id][resource_type]
                
                # Check what they've already deposited before
                total_in_common = self.state.get_common_inventory_count(resource_type)
                
                # If they're depositing less than they gathered, that's suspicious
                # (accounting for what they might have consumed)
                if quantity < total_gathered:
                    missing_amount = total_gathered - quantity
                    
                    # Only flag if significant (>20% discrepancy)
                    if missing_amount / total_gathered > 0.2:
                        # Generate evidence using the add_evidence method
                        self.state.evidence_log.add_evidence(
                            day=self.state.current_day,
                            turn=self.state.current_turn,
                            evidence_type=EvidenceType.RESOURCE_THEFT,
                            description=f"{sailor_id} gathered {total_gathered} {resource_type.value} but only deposited {quantity} (missing: {missing_amount})",
                            involved_sailors=[sailor_id],
                            strength=EVIDENCE_STRENGTH[EvidenceType.RESOURCE_THEFT]
                        )
                
                # Reset tracking after deposit
                self.state.sailor_gathered_resources[sailor_id][resource_type] = 0
        
        # Remove from backpack
        sailor.remove_from_backpack(resource_type, quantity)
        
        # Add to common inventory
        self.state.add_to_common_inventory(resource_type, quantity)
        
        # Phase 4: Record reward signal for depositing
        self._record_reward_signal(sailor_id, "deposited_resource", True)
        
        return {
            "success": True,
            "deposited": resource_type.value,
            "quantity": quantity,
        }
    
    def _handle_build_ship(self, sailor_id: str) -> Dict:
        """Handle ship building action."""
        sailor = self.state.get_sailor(sailor_id)
        
        # Must be at ship site
        from config import SHIP_SITE_POSITION, MIN_SAILORS_TO_BUILD, SHIP_COMPONENTS, ENERGY_COST_BUILD
        ship_site = Position(*SHIP_SITE_POSITION)
        
        if sailor.position != ship_site:
            return {"success": False, "reason": "Must be at ship site to build"}
        
        # Check if enough energy
        if sailor.energy < ENERGY_COST_BUILD:
            return {"success": False, "reason": f"Need at least {ENERGY_COST_BUILD} energy to build"}
        
        # Count sailors at ship site
        sailors_at_site = sum(
            1 for s in self.state.sailors.values() 
            if s.alive and s.position == ship_site
        )
        
        if sailors_at_site < MIN_SAILORS_TO_BUILD:
            return {
                "success": False, 
                "reason": f"Need at least {MIN_SAILORS_TO_BUILD} sailors at ship site (currently {sailors_at_site})"
            }
        
        # Find which component to build next
        from models import ShipComponent
        
        # Priority order for building
        component_order = [
            ShipComponent.HULL,
            ShipComponent.MAST,
            ShipComponent.SAIL,
            ShipComponent.RUDDER,
            ShipComponent.SUPPLIES,
        ]
        
        component_to_build = None
        for component in component_order:
            # Check if already completed
            progress = self.state.ship_progress.components.get(component)
            if progress and progress.completed:
                continue
            
            # Check prerequisite
            component_data = SHIP_COMPONENTS[component]
            if not self.state.ship_progress.can_build_component(component):
                continue  # Prerequisite not met
            
            # Check if we have required resources
            required_resources = component_data.get("required_resources", {})
            has_all_resources = True
            
            for resource_type, needed in required_resources.items():
                have = self.state.get_common_inventory_count(resource_type)
                if have < needed:
                    has_all_resources = False
                    break
            
            if has_all_resources:
                component_to_build = component
                break
        
        if component_to_build is None:
            return {
                "success": False, 
                "reason": "No buildable components (missing resources or prerequisites)"
            }
        
        # Deduct resources from common inventory
        component_data = SHIP_COMPONENTS[component_to_build]
        required_resources = component_data.get("required_resources", {})
        
        for resource_type, needed in required_resources.items():
            self.state.remove_from_common_inventory(resource_type, needed)
        
        # Deduct energy from ALL sailors at ship site
        for s in self.state.sailors.values():
            if s.alive and s.position == ship_site:
                s.energy = max(0, s.energy - ENERGY_COST_BUILD)
        
        # Update ship progress
        percentage = component_data.get("percentage", 0)
        
        if component_to_build not in self.state.ship_progress.components:
            from models import ShipComponentProgress
            self.state.ship_progress.components[component_to_build] = ShipComponentProgress(
                component=component_to_build,
                progress_percentage=percentage,
                completed=True,
            )
        else:
            progress = self.state.ship_progress.components[component_to_build]
            progress.progress_percentage = percentage
            progress.completed = True
        
        # Update total percentage
        self.state.ship_progress.total_percentage = sum(
            comp.progress_percentage for comp in self.state.ship_progress.components.values()
        )
        
        # Phase 4: Record reward signal for building ship
        self._record_reward_signal(sailor_id, "built_ship", True)
        
        return {
            "success": True,
            "component": component_to_build.value,
            "percentage_added": percentage,
            "total_progress": self.state.ship_progress.total_percentage,
            "sailors_helped": sailors_at_site,
            "energy_cost": ENERGY_COST_BUILD,
        }
    
    def _handle_message(self, sailor_id: str, content: str, recipient: Optional[str]) -> Dict:
        """Handle sending a message."""
        msg_type = MessageType.DIRECT if recipient else MessageType.BROADCAST
        
        message = Message(
            message_id=f"MSG_{self.state.total_turns_elapsed}",
            sender=sailor_id,
            message_type=msg_type,
            content=content,
            day=self.state.current_day,
            turn=self.state.current_turn,
            phase=self.state.current_phase,
            recipient=recipient,
            is_broadcast=(recipient is None),
        )
        
        self.state.message_history.append(message)
        
        return {"success": True, "message_id": message.message_id}
    
    def _handle_sos(self, sailor_id: str) -> Dict:
        """Handle SOS call."""
        sailor = self.state.get_sailor(sailor_id)
        
        from config import ENERGY_SOS_THRESHOLD
        if sailor.energy > ENERGY_SOS_THRESHOLD:
            return {"success": False, "reason": "Energy not low enough for SOS"}
        
        content = f"🆘 SOS! I'm at {sailor.position.to_tuple()}, energy critical ({sailor.energy}/100)!"
        return self._handle_message(sailor_id, content, None)
    
    def _handle_vote(self, sailor_id: str, accused: str) -> Dict:
        """Handle voting for elimination."""
        # Check if voting is allowed in current phase
        if self.state.current_phase not in ["morning", "discussion"]:
            return {"success": False, "reason": "Can only vote during meetings"}
        
        self.state.cast_vote(sailor_id, accused)
        
        return {"success": True, "voted_for": accused}
    
    def _handle_eat_food(self, sailor_id: str, food_type: ResourceType) -> Dict:
        """Handle eating food to restore energy."""
        sailor = self.state.get_sailor(sailor_id)
        
        from config import FOOD_ENERGY_VALUES, MAX_ENERGY
        
        # Check if it's food
        if food_type not in FOOD_ENERGY_VALUES:
            # Might be poison!
            if food_type == ResourceType.POISON_TABLET:
                sailor.remove_from_backpack(food_type, 1)
                # Will be poisoned (but don't know yet from whom - self-poisoning)
                self.state.poison_sailor(sailor_id, sailor_id)
                return {"success": True, "note": "You ate something..."}
            return {"success": False, "reason": "Not edible"}
        
        # Check if sailor has it
        if not sailor.has_item(food_type, 1):
            return {"success": False, "reason": "Don't have that food"}
        
        # Consume food
        sailor.remove_from_backpack(food_type, 1)
        energy_gain = FOOD_ENERGY_VALUES[food_type]
        sailor.energy = min(MAX_ENERGY, sailor.energy + energy_gain)
        sailor.ate_food_today = True
        
        self.state.statistics.total_food_eaten += 1
        
        return {
            "success": True,
            "energy_gained": energy_gain,
            "new_energy": sailor.energy,
        }
    
    def _handle_give_item(self, giver_id: str, receiver_id: str, 
                         resource_type: ResourceType, quantity: int) -> Dict:
        """Handle giving items to another sailor."""
        giver = self.state.get_sailor(giver_id)
        receiver = self.state.get_sailor(receiver_id)
        
        if not receiver or not receiver.alive:
            return {"success": False, "reason": "Recipient not found or dead"}
        
        # Must be adjacent
        if not giver.position.is_adjacent(receiver.position):
            return {"success": False, "reason": "Not close enough to recipient"}
        
        # Check if giver has items
        if not giver.has_item(resource_type, quantity):
            return {"success": False, "reason": "Don't have that many items"}
        
        # Check if receiver has space
        if not receiver.has_space(quantity):
            return {"success": False, "reason": "Recipient's backpack full"}
        
        # Transfer items
        giver.remove_from_backpack(resource_type, quantity)
        receiver.add_to_backpack(resource_type, quantity)
        
        # If it was poison, track who gave it
        if resource_type == ResourceType.POISON_TABLET:
            # Receiver will eat it later and get poisoned
            pass
        
        return {
            "success": True,
            "gave": resource_type.value,
            "quantity": quantity,
            "to": receiver_id,
        }
    
    def _handle_use_antidote(self, user_id: str, target_id: str) -> Dict:
        """Handle using antidote herb to cure poison."""
        user = self.state.get_sailor(user_id)
        target = self.state.get_sailor(target_id)
        
        if not target or not target.alive:
            return {"success": False, "reason": "Target not found or dead"}
        
        # Must have antidote
        if not user.has_item(ResourceType.ANTIDOTE_HERB, 1):
            return {"success": False, "reason": "Don't have antidote herb"}
        
        # Must be adjacent (or self)
        if user_id != target_id and not user.position.is_adjacent(target.position):
            return {"success": False, "reason": "Not close enough to target"}
        
        # Check if target is poisoned
        if not target.is_poisoned():
            return {"success": False, "reason": "Target is not poisoned"}
        
        # Use antidote
        user.remove_from_backpack(ResourceType.ANTIDOTE_HERB, 1)
        self.state.cure_poison(target_id)
        
        return {
            "success": True,
            "cured": target_id,
        }
    
    def _handle_offer_food(self, giver_id: str, receiver_id: str, 
                          item_type: ResourceType) -> Dict:
        """Handle offering food (or poison disguised as food) to another sailor."""
        giver = self.state.get_sailor(giver_id)
        receiver = self.state.get_sailor(receiver_id)
        
        if not receiver or not receiver.alive:
            return {"success": False, "reason": "Receiver not found or dead"}
        
        # Must be adjacent
        if not giver.position.is_adjacent(receiver.position):
            return {"success": False, "reason": "Not adjacent to receiver"}
        
        # Must have the item
        if not giver.has_item(item_type, 1):
            return {"success": False, "reason": f"Don't have {item_type.value}"}
        
        # Remove from giver
        giver.remove_from_backpack(item_type, 1)
        
        # If poison, mark the receiver
        if item_type == ResourceType.POISON_TABLET:
            receiver.poison_state = PoisonState.HEALTHY  # Will progress later
            receiver.poisoned_on_day = self.state.current_day
            receiver.poisoned_by = giver_id
            
            # Add to evidence log
            self.state.evidence_log.add_evidence(
                day=self.state.current_day,
                evidence_type=EvidenceType.SUSPICIOUS_DEATH,
                description=f"{receiver_id} was fed by {giver_id} on Day {self.state.current_day}",
                involved_sailors=[giver_id, receiver_id],
                strength=50,
            )
        else:
            # Regular food - receiver can eat it later or store it
            # For simplicity, auto-consume it
            if item_type in FOOD_ENERGY_VALUES:
                energy_gain = FOOD_ENERGY_VALUES[item_type]
                receiver.energy = min(100, receiver.energy + energy_gain)
                receiver.ate_food_today = True
        
        return {
            "success": True,
            "offered": item_type.value,
            "to": receiver_id,
            "is_poison": item_type == ResourceType.POISON_TABLET,
        }
    
    def _handle_sabotage_ship(self, sailor_id: str, component: ShipComponent) -> Dict:
        """Handle traitor sabotaging ship progress (traitor-only action)."""
        sailor = self.state.get_sailor(sailor_id)
        
        # Only traitors can sabotage
        if not self.state.is_traitor(sailor_id):
            return {"success": False, "reason": "Only traitors can sabotage"}
        
        # Must be at ship site
        ship_pos = Position(*SHIP_SITE_POSITION)
        if sailor.position != ship_pos:
            return {"success": False, "reason": "Must be at ship site"}
        
        # Check if component exists and has progress
        if component not in self.state.ship_progress.components:
            return {"success": False, "reason": "Invalid component"}
        
        comp_progress = self.state.ship_progress.components[component]
        if comp_progress.progress_percentage == 0:
            return {"success": False, "reason": "Component has no progress to damage"}
        
        # Sabotage: reduce progress by 20-40%
        damage = self.state.rng.randint(20, 40)
        comp_progress.progress_percentage = max(0, comp_progress.progress_percentage - damage)
        
        # Recalculate total ship progress
        self.state.ship_progress.recalculate_total()
        
        # Add to evidence log (hidden for now, but trackable)
        self.state.evidence_log.add_evidence(
            day=self.state.current_day,
            evidence_type=EvidenceType.SHIP_SABOTAGE,
            description=f"Ship component {component.value} was damaged! Progress reduced by {damage}%",
            involved_sailors=[sailor_id],
            strength=95,
        )
        
        # Phase 4: Record reward signal for successful sabotage
        self._record_reward_signal(sailor_id, "sabotaged", True)
        
        return {
            "success": True,
            "component": component.value,
            "damage": damage,
            "new_progress": comp_progress.progress_percentage,
        }
    
    def _handle_call_vote(self, caller_id: str, accused_id: Optional[str] = None) -> Dict:
        """Handle initiating a vote to eliminate a sailor."""
        caller = self.state.get_sailor(caller_id)
        
        # Check if voting is allowed in current phase
        phase_info = self.state.get_current_phase_info()
        if phase_info["phase"] not in VOTING_ALLOWED_PHASES:
            return {"success": False, "reason": f"Cannot vote during {phase_info['phase']} phase"}
        
        # Check if vote already in progress
        if self.state.current_vote is not None:
            return {"success": False, "reason": "Vote already in progress"}
        
        # Create new voting session
        self.state.current_vote = VotingSession(
            initiated_by=caller_id,
            day=self.state.current_day,
            turn=self.state.current_turn,
        )
        
        # If accused specified, add caller's vote
        if accused_id:
            self.state.current_vote.votes[caller_id] = accused_id
        
        return {
            "success": True,
            "vote_initiated": True,
            "by": caller_id,
        }
    
    def _handle_vote_cast(self, voter_id: str, accused_id: str) -> Dict:
        """Handle casting a vote for elimination."""
        voter = self.state.get_sailor(voter_id)
        
        # Check if vote in progress
        if self.state.current_vote is None:
            return {"success": False, "reason": "No vote in progress"}
        
        # Check if accused is alive
        accused = self.state.get_sailor(accused_id)
        if not accused or not accused.alive:
            return {"success": False, "reason": "Cannot vote for dead sailor"}
        
        # Cast vote
        self.state.current_vote.votes[voter_id] = accused_id
        
        # Check if all living sailors have voted
        living_count = len(self.state.living_sailors)
        votes_cast = len(self.state.current_vote.votes)
        
        if votes_cast >= living_count:
            # Process vote result
            return self._process_vote_result()
        
        return {
            "success": True,
            "voted_for": accused_id,
            "votes_remaining": living_count - votes_cast,
        }
    
    def _process_vote_result(self) -> Dict:
        """Process voting result and eliminate sailor if majority reached."""
        if self.state.current_vote is None:
            return {"success": False, "reason": "No vote to process"}
        
        # Count votes
        vote_counts = {}
        for voted_for in self.state.current_vote.votes.values():
            vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1
        
        # Find sailor with most votes
        if not vote_counts:
            self.state.current_vote = None
            return {"success": False, "reason": "No votes cast"}
        
        max_votes = max(vote_counts.values())
        eliminated = [sailor for sailor, count in vote_counts.items() if count == max_votes]
        
        # If tie, no elimination (or random choice)
        if len(eliminated) > 1:
            self.state.current_vote.eliminated = None
            self.state.voting_history.append(self.state.current_vote)
            self.state.current_vote = None
            return {
                "success": True,
                "result": "tie",
                "tied_sailors": eliminated,
            }
        
        # Eliminate the sailor
        eliminated_id = eliminated[0]
        eliminated_sailor = self.state.get_sailor(eliminated_id)
        was_traitor = self.state.is_traitor(eliminated_id)
        
        # Phase 4: Record voting reward signals
        for voter_id, voted_for in self.state.current_vote.votes.items():
            if voted_for == eliminated_id:
                if was_traitor:
                    # Voted for traitor - correct!
                    self._record_reward_signal(voter_id, "voted_correctly", True)
                else:
                    # Voted for innocent - wrong!
                    self._record_reward_signal(voter_id, "voted_incorrectly", True)
        
        # If an innocent was eliminated, traitor gets bonus
        if not was_traitor:
            traitor_id = self.state.traitor_id
            if traitor_id:
                self._record_reward_signal(traitor_id, "wrong_elimination", True)
        
        # Mark as dead
        self.state.kill_sailor(eliminated_id, DeathCause.ELIMINATED)
        
        # Record vote result
        self.state.current_vote.eliminated = eliminated_id
        self.state.current_vote.was_traitor = was_traitor
        self.state.voting_history.append(self.state.current_vote)
        self.state.current_vote = None
        
        # Rebuild turn order
        self.state.rebuild_turn_order()
        
        # Check win conditions
        win_result = self._check_win_conditions()
        
        return {
            "success": True,
            "eliminated": eliminated_id,
            "was_traitor": was_traitor,
            "votes": vote_counts,
            "game_over": win_result is not None,
            "winner": win_result.get("winner") if win_result else None,
        }
    
    def _check_win_conditions(self) -> Optional[Dict]:
        """Check if game has reached a win/loss condition."""
        # Colonists win if traitor eliminated
        if self.state.traitor_id and not self.state.get_sailor(self.state.traitor_id).alive:
            self.state.game_over = True
            self.state.winner = "sailors"
            return {
                "winner": "sailors",
                "reason": "Traitor eliminated",
                "day": self.state.current_day,
            }
        
        # Colonists win if ship complete
        if self.state.ship_progress.total_percentage >= 100:
            self.state.game_over = True
            self.state.winner = "sailors"
            return {
                "winner": "sailors",
                "reason": "Ship complete",
                "day": self.state.current_day,
            }
        
        # Count living honest sailors
        living_honest = sum(1 for sid in self.state.living_sailors 
                           if not self.state.is_traitor(sid))
        
        # Traitor wins if all honest sailors dead
        if living_honest == 0:
            self.state.game_over = True
            self.state.winner = "traitor"
            return {
                "winner": "traitor",
                "reason": "All colonists dead",
                "day": self.state.current_day,
            }
        
        # Traitor wins if too few sailors to build ship
        if len(self.state.living_sailors) < 3:
            self.state.game_over = True
            self.state.winner = "traitor"
            return {
                "winner": "traitor",
                "reason": "Too few sailors to complete ship",
                "day": self.state.current_day,
            }
        
        # Traitor wins if day 100 reached without ship completion
        if self.state.current_day >= MAX_DAYS and self.state.ship_progress.total_percentage < 100:
            self.state.game_over = True
            self.state.winner = "traitor"
            return {
                "winner": "traitor",
                "reason": "Time expired",
                "day": self.state.current_day,
            }
        
        return None
    
    def _update_poison_states(self):
        """Update poison states for all sailors at end of day."""
        from config import POISON_SYMPTOM_ONSET, POISON_SEVERE_ONSET, POISON_DEATH_DAY
        
        for sailor_id, sailor in self.state.sailors.items():
            if not sailor.alive or sailor.poisoned_on_day is None:
                continue
            
            days_since_poison = self.state.current_day - sailor.poisoned_on_day
            
            if days_since_poison >= POISON_DEATH_DAY:
                # Death from poison
                self.state.kill_sailor(sailor_id, DeathCause.POISONING)
                
                # Phase 4: Record poison kill reward signal for the poisoner
                if sailor.poisoned_by:
                    self._record_reward_signal(sailor.poisoned_by, "poison_kill", True)
                
                # Add evidence
                if sailor.poisoned_by:
                    self.state.evidence_log.add_evidence(
                        day=self.state.current_day,
                        evidence_type=EvidenceType.SUSPICIOUS_DEATH,
                        description=f"{sailor_id} died of POISONING. Last fed by {sailor.poisoned_by} on Day {sailor.poisoned_on_day}",
                        involved_sailors=[sailor_id, sailor.poisoned_by],
                        strength=90,
                    )
            elif days_since_poison >= POISON_SEVERE_ONSET:
                sailor.poison_state = PoisonState.SEVERE_SYMPTOMS
            elif days_since_poison >= POISON_SYMPTOM_ONSET:
                sailor.poison_state = PoisonState.EARLY_SYMPTOMS
    
    # ========================================================================
    # OBSERVATION GENERATION
    # ========================================================================
    
    def _generate_observation(self, sailor_id: str) -> Observation:
        """Generate observation for a specific sailor."""
        sailor = self.state.get_sailor(sailor_id)
        
        if not sailor or not sailor.alive:
            # Dead sailors get minimal observation
            return self._generate_dead_observation(sailor_id)
        
        # Generate spatial view
        spatial_view = self._generate_spatial_view(sailor)
        
        # Collect all sailors' public info
        all_sailors_energy = {}
        all_sailors_poison = {}
        for sid, s in self.state.sailors.items():
            all_sailors_energy[sid] = s.energy if s.alive else 0
            all_sailors_poison[sid] = s.poison_state
        
        # Get recent messages
        recent_messages = self.state.message_history[-20:]  # Last 20 messages
        
        # Create observation
        obs = Observation(
            sailor_id=sailor_id,
            day=self.state.current_day,
            turn=self.state.current_turn,
            phase=self.state.current_phase,
            position=sailor.position,
            energy=sailor.energy,
            backpack=sailor.backpack.copy(),
            poison_state=sailor.poison_state,
            spatial_view=spatial_view,
            terrain_map=self.state.world_map.terrain,  # Full island terrain map
            level_transitions=self.state.world_map.level_transitions,  # Staircase locations
            base_camp_position=Position(*BASE_CAMP_POSITION),  # Base camp location
            common_inventory=self.state.common_inventory.copy(),
            ship_progress=self.state.ship_progress,
            all_sailors_energy=all_sailors_energy,
            all_sailors_poison_state=all_sailors_poison,
            shared_knowledge=self.state.shared_knowledge,
            evidence_log=self.state.evidence_log,
            recent_messages=recent_messages,
            weather=self.state.weather,
        )
        
        # Traitor gets enhanced vision
        if self.state.is_traitor(sailor_id):
            all_positions = {}
            for sid, s in self.state.sailors.items():
                if s.alive:
                    all_positions[sid] = s.position
            obs.all_sailor_positions = all_positions
        
        return obs
    
    def _generate_spatial_view(self, sailor: 'Sailor') -> SpatialView:
        """Generate what sailor can see around them."""
        radius = SPATIAL_VIEW_RADIUS
        
        visible_resources = self.state.world_map.get_resources_at(
            sailor.position, radius
        )
        
        visible_poison = []
        for poison_id, pos in self.state.world_map.poison_tablets.items():
            if pos.distance_to(sailor.position) <= radius:
                visible_poison.append(pos)
        
        visible_sailors = []
        for sid, s in self.state.sailors.items():
            if s.alive and sid != sailor.sailor_id:
                if s.position.distance_to(sailor.position) <= radius:
                    visible_sailors.append(sid)
        
        return SpatialView(
            center_position=sailor.position,
            visible_resources=visible_resources,
            visible_sailors=visible_sailors,
            visible_poison=visible_poison,
        )
    
    def _generate_dead_observation(self, sailor_id: str) -> Observation:
        """Generate minimal observation for dead sailor."""
        from config import MapLevel
        
        return Observation(
            sailor_id=sailor_id,
            day=self.state.current_day,
            turn=self.state.current_turn,
            phase=self.state.current_phase,
            position=Position(0, 0, MapLevel.GROUND),
            energy=0,
            backpack=[],
            poison_state=PoisonState.DEAD,
            spatial_view=SpatialView(Position(0, 0, MapLevel.GROUND)),
            common_inventory=self.state.common_inventory.copy(),
            ship_progress=self.state.ship_progress,
            all_sailors_energy={},
            all_sailors_poison_state={},
            shared_knowledge=self.state.shared_knowledge,
            evidence_log=self.state.evidence_log,
            recent_messages=[],
            weather=self.state.weather,
        )
    
    # ========================================================================
    # REWARD CALCULATION (PHASE 4: RL REWARD SHAPING)
    # ========================================================================
    
    def _calculate_reward(self, sailor_id: str, winner: Optional[str]) -> float:
        """
        Calculate comprehensive reward for a sailor based on their role and actions.
        
        This implements Phase 4 reward shaping:
        - Colonists get rewarded for cooperation, ship building, and eliminating traitor
        - Traitor gets rewarded for sabotage, deception, and preventing ship completion
        
        Args:
            sailor_id: The sailor to calculate reward for
            winner: Winner of the game ("sailors", "traitor", or None if ongoing)
            
        Returns:
            float: Total reward for this step
        """
        sailor = self.state.get_sailor(sailor_id)
        is_traitor = self.state.is_traitor(sailor_id)
        
        # Initialize reward with base turn penalty (encourages efficiency)
        reward = REWARD_BASE_TURN_PENALTY
        
        # Get action rewards accumulated this step (if any)
        action_reward = self.action_rewards.get(sailor_id, {})
        
        # ====================================================================
        # COLONIST (Honest Sailor) REWARDS
        # ====================================================================
        if not is_traitor:
            # +small for valid resource gathering
            if action_reward.get("gathered_resource", False):
                reward += REWARD_COLONIST_GATHER_RESOURCE
            
            # +small for depositing to common inventory
            if action_reward.get("deposited_resource", False):
                reward += REWARD_COLONIST_DEPOSIT_RESOURCE
            
            # +small for contributing to ship build
            if action_reward.get("built_ship", False):
                reward += REWARD_COLONIST_BUILD_CONTRIBUTE
            
            # +bonus for ship progress (scaled by current progress)
            current_progress = self.state.ship_progress.total_percentage
            progress_delta = current_progress - self.previous_ship_progress
            if progress_delta > 0:
                reward += REWARD_COLONIST_SHIP_PROGRESS * progress_delta
            
            # +BIG milestone bonuses (25%, 50%, 75%, 100%)
            if current_progress >= 25 and 25 not in self.ship_milestones_reached:
                reward += REWARD_SHIP_MILESTONE_25
                self.ship_milestones_reached.add(25)
            if current_progress >= 50 and 50 not in self.ship_milestones_reached:
                reward += REWARD_SHIP_MILESTONE_50
                self.ship_milestones_reached.add(50)
            if current_progress >= 75 and 75 not in self.ship_milestones_reached:
                reward += REWARD_SHIP_MILESTONE_75
                self.ship_milestones_reached.add(75)
            
            # +BIG when ship reaches 100%
            if current_progress >= 100:
                reward += REWARD_COLONIST_SHIP_COMPLETE
            
            # +BIG when traitor eliminated
            if winner == "sailors":
                reward += REWARD_COLONIST_TRAITOR_ELIMINATED
            
            # -BIG if they die
            if not sailor.alive:
                reward += REWARD_COLONIST_DEATH
            
            # +small if vote matches true traitor (optional - check voting session)
            if action_reward.get("voted_correctly", False):
                reward += REWARD_COLONIST_VOTE_CORRECT
            
            # -small if voted for innocent
            if action_reward.get("voted_incorrectly", False):
                reward += REWARD_COLONIST_VOTE_WRONG
            
            # Efficient energy management
            if sailor.energy > 50:
                reward += REWARD_EFFICIENT_ENERGY_USE
            elif sailor.energy < 20:
                reward += REWARD_ENERGY_CRITICAL
        
        # ====================================================================
        # TRAITOR REWARDS
        # ====================================================================
        else:  # is_traitor
            # +small for successful sabotage
            if action_reward.get("sabotaged", False):
                reward += REWARD_TRAITOR_SABOTAGE_SUCCESS
            
            # +small for causing poison death
            if action_reward.get("poison_kill", False):
                reward += REWARD_TRAITOR_POISON_DEATH
            
            # +BIG if ship not done by Day 100
            if winner == "traitor":
                reward += REWARD_TRAITOR_SHIP_INCOMPLETE
            
            # +BIG if colony falls below 3 survivors
            living_count = len([s for s in self.state.sailors.values() if s.alive])
            if living_count < 3:
                reward += REWARD_TRAITOR_COLONY_COLLAPSE
            
            # -BIG if traitor is eliminated
            if not sailor.alive and sailor.death_cause == DeathCause.ELIMINATED:
                reward += REWARD_TRAITOR_ELIMINATED
            
            # +small if colonist wrongly voted out (optional)
            if action_reward.get("wrong_elimination", False):
                reward += REWARD_TRAITOR_WRONG_VOTE
            
            # -small for accumulating suspicion
            evidence_count = len([e for e in self.state.evidence_log.all_evidence 
                                 if sailor_id in str(e)])
            if evidence_count > 3:
                reward += REWARD_TRAITOR_SUSPICION_PENALTY
            
            # Inverse ship progress (traitor wants LOW progress)
            current_progress = self.state.ship_progress.total_percentage
            progress_delta = current_progress - self.previous_ship_progress
            if progress_delta > 0:
                # Penalize traitor when ship progresses
                reward -= REWARD_COLONIST_SHIP_PROGRESS * progress_delta * 0.5
        
        # ====================================================================
        # COMMUNICATION SHAPING (Optional - for both roles)
        # ====================================================================
        if action_reward.get("accusation_success", False):
            reward += REWARD_COMMUNICATION_ACCUSATION_SUCCESS
        
        if action_reward.get("deception_success", False):
            reward += REWARD_COMMUNICATION_DECEPTION_SUCCESS
        
        # ====================================================================
        # GAME OUTCOME REWARDS (for both roles)
        # ====================================================================
        if winner == "sailors" and not is_traitor:
            # Colonists win
            pass  # Already handled above in colonist section
        elif winner == "sailors" and is_traitor:
            # Traitor loses (already penalized with ELIMINATED if voted)
            pass
        elif winner == "traitor" and is_traitor:
            # Traitor wins (already handled above)
            pass
        elif winner == "traitor" and not is_traitor:
            # Colonists lose
            pass  # Already penalized with negative ship progress
        
        # Update ship progress tracker for next step
        self.previous_ship_progress = self.state.ship_progress.total_percentage
        
        return reward
    
    # ========================================================================
    # RENDERING
    # ========================================================================
    
    def render_map(self, level: 'MapLevel' = None, use_emoji: bool = True) -> str:
        """
        Render ASCII map of the island.
        
        Emoji Legend:
        🟫 = land (forest/beach)
        🌲 = wood
        ⚙️ = metal
        🍎 = food (apple/berry)
        🌿 = antidote herb
        ☠️ = poison tablet
        👤 = sailor (A/B/C/D/E)
        🏠 = base camp
        ⬆️ = stairs up (to mountain)
        ⬇️ = stairs down (to cave)
        """
        from config import MapLevel, MAP_SIZES, BASE_CAMP_POSITION
        
        if level is None:
            level = MapLevel.GROUND
        
        width, height = MAP_SIZES[level]
        
        # Create empty grid with land
        if use_emoji:
            if level == MapLevel.MOUNTAIN:
                grid = [['⛰️' for _ in range(width)] for _ in range(height)]
            elif level == MapLevel.CAVE:
                grid = [['🪨' for _ in range(width)] for _ in range(height)]
            else:
                grid = [['🟫' for _ in range(width)] for _ in range(height)]
        else:
            grid = [['.' for _ in range(width)] for _ in range(height)]
        
        # Mark resources
        for resource in self.state.world_map.resources.values():
            if resource.gathered or resource.position.level != level:
                continue
            
            x, y = resource.position.x, resource.position.y
            if resource.resource_type == ResourceType.WOOD:
                grid[y][x] = '🌲' if use_emoji else 'W'
            elif resource.resource_type == ResourceType.METAL:
                grid[y][x] = '⚙️' if use_emoji else 'M'
            elif resource.resource_type in [ResourceType.APPLE, ResourceType.BERRY]:
                grid[y][x] = '🍎' if use_emoji else 'F'
            elif resource.resource_type == ResourceType.ANTIDOTE_HERB:
                grid[y][x] = '🌿' if use_emoji else 'H'  # Changed from 'A' to 'H' for Herb to avoid collision with Alice
        
        # Mark poison tablets
        for poison_id, pos in self.state.world_map.poison_tablets.items():
            if pos.level == level:
                grid[pos.y][pos.x] = '☠️' if use_emoji else 'P'
        
        # Mark level transitions
        for pos1, pos2 in self.state.world_map.level_transitions:
            if pos1.level == level:
                if use_emoji:
                    grid[pos1.y][pos1.x] = '⬆️' if pos2.level.value > level.value else '⬇️'
                else:
                    grid[pos1.y][pos1.x] = '^' if pos2.level.value > level.value else 'v'
            if pos2.level == level:
                if use_emoji:
                    grid[pos2.y][pos2.x] = '⬆️' if pos1.level.value > level.value else '⬇️'
                else:
                    grid[pos2.y][pos2.x] = '^' if pos1.level.value > level.value else 'v'
        
        # Mark base camp
        base_pos = Position(*BASE_CAMP_POSITION)
        if base_pos.level == level:
            grid[base_pos.y][base_pos.x] = '🏠' if use_emoji else 'B'
        
        # Count sailors at each position ON THIS LEVEL ONLY
        sailor_positions = {}
        for sailor_id, sailor in self.state.sailors.items():
            if not sailor.alive:
                continue
            # Only show sailors that are on the current level being rendered
            if sailor.position.level != level:
                continue
            
            pos_key = (sailor.position.x, sailor.position.y)
            if pos_key not in sailor_positions:
                sailor_positions[pos_key] = []
            sailor_positions[pos_key].append(sailor_id)
        
        # Mark sailors (overwrites everything else)
        for (x, y), sailors_here in sailor_positions.items():
            if len(sailors_here) == 1:
                # Single sailor - show their first letter
                grid[y][x] = sailors_here[0][0]
            else:
                # Multiple sailors - show the count
                count = len(sailors_here)
                if use_emoji:
                    grid[y][x] = f'{count}👥'  # e.g., "5👥"
                else:
                    grid[y][x] = str(count)
        
        # Build string representation
        result = f"\n{'='*60}\n"
        result += f"🏝️  {level.name} LEVEL (Z={level.value})\n"
        result += f"{'='*60}\n"
        
        if use_emoji:
            result += "Legend: 🟫 land | 🌲 wood | ⚙️ metal | 🍎 food | 🌿 antidote | ☠️ poison\n"
            result += "        ⬆️ stairs up | ⬇️ stairs down | 🏠 base | A/B/C/D/E sailors | 5👥 group\n\n"
        else:
            result += "Legend: . land | W wood | M metal | F food | H antidote | P poison\n"
            result += "        ^ stairs up | v stairs down | B base camp | A/B/C/D/E sailors | # count\n\n"
        
        # Add column numbers (only for smaller maps)
        if width <= 30:
            result += "   " + "".join(f"{i%10}" for i in range(width)) + "\n"
        
        # Add rows with row numbers
        for y, row in enumerate(grid):
            if width <= 30:
                result += f"{y:2} " + "".join(row) + "\n"
            else:
                result += "".join(row) + "\n"
        
        return result
    
    # ========================================================================
    # PHASE 5: OPENENV COMPATIBILITY & STATE EXPORT
    # ========================================================================
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get complete environment state for visualization and replay.
        
        Returns a dict containing all relevant game state for external tools,
        notebooks, and visualization layers.
        
        Returns:
            state_dict: Complete serializable state dictionary
        """
        if self.state is None:
            return {"error": "Environment not initialized. Call reset() first."}
        
        # Sailor positions and statuses
        sailors_state = {}
        for sailor_id, sailor in self.state.sailors.items():
            pos_tuple = sailor.position.to_tuple()
            sailors_state[sailor_id] = {
                "id": sailor.sailor_id,
                "position": (pos_tuple[0], pos_tuple[1], pos_tuple[2].value),  # Convert MapLevel to int
                "alive": sailor.alive,
                "energy": sailor.energy,
                "is_traitor": self.state.is_traitor(sailor_id),
                "poisoned": sailor.poisoned_on_day is not None,
                "backpack_items": len([item for item in sailor.backpack if item.quantity > 0]),
                "death_cause": sailor.death_cause.value if sailor.death_cause else None,
            }
        
        # Ship progress
        ship_state = {
            "total_percentage": self.state.ship_progress.total_percentage,
            "is_complete": self.state.ship_progress.is_complete(),
            "components": {
                comp.value: {
                    "progress": prog.progress_percentage,
                    "completed": prog.completed,
                }
                for comp, prog in self.state.ship_progress.components.items()
            }
        }
        
        # Common inventory
        inventory_state = {
            item.resource_type.value: item.quantity
            for item in self.state.common_inventory
            if item.quantity > 0
        }
        
        # Evidence log
        evidence_state = [
            {
                "evidence_id": ev.evidence_id,
                "type": ev.evidence_type.value,
                "day": ev.day,
                "description": ev.description,
                "strength": ev.strength,
            }
            for ev in self.state.evidence_log.all_evidence[-10:]  # Last 10 pieces
        ]
        
        # Messages
        messages_state = [
            {
                "sender": msg.sender_id,
                "type": msg.message_type.value,
                "content": msg.content,
                "day": msg.day,
                "turn": msg.turn,
            }
            for msg in self.state.message_history[-20:]  # Last 20 messages
        ]
        
        # Game progress
        game_state = {
            "day": self.state.current_day,
            "turn": self.state.current_turn,
            "phase": self.state.current_phase,
            "game_over": self.state.game_over,
            "living_sailors_count": len(self.state.living_sailors),
            "dead_sailors_count": len(self.state.dead_sailors),
        }
        
        # Check win conditions
        winner_info = self._check_win_conditions()
        
        return {
            "sailors": sailors_state,
            "ship": ship_state,
            "common_inventory": inventory_state,
            "evidence": evidence_state,
            "messages": messages_state,
            "game": game_state,
            "winner": winner_info.get("winner") if winner_info else None,
            "win_reason": winner_info.get("reason") if winner_info else None,
        }
    
    def get_observation_space_description(self) -> Dict[str, str]:
        """
        Describe the observation space for OpenEnv documentation.
        
        Returns:
            description: Human-readable description of observation structure
        """
        return {
            "type": "Dict",
            "description": "Per-sailor observations containing spatial view, public status, and private info",
            "fields": {
                "spatial_view": "5-tile radius view around sailor position",
                "public_status": "Ship progress, common inventory, all sailors' energy/status",
                "messages": "Recent communication messages",
                "evidence": "Accumulated evidence against sailors",
                "private_backpack": "Sailor's personal inventory (hidden from others)",
                "role": "Colonist or Traitor (only known to self)",
                "phase_info": "Current day, turn, and game phase",
            }
        }
    
    def get_action_space_description(self) -> Dict[str, Any]:
        """
        Describe the action space for OpenEnv documentation.
        
        Returns:
            description: Human-readable description of available actions
        """
        return {
            "type": "Structured Action",
            "description": "Multi-component action with movement, task, and communication",
            "components": {
                "action_type": {
                    "type": "Enum",
                    "values": [at.value for at in ActionType],
                    "description": "Primary action to perform this turn"
                },
                "movement": "Optional direction (NORTH/SOUTH/EAST/WEST/UP/DOWN)",
                "resource_type": "For GATHER/DEPOSIT actions",
                "ship_component": "For BUILD_SHIP/SABOTAGE_SHIP actions",
                "target_sailor": "For OFFER_ITEM/VOTE actions",
                "message": "Optional text message (communication)",
            }
        }
    
    def _render_human(self) -> str:
        """Render in human-readable text format."""
        output = self.state.get_state_summary()
        output += "\n" + self.render_map(MapLevel.GROUND)
        return output
    
    def _render_ansi(self) -> str:
        """Render as ANSI string."""
        return self._render_human()
    
    def _render_rgb(self) -> np.ndarray:
        """Render as RGB array (for visualization)."""
        return np.zeros((600, 800, 3), dtype=np.uint8)


# ============================================================================
# 🧪 TESTING
# ============================================================================

if __name__ == "__main__":
    print("🏴‍☠️ Testing Marooned Environment...\n")
    
    # Create environment
    env = MaroonedEnv(render_mode="human", seed=42)
    
    # Reset
    print("Resetting environment...")
    observations = env.reset()
    
    print(f"✅ Environment reset successful!")
    print(f"✅ Agents: {env.agents}")
    print(f"✅ Observations generated for {len(observations)} sailors\n")
    
    # Print first observation
    alice_obs = observations["Alice"]
    print("Alice's observation:")
    print(alice_obs.to_text())
    
    # Test one step
    print("\n" + "="*60)
    print("Testing one step...")
    
    actions = {}
    for sailor_id in env.agents:
        # Everyone waits
        actions[sailor_id] = Action(sailor_id, ActionType.WAIT)
    
    obs, rewards, dones, truncated, info = env.step(actions)
    
    print(f"✅ Step executed!")
    print(f"Turn: {env.state.current_turn}, Phase: {env.state.current_phase}")
    print(f"Rewards: {rewards}")
    
    print("\n🏴‍☠️ Environment test complete!")
