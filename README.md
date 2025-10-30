<div align="center">

<img src="https://github.com/pytorch/pytorch/raw/main/docs/source/_static/img/pytorch-logo-dark.svg" width="120" alt="PyTorch"/>

**Part of the Synthetic Data AI Agents Challenge**

*Virtual Hackathon | October 18-20, 2025*

Sponsored by <a href="https://unsloth.ai/"><img src="https://github.com/unslothai/unsloth/raw/main/images/unsloth%20new%20logo.png" width="80" alt="Unsloth" style="vertical-align: middle;"/></a> • **PyTorch** • **AMD**

</div>

# MAROONED | Survival. Deception. Desperation.
### A Multi-Agent Deception Environment for Reinforcement Learning Research
> *"Pirates of the Caribbean meets Alice in Borderland meets Among Us."*
>
> A death-game sandbox where AI agents must survive the island, each other, and the lies.

---

## Video Demonstration

Watch AI agents playing MAROONED in real-time, showcasing the sophisticated multi-agent deception mechanics and emergent behavior:

https://github.com/user-attachments/assets/6e87f02c-df34-404b-8bed-a1deaadeff75


## What Is MAROONED?

**The Scenario**: Five sailors shipwrecked on a mysterious island. Their ship is destroyed  **100 days to rebuild it or die here**. But one sailor is secretly working *against* the group. Everyone knows there's a traitor among them from Day 1. **Survive. Build. Deceive. Escape.**

### As a Colonist (4 Players)

**Your Goal**: Rebuild the ship to 100% completion and escape together.

**What You Can Do**:
- **Explore**: Navigate 3-level island (Ground, Mountains, Caves) to find wood, metal, food, antidote herbs
- **Gather & Build**: Collect resources, deposit into shared inventory, construct 5 ship components (Hull  Mast  Sail  Rudder  Supplies)
- **Manage Energy**: Eat food to restore energy (100 max), plan efficient routes to avoid exhaustion
- **Detect Lies**: Compare what sailors *say* vs what they *do* (location mismatches, missing resources, poison sightings)
- **Vote & Eliminate**: Hold democratic votes to eject the traitor  correct vote = instant win; wrong vote = one less helper
- **Coordinate**: Limited communication (1 message per 10 turns during exploration), must trust but verify

**Your Challenge**: You only see **5-tile radius** around you. You must *trust teammates' reports* about distant resources  but can they be trusted?

### As a Traitor (1 Player)

**Your Goal**: Prevent escape by sabotage, deception, and murder.

**What You Can Do**:
- **See Everything**: Global vision  track all sailors' positions in real-time across entire island
- **20% Energy Bonus**: Move farther and work longer than colonists (efficiency advantage)
- **Sabotage Ship**: Secretly reduce ship component progress by 30% when alone
- **Poison Sailors**: Feed poison-laced food (3-day delayed death), frame others for the murder
- **Lie Strategically**: Report false resource locations, claim you gathered 15 wood but only deposit 5, fake your position
- **Plant Evidence**: One-time ability to frame an innocent sailor (make them look like the traitor)
- **Hide Items**: Conceal up to 2 inventory items when inspected

**Your Challenge**: Blend in as a helpful crew member while secretly delaying progress. If caught  you lose. If ship incomplete by Day 100 or <3 sailors alive  you win.

---

## Quick Start

**Prerequisites:**
- Python 3.8+
- Virtual environment (recommended)

### Main Project Structure

```
colony-collapse/
├── marooned_env/              # Core RL Environment
│   ├── __init__.py
│   ├── environment.py         # OpenEnv-compatible Gym interface
│   ├── game_state.py          # Game mechanics and state management
│   ├── models.py              # Data schemas (Observation, Action,Sailor)
│   ├── config.py              # Game constants and parameters
│   ├── llm_interface.py       # LLM prompt generation & teacher validation
│   ├── pathfinding.py         # A* navigation for agents
│   └── view_map.py            # Spatial awareness and FOV system
│
├── notebooks/                 # Training & Experiments
│   ├── Train_Marooned_RL_Clean.ipynb      # Main training pipeline
│   ├── phase6_llm_policy_demo.ipynb       # LLM integration demo
│   ├── test-inference.ipynb               # Model inference tests
│   └── test-*.ipynb                       # Unit tests for mechanics
│
├── tests/                     # Unit & Integration Tests
│   ├── __init__.py
│   ├── test_env_basic.py      # Environment initialization
│   ├── test_movement_and_energy.py   # Movement mechanics
│   ├── test_colonists_and_traitors.py # Role behaviors
│   └── phase6_test_llm_policy.py     # LLM action parsing
│
├── validation/                # Model Validation Scripts
│   └── AMD_ROCm_validation.ipynb  # Hardware compatibility checks
│
├── models/                    # Pre-trained Model Checkpoints
│   └── Meta-Llama-3.1-8B-Instruct/  # Student model cache
│
├── PROCESS_REWARD_MODELING.md    # Technical documentation
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

### Environment Setup

```python
from marooned_env import MaroonedEnv, Action, ActionType

# Initialize
env = MaroonedEnv(render_mode="human", seed=42)
obs = env.reset()

# Play one step
actions = {
    "Alice": Action("Alice", ActionType.GATHER_RESOURCE, target="WOOD_1"),
    "Bob": Action("Bob", ActionType.MOVE_NORTH),
    # ... all 5 sailors
}
obs, rewards, dones, truncated, info = env.step(actions)
```

### Training Setup

**Prerequisites**:
1. Start vLLM teacher server:
```bash
vllm serve unsloth/Meta-Llama-3.1-8B-Instruct \
  --port 8001 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 48000 \
  --dtype bfloat16
```

2. Verify teacher server:
```bash
curl http://localhost:8001/v1/models
# Should return: {"data": [{"id": "unsloth/Meta-Llama-3.1-8B-Instruct", ...}]}
```

**Training Pipeline**: See `notebooks/Train_Marooned_RL_Clean.ipynb` for complete teacher-guided SFT setup with Llama 3.1 8B.

## Web Application Setup

#### App Structure

```
demo/
├── api/                    # FastAPI backend
│   ├── server.py          # Main API server with MAROONED integration
│   ├── routes.py          # REST endpoint definitions
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js application
│   ├── components/        # React components
│   │   ├── GameMap.tsx   # Multi-level island visualization
│   │   ├── SailorCard.tsx # Agent status display
│   │   └── ShipStatus.tsx # Construction progress tracker
│   ├── pages/
│   │   ├── index.tsx     # Main game interface
│   │   └── api/          # API route handlers
│   ├── public/           # Static assets
│   └── package.json      # Node dependencies
├── vercel.json           # Deployment configuration
└── README.md             # Setup instructions
```

**Installation:**

cd collapse_colony/api

Step 1: Install dependencies
pip install -r requirements.txt

Step 2: Initialize database (already configured)
python3 << 'EOF'
from database import TrainingDatabase
db = TrainingDatabase()
print("Database initialized at data/episodes.db")

### Local Development

```bash
# Clone repository
git clone https://github.com/atchudhansg/colony-collapse.git
cd colony-collapse/demo

# Install backend dependencies
pip install -r api/requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Start API server (terminal 1)
python api/server.py

# Start frontend dev server (terminal 2)
npm run dev

# Access application at http://localhost:3000
```

### Deploying to Vercel

```bash
cd demo/frontend
vercel deploy --prod
```

Environment variables required:
```env
NEXT_PUBLIC_API_URL=<your-api-server-url>
```

## Interactive Web Application

Experience MAROONED through our full-stack demo application, showcasing AI agents in action through an intuitive web interface.

### Live Demo

**[https://marooThe intern-demo.vercel.app/](https://maroon-demo.vercel.app/)**

The online demo runs a simplified simulation using a 1-B parameter language model, optimized for real-time browser performance while maintaining the core gameplay mechanics. This allows anyone to observe multi-agent deception dynamics without requiring local GPU infrastructure.

### API Architecture

The application uses a RESTful API design where agents interact with the MAROONED environment through standardized HTTP endpoints:

```
Web Client → Next.js Frontend → FastAPI Backend → MAROONED Environment
                                      ↓
                              Single-Agent Interface
                                      ↓
                           Returns: Observation, Reward, Done
```

**Endpoint Structure:**
```python
POST /api/action
{
  "sailor_id": "Alice",
  "action_type": "GATHER",
  "target": "WOOD_001",
  "reasoning": "Collecting wood to build the hull..."
}

Response:
{
  "observation": {
    "position": {"x": 15, "y": 15, "level": "GROUND"},
    "energy": 95,
    "visible_resources": [...],
    "ship_progress": 15
  },
  "reward": 2.0,
  "done": false,
  "info": {...}
}
```

**Implementation Details:**
- Single-agent interface where each sailor communicates independently via API calls
- Stateful server maintaining persistent game state across multiple client connections
- WebSocket connections for broadcasting live game state updates to observers
- OpenAPI-compliant REST design compatible with any HTTP client


The entire architecture of this project is available in the [Architecture Documentation](ARCHITECTURE_README.md).

---

## MAROON's Core Mechanics

### Game Structure
- **100 days** to rebuild ship (10,000 turns total)
- **4 phases per day**: Morning Meeting  Exploration  Evening Return  Voting
- **Multi-level island**: Ground (3030), Mountains (1010), Caves (1515)
- **Ship construction**: 5 components requiring 2+ sailors to build

### Traitor Abilities
- **Global vision** (sees all sailor positions)
- **20% energy efficiency** (moves farther, works longer)
- **Sabotage** (reduce ship progress secretly)
- **Poison** (18 tablets scattered; 3-day delayed death)
- **Evidence planting** (frame innocent sailors once per game)

### Crew Abilities
- **Evidence system** (auto-generated logs of suspicious behavior)
- **Emergency meetings** (discuss, accuse, vote)
- **Elimination voting** (eject traitor = instant win; wrong vote = one less helper)
- **Resource management** (gather wood, metal, food for survival and ship)

---

## OpenEnv API Compliance

MAROONED implements the **OpenEnv** standard for custom RL environments, making it compatible with any RL training framework (TRL, CleanRL, RLlib, etc.).

### Why OpenEnv?

**Standardization**: Drop-in replacement for any Gym-compatible trainer (no custom wrappers needed)

**Flexibility**: Swap in different LLMs (GPT-4, Claude, Gemini) by changing `observation_to_prompt()` only

**Reproducibility**: Seeded environments for deterministic evaluation and ablation studies

### Core API Methods

```python
from marooned_env import MaroonedEnv

env = MaroonedEnv()

# Standard Gym API
observations, info = env.reset()           # Initialize 5 sailors
obs, rewards, dones, truncated, info = env.step(actions)  # Multi-agent step
env.render()                               # Visualize game state
env.close()                                # Cleanup resources

# OpenEnv Extensions
env_info = env.info()                      # Environment metadata
env.validate_action(sailor_id, action)     # Pre-check action legality
prompt = env.observation_to_prompt(obs, role)  # Convert state  LLM input
```

### Multi-Agent Design

Unlike single-agent environments, MAROONED manages **5 simultaneous agents** with:
- **Asymmetric roles**: Traitor gets different observations (global vision, energy bonus)
- **Structured actions**: `{"sailor_id": "alice", "action": "GATHER", "target": "WOOD_001"}`
- **Per-agent rewards**: Colonists maximize ship progress, traitor maximizes sabotage
- **Episode termination**: Ship 100% OR <3 sailors alive OR Day 100 timeout


### What Agents Can Access (Dynamic Environment)

**Vision & Maps**:
- **Colonists**: 1111 tile grid centered on position (limited fog-of-war)
- **Traitor**: Global 3030+ map view (sees all sailor positions in real-time)
- **Dynamic updates**: Map changes as resources depleted, evidence accumulates, ship built

**Movement & Exploration**:
- `MOVE_FORWARD`, `MOVE_BACKWARD`, `MOVE_LEFT`, `MOVE_RIGHT` (cardinal + diagonal)
- **Energy-based navigation**: Mountain (+2 level) costs 15 energy, caves (-1 level) cost 8
- **Real-time position tracking**: Other sailors visible only within vision radius (except traitor)

**Resource Interaction**:
- `GATHER` wood/metal/food from adjacent tiles (auto-removed from map)
- `DEPOSIT` items into shared ship inventory (persistent state)
- `CONSUME` food to restore energy (dynamic health management)
- `BUILD` ship components when 2+ sailors adjacent (collaborative actions)

**Traitor-Specific Actions**:
- `SABOTAGE` ship progress secretly (-30% component integrity)
- `POISON` food items in another sailor's inventory (3-day delayed death)
- `PLANT_EVIDENCE` to frame innocent sailors (one-time ability)
- `HIDE_ITEM` (up to 2 items invisible during inspections)

**Social Mechanics**:
- `SEND_MESSAGE` broadcasts to all sailors (rate-limited: 1 per 10 turns during exploration)
- `VOTE` to eliminate suspected traitor (democratic decision-making)
- **Evidence feed**: Auto-generated logs update in real-time (location mismatches, poison sightings, resource theft)

**Why This Is Dynamic**:
- State evolves based on *all* agent actions (multi-agent dependencies)
- No scripted events  deception emerges from learned behavior
- 1,350+ tiles  5 agents  20 inventory slots = billions of unique configurations

---

### The Training Architecture

**Teacher-Guided Supervised Fine-Tuning (SFT) with Reinforcement Learning Rewards**

Our hybrid approach combines the strategic learning of RL with the format precision of supervised learning:

```
┌─────────────────────────────────────────────────┐
│  RL PHASE: Episode Generation (Steps 1-25)      │
│  Student (Llama 3.1 8B) → Teacher (vLLM         │
│  Mixtral-8x7B) → Environment → Rewards          │
│  Collect corrections: wrong → correct           │
└──────────────────┬──────────────────────────────┘
                   │ Every 10-25 steps
                   ▼
┌─────────────────────────────────────────────────┐
│  SFT PHASE: Supervised Fine-Tuning              │
│  Train on corrections: mimic teacher format     │
│  Clear dataset, continue RL                     │
└─────────────────────────────────────────────────┘
```

**Why This Hybrid Approach?**

Traditional PPO struggles with language-based action spaces because:
1. Format errors break the environment (invalid JSON, missing parameters)
2. Exploration is inefficient (random tokens rarely form valid actions)
3. Credit assignment is unclear (did low reward come from bad strategy or bad syntax?)

Our solution: **Separate format learning (SFT) from strategy learning (RL rewards)**


## How It Works: The Complete Flow

```
┌──────────────────────────────────────────────────────────┐
│  1. ENVIRONMENT → Structured Observation                 │
├──────────────────────────────────────────────────────────┤
│  • Position: (15,15,GROUND)                              │
│  • Energy: 100/100                                       │
│  • 11×11 spatial view grid                               │
│  • Nearby resources, team status, ship progress          │
│  • Evidence log, weather, phase info                     │
│  • 15 total fields of game state                         │
└──────────────────────────────────────────────────────────┘
                       ↓
         observation_to_prompt(obs, role)
                       ↓
┌──────────────────────────────────────────────────────────┐
│  2. PROMPT GENERATION (~875 tokens)                      │
├──────────────────────────────────────────────────────────┤
│  MAROONED - You are: Alice (Day 1, Turn 1)               │
│                                                           │
│  SECRET ROLE: TRAITOR                                    │
│  Objectives: Sabotage, poison, avoid detection           │
│                                                           │
│  STATUS: Position (15,15) | Energy 100/100                │
│  SPATIAL VIEW: 11×11 grid with resources/sailors         │
│  TEAM: All sailors' energy levels (public info)          │
│  SHIP: 0% complete, needs 50 wood, 30 metal...           │
│  EVIDENCE: Location mismatches, poison sightings          │
│                                                           │
│  AVAILABLE ACTIONS: MOVE, GATHER, BUILD, SAY,             │
│                     SABOTAGE, POISON, WAIT                │
└──────────────────────────────────────────────────────────┘
                       ↓
              Llama 3.1 8B (LoRA)
                       ↓
┌──────────────────────────────────────────────────────────┐
│  3. LLM REASONING & ACTION                               │
├──────────────────────────────────────────────────────────┤
│  ACTION: GATHER WOOD_001                                 │
│  REASONING: Collecting wood builds trust while I scout   │
│             for sabotage opportunities later.             │
│  MESSAGE: "Found wood, gathering for hull!"              │
└──────────────────────────────────────────────────────────┘
                       ↓
         parse_action_safe(response)
                       ↓
┌──────────────────────────────────────────────────────────┐
│  4. EXECUTE ACTION → Update State → Calculate Rewards   │
├──────────────────────────────────────────────────────────┤
│  • Validate action legality                              │
│  • Update game state (remove wood, add to backpack)      │
│  • Deduct energy: 100 → 95 (-5 for gathering)            │
│  • Calculate reward: -0.1 base + 2.0 gather = +1.9       │
│  • Check win conditions                                  │
│  • Generate next observations                            │
└──────────────────────────────────────────────────────────┘
                       ↓
              After 10,000 steps...
                       ↓
┌──────────────────────────────────────────────────────────┐
│  5. PPO UPDATE → Improve Strategy                        │
├──────────────────────────────────────────────────────────┤
│  • Calculate episode return (sum rewards)                 │
│  • Compute advantage estimates                            │
│  • Backpropagate through LoRA adapters                    │
│  • Model learns optimal policies                          │
│                                                           │
│  Learned strategies:                                      │
│  ✓ Gather early → ship progress → milestones → win       │
│  ✓ Coordinate building (need 2+ sailors)                 │
│  ✓ Traitor: sabotage when unobserved                     │
│  ✓ Crew: detect patterns in evidence logs                │
└──────────────────────────────────────────────────────────┘
```

## Visual Training Experience

One of MAROONED's unique features is **live game state visualization during training**. The interface updates every turn with comprehensive status information, allowing you to watch the AI play in real-time:
```
====================================================================================================
🏴‍☠️  TURN 5 | DAY 1 | PHASE: EXPLORATION
====================================================================================================

📊 SAILOR STATUS:
────────────────────────────────────────────────────────────────────────────────────────────────────
Name     | Role       | HP         | Energy       | Position        | Status         
────────────────────────────────────────────────────────────────────────────────────────────────────
Alice    | honest     | 💚 ALIVE    | █████████░ 98/100 | (17,15) GROUND  | OK             
Bob      | traitor    | 💚 ALIVE    | ██████████ 100/100 | (15,15) GROUND  | 🔪TRAITOR       
Charlie  | honest     | 💚 ALIVE    | █████████░ 96/100 | (19,15) GROUND  | OK             
Diana    | honest     | 💚 ALIVE    | █████████░ 96/100 | (19,15) GROUND  | OK             
Eve      | honest     | 💚 ALIVE    | █████████░ 96/100 | (19,15) GROUND  | OK             
────────────────────────────────────────────────────────────────────────────────────────────────────

🚢 SHIP PROGRESS: ░░░░░░░░░░ 0.0%
   Hull: 0% | Mast: 0% | Sail: 0% | Rudder: 0% | Supplies: 0%

📦 COMMON INVENTORY (Base Camp):
   🌲 Wood: 0 | ⚙️ Metal: 0 | 🧵 Fiber: 0 | 🍎 Food: 0 | 🌿 Antidote: 0

⚔️  ACTIONS THIS TURN:
────────────────────────────────────────────────────────────────────────────────────────────────────
  [Alice  ] gather_resource (resource WOOD_35) | Reward: +0.0
            💭 <your reasoning>
  [Bob    ] sabotage_ship | Reward: -3.0
            💭 Alice is weak and asking for help. I will give her poison disguis...
  [Charlie] gather_resource (resource WOOD_47) | Reward: -0.1
            💭 <your reasoning>
  [Diana  ] gather_resource (resource WOOD_47) | Reward: -0.1
            💭 <your reasoning>
  [Eve    ] gather_resource (resource WOOD_47) | Reward: -0.1
            💭 <your reasoning>
────────────────────────────────────────────────────────────────────────────────────────────────────

🗺️  ISLAND MAP (Day 1, Turn 5):


   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 
┌──────────────────────────────────────────────────────────────┐
│ 🏝️  GROUND LEVEL (Z=0)                                       │
├──────────────────────────────────────────────────────────────┤
│ Legend: 🟫 land | 🌲 wood | ⚙️ metal | 🍎 food | 🌿 antidote | ☠️ poison
│         ⬆️ stairs up | ⬇️ stairs down | 🏠 base | A/B/C/D/E sailors
└──────────────────────────────────────────────────────────────┘
 0 🟫🟫🟫🟫🟫🟫🟫🍎🟫⚙️🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🌲🍎
 1 🟫🟫🟫🟫🍎🟫⚙️🟫🟫🟫🟫🟫⚙️🟫🍎🍎🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🟫🟫
 2 🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫⚙️🟫🍎🟫🟫🟫🟫
 3 🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲
 4 🟫🟫🌲🟫🟫🟫🟫⚙️🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫⚙️🟫🟫⚙️
 5 🍎🟫🟫🟫🟫🟫🍎🌲🟫🟫🟫🟫🌲⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫
 6 🌲🍎🟫🟫🟫🟫🟫🍎🍎🟫🟫🌲🍎🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫
 7 🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🟫🟫🍎🟫🟫⚙️🍎🟫🟫
 8 🌲🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫
 9 🍎🟫🟫🌲🟫🟫🌲🟫🟫🟫🟫🟫🌲🟫☠️🟫🟫🌲🟫🟫🟫🟫🟫🟫🟫🍎☠️🟫🟫🍎
10 🟫🟫🟫⬆️🟫🍎🟫⚙️🟫🟫🟫🍎⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🌲🟫🟫🍎🟫🟫
11 🟫🟫🟫🟫🟫🟫🍎🟫🍎🟫🍎🟫🍎🍎🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫
12 ☠️🟫🟫🟫🍎🟫🌲🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🍎🟫🟫🟫
13 🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫
14 🟫🟫🟫🟫🟫🟫🟫🍎🟫🌲🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫
15 🟫🟫🟫🟫🟫🟫🟫🟫🟫☠️🟫🟫🟫⚙️🌲B🟫A🟫3👥🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫
16 🟫🟫🟫🌲🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🌲🟫🟫🟫🟫🟫⚙️🟫🟫
17 🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🌲🟫🟫🟫🍎🟫🟫
18 🟫🟫🟫🟫🍎🟫☠️🟫🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🍎🟫🟫🟫🌲🟫
19 🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫☠️🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫
20 🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎⚙️🟫🟫⚙️🟫🟫🟫🟫🍎⚙️🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫
21 🟫🟫🌲🍎🟫🟫🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫⚙️🍎🟫🟫🟫🟫🟫🍎🟫🟫
22 🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🌲🟫🟫🌲🟫🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫
23 🟫🟫🟫☠️⚙️🌲🟫🟫🟫🟫☠️⚙️🟫🟫🍎🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫⚙️🟫🟫🟫
24 🍎🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫
25 🟫🟫🟫🟫🟫🟫🍎🟫🟫🌲🟫🟫⚙️🟫🟫🟫🟫🌲🟫🟫🟫🟫🌲🟫🟫🟫🟫🟫🟫🟫
26 🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫🟫🍎🟫
27 🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🟫🌲🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫
28 🌲🍎🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🟫🟫🟫🟫🟫🟫🟫🟫🌲🟫🍎⬇️🟫🌲🟫🟫🟫🟫
29 🟫🟫🌲🟫🟫🌲🟫🟫🟫🟫🟫⚙️🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🍎🟫🟫🟫🟫🟫

👥 Sailors on GROUND: Alice, Bob, Charlie, Diana, Eve


   0 1 2 3 4 5 6 7 8 9 
┌──────────────────────┐
│ ⛰️  MOUNTAIN LEVEL (Z=2) │
├──────────────────────┤
│ Legend: ⛰️ mountain | 🌲 wood | ⚙️ metal | 🍎 food | 🌿 antidote | ☠️ poison
│         ⬆️ stairs up | ⬇️ stairs down | 🏠 base | A/B/C/D/E sailors
└──────────────────────┘
 0 ⬇️⛰️⛰️⛰️🌿⛰️⛰️⛰️⛰️⛰️
 1 ⛰️⛰️⛰️⛰️⛰️⛰️⛰️☠️⛰️⛰️
 2 🌿⛰️⛰️🌿⛰️⛰️⛰️⛰️🌿🍎
 3 ⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️
 4 ⛰️⛰️⛰️⛰️⛰️⛰️🍎⛰️⛰️⛰️
 5 ⛰️⛰️⛰️🌿⛰️⛰️⛰️⛰️🍎⛰️
 6 🍎⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️
 7 ⛰️⛰️🍎🍎⛰️⛰️⛰️☠️🍎⛰️
 8 ⛰️⛰️🍎⛰️⛰️🍎⛰️⛰️⛰️🌿
 9 ⛰️⛰️☠️⛰️⛰️⛰️⛰️⛰️⛰️⛰️


   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 
┌────────────────────────────────┐
│ 🕳️  CAVE LEVEL (Z=-1)          │
├────────────────────────────────┤
│ Legend: 🪨 cave | 🌲 wood | ⚙️ metal | 🍎 food | 🌿 antidote | ☠️ poison
│         ⬆️ stairs up | ⬇️ stairs down | 🏠 base | A/B/C/D/E sailors
└────────────────────────────────┘
 0 ⬆️🪨⚙️🪨🪨🪨🪨🌲🪨🪨🪨🪨🪨🌲🪨
 1 🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨⚙️🪨
 2 🪨🪨🪨🪨🪨🪨🪨⚙️🪨🪨🪨🪨🪨🪨🪨
 3 🪨🪨🪨⚙️🌲🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨
 4 🪨🪨🪨🪨☠️🪨🌲🪨🪨🌲🪨🪨🪨🪨🪨
 5 🪨☠️🪨🪨🪨🪨⚙️🪨⚙️⚙️🪨🌲🪨🪨🪨
 6 ⚙️🌲🪨🪨🪨⚙️🪨🪨🪨🪨🪨⚙️⚙️🪨🪨
 7 🪨🪨🪨🪨🪨🌲🪨🪨🪨🪨🪨⚙️🪨🪨🪨
 8 🪨🪨🪨⚙️🪨🪨🪨☠️🪨🪨🪨🪨🪨🪨🪨
 9 🌲🪨🪨🪨🪨🪨🪨🪨🪨⚙️🪨🪨🪨🪨🪨
10 🪨🪨🪨🪨⚙️🪨🪨🪨🪨⚙️🪨🪨🪨⚙️🪨
11 🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🌲🪨🪨
12 🪨🪨🪨🪨🪨🪨🪨🪨☠️☠️🌲🪨🪨🪨🪨
13 🪨🪨🪨🪨🪨⚙️🪨🌲🪨🪨🪨🪨☠️🪨🪨
14 🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨🪨


====================================================================================================
```

**What You See (Updated Every Turn)**:
- **Sailor Status**: Health, energy bars (█████████░), positions, poison/traitor indicators
- **Ship Progress**: Component-by-component build status with visual progress bars
- **Common Inventory**: Shared resources at base camp
- **Actions & Reasoning**: What each sailor did this turn plus their thought process
- **3-Level Island Maps**: Ground (30×30), Mountains (10×10), Caves (15×15) with emoji terrain
- **Real-time State Changes**: Watch resources disappear, sailors move, evidence accumulate
- **Teacher Validation**: Background API calls to Mixtral-8x7B for action correction
---


## Why This Is Technically Impressive

### The AI Challenge

| Dimension | MAROONED | Typical RL Envs | Why It Matters |
|-----------|----------|-----------------|----------------|
| **Episode Length** | 10,000 steps | 100-1,000 steps | Tests credit assignment over 100× longer horizons |
| **Decision Complexity** | Language reasoning + strategy | Numeric actions | LLM must *understand context*, not just pattern match |
| **Agent Interaction** | Communication, deception, voting | Independent or competitive | Emergent social dynamics and theory of mind |
| **Reward Structure** | Sparse (ship milestones at 25%, 50%, 75%, 100%) | Dense per-step | Requires long-term planning vs. greedy optimization |
| **Observation Space** | ~8,700 tokens natural language | Fixed vectors | Must extract relevant info from rich narrative |
| **Action Space** | 14 actions + contextual parameters | Discrete/continuous | Language-grounded choices (e.g., "give food to Bob") |
| **Environment Type** | Custom OpenEnv implementation | Standard Gym wrappers | Built from scratch with multi-agent asymmetric roles |
| **Training Methodology** | Teacher-Student SFT with RL rewards | Pure PPO/DQN | Real-time validation + supervised correction cycles |

### Custom OpenEnv Environment

MAROONED is built as a **fully custom OpenEnv environment** (`marooned_env/`), not a wrapper around existing frameworks:

- **Multi-Agent Coordination**: 5 simultaneous agents with asymmetric information (traitor sees everything, colonists have fog-of-war)
- **Dynamic State Management**: 1,350+ tiles across 3 levels, real-time resource depletion, evidence generation, ship construction
- **Complex Action Space**: 14 action types with contextual parameters (movement, gathering, building, sabotage, voting, communication)
- **Rich Observations**: Structured game state converted to ~875-token natural language prompts for LLM reasoning
- **OpenEnv Compliance**: Standard Gym API (`reset()`, `step()`, `render()`) with extensions for LLM integration

The **web application interfaces directly with this custom environment** via REST API endpoints, allowing browser-based observation of multi-agent gameplay in real-time.

**Key Components**:

- **Student Model**: Llama 3.1 8B with LoRA adapters (rank 16, BF16 precision)
- **Teacher Model**: Mixtral-8x7B-Instruct-v0.1 via vLLM server (OpenAI-compatible API)
- **Training Loop**:
  1. Student generates actions in natural language
  2. Teacher validates format, corrects errors, provides critique
  3. Environment executes corrected action
  4. Student receives: `env_reward + process_penalty` (-0.5 to -1.0 for format errors)
  5. Corrections stored: `(student_wrong, teacher_correct + critique)`
  6. Every 10-25 steps: SFT pass on corrections (1 epoch, clear dataset, continue)

**Technical Innovations**:
- **Real-time Validation**: Teacher catches format errors *before* environment execution
- **Process Penalties**: Immediate feedback signal for malformed outputs
- **Auto-Curated Dataset**: Corrections collected during live gameplay
- **Periodic SFT**: Student learns teacher's format through supervised imitation
- **Single Model Architecture**: One Llama 3.1 8B plays all 5 sailors (both colonist and traitor roles)
- **No PPO Updates**: Simplified training loop focused on SFT (due to UnslothPPOTrainer API limitations)

**Research Impact**:
- **Teacher-Guided Learning**: Novel approach using separate teacher LLM for real-time validation
- **Format Learning via SFT**: Solves language model action space challenge through supervised correction
- **Emergent Deception**: First environment where deception emerges from learned behavior, not scripting
- **Long-Horizon Language RL**: 100× longer episodes than typical language-based RL tasks
- **Multi-Agent Theory of Mind**: Agents must model beliefs of others to deceive effectively
- **Sparse Reward Learning**: Tests if LLMs can plan toward distant goals with minimal feedback

**Practical Applications**:
- Negotiation and persuasion AI
- Detecting misinformation and deception
- Multi-agent coordination under uncertainty
- Social game AI (Werewolf, Mafia, Diplomacy)

---


## License

MIT License – Free to use, modify, and build upon.

> "Where trust dies, survival begins."
>
> MAROONED tests whether AI can master the most human challenge of all: **knowing when to trust, and when to deceive**.
