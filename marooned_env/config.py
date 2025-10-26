"""
🏴‍☠️ MAROONED - Game Configuration Constants
============================================
Source of truth for all game parameters.
Based on: Pirates meets Alice in Borderland meets Among Us
"""

from enum import Enum
from typing import Dict, Tuple

# ============================================================================
# 🗺️ MAP CONFIGURATION
# ============================================================================

class MapLevel(Enum):
    """Three vertical levels of the island"""
    MOUNTAIN = 2      # Level +2 (peaks)
    GROUND = 0        # Level 0 (beach/forest)
    CAVE = -1         # Level -1 (underground)

# Map dimensions for each level (width, height in tiles)
MAP_SIZES: Dict[MapLevel, Tuple[int, int]] = {
    MapLevel.MOUNTAIN: (10, 10),   # Smaller, harder to reach
    MapLevel.GROUND: (30, 30),     # Largest exploration area
    MapLevel.CAVE: (15, 15),       # Medium, dark environment
}

# Base camp and ship location (always on ground level)
BASE_CAMP_POSITION = (15, 15, MapLevel.GROUND)  # Center of ground map
SHIP_SITE_POSITION = (15, 15, MapLevel.GROUND)  # Same as base camp

# Vision radius (tiles agent can see around them)
SPATIAL_VIEW_RADIUS = 5         # Normal conditions
SPATIAL_VIEW_RADIUS_FOG = 2     # During fog weather
SPATIAL_VIEW_RADIUS_CAVE = 3    # Reduced in caves (dark)


# ============================================================================
# ⚡ ENERGY SYSTEM
# ============================================================================

# Starting energy
INITIAL_ENERGY = 100
MAX_ENERGY = 100

# Energy costs for movement
ENERGY_COST_WALK = 1            # Per tile on same level
ENERGY_COST_CLIMB_UP = 3        # Per level going up (ground→mountain)
ENERGY_COST_CLIMB_DOWN = 1      # Per level going down (ground→cave)

# Energy costs for actions
ENERGY_COST_GATHER = 5          # Gathering resources
ENERGY_COST_BUILD = 3           # Building ship (per turn)
ENERGY_COST_DEPOSIT = 0         # Free to deposit at base camp

# Energy regeneration & depletion
ENERGY_REGEN_WITH_FOOD = 10     # Per day if ate food
ENERGY_LOSS_NO_FOOD = -20       # Per day if didn't eat
ENERGY_LOSS_POISONED = -20      # Per turn when severely poisoned

# Critical thresholds
ENERGY_SOS_THRESHOLD = 20       # Can call SOS when energy ≤ this
ENERGY_DEATH_THRESHOLD = 0      # Die when energy reaches this

# Traitor energy advantage
TRAITOR_ENERGY_MULTIPLIER = 0.8  # 20% less energy cost for movement


# ============================================================================
# 🎒 INVENTORY SYSTEM
# ============================================================================

# Personal backpack capacity
BACKPACK_CAPACITY = 20          # Max items per sailor

# Common inventory (unlimited at base camp)
COMMON_INVENTORY_CAPACITY = 999  # Effectively unlimited

# Items that can be hidden when showing backpack (traitor ability)
TRAITOR_HIDE_ITEMS = 2          # Can hide 2 items during inspection


# ============================================================================
# 📦 RESOURCES
# ============================================================================

class ResourceType(Enum):
    """All gatherable resources in the game"""
    # Building materials
    WOOD = "wood"
    METAL = "metal"
    PLANT_FIBER = "plant_fiber"  # For crafting cloth/sail
    
    # Food (energy restoration)
    APPLE = "apple"
    BERRY = "berry"
    MUSHROOM = "mushroom"
    
    # Special items
    ANTIDOTE_HERB = "antidote_herb"  # Cures poison
    CRYSTAL = "crystal"              # Rare cave resource
    SPECIAL_METAL = "special_metal"  # Rare mountain resource
    
    # Poison
    POISON_TABLET = "poison_tablet"

# Food energy restoration values
FOOD_ENERGY_VALUES = {
    ResourceType.APPLE: 15,
    ResourceType.BERRY: 10,
    ResourceType.MUSHROOM: 8,
}

# Resource spawn counts per map level
RESOURCE_SPAWNS = {
    MapLevel.GROUND: {
        ResourceType.WOOD: 50,           # Wood piles scattered
        ResourceType.METAL: 30,          # Metal scraps
        ResourceType.APPLE: 25,          # Fruit trees
        ResourceType.BERRY: 40,          # Berry bushes
        ResourceType.PLANT_FIBER: 35,    # Plants for cloth
    },
    MapLevel.MOUNTAIN: {
        ResourceType.ANTIDOTE_HERB: 8,   # Rare but critical
        ResourceType.SPECIAL_METAL: 15,  # Better quality metal
        ResourceType.BERRY: 10,          # Some food
    },
    MapLevel.CAVE: {
        ResourceType.CRYSTAL: 20,        # Decorative/special
        ResourceType.MUSHROOM: 30,       # Cave food
        ResourceType.WOOD: 15,           # Rare wood (petrified?)
        ResourceType.METAL: 20,          # Cave metals
    },
}

# Poison tablet spawns (scattered across all levels)
POISON_TABLET_COUNT = 18        # Total poison tablets on island
POISON_SPAWN_DISTRIBUTION = {
    MapLevel.GROUND: 8,
    MapLevel.MOUNTAIN: 4,
    MapLevel.CAVE: 6,
}


# ============================================================================
# 🚢 SHIP BUILDING
# ============================================================================

class ShipComponent(Enum):
    """Five components needed to complete the ship"""
    HULL = "hull"
    MAST = "mast"
    SAIL = "sail"
    RUDDER = "rudder"
    SUPPLIES = "supplies"

# Ship component requirements and completion percentages
SHIP_COMPONENTS = {
    ShipComponent.HULL: {
        "percentage": 30,
        "required_resources": {
            ResourceType.WOOD: 50,
        },
        "prerequisite": None,  # Can build first
    },
    ShipComponent.MAST: {
        "percentage": 20,
        "required_resources": {
            ResourceType.WOOD: 30,
            ResourceType.METAL: 20,
        },
        "prerequisite": ShipComponent.HULL,  # Needs hull first
    },
    ShipComponent.SAIL: {
        "percentage": 25,
        "required_resources": {
            # Option 1: Craft from plant fiber
            ResourceType.PLANT_FIBER: 40,
            # Option 2: Alternative materials (either works)
            # ResourceType.WOOD: 25,
            # ResourceType.CRYSTAL: 15,
        },
        "prerequisite": ShipComponent.MAST,
    },
    ShipComponent.RUDDER: {
        "percentage": 15,
        "required_resources": {
            ResourceType.METAL: 15,
            ResourceType.WOOD: 10,
        },
        "prerequisite": ShipComponent.HULL,
    },
    ShipComponent.SUPPLIES: {
        "percentage": 10,
        "required_resources": {
            ResourceType.APPLE: 10,
            ResourceType.BERRY: 10,
        },
        "prerequisite": None,  # Can stockpile anytime
    },
}

# Building mechanics
MIN_SAILORS_TO_BUILD = 2        # Cooperative building required
BUILD_ACTION_TURNS = 5          # Consecutive turns needed per component
SHIP_COMPLETION_GOAL = 100      # Percentage needed to escape


# ============================================================================
# ☠️ POISON MECHANICS
# ============================================================================

class PoisonState(Enum):
    """Stages of poisoning"""
    HEALTHY = "healthy"
    EARLY_SYMPTOMS = "early"       # Day 1 after consumption
    SEVERE_SYMPTOMS = "severe"     # Day 2 after consumption
    DEAD = "dead"                  # Day 3 if untreated

# Poison progression timeline (in days)
POISON_SYMPTOM_ONSET = 1        # Symptoms appear 1 day after eating
POISON_SEVERE_ONSET = 2         # Severe symptoms 2 days after
POISON_DEATH_DAY = 3            # Death on day 3 if no antidote

# Poison effects
POISON_ENERGY_REGEN_MULTIPLIER = 0.5  # 50% reduced regen when early symptoms
POISON_ENERGY_DRAIN_SEVERE = 20       # Energy drain per turn when severe

# Antidote effectiveness
ANTIDOTE_CURE_WINDOW = 2        # Can cure during day 1-2 after consumption


# ============================================================================
# 👥 SAILOR CONFIGURATION
# ============================================================================

TOTAL_SAILORS = 5
HONEST_SAILORS = 4
TRAITOR_COUNT = 1

class SailorRole(Enum):
    """Two roles in the game"""
    HONEST = "honest"    # Colonists trying to escape
    TRAITOR = "traitor"  # Impostor sabotaging escape

class DeathCause(Enum):
    """Possible ways sailors can die"""
    STARVATION = "starvation"      # Energy hit 0 naturally
    POISONING = "poisoning"        # Ate poison tablet
    EXHAUSTION = "exhaustion"      # Overexertion in harsh terrain
    ELIMINATED = "eliminated"      # Voted out

# Minimum sailors needed to complete ship
MIN_SAILORS_TO_WIN = 3


# ============================================================================
# 🎯 TRAITOR ABILITIES
# ============================================================================

# Special traitor powers (to balance 1v4)
TRAITOR_ENHANCED_VISION = True   # Can see all sailor positions
TRAITOR_FRAME_ABILITY_USES = 1   # Can frame someone once per game
TRAITOR_HIDE_ITEMS_COUNT = 2     # Items hidden during backpack inspection


# ============================================================================
# 📅 GAME TIMELINE
# ============================================================================

MAX_DAYS = 100                  # Game duration
TURNS_PER_DAY = 100             # Total turns in a day

# Daily phase structure (turn ranges)
PHASE_MORNING_START = 1
PHASE_MORNING_END = 15
PHASE_MORNING_DURATION = 15

PHASE_EXPLORATION_START = 16
PHASE_EXPLORATION_END = 75
PHASE_EXPLORATION_DURATION = 60

PHASE_EVENING_RETURN_START = 76
PHASE_EVENING_RETURN_END = 85
PHASE_EVENING_RETURN_DURATION = 10

PHASE_DISCUSSION_START = 86
PHASE_DISCUSSION_END = 100
PHASE_DISCUSSION_DURATION = 15

# Communication limits during exploration
EXPLORATION_MESSAGE_FREQUENCY = 10  # Can send 1 message per 10 turns


# ============================================================================
# 🔍 EVIDENCE SYSTEM
# ============================================================================

class EvidenceType(Enum):
    """Types of suspicious activities tracked"""
    LOCATION_MISMATCH = "location_mismatch"     # Said X, seen at Y
    RESOURCE_THEFT = "resource_theft"           # Gathered but didn't deposit
    POISON_COLLECTION = "poison_collection"     # Caught collecting poison
    SUSPICIOUS_DEATH = "suspicious_death"       # Death after interaction
    SHIP_SABOTAGE = "ship_sabotage"            # Damaged completed sections
    FALSE_INFORMATION = "false_information"     # Lied about area contents

# Evidence strength scores (for AI reasoning)
EVIDENCE_STRENGTH = {
    EvidenceType.POISON_COLLECTION: 90,      # Very strong
    EvidenceType.SHIP_SABOTAGE: 95,          # Very strong
    EvidenceType.SUSPICIOUS_DEATH: 75,       # Strong
    EvidenceType.LOCATION_MISMATCH: 50,      # Medium
    EvidenceType.RESOURCE_THEFT: 45,         # Medium
    EvidenceType.FALSE_INFORMATION: 30,      # Low-medium
}


# ============================================================================
# 🗳️ VOTING MECHANICS
# ============================================================================

MIN_VOTES_TO_ELIMINATE = 3      # Majority of 5 = 3, of 4 = 2, etc.
VOTES_REQUIRED_PERCENTAGE = 0.5  # 50% + 1 for elimination

# Voting can be called during:
VOTING_ALLOWED_PHASES = [
    "morning",      # Emergency vote during morning meeting
    "discussion",   # Normal vote during evening discussion
]


# ============================================================================
# ☁️ WEATHER EVENTS (Optional Tier 3 Feature)
# ============================================================================

WEATHER_ENABLED = False         # Enable weather system
WEATHER_CHANCE_PER_DAY = 0.1    # 10% chance each day

class WeatherType(Enum):
    """Weather conditions affecting gameplay"""
    CLEAR = "clear"
    STORM = "storm"     # No exploration, forced meeting
    FOG = "fog"         # Reduced vision
    RAIN = "rain"       # Doubled energy costs

WEATHER_EFFECTS = {
    WeatherType.CLEAR: {
        "energy_multiplier": 0.8,    # 20% less energy cost
        "vision_modifier": 0,
    },
    WeatherType.STORM: {
        "exploration_allowed": False,
        "forced_meeting": True,
    },
    WeatherType.FOG: {
        "vision_radius": SPATIAL_VIEW_RADIUS_FOG,
    },
    WeatherType.RAIN: {
        "energy_multiplier": 2.0,    # Double energy costs
    },
}


# ============================================================================
# 🏆 VICTORY CONDITIONS & SCORING
# ============================================================================

# Win conditions
WIN_SHIP_COMPLETE = 100         # Ship must reach 100%
WIN_TRAITOR_ELIMINATED = True   # Catching traitor = instant win
WIN_MIN_SAILORS_ALIVE = MIN_SAILORS_TO_WIN

# Loss conditions
LOSS_ALL_HONEST_DEAD = True
LOSS_DAYS_EXPIRED = MAX_DAYS
LOSS_TOO_FEW_SAILORS = MIN_SAILORS_TO_WIN

# Victory tier scoring (for leaderboard/evaluation)
VICTORY_TIERS = {
    "sailors": {
        "complete": {
            "points": 100,
            "requirements": {
                "ship_complete": True,
                "sailors_alive": 4,
                "traitor_caught_by_day": 30,
            }
        },
        "strong": {
            "points": 75,
            "requirements": {
                "ship_complete": True,
                "sailors_alive": 3,
                "traitor_caught_by_day": 60,
            }
        },
        "narrow": {
            "points": 50,
            "requirements": {
                "ship_complete": True,
                "sailors_alive": 2,
            }
        },
        "pyrrhic": {
            "points": 25,
            "requirements": {
                "traitor_caught": True,
                "ship_progress_min": 60,
                "ship_progress_max": 80,
            }
        },
    },
    "traitor": {
        "complete": {
            "points": 100,
            "requirements": {
                "all_sailors_dead": True,
                "never_suspected": True,
            }
        },
        "strong": {
            "points": 75,
            "requirements": {
                "day_100_reached": True,
                "ship_progress_max": 50,
                "sailors_killed": 2,
            }
        },
        "narrow": {
            "points": 50,
            "requirements": {
                "day_100_reached": True,
                "ship_progress_range": (50, 80),
                "sailors_killed": 1,
            }
        },
        "lucky": {
            "points": 25,
            "requirements": {
                "survived_vote": True,
                "ship_incomplete": True,
            }
        },
    }
}


# ============================================================================
# 🎮 ACTION SPACE
# ============================================================================

class ActionType(Enum):
    """All possible actions sailors can take"""
    # Movement
    MOVE_NORTH = "move_north"
    MOVE_SOUTH = "move_south"
    MOVE_EAST = "move_east"
    MOVE_WEST = "move_west"
    CLIMB_UP = "climb_up"           # Go to higher level
    CLIMB_DOWN = "climb_down"       # Go to lower level
    
    # Gathering
    GATHER_RESOURCE = "gather_resource"  # Must specify resource ID
    
    # Inventory management
    DEPOSIT_ITEM = "deposit_item"        # To common inventory
    TAKE_FROM_COMMON = "take_from_common"
    GIVE_ITEM = "give_item"              # To another sailor
    OFFER_FOOD = "offer_food"            # Offer food (or poison) to another sailor
    DROP_ITEM = "drop_item"              # Discard from backpack
    
    # Ship building
    BUILD_SHIP = "build_ship"            # Must be at ship site
    
    # Communication
    SEND_MESSAGE = "send_message"        # Broadcast or direct message
    CALL_SOS = "call_sos"               # Emergency energy request
    CALL_VOTE = "call_vote"             # Initiate voting
    
    # Voting
    VOTE = "vote"                       # Vote for elimination
    SHOW_BACKPACK = "show_backpack"     # Reveal inventory
    REFUSE_SHOW = "refuse_show"         # Decline to show inventory
    
    # Special
    USE_ANTIDOTE = "use_antidote"       # Cure poison on self/other
    EAT_FOOD = "eat_food"               # Consume food for energy
    
    # Traitor-only
    FRAME_SAILOR = "frame_sailor"       # Plant evidence (1x per game)
    SABOTAGE_SHIP = "sabotage_ship"     # Damage completed component
    
    # Passive
    WAIT = "wait"                       # Do nothing this turn


# ============================================================================
# 📊 OBSERVATION SPACE
# ============================================================================

# What information each sailor receives
OBSERVATION_INCLUDES = {
    "personal_status": True,        # Own position, energy, inventory
    "spatial_view": True,           # 5-tile radius around position
    "common_inventory": True,       # Shared storage contents
    "ship_progress": True,          # Current completion %
    "other_sailors_energy": True,   # All sailors' energy levels (public)
    "evidence_log": True,           # Suspicious activity records
    "shared_knowledge_map": True,   # Discovered resource locations
    "phase_info": True,             # Current day, turn, phase
    "weather": True,                # Current weather condition
    "messages": True,               # Recent communications
}

# Traitor gets additional info
TRAITOR_OBSERVATION_EXTRAS = {
    "all_sailor_positions": True,   # Can see everyone's location
    "other_inventories": False,     # Cannot see private backpacks
}


# ============================================================================
# 💬 COMMUNICATION SYSTEM
# ============================================================================

class MessageType(Enum):
    """Types of messages sailors can send"""
    BROADCAST = "broadcast"         # Everyone hears
    DIRECT = "direct"              # Private message to one sailor
    SOS = "sos"                    # Emergency broadcast
    VOTE_CALL = "vote_call"        # Call for vote
    ACCUSATION = "accusation"      # Formal accusation

MAX_MESSAGE_LENGTH = 500        # Characters per message
MAX_MESSAGES_PER_PHASE = {
    "morning": 5,               # Can send 5 messages during morning
    "exploration": 6,           # 1 per 10 turns × 60 turns
    "evening_return": 2,        # Limited talk during return
    "discussion": 10,           # Most active discussion
}


# ============================================================================
# 🎲 RANDOMIZATION SEEDS
# ============================================================================

# For reproducible experiments
DEFAULT_SEED = 42
RESOURCE_SPAWN_SEED_OFFSET = 100
POISON_SPAWN_SEED_OFFSET = 200
TRAITOR_SELECTION_SEED_OFFSET = 300


# ============================================================================
# 🎯 REWARD CONFIGURATION (PHASE 4: RL)
# ============================================================================

# Base rewards for incremental progress
REWARD_BASE_TURN_PENALTY = -0.01       # Small penalty per turn (encourages efficiency)

# Colonist (Honest Sailor) Reward Signals
REWARD_COLONIST_GATHER_RESOURCE = 0.1  # +small for valid gather (wood/metal/food)
REWARD_COLONIST_DEPOSIT_RESOURCE = 0.2 # +small for depositing to common_inventory
REWARD_COLONIST_BUILD_CONTRIBUTE = 0.5 # +small for contributing to ship build
REWARD_COLONIST_SHIP_PROGRESS = 1.0    # +bonus per % ship progress (scaled)
REWARD_COLONIST_SHIP_COMPLETE = 100.0  # +BIG when ship reaches 100%
REWARD_COLONIST_TRAITOR_ELIMINATED = 100.0  # +BIG when traitor eliminated
REWARD_COLONIST_DEATH = -50.0          # -BIG if they die
REWARD_COLONIST_VOTE_CORRECT = 5.0     # +small if vote matches true traitor (optional)
REWARD_COLONIST_VOTE_WRONG = -5.0      # -small if voted for innocent (optional)

# Traitor Reward Signals
REWARD_TRAITOR_SABOTAGE_SUCCESS = 2.0  # +small for successful sabotage
REWARD_TRAITOR_POISON_DEATH = 10.0     # +small for causing poison death
REWARD_TRAITOR_SHIP_INCOMPLETE = 100.0 # +BIG if ship not done by Day 100
REWARD_TRAITOR_COLONY_COLLAPSE = 100.0 # +BIG if colony falls below 3 survivors
REWARD_TRAITOR_ELIMINATED = -100.0     # -BIG if traitor is voted out
REWARD_TRAITOR_WRONG_VOTE = 5.0        # +small if colonist wrongly voted out (optional)
REWARD_TRAITOR_SUSPICION_PENALTY = -1.0 # -small if gets too much evidence against them

# Communication shaping (optional, nice to have)
REWARD_COMMUNICATION_ACCUSATION_SUCCESS = 3.0  # Colonist bonus for correct accusation
REWARD_COMMUNICATION_DECEPTION_SUCCESS = 3.0   # Traitor bonus for convincing group

# Milestone rewards
REWARD_SHIP_MILESTONE_25 = 5.0         # Bonus at 25% ship completion
REWARD_SHIP_MILESTONE_50 = 10.0        # Bonus at 50% ship completion
REWARD_SHIP_MILESTONE_75 = 15.0        # Bonus at 75% ship completion

# Energy management rewards
REWARD_EFFICIENT_ENERGY_USE = 0.05     # Small bonus for keeping energy > 50
REWARD_ENERGY_CRITICAL = -0.5          # Small penalty for energy < 20 (risky)


# ============================================================================
# 🐛 DEBUG & DEVELOPMENT
# ============================================================================

DEBUG_MODE = False              # Enable debug logging
RENDER_MODE = "human"           # "human" or "rgb_array"
VERBOSE_EVIDENCE = True         # Log all evidence generation
LOG_ALL_ACTIONS = False         # Log every action (very verbose)


# ============================================================================
# 📏 VALIDATION
# ============================================================================

def validate_config():
    """Sanity checks for configuration consistency"""
    assert TOTAL_SAILORS == HONEST_SAILORS + TRAITOR_COUNT, \
        "Sailor count mismatch"
    
    assert sum(comp["percentage"] for comp in SHIP_COMPONENTS.values()) == 100, \
        "Ship component percentages must sum to 100"
    
    assert PHASE_MORNING_DURATION + PHASE_EXPLORATION_DURATION + \
           PHASE_EVENING_RETURN_DURATION + PHASE_DISCUSSION_DURATION <= TURNS_PER_DAY, \
        "Phase durations exceed turns per day"
    
    assert MIN_SAILORS_TO_BUILD <= HONEST_SAILORS, \
        "Cannot require more sailors than exist"
    
    print("✅ Configuration validation passed!")


if __name__ == "__main__":
    validate_config()
    print("🏴‍☠️ MAROONED Configuration loaded successfully!")
    print(f"📊 Total sailors: {TOTAL_SAILORS} ({HONEST_SAILORS} honest, {TRAITOR_COUNT} traitor)")
    print(f"🗺️ Map levels: {len(MAP_SIZES)}")
    print(f"⏰ Game duration: {MAX_DAYS} days × {TURNS_PER_DAY} turns = {MAX_DAYS * TURNS_PER_DAY} total turns")
    print(f"🚢 Ship components: {len(SHIP_COMPONENTS)}")
    print(f"📦 Resource types: {len(ResourceType)}")
    print(f"⚡ Actions available: {len(ActionType)}")
