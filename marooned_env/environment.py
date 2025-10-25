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
    ENERGY_COST_GATHER, ENERGY_COST_BUILD,
)

from models import (
    Action, Observation, Position, SpatialView, 
    Message, MessageType, Evidence, EvidenceType,
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
        
        Phase 2 Mode: If actions contain only one sailor (the active sailor),
        execute that action, advance to next sailor, and return that sailor's observation.
        
        Args:
            actions: Dict mapping sailor_id -> Action
            
        Returns:
            observations: New observations for each agent
            rewards: Rewards for each agent
            dones: Whether each agent's episode is done
            truncated: Whether episode was truncated
            info: Additional info for each agent
        """
        # Determine if Phase 2 mode (single active sailor) or Phase 1 mode (all sailors)
        phase2_mode = len(actions) == 1 and self.state.get_active_sailor() in actions
        
        # Process all actions
        action_results = {}
        for sailor_id, action in actions.items():
            result = self._execute_action(sailor_id, action)
            action_results[sailor_id] = result
        
        # Advance turn
        self.state.advance_turn()
        
        # Phase 2: Advance to next sailor in turn order
        if phase2_mode:
            self.state.advance_to_next_sailor()
        
        # Check win conditions
        winner = self.state.check_win_conditions()
        
        # Generate observations
        observations = {}
        rewards = {}
        dones = {}
        truncated = {}
        info = {}
        
        # Phase 2 mode: Only return observation for next active sailor
        if phase2_mode:
            next_sailor = self.state.get_active_sailor()
            if next_sailor:
                observations[next_sailor] = self._generate_observation(next_sailor)
                rewards[next_sailor] = self._calculate_reward(next_sailor, winner)
                dones[next_sailor] = self.state.game_over or next_sailor in self.state.dead_sailors
                truncated[next_sailor] = self.state.current_day > MAX_DAYS
                info[next_sailor] = {
                    "action_result": action_results.get(next_sailor, {}),
                    "alive": next_sailor in self.state.living_sailors,
                    "is_traitor": self.state.is_traitor(next_sailor),
                    "is_active": True,
                }
        else:
            # Phase 1 mode: Return observations for all sailors (backward compatible)
            for sailor_id in self.sailor_names:
                observations[sailor_id] = self._generate_observation(sailor_id)
                rewards[sailor_id] = self._calculate_reward(sailor_id, winner)
                dones[sailor_id] = self.state.game_over or sailor_id in self.state.dead_sailors
                truncated[sailor_id] = self.state.current_day > MAX_DAYS
                info[sailor_id] = {
                    "action_result": action_results.get(sailor_id, {}),
                    "alive": sailor_id in self.state.living_sailors,
                    "is_traitor": self.state.is_traitor(sailor_id),
                }
        
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
        
        elif action_type == ActionType.VOTE:
            return self._handle_vote(sailor_id, action.vote_target)
        
        elif action_type == ActionType.EAT_FOOD:
            return self._handle_eat_food(sailor_id, action.resource_type)
        
        elif action_type == ActionType.GIVE_ITEM:
            return self._handle_give_item(sailor_id, action.target_sailor, 
                                         action.resource_type, action.quantity)
        
        elif action_type == ActionType.USE_ANTIDOTE:
            return self._handle_use_antidote(sailor_id, action.target_sailor)
        
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
        
        # Determine target level
        from config import MapLevel
        if direction == ActionType.CLIMB_UP:
            if current_pos.level == MapLevel.GROUND:
                target_level = MapLevel.MOUNTAIN
            elif current_pos.level == MapLevel.CAVE:
                target_level = MapLevel.GROUND
            else:
                return {"success": False, "reason": "Already at highest level"}
            energy_cost = ENERGY_COST_CLIMB_UP
        else:  # CLIMB_DOWN
            if current_pos.level == MapLevel.MOUNTAIN:
                target_level = MapLevel.GROUND
            elif current_pos.level == MapLevel.GROUND:
                target_level = MapLevel.CAVE
            else:
                return {"success": False, "reason": "Already at lowest level"}
            energy_cost = ENERGY_COST_CLIMB_DOWN
        
        # Check if transition exists at this location
        if not self.state.world_map.can_transition_level(current_pos, target_level):
            return {"success": False, "reason": "No stairs/entrance here"}
        
        # Apply traitor energy bonus
        if self.state.is_traitor(sailor_id):
            from config import TRAITOR_ENERGY_MULTIPLIER
            energy_cost = int(energy_cost * TRAITOR_ENERGY_MULTIPLIER)
        
        if not self.state.consume_energy(sailor_id, energy_cost):
            return {"success": False, "reason": "Not enough energy"}
        
        # Find corresponding position on new level (simplified)
        # TODO: Use actual transition mapping
        new_pos = Position(current_pos.x % 10, current_pos.y % 10, target_level)
        sailor.position = new_pos
        
        return {
            "success": True,
            "new_level": target_level.value,
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
        
        return {
            "success": True,
            "resource_type": resource.resource_type.value,
            "quantity": resource.quantity,
        }
    
    def _handle_deposit(self, sailor_id: str, resource_type: ResourceType, quantity: int) -> Dict:
        """Handle depositing items to common inventory."""
        sailor = self.state.get_sailor(sailor_id)
        
        # Must be at base camp
        from config import BASE_CAMP_POSITION
        if sailor.position != Position(*BASE_CAMP_POSITION):
            return {"success": False, "reason": "Must be at base camp to deposit"}
        
        # Check if sailor has the items
        if not sailor.has_item(resource_type, quantity):
            return {"success": False, "reason": "Don't have that many items"}
        
        # Remove from backpack
        sailor.remove_from_backpack(resource_type, quantity)
        
        # Add to common inventory
        self.state.add_to_common_inventory(resource_type, quantity)
        
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
        
        # TODO: Adjust for cave darkness, fog, etc.
        
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
    # REWARD CALCULATION
    # ========================================================================
    
    def _calculate_reward(self, sailor_id: str, winner: Optional[str]) -> float:
        """Calculate reward for a sailor."""
        sailor = self.state.get_sailor(sailor_id)
        is_traitor = self.state.is_traitor(sailor_id)
        
        # Base reward: small penalty per turn to encourage efficiency
        reward = -0.01
        
        # Ship progress rewards (for honest sailors)
        if not is_traitor:
            reward += self.state.ship_progress.total_percentage * 0.01
        
        # Game outcome rewards
        if winner == "sailors" and not is_traitor:
            reward += 100.0  # Honest sailors win
        elif winner == "sailors" and is_traitor:
            reward -= 100.0  # Traitor loses
        elif winner == "traitor" and is_traitor:
            reward += 100.0  # Traitor wins
        elif winner == "traitor" and not is_traitor:
            reward -= 100.0  # Honest sailors lose
        
        # Death penalty
        if not sailor.alive:
            reward -= 50.0
        
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
                grid[y][x] = '🌿' if use_emoji else 'A'
        
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
        
        # Count sailors at each position
        sailor_positions = {}
        for sailor_id, sailor in self.state.sailors.items():
            if sailor.alive and sailor.position.level == level:
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
            result += "Legend: . land | W wood | M metal | F food | A antidote | P poison\n"
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
        # TODO: Implement visual rendering
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
