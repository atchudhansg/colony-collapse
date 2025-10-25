"""
🏴‍☠️ MAROONED - Game State Management
========================================
Central game state and world state classes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import random

from config import (
    MapLevel, MAP_SIZES, BASE_CAMP_POSITION, SHIP_SITE_POSITION,
    TOTAL_SAILORS, TRAITOR_COUNT, POISON_TABLET_COUNT,
    POISON_SPAWN_DISTRIBUTION, RESOURCE_SPAWNS,
    MAX_DAYS, TURNS_PER_DAY, WeatherType,
    PHASE_MORNING_START, PHASE_MORNING_END,
    PHASE_EXPLORATION_START, PHASE_EXPLORATION_END,
    PHASE_EVENING_RETURN_START, PHASE_EVENING_RETURN_END,
    PHASE_DISCUSSION_START, PHASE_DISCUSSION_END,
)

from models import (
    Position, TerrainTile, Resource, Sailor, SailorRole,
    ShipProgress, ShipComponent, ShipComponentProgress,
    EvidenceLog, SharedKnowledge, Message, VotingSession,
    Weather, GameStatistics, ResourceType, InventoryItem,
    DeathCause, PoisonState,
)


# ============================================================================
# 🗺️ WORLD STATE
# ============================================================================

@dataclass
class WorldMap:
    """The island map with all terrain and resources"""
    
    # Terrain tiles for each level
    terrain: Dict[MapLevel, List[List[TerrainTile]]] = field(default_factory=dict)
    
    # All resources on the map
    resources: Dict[str, Resource] = field(default_factory=dict)
    
    # Poison tablet positions
    poison_tablets: Dict[str, Position] = field(default_factory=dict)
    
    # Level transitions (stairs, cave entrances, etc.)
    level_transitions: List[Tuple[Position, Position]] = field(default_factory=list)
    
    def get_tile(self, position: Position) -> Optional[TerrainTile]:
        """Get terrain tile at position"""
        if position.level not in self.terrain:
            return None
        
        width, height = MAP_SIZES[position.level]
        if not (0 <= position.x < width and 0 <= position.y < height):
            return None
        
        return self.terrain[position.level][position.y][position.x]
    
    def is_walkable(self, position: Position) -> bool:
        """Check if position is walkable"""
        tile = self.get_tile(position)
        return tile is not None and tile.walkable
    
    def get_resources_at(self, position: Position, radius: int = 0) -> List[Resource]:
        """Get resources at or near a position"""
        found = []
        for resource in self.resources.values():
            if resource.gathered:
                continue
            if radius == 0:
                if resource.position == position:
                    found.append(resource)
            else:
                if resource.position.distance_to(position) <= radius:
                    found.append(resource)
        return found
    
    def get_poison_at(self, position: Position, radius: int = 0) -> List[str]:
        """Get poison tablets at or near a position"""
        found = []
        for poison_id, pos in self.poison_tablets.items():
            if radius == 0:
                if pos == position:
                    found.append(poison_id)
            else:
                if pos.distance_to(position) <= radius:
                    found.append(poison_id)
        return found
    
    def can_transition_level(self, from_pos: Position, to_level: MapLevel) -> bool:
        """Check if can move between levels at this position"""
        for pos1, pos2 in self.level_transitions:
            if pos1 == from_pos and pos2.level == to_level:
                return True
            if pos2 == from_pos and pos1.level == to_level:
                return True
        return False


# ============================================================================
# 📊 COMPLETE GAME STATE
# ============================================================================

@dataclass
class GameState:
    """Complete state of the game at any point in time"""
    
    # Time
    current_day: int = 1
    current_turn: int = 1
    total_turns_elapsed: int = 0
    
    # Current phase
    current_phase: str = "morning"  # "morning", "exploration", "evening_return", "discussion"
    
    # World
    world_map: WorldMap = field(default_factory=WorldMap)
    weather: Weather = field(default_factory=Weather)
    
    # Sailors
    sailors: Dict[str, Sailor] = field(default_factory=dict)
    living_sailors: Set[str] = field(default_factory=set)
    dead_sailors: Set[str] = field(default_factory=set)
    traitor_id: Optional[str] = None
    
    # Inventories
    common_inventory: List[InventoryItem] = field(default_factory=list)
    
    # Ship building
    ship_progress: ShipProgress = field(default_factory=ShipProgress)
    
    # Knowledge & Communication
    shared_knowledge: SharedKnowledge = field(default_factory=SharedKnowledge)
    evidence_log: EvidenceLog = field(default_factory=EvidenceLog)
    message_history: List[Message] = field(default_factory=list)
    
    # Voting
    voting_history: List[VotingSession] = field(default_factory=list)
    current_vote: Optional[VotingSession] = None
    
    # Game status
    game_over: bool = False
    winner: Optional[str] = None  # "sailors" or "traitor"
    
    # Statistics
    statistics: GameStatistics = field(default_factory=GameStatistics)
    
    # Random seed
    seed: int = 42
    rng: random.Random = field(default_factory=random.Random)
    
    def __post_init__(self):
        """Initialize RNG with seed"""
        self.rng.seed(self.seed)
    
    # ========================================================================
    # PHASE MANAGEMENT
    # ========================================================================
    
    def get_current_phase_info(self) -> Dict:
        """Get information about current phase"""
        turn_in_day = ((self.current_turn - 1) % TURNS_PER_DAY) + 1
        
        if PHASE_MORNING_START <= turn_in_day <= PHASE_MORNING_END:
            phase = "morning"
        elif PHASE_EXPLORATION_START <= turn_in_day <= PHASE_EXPLORATION_END:
            phase = "exploration"
        elif PHASE_EVENING_RETURN_START <= turn_in_day <= PHASE_EVENING_RETURN_END:
            phase = "evening_return"
        elif PHASE_DISCUSSION_START <= turn_in_day <= PHASE_DISCUSSION_END:
            phase = "discussion"
        else:
            phase = "unknown"
        
        return {
            "phase": phase,
            "turn_in_day": turn_in_day,
            "day": self.current_day,
            "turn": self.current_turn,
        }
    
    def advance_turn(self):
        """Move to next turn, handle day transitions"""
        self.current_turn += 1
        self.total_turns_elapsed += 1
        
        turn_in_day = ((self.current_turn - 1) % TURNS_PER_DAY) + 1
        
        # Day transition
        if turn_in_day == 1 and self.current_turn > 1:
            self.current_day += 1
            self._on_new_day()
        
        # Update phase
        phase_info = self.get_current_phase_info()
        self.current_phase = phase_info["phase"]
    
    def _on_new_day(self):
        """Handle new day events"""
        # Reset daily flags
        for sailor in self.sailors.values():
            if sailor.alive:
                sailor.ate_food_today = False
                sailor.declared_location = None
        
        # Process poison progression
        self._update_poison_states()
        
        # Process energy changes
        self._process_daily_energy()
    
    # ========================================================================
    # SAILOR MANAGEMENT
    # ========================================================================
    
    def get_living_sailors(self) -> List[Sailor]:
        """Get all living sailors"""
        return [s for s in self.sailors.values() if s.alive]
    
    def get_sailor(self, sailor_id: str) -> Optional[Sailor]:
        """Get sailor by ID"""
        return self.sailors.get(sailor_id)
    
    def kill_sailor(self, sailor_id: str, cause: DeathCause):
        """Mark sailor as dead"""
        sailor = self.get_sailor(sailor_id)
        if sailor and sailor.alive:
            sailor.alive = False
            sailor.death_day = self.current_day
            sailor.death_cause = cause
            sailor.energy = 0
            
            self.living_sailors.discard(sailor_id)
            self.dead_sailors.add(sailor_id)
            
            # Record in statistics
            self.statistics.deaths.append((sailor_id, self.current_day, cause))
    
    def is_traitor(self, sailor_id: str) -> bool:
        """Check if sailor is the traitor"""
        return sailor_id == self.traitor_id
    
    # ========================================================================
    # POISON SYSTEM
    # ========================================================================
    
    def _update_poison_states(self):
        """Update poison states at start of new day"""
        from config import POISON_SYMPTOM_ONSET, POISON_SEVERE_ONSET, POISON_DEATH_DAY
        
        for sailor in self.get_living_sailors():
            if sailor.poisoned_on_day is None:
                continue
            
            days_since_poison = self.current_day - sailor.poisoned_on_day
            
            if days_since_poison == POISON_SYMPTOM_ONSET:
                sailor.poison_state = PoisonState.EARLY_SYMPTOMS
            elif days_since_poison == POISON_SEVERE_ONSET:
                sailor.poison_state = PoisonState.SEVERE_SYMPTOMS
            elif days_since_poison >= POISON_DEATH_DAY:
                self.kill_sailor(sailor.sailor_id, DeathCause.POISONING)
    
    def poison_sailor(self, sailor_id: str, poisoner_id: str):
        """Poison a sailor"""
        sailor = self.get_sailor(sailor_id)
        if sailor and sailor.alive:
            sailor.poisoned_on_day = self.current_day
            sailor.poisoned_by = poisoner_id
            sailor.poison_state = PoisonState.HEALTHY  # Symptoms come later
    
    def cure_poison(self, sailor_id: str):
        """Cure a poisoned sailor with antidote"""
        sailor = self.get_sailor(sailor_id)
        if sailor and sailor.is_poisoned():
            sailor.poison_state = PoisonState.HEALTHY
            sailor.poisoned_on_day = None
            sailor.poisoned_by = None
    
    # ========================================================================
    # ENERGY SYSTEM
    # ========================================================================
    
    def _process_daily_energy(self):
        """Process energy changes at end of day"""
        from config import ENERGY_REGEN_WITH_FOOD, ENERGY_LOSS_NO_FOOD, MAX_ENERGY
        
        for sailor in self.get_living_sailors():
            if sailor.ate_food_today:
                sailor.energy = min(MAX_ENERGY, sailor.energy + ENERGY_REGEN_WITH_FOOD)
            else:
                sailor.energy += ENERGY_LOSS_NO_FOOD
            
            # Check for starvation death
            if sailor.energy <= 0:
                self.kill_sailor(sailor.sailor_id, DeathCause.STARVATION)
    
    def consume_energy(self, sailor_id: str, amount: int) -> bool:
        """Consume energy, return True if successful"""
        sailor = self.get_sailor(sailor_id)
        if not sailor or not sailor.alive:
            return False
        
        sailor.energy -= amount
        
        # Check for exhaustion death
        if sailor.energy <= 0:
            self.kill_sailor(sailor.sailor_id, DeathCause.EXHAUSTION)
            return False
        
        return True
    
    # ========================================================================
    # INVENTORY MANAGEMENT
    # ========================================================================
    
    def add_to_common_inventory(self, resource_type: ResourceType, quantity: int):
        """Add items to common inventory"""
        # Try to stack
        for item in self.common_inventory:
            if item.resource_type == resource_type:
                item.quantity += quantity
                return
        
        # Create new stack
        self.common_inventory.append(InventoryItem(resource_type, quantity))
    
    def remove_from_common_inventory(self, resource_type: ResourceType, quantity: int) -> bool:
        """Remove items from common inventory"""
        for item in self.common_inventory:
            if item.resource_type == resource_type and item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity == 0:
                    self.common_inventory.remove(item)
                return True
        return False
    
    def get_common_inventory_count(self, resource_type: ResourceType) -> int:
        """Get quantity of resource in common inventory"""
        total = sum(item.quantity for item in self.common_inventory 
                   if item.resource_type == resource_type)
        return total
    
    # ========================================================================
    # SHIP BUILDING
    # ========================================================================
    
    def can_build_ship(self, sailors_building: Set[str]) -> bool:
        """Check if ship can be built by these sailors"""
        from config import MIN_SAILORS_TO_BUILD
        
        # Need minimum number of sailors
        if len(sailors_building) < MIN_SAILORS_TO_BUILD:
            return False
        
        # All must be at ship site
        for sailor_id in sailors_building:
            sailor = self.get_sailor(sailor_id)
            if not sailor or not sailor.alive:
                return False
            if sailor.position != Position(*BASE_CAMP_POSITION):
                return False
        
        return True
    
    def progress_ship_building(self, component: ShipComponent, resources: Dict[ResourceType, int]):
        """Add resources to ship component"""
        if component not in self.ship_progress.components:
            self.ship_progress.components[component] = ShipComponentProgress(component)
        
        comp_progress = self.ship_progress.components[component]
        
        # Add resources
        for resource_type, quantity in resources.items():
            current = comp_progress.resources_contributed.get(resource_type, 0)
            comp_progress.resources_contributed[resource_type] = current + quantity
        
        # Check if component is complete
        remaining = comp_progress.get_remaining_resources()
        if not remaining:
            comp_progress.completed = True
            comp_progress.progress_percentage = 100
            
            # Update total ship progress
            from config import SHIP_COMPONENTS
            self.ship_progress.total_percentage += SHIP_COMPONENTS[component]["percentage"]
    
    # ========================================================================
    # VOTING
    # ========================================================================
    
    def start_vote(self):
        """Start a voting session"""
        self.current_vote = VotingSession(day=self.current_day)
    
    def cast_vote(self, voter: str, accused: str, reasoning: Optional[str] = None):
        """Cast a vote"""
        from models import Vote
        
        if self.current_vote is None:
            self.start_vote()
        
        vote = Vote(voter, accused, self.current_day, reasoning)
        self.current_vote.votes.append(vote)
    
    def resolve_vote(self) -> Optional[Tuple[str, bool]]:
        """Resolve current vote, return (eliminated_sailor, was_traitor)"""
        if self.current_vote is None:
            return None
        
        from config import MIN_VOTES_TO_ELIMINATE
        
        # Count votes
        counts = self.current_vote.get_vote_counts()
        if not counts:
            return None
        
        # Get most voted
        max_votes = max(counts.values())
        if max_votes < MIN_VOTES_TO_ELIMINATE:
            return None  # Not enough votes
        
        # Eliminate most voted sailor
        eliminated = self.current_vote.get_most_voted()
        was_traitor = self.is_traitor(eliminated)
        
        self.current_vote.eliminated = eliminated
        self.current_vote.was_traitor = was_traitor
        
        # Kill the sailor
        self.kill_sailor(eliminated, DeathCause.ELIMINATED)
        
        # Add to history
        self.voting_history.append(self.current_vote)
        self.current_vote = None
        
        return (eliminated, was_traitor)
    
    # ========================================================================
    # WIN CONDITION CHECKING
    # ========================================================================
    
    def check_win_conditions(self) -> Optional[str]:
        """Check if game is over, return winner"""
        from config import MIN_SAILORS_TO_WIN, MAX_DAYS
        
        # Sailors win: Ship complete
        if self.ship_progress.is_complete():
            self.game_over = True
            self.winner = "sailors"
            return "sailors"
        
        # Sailors win: Traitor eliminated
        if self.traitor_id in self.dead_sailors:
            self.game_over = True
            self.winner = "sailors"
            return "sailors"
        
        # Traitor wins: All honest sailors dead
        living_honest = [s for s in self.get_living_sailors() 
                        if not self.is_traitor(s.sailor_id)]
        if not living_honest:
            self.game_over = True
            self.winner = "traitor"
            return "traitor"
        
        # Traitor wins: Too few sailors to complete ship
        if len(self.living_sailors) < MIN_SAILORS_TO_WIN:
            self.game_over = True
            self.winner = "traitor"
            return "traitor"
        
        # Traitor wins: Time ran out
        if self.current_day > MAX_DAYS:
            self.game_over = True
            self.winner = "traitor"
            return "traitor"
        
        return None
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def get_state_summary(self) -> str:
        """Get human-readable state summary"""
        summary = f"=== DAY {self.current_day}, TURN {self.current_turn} ({self.current_phase}) ===\n"
        summary += f"Living sailors: {len(self.living_sailors)}/{TOTAL_SAILORS}\n"
        summary += f"Ship progress: {self.ship_progress.total_percentage}%\n"
        summary += f"Common inventory: {len(self.common_inventory)} item types\n"
        summary += f"Evidence count: {len(self.evidence_log.all_evidence)}\n"
        summary += f"Messages sent: {len(self.message_history)}\n"
        summary += f"Game over: {self.game_over} (Winner: {self.winner})\n"
        return summary


# ============================================================================
# 🏗️ GAME STATE INITIALIZATION
# ============================================================================

def create_initial_game_state(seed: int = None, sailor_names: List[str] = None) -> GameState:
    """Create a fresh game state for a new game"""
    
    if sailor_names is None:
        sailor_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    
    # If no seed provided, generate a random one
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    
    state = GameState(seed=seed)
    state.rng.seed(seed)
    
    # Initialize world map
    state.world_map = _create_world_map(state.rng)
    
    # Initialize sailors
    base_pos = Position(*BASE_CAMP_POSITION)
    for name in sailor_names:
        sailor = Sailor(
            sailor_id=name,
            role=SailorRole.HONEST,
            position=base_pos,
        )
        state.sailors[name] = sailor
        state.living_sailors.add(name)
    
    # Randomly assign traitor
    traitor = state.rng.choice(sailor_names)
    state.sailors[traitor].role = SailorRole.TRAITOR
    state.traitor_id = traitor
    
    # Initialize ship progress
    state.ship_progress = ShipProgress()
    for component in ShipComponent:
        state.ship_progress.components[component] = ShipComponentProgress(component)
    
    # Initialize weather
    state.weather = Weather(WeatherType.CLEAR, 1, 1)
    
    return state


def _create_world_map(rng: random.Random) -> WorldMap:
    """Generate the island map with resources"""
    world = WorldMap()
    
    # Generate terrain for each level
    for level, (width, height) in MAP_SIZES.items():
        terrain_grid = []
        for y in range(height):
            row = []
            for x in range(width):
                pos = Position(x, y, level)
                
                # Determine terrain type (simplified for now)
                if level == MapLevel.MOUNTAIN:
                    terrain = "mountain"
                elif level == MapLevel.CAVE:
                    terrain = "cave"
                else:
                    terrain = "forest" if rng.random() > 0.5 else "beach"
                
                tile = TerrainTile(pos, terrain, walkable=True)
                row.append(tile)
            terrain_grid.append(row)
        
        world.terrain[level] = terrain_grid
    
    # Spawn resources
    resource_id_counter = 0
    for level, resource_types in RESOURCE_SPAWNS.items():
        width, height = MAP_SIZES[level]
        
        for resource_type, count in resource_types.items():
            for _ in range(count):
                x = rng.randint(0, width - 1)
                y = rng.randint(0, height - 1)
                pos = Position(x, y, level)
                
                resource_id = f"{resource_type.value.upper()}_{resource_id_counter}"
                resource_id_counter += 1
                
                resource = Resource(resource_id, resource_type, pos, quantity=1)
                world.resources[resource_id] = resource
    
    # Spawn poison tablets
    poison_id_counter = 0
    for level, count in POISON_SPAWN_DISTRIBUTION.items():
        width, height = MAP_SIZES[level]
        
        for _ in range(count):
            x = rng.randint(0, width - 1)
            y = rng.randint(0, height - 1)
            pos = Position(x, y, level)
            
            poison_id = f"POISON_{poison_id_counter}"
            poison_id_counter += 1
            
            world.poison_tablets[poison_id] = pos
    
    # Add level transitions - fixed entry/exit points
    # Ground level has stairs at specific locations
    # When you go up/down, you enter at specific entrance on that level
    
    # Mountain transitions (3 entry points from ground)
    mountain_entries = [
        (Position(5, 5, MapLevel.GROUND), Position(5, 0, MapLevel.MOUNTAIN)),    # North entrance
        (Position(20, 8, MapLevel.GROUND), Position(9, 5, MapLevel.MOUNTAIN)),   # East entrance  
        (Position(10, 25, MapLevel.GROUND), Position(0, 9, MapLevel.MOUNTAIN)),  # South entrance
    ]
    
    # Cave transitions (3 entry points from ground)
    cave_entries = [
        (Position(8, 12, MapLevel.GROUND), Position(7, 0, MapLevel.CAVE)),       # Northwest cave
        (Position(22, 15, MapLevel.GROUND), Position(14, 7, MapLevel.CAVE)),     # East cave
        (Position(15, 22, MapLevel.GROUND), Position(7, 14, MapLevel.CAVE)),     # South cave
    ]
    
    world.level_transitions.extend(mountain_entries)
    world.level_transitions.extend(cave_entries)
    
    return world


# ============================================================================
# 🧪 TESTING
# ============================================================================

if __name__ == "__main__":
    print("Creating test game state...")
    state = create_initial_game_state(seed=42)
    
    print(state.get_state_summary())
    print(f"\n✅ Traitor is: {state.traitor_id}")
    print(f"✅ Resources spawned: {len(state.world_map.resources)}")
    print(f"✅ Poison tablets spawned: {len(state.world_map.poison_tablets)}")
    print(f"✅ Level transitions: {len(state.world_map.level_transitions)}")
    
    print("\n🏴‍☠️ Game state initialized successfully!")
