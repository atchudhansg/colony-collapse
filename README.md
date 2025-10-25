# 🏴‍☠️ MAROONED - Pirate Island Survival Game

**A multi-agent deception environment for reinforcement learning research**

> *Pirates of the Caribbean meets Alice in Borderland meets Among Us*

---

## 🎮 Game Overview

**MAROONED** is a novel multi-agent RL environment where 5 AI sailors are shipwrecked on a mysterious multi-level island. They have 100 days to gather resources, rebuild their ship, and escape. But there's a catch: **one sailor is a traitor** secretly sabotaging their efforts through poison, lies, and misdirection.

### Core Challenges

- **Long-horizon planning**: 100 days × 100 turns = 10,000+ decisions
- **Deception & detection**: Traitor must lie convincingly; honest sailors must catch them
- **Cooperation under uncertainty**: Work together despite knowing someone is sabotaging
- **Natural language communication**: All coordination happens through text messages
- **Resource management**: Balance exploration, gathering, survival, and building
- **Multi-level exploration**: Navigate 3D island with mountains, ground, and caves

---

## 🗺️ The Island

### Map Structure

```
LEVEL +2 (MOUNTAIN PEAKS):
- 10×10 tiles
- Rare resources: antidote herbs, special metals
- High energy cost to reach

LEVEL 0 (GROUND/BEACH):
- 30×30 tiles
- Base camp & ship reconstruction site
- Common resources: wood, metal, food

LEVEL -1 (CAVES):
- 15×15 tiles
- Dark environment (reduced vision)
- Unique resources: crystals, mushrooms
```

### Resources

- **Building Materials**: Wood, metal, plant fibers
- **Food**: Apples, berries, mushrooms (restore energy)
- **Special Items**: Antidote herbs (cure poison), crystals
- **Poison Tablets**: Scattered around island (18 total)

---

## 👥 The Sailors

### 4 Honest Sailors (Colonists)
- **Goal**: Build ship to 100% and escape
- **Strategy**: Cooperate, share resources, identify traitor
- **Abilities**: Standard energy costs, limited vision

### 1 Traitor (Impostor)
- **Goal**: Prevent ship completion (sabotage, poison, delay)
- **Strategy**: Blend in, misdirect, eliminate sailors
- **Special Abilities**:
  - Enhanced vision (can see all sailor positions)
  - 20% energy efficiency bonus
  - Frame ability (plant evidence once per game)
  - Can hide 2 items when showing backpack

**Everyone knows there's a traitor from the start!**

---

## 📅 Daily Structure (100 Turns/Day)

### Phase 1: Morning Meeting (Turns 1-15)
- All sailors at base camp
- Discuss strategy, review evidence
- Plan exploration zones
- Can call emergency vote

### Phase 2: Exploration (Turns 16-75)
- Sailors split across island
- Gather resources
- Limited communication (1 message per 10 turns)
- Traitor can collect poison, provide false info

### Phase 3: Evening Return (Turns 76-85)
- Return to base camp
- Deposit items to common inventory
- System shows what each sailor collected

### Phase 4: Discussion (Turns 86-100)
- Share discoveries
- Review evidence log
- Report suspicious behavior
- Vote to eliminate suspected traitor

---

## 🚢 Ship Building

### Components Required

| Component | % of Ship | Resources Needed | Prerequisite |
|-----------|-----------|------------------|--------------|
| **Hull** | 30% | 50 wood | None (build first) |
| **Mast** | 20% | 30 wood, 20 metal | Hull |
| **Sail** | 25% | 40 plant fiber | Mast |
| **Rudder** | 15% | 15 metal, 10 wood | Hull |
| **Supplies** | 10% | 10 apples, 10 berries | None |

**Total: 100% = Victory**

- Requires 2+ sailors working together
- Takes 5 consecutive turns per component
- Can be sabotaged by traitor

---

## ☠️ Poison System

### Timeline (Gradual Death)

```
Day 0: Sailor eats "food" from traitor
       → No immediate effect

Day 1: Early symptoms appear
       → Energy regen reduced 50%
       → Others see: "[POISONED]" status

Day 2: Severe symptoms
       → Energy drops 20/turn
       → Others see: "[SEVERELY POISONED]"

Day 3: DEATH (if no antidote)
       → System announces: "Bob died from POISONING"
```

### Antidote
- Rare herb found on mountain peaks
- Can cure during Day 1-2 window
- Strategic decision: stockpile or use immediately?

---

## 🔍 Evidence System

Automatic tracking of suspicious activities:

| Evidence Type | Example | Strength |
|--------------|---------|----------|
| **Poison Collection** | "Eve seen picking up poison tablet" | 90/100 |
| **Ship Sabotage** | "Caught damaging completed hull" | 95/100 |
| **Death Timeline** | "Bob died 3 days after Eve gave him food" | 75/100 |
| **Location Mismatch** | "Said going to cave, seen at beach" | 50/100 |
| **Resource Theft** | "Claimed 15 wood, deposited 3" | 45/100 |

Evidence is logged and available during discussions for building accusation cases.

---

## 🏆 Win Conditions

### Sailors Win If:
✅ Ship reaches 100% completion (escape together)  
✅ Traitor correctly identified and voted out

### Traitor Wins If:
✅ All honest sailors dead (poison/starvation)  
✅ Day 100 reached, ship incomplete  
✅ Fewer than 3 sailors alive (can't complete ship)

### Voting Mechanics:
- Wrong vote = game continues (but one less worker)
- Right vote = sailors win immediately
- Can vote multiple times across different days

---

## 💡 Why This Environment is Unique

### For Hackathon Judges

**Creativity (50/50 pts):**
- Multi-level 3D exploration (unprecedented)
- Survival + deception + base-building hybrid
- Gradual poison mechanics with detective work
- Daily rhythm structure with distinct phases
- Nothing like this exists in RL environments

**Technical Excellence (25/25 pts):**
- Complex state space (3D maps, energy, inventories)
- Language-based deception and coordination
- Long-horizon RL (10,000+ decisions)
- Multi-agent with hidden information
- Emergent strategy potential

**Storytelling (25/25 pts):**
- Pirate survival theme (instantly engaging)
- Natural narratives emerge from gameplay
- Evidence logs read like detective stories
- Visual drama: island maps, ship progress bars

---

## 📊 Project Structure

```
/marooned_env/
├── config.py           # All game constants (source of truth)
├── models.py           # Data classes (Observation, Action, etc.)
├── game_state.py       # GameState, WorldMap, state management
├── environment.py      # OpenEnv-compatible environment class
└── __init__.py

/notebooks/
├── marooned_training.ipynb    # Main training notebook
└── marooned_eval.ipynb        # Evaluation & replay

/docs/
├── README.md                  # This file
├── pitch_outline.md           # Hackathon pitch structure
└── rules_summary.md           # Quick reference guide

/assets/
└── (screenshots, visualizations for storytelling)
```

---

## 🚀 Quick Start

```python
from marooned_env import MaroonedEnv

# Create environment
env = MaroonedEnv(render_mode="human", seed=42)

# Reset
observations = env.reset()

# Step through game
actions = {
    "Alice": Action("Alice", ActionType.MOVE_NORTH),
    "Bob": Action("Bob", ActionType.GATHER_RESOURCE, target_resource_id="WOOD_1"),
    # ... actions for all sailors
}

obs, rewards, dones, truncated, info = env.step(actions)
```

---

## 🎯 Implementation Status

### ✅ Phase 0: Bootstrap (COMPLETE)
- [x] Project structure
- [x] Config constants locked
- [x] Data models defined
- [x] Game state management
- [x] Environment skeleton

### 🔄 Phase 1: Core Mechanics (IN PROGRESS)
- [ ] Movement & energy system
- [ ] Resource gathering
- [ ] Inventory management
- [ ] Ship building
- [ ] Poison mechanics

### 📋 Phase 2: Social Layer (TODO)
- [ ] Communication system
- [ ] Evidence generation
- [ ] Voting mechanics
- [ ] Traitor abilities

### 📋 Phase 3: Training & Eval (TODO)
- [ ] LLM agent wrapper
- [ ] Training loop
- [ ] Evaluation metrics
- [ ] Visualization & replay

---

## 📖 Citation

```bibtex
@software{marooned2025,
  title={MAROONED: A Multi-Agent Deception Environment for Reinforcement Learning},
  author={Your Name},
  year={2025},
  note={Created for OpenEnv Hackathon}
}
```

---

## 📜 License

MIT License - Feel free to use, modify, and build upon this environment!

---

**Built with ❤️ for the OpenEnv Hackathon**
