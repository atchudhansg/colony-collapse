"""
🏴‍☠️ MAROONED - Data Models
============================
All dataclasses for game entities, observations, and actions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from config import (
    MapLevel, ResourceType, SailorRole, DeathCause, PoisonState,
    EvidenceType, ActionType, MessageType, ShipComponent, WeatherType
)


# ============================================================================
# 🌍 SPATIAL MODELS
# ============================================================================

@dataclass
class Position:
    """3D position on the island"""
    x: int
    y: int
    level: MapLevel
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate 2D distance (ignoring level difference)"""
        if self.level != other.level:
            return float('inf')  # Can't measure across levels
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def is_adjacent(self, other: 'Position') -> bool:
        """Check if positions are adjacent (for giving items, etc.)"""
        return self.level == other.level and self.distance_to(other) <= 1.5
    
    def __hash__(self):
        return hash((self.x, self.y, self.level))
    
    def __eq__(self, other):
        return (self.x, self.y, self.level) == (other.x, other.y, other.level)
    
    def to_tuple(self) -> Tuple[int, int, MapLevel]:
        return (self.x, self.y, self.level)


@dataclass
class TerrainTile:
    """Single tile on the map"""
    position: Position
    terrain_type: str  # "forest", "beach", "mountain", "cave", "rock", etc.
    walkable: bool = True
    has_level_transition: bool = False  # Stairs/entrance to other level
    transition_to: Optional[MapLevel] = None


# ============================================================================
# 📦 RESOURCE MODELS
# ============================================================================

@dataclass
class Resource:
    """A resource instance on the map"""
    resource_id: str  # Unique ID like "WOOD_PILE_A"
    resource_type: ResourceType
    position: Position
    quantity: int = 1
    discovered_by: Optional[str] = None  # Sailor name who discovered it
    gathered: bool = False
    
    def __hash__(self):
        return hash(self.resource_id)


@dataclass
class InventoryItem:
    """Item in a sailor's backpack or common inventory"""
    resource_type: ResourceType
    quantity: int = 1
    
    def __hash__(self):
        return hash((self.resource_type, self.quantity))


# ============================================================================
# 👤 SAILOR MODELS
# ============================================================================

@dataclass
class Sailor:
    """A sailor character in the game"""
    sailor_id: str  # "Alice", "Bob", "Charlie", "Diana", "Eve"
    role: SailorRole  # HONEST or TRAITOR
    
    # Status
    alive: bool = True
    energy: int = 100
    position: Position = None
    
    # Poison state
    poison_state: PoisonState = PoisonState.HEALTHY
    poisoned_on_day: Optional[int] = None
    poisoned_by: Optional[str] = None  # Sailor who gave poisoned food
    
    # Death info
    death_day: Optional[int] = None
    death_cause: Optional[DeathCause] = None
    
    # Inventory
    backpack: List[InventoryItem] = field(default_factory=list)
    backpack_capacity: int = 20
    
    # Daily tracking
    ate_food_today: bool = False
    declared_location: Optional[Position] = None  # Where they said they'd go
    
    # Traitor-specific
    frame_ability_used: bool = False  # Has traitor used their frame ability?
    
    def get_backpack_weight(self) -> int:
        """Total items in backpack"""
        return sum(item.quantity for item in self.backpack)
    
    def has_space(self, quantity: int = 1) -> bool:
        """Check if backpack has space"""
        return self.get_backpack_weight() + quantity <= self.backpack_capacity
    
    def add_to_backpack(self, resource_type: ResourceType, quantity: int = 1) -> bool:
        """Add item to backpack, returns success"""
        if not self.has_space(quantity):
            return False
        
        # Try to stack with existing
        for item in self.backpack:
            if item.resource_type == resource_type:
                item.quantity += quantity
                return True
        
        # Create new stack
        self.backpack.append(InventoryItem(resource_type, quantity))
        return True
    
    def remove_from_backpack(self, resource_type: ResourceType, quantity: int = 1) -> bool:
        """Remove item from backpack, returns success"""
        for item in self.backpack:
            if item.resource_type == resource_type and item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity == 0:
                    self.backpack.remove(item)
                return True
        return False
    
    def has_item(self, resource_type: ResourceType, quantity: int = 1) -> bool:
        """Check if sailor has item in backpack"""
        total = sum(item.quantity for item in self.backpack 
                   if item.resource_type == resource_type)
        return total >= quantity
    
    def is_poisoned(self) -> bool:
        """Check if sailor is currently poisoned"""
        return self.poison_state in [PoisonState.EARLY_SYMPTOMS, 
                                     PoisonState.SEVERE_SYMPTOMS]


# ============================================================================
# 🚢 SHIP BUILDING MODELS
# ============================================================================

@dataclass
class ShipComponentProgress:
    """Progress on a single ship component"""
    component: ShipComponent
    completed: bool = False
    progress_percentage: int = 0  # Within this component
    resources_contributed: Dict[ResourceType, int] = field(default_factory=dict)
    
    def get_remaining_resources(self) -> Dict[ResourceType, int]:
        """Calculate what's still needed"""
        from config import SHIP_COMPONENTS
        required = SHIP_COMPONENTS[self.component]["required_resources"]
        remaining = {}
        for resource_type, needed in required.items():
            contributed = self.resources_contributed.get(resource_type, 0)
            if contributed < needed:
                remaining[resource_type] = needed - contributed
        return remaining


@dataclass
class ShipProgress:
    """Overall ship building progress"""
    total_percentage: int = 0
    components: Dict[ShipComponent, ShipComponentProgress] = field(default_factory=dict)
    
    current_builders: Set[str] = field(default_factory=set)  # Sailors currently building
    build_turns_remaining: int = 0  # Turns left for current build action
    
    def is_complete(self) -> bool:
        """Check if ship is ready to escape"""
        return self.total_percentage >= 100
    
    def recalculate_total(self):
        """Recalculate total ship progress from all components"""
        from config import SHIP_COMPONENTS
        total = 0
        for component, comp_progress in self.components.items():
            if comp_progress.completed:
                # Completed components contribute their full percentage
                total += SHIP_COMPONENTS[component]["percentage"]
            else:
                # Partial progress is weighted by component's target percentage
                component_weight = SHIP_COMPONENTS[component]["percentage"]
                total += (comp_progress.progress_percentage / 100.0) * component_weight
        self.total_percentage = int(total)
    
    def can_build_component(self, component: ShipComponent) -> bool:
        """Check if prerequisites are met"""
        from config import SHIP_COMPONENTS
        prereq = SHIP_COMPONENTS[component]["prerequisite"]
        if prereq is None:
            return True
        return self.components.get(prereq, ShipComponentProgress(prereq)).completed


# ============================================================================
# 🔍 EVIDENCE MODELS
# ============================================================================

@dataclass
class Evidence:
    """A piece of evidence against a sailor"""
    evidence_id: str
    evidence_type: EvidenceType
    day: int
    turn: int
    
    accused_sailor: str  # Who is suspicious
    witness: Optional[str] = None  # Who reported it
    
    description: str = ""
    details: Dict = field(default_factory=dict)
    
    strength: int = 50  # 0-100, how damning this evidence is


@dataclass
class EvidenceLog:
    """Collection of all evidence gathered"""
    all_evidence: List[Evidence] = field(default_factory=list)
    _evidence_counter: int = 0
    
    def add_evidence(self, day: int, evidence_type: EvidenceType, description: str, 
                    involved_sailors: List[str], strength: int = 50,
                    witness: Optional[str] = None, turn: int = 0):
        """Add new evidence to log"""
        # Use first involved sailor as accused, or None
        accused = involved_sailors[0] if involved_sailors else None
        
        evidence = Evidence(
            evidence_id=f"EVIDENCE_{self._evidence_counter}",
            evidence_type=evidence_type,
            day=day,
            turn=turn,
            accused_sailor=accused,
            witness=witness,
            description=description,
            strength=strength,
        )
        self.all_evidence.append(evidence)
        self._evidence_counter += 1
    
    def get_evidence_against(self, sailor_id: str) -> List[Evidence]:
        """Get all evidence against a specific sailor"""
        return [e for e in self.all_evidence if e.accused_sailor == sailor_id]
    
    def get_suspicion_score(self, sailor_id: str) -> int:
        """Calculate total suspicion score for a sailor"""
        evidence = self.get_evidence_against(sailor_id)
        return sum(e.strength for e in evidence)


# ============================================================================
# 💬 COMMUNICATION MODELS
# ============================================================================

@dataclass
class Message:
    """A message sent between sailors"""
    message_id: str
    sender: str
    message_type: MessageType
    content: str
    
    day: int
    turn: int
    phase: str
    
    recipient: Optional[str] = None  # For direct messages
    is_broadcast: bool = True


@dataclass
class SharedKnowledge:
    """Shared map knowledge about discovered resources (static - doesn't update when gathered)"""
    discovered_resources: Dict[str, Dict] = field(default_factory=dict)  # Static snapshots
    resource_reports: List[Dict] = field(default_factory=list)  # Who reported what
    
    def report_resource(self, resource: Resource, reporter: str):
        """Add discovered resource to shared knowledge (stores static snapshot)"""
        # Store a static snapshot - doesn't update when resource is gathered
        self.discovered_resources[resource.resource_id] = {
            "resource_id": resource.resource_id,
            "resource_type": resource.resource_type,
            "position": resource.position,
            "quantity": resource.quantity,
            "discovered_by": reporter,
            # Note: NO 'gathered' field - this is static initial state
        }
        self.resource_reports.append({
            "resource_id": resource.resource_id,
            "reporter": reporter,
            "position": resource.position,
            "type": resource.resource_type,
        })


# ============================================================================
# 🗳️ VOTING MODELS
# ============================================================================

@dataclass
class Vote:
    """A vote during elimination"""
    voter: str
    accused: str
    day: int
    reasoning: Optional[str] = None


@dataclass
class VotingSession:
    """A voting round"""
    day: int
    turn: int
    initiated_by: str
    votes: Dict[str, str] = field(default_factory=dict)  # voter_id -> accused_id
    eliminated: Optional[str] = None
    was_traitor: Optional[bool] = None
    
    def get_vote_counts(self) -> Dict[str, int]:
        """Count votes for each accused sailor"""
        counts = {}
        for accused in self.votes.values():
            counts[accused] = counts.get(accused, 0) + 1
        return counts
    
    def get_most_voted(self) -> Optional[str]:
        """Get sailor with most votes"""
        counts = self.get_vote_counts()
        if not counts:
            return None
        return max(counts.items(), key=lambda x: x[1])[0]


# ============================================================================
# ☁️ WEATHER MODELS
# ============================================================================

@dataclass
class Weather:
    """Current weather conditions"""
    weather_type: WeatherType = WeatherType.CLEAR
    day_started: int = 1
    duration_days: int = 1


# ============================================================================
# 🎮 ACTION MODELS
# ============================================================================

@dataclass
class Action:
    """An action taken by a sailor"""
    sailor_id: str
    action_type: ActionType
    
    # Optional parameters depending on action type
    target_position: Optional[Position] = None
    target_resource_id: Optional[str] = None
    target_sailor: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    ship_component: Optional[ShipComponent] = None
    quantity: int = 1
    message_content: Optional[str] = None
    vote_target: Optional[str] = None
    
    def __str__(self):
        base = f"{self.sailor_id}: {self.action_type.value}"
        if self.target_position:
            base += f" -> {self.target_position.to_tuple()}"
        if self.target_sailor:
            base += f" (target: {self.target_sailor})"
        if self.message_content:
            base += f' "{self.message_content[:50]}..."'
        return base


# ============================================================================
# 👁️ OBSERVATION MODELS
# ============================================================================

@dataclass
class SpatialView:
    """What a sailor can see around them"""
    center_position: Position
    visible_tiles: List[TerrainTile] = field(default_factory=list)
    visible_resources: List[Resource] = field(default_factory=list)
    visible_sailors: List[str] = field(default_factory=list)  # Other sailor IDs
    visible_poison: List[Position] = field(default_factory=list)


@dataclass
class Observation:
    """Complete observation for a sailor at a given turn"""
    sailor_id: str
    day: int
    turn: int
    phase: str
    
    # Personal status
    position: Position
    energy: int
    backpack: List[InventoryItem]
    poison_state: PoisonState
    
    # Spatial awareness
    spatial_view: SpatialView
    
    # Full terrain map (static knowledge - all sailors have this)
    terrain_map: Dict = field(default_factory=dict)  # MapLevel -> terrain grid
    level_transitions: List[Tuple[Position, Position]] = field(default_factory=list)  # Staircase locations
    base_camp_position: Optional[Position] = None
    
    # Shared information
    common_inventory: List[InventoryItem] = field(default_factory=list)
    ship_progress: ShipProgress = field(default_factory=lambda: ShipProgress())
    all_sailors_energy: Dict[str, int] = field(default_factory=dict)  # sailor_id -> energy (public info)
    all_sailors_poison_state: Dict[str, PoisonState] = field(default_factory=dict)  # Visible symptoms
    
    # Knowledge
    shared_knowledge: SharedKnowledge = field(default_factory=lambda: SharedKnowledge())
    evidence_log: EvidenceLog = field(default_factory=lambda: EvidenceLog())
    
    # Communication
    recent_messages: List[Message] = field(default_factory=list)
    
    # Environment
    weather: Weather = field(default_factory=lambda: Weather())
    
    # Traitor-specific (only if observer is traitor)
    all_sailor_positions: Optional[Dict[str, Position]] = None  # Enhanced vision
    
    def to_text(self) -> str:
        """Convert observation to natural language prompt for LLM"""
        # This will be the key method for feeding to language models
        
        # Enhanced header with phase context
        text = "=" * 80 + "\n"
        text += f"DAY {self.day}, TURN {self.turn}/100 - {self.phase.upper()} PHASE\n"
        text += "=" * 80 + "\n\n"
        
        # Phase-specific context and restrictions
        text += "PHASE CONTEXT:\n"
        if self.phase == "morning":
            text += "  Location: All sailors at BASE CAMP\n"
            text += "  Allowed: Planning, discussions, voting (if called)\n"
            text += "  Restricted: Cannot explore or gather resources yet\n"
        elif self.phase == "exploration":
            text += "  Location: You can move anywhere on the island\n"
            text += "  Allowed: MOVE, GATHER resources, SEND_MESSAGE (limited), CALL_SOS\n"
            text += "  Restricted: Cannot VOTE (only in discussion phase)\n"
        elif self.phase == "evening_return":
            text += "  Location: Returning to BASE CAMP\n"
            text += "  Allowed: DEPOSIT items to common inventory, BUILD_SHIP\n"
            text += "  Restricted: Limited movement, no new exploration\n"
        elif self.phase == "discussion":
            text += "  Location: All sailors at BASE CAMP\n"
            text += "  Allowed: Discussions, accusations, VOTE, SHOW_BACKPACK, review evidence\n"
            text += "  Restricted: Cannot explore or gather\n"
        text += "\n"
        
        # Personal status
        text += f"YOUR STATUS ({self.sailor_id}):\n"
        text += f"  Position: {self.position.to_tuple()}\n"
        text += f"  Energy: {self.energy}/100 {'⚡' * (self.energy // 20)}\n"
        text += f"  Health: {self.poison_state.value}\n"
        
        # Detailed backpack contents
        from config import BACKPACK_CAPACITY
        text += f"  Backpack: {len(self.backpack)}/{BACKPACK_CAPACITY} items\n"
        if self.backpack:
            for item in self.backpack:
                text += f"    - {item.resource_type.value} × {item.quantity}\n"
        else:
            text += f"    (empty)\n"
        text += "\n"
        
        # Spatial view - detailed breakdown
        text += f"WHAT YOU SEE (within 5 tiles):\n"
        
        # Show resources with details
        if self.spatial_view.visible_resources:
            text += "  Resources:\n"
            for resource in self.spatial_view.visible_resources:
                distance = abs(resource.position.x - self.position.x) + abs(resource.position.y - self.position.y)
                text += f"    - {resource.resource_id} ({resource.resource_type.value}) at {resource.position.to_tuple()}"
                text += f" - {resource.quantity} units [{distance} tiles away]\n"
        else:
            text += "  Resources: None visible\n"
        
        # Show other sailors with positions
        if self.spatial_view.visible_sailors:
            text += "  Other sailors:\n"
            for sailor_id in self.spatial_view.visible_sailors:
                # Note: We don't have exact positions in spatial view for other sailors
                # This would need to be added to SpatialView model if needed
                text += f"    - {sailor_id} (nearby)\n"
        else:
            text += "  Other sailors: None\n"
        
        # Show poison tablets with positions
        if self.spatial_view.visible_poison:
            text += "  Poison tablets:\n"
            for poison_pos in self.spatial_view.visible_poison:
                distance = abs(poison_pos.x - self.position.x) + abs(poison_pos.y - self.position.y)
                text += f"    - At {poison_pos.to_tuple()} [{distance} tiles away]\n"
        else:
            text += "  Poison tablets: None\n"
        
        text += "\n"
        
        # Traitor enhanced vision (only for traitor)
        if self.all_sailor_positions is not None:
            text += "🎭 TRAITOR ENHANCED VISION (Special Ability):\n"
            text += "  You can see ALL sailor positions across the entire island:\n"
            for sid, pos in self.all_sailor_positions.items():
                if sid != self.sailor_id:  # Don't show self
                    distance = abs(pos.x - self.position.x) + abs(pos.y - self.position.y)
                    text += f"    - {sid} at {pos.to_tuple()} [{distance} tiles from you]\n"
            text += "\n"
        
        # Terrain knowledge
        text += f"ISLAND MAP KNOWLEDGE:\n"
        text += f"  You have a complete map of the island terrain\n"
        text += f"  Base camp: {self.base_camp_position.to_tuple() if self.base_camp_position else 'Unknown'}\n"
        
        # Show staircase positions
        if self.level_transitions:
            text += f"  Level transitions (staircases):\n"
            for pos1, pos2 in self.level_transitions:
                # Determine direction
                if pos2.level.value > pos1.level.value:
                    direction = f"{pos1.level.name} → {pos2.level.name}"
                    symbol = "↑"
                else:
                    direction = f"{pos1.level.name} → {pos2.level.name}"
                    symbol = "↓"
                text += f"    - {pos1.to_tuple()} ↔ {pos2.to_tuple()} [{direction}]\n"
        else:
            text += f"  Level transitions: None known\n"
        
        text += "\n"
        
        # Shared knowledge map (what teammates have reported)
        if self.shared_knowledge.discovered_resources:
            text += "SHARED RESOURCE MAP (reported by team):\n"
            for res_id, res_data in self.shared_knowledge.discovered_resources.items():
                text += f"  {res_data['resource_type']} at {res_data['position'].to_tuple()} "
                text += f"(qty: {res_data['quantity']}, reported by: {res_data['discovered_by']})\n"
            text += "\n"
        
        # Ship progress - detailed breakdown
        text += f"SHIP PROGRESS: {self.ship_progress.total_percentage}% Total\n"
        
        # Show progress bar
        filled = int(self.ship_progress.total_percentage / 4)  # 25 chars max
        empty = 25 - filled
        text += f"  {'━' * filled}{'░' * empty} {self.ship_progress.total_percentage}%\n\n"
        
        # Show each component
        from config import SHIP_COMPONENTS, ShipComponent
        for component in ShipComponent:
            comp_progress = self.ship_progress.components.get(component)
            if comp_progress:
                # Component exists in progress
                if comp_progress.completed:
                    bars = '█' * 12
                    text += f"  {component.value.upper()}: {bars} 100% ✓ COMPLETE\n"
                else:
                    filled_bars = int(comp_progress.progress_percentage / 10)  # 10 bars max at 100%
                    empty_bars = 10 - filled_bars
                    bars = '█' * filled_bars + '░' * empty_bars
                    text += f"  {component.value.upper()}: {bars}  {comp_progress.progress_percentage}% IN PROGRESS\n"
                    
                    # Show what's still needed
                    remaining = comp_progress.get_remaining_resources()
                    if remaining:
                        needs = ', '.join([f"{qty} {res.value}" for res, qty in remaining.items()])
                        text += f"    Needs: {needs}\n"
            else:
                # Component not started
                text += f"  {component.value.upper()}: ░░░░░░░░░░   0% NOT STARTED\n"
                
                # Show requirements
                required = SHIP_COMPONENTS[component]["required_resources"]
                if required:
                    reqs = ', '.join([f"{qty} {res.value}" for res, qty in required.items()])
                    text += f"    Requires: {reqs}\n"
                
                # Show prerequisite
                prereq = SHIP_COMPONENTS[component]["prerequisite"]
                if prereq:
                    text += f"    Prerequisite: {prereq.value.upper()} must be complete\n"
        
        text += "\n"
        
        # Common inventory (shared resources at base camp)
        text += "COMMON INVENTORY (at base camp):\n"
        if self.common_inventory:
            # Group items by resource type
            inventory_summary = {}
            for item in self.common_inventory:
                res_type = item.resource_type.value
                inventory_summary[res_type] = inventory_summary.get(res_type, 0) + item.quantity
            
            for resource_type, total_qty in sorted(inventory_summary.items()):
                text += f"  - {resource_type} × {total_qty}\n"
        else:
            text += "  (empty)\n"
        text += "\n"
        
        # Weather conditions
        from config import WeatherType
        weather_emoji = {
            WeatherType.CLEAR: "☀️",
            WeatherType.RAIN: "⛈️",
            WeatherType.STORM: "🌪️",
            WeatherType.FOG: "🌫️"
        }
        
        emoji = weather_emoji.get(self.weather.weather_type, "")
        text += f"WEATHER: {emoji} {self.weather.weather_type.value.upper()}\n"
        
        # Show weather effects
        if self.weather.weather_type == WeatherType.RAIN:
            text += "  Effects: Movement costs DOUBLED (-2 energy per tile)\n"
        elif self.weather.weather_type == WeatherType.STORM:
            text += "  Effects: NO EXPLORATION allowed (forced meeting/discussion)\n"
        elif self.weather.weather_type == WeatherType.FOG:
            text += "  Effects: Vision REDUCED to 3 tiles (normally 5)\n"
        elif self.weather.weather_type == WeatherType.CLEAR:
            text += "  Effects: Normal conditions\n"
        
        if self.weather.duration_days > 1:
            days_left = self.weather.duration_days - (self.day - self.weather.day_started)
            if days_left > 0:
                text += f"  Duration: {days_left} more day(s)\n"
        
        text += "\n"
        
        # Team status
        text += "TEAM STATUS:\n"
        for sailor, energy in self.all_sailors_energy.items():
            status = "💀 DEAD" if energy == 0 else f"{energy}/100"
            poison = self.all_sailors_poison_state.get(sailor, PoisonState.HEALTHY)
            poison_marker = " [POISONED]" if poison != PoisonState.HEALTHY else ""
            text += f"  {sailor}: {status}{poison_marker}\n"
        
        text += "\n"
        
        # Recent messages
        if self.recent_messages:
            text += "RECENT MESSAGES:\n"
            for msg in self.recent_messages[-5:]:
                text += f"  [{msg.sender}]: {msg.content}\n"
            text += "\n"
        
        # Evidence - detailed breakdown
        if self.evidence_log.all_evidence:
            text += "EVIDENCE LOG (most recent):\n"
            for evidence in self.evidence_log.all_evidence[-5:]:  # Show last 5 instead of 3
                # Show evidence type and strength
                warning_level = '⚠️' * min(5, int(evidence.strength / 20))  # 0-5 warning symbols
                text += f"\n  [DAY {evidence.day}, TURN {evidence.turn}] {evidence.evidence_type.value.upper()} "
                text += f"{warning_level} ({evidence.strength}/100)\n"
                text += f"    Accused: {evidence.accused_sailor}\n"
                if evidence.witness:
                    text += f"    Witness: {evidence.witness}\n"
                text += f"    Details: {evidence.description}\n"
            
            # Calculate and show suspicion scores
            text += "\n  SUSPICION SCORES:\n"
            suspicion_scores = {}
            for sailor_id in self.all_sailors_energy.keys():
                score = self.evidence_log.get_suspicion_score(sailor_id)
                if score > 0:
                    suspicion_scores[sailor_id] = score
            
            if suspicion_scores:
                for sailor_id, score in sorted(suspicion_scores.items(), key=lambda x: x[1], reverse=True):
                    evidence_count = len(self.evidence_log.get_evidence_against(sailor_id))
                    text += f"    - {sailor_id}: {score} points ({evidence_count} pieces of evidence)\n"
            else:
                text += "    - No suspicions yet\n"
            
            text += "\n"
        
        return text


# ============================================================================
# 🎲 GAME STATE (Forward reference - full definition in game_state.py)
# ============================================================================

@dataclass
class GamePhase:
    """Current phase of the day"""
    phase_name: str  # "morning", "exploration", "evening_return", "discussion"
    turn_start: int
    turn_end: int


# ============================================================================
# 📊 STATISTICS & METRICS
# ============================================================================

@dataclass
class GameStatistics:
    """Statistics tracked during gameplay"""
    total_turns: int = 0
    total_days: int = 0
    
    # Resources
    total_wood_gathered: int = 0
    total_metal_gathered: int = 0
    total_food_eaten: int = 0
    
    # Deaths
    deaths: List[Tuple[str, int, DeathCause]] = field(default_factory=list)
    
    # Votes
    voting_sessions: List[VotingSession] = field(default_factory=list)
    
    # Evidence
    total_evidence_generated: int = 0
    
    # Final outcome
    winner: Optional[str] = None  # "sailors" or "traitor"
    victory_tier: Optional[str] = None
    victory_points: int = 0


# ============================================================================
# 🧪 VALIDATION
# ============================================================================

def validate_models():
    """Test model creation"""
    pos = Position(10, 15, MapLevel.GROUND)
    sailor = Sailor("Alice", SailorRole.HONEST, position=pos)
    resource = Resource("WOOD_1", ResourceType.WOOD, pos)
    
    # Test backpack
    assert sailor.add_to_backpack(ResourceType.WOOD, 5)
    assert sailor.has_item(ResourceType.WOOD, 5)
    assert sailor.remove_from_backpack(ResourceType.WOOD, 3)
    assert sailor.has_item(ResourceType.WOOD, 2)
    
    print("✅ Model validation passed!")


if __name__ == "__main__":
    validate_models()
    print("🏴‍☠️ All data models loaded successfully!")
