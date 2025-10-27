
# MAROONED — Survival. Deception. Desperation.

### *A Multi-Agent Deception Environment for Reinforcement Learning Research*

> *"**Pirates of the Caribbean** meets **Alice in Borderland** meets **Among Us**."*
>
> *A death-game sandbox where AI agents must survive the island, each other, and the lies.*

<div align="center">
  <img src="https://miro.medium.com/v2/resize:fit:1400/0*c5_m_uaIMUKVK-P_.png" alt="MAROONED Poster" width="800"/>
</div>

---

## What Is MAROONED?

**The Scenario**: Five sailors shipwrecked on a mysterious island. Their ship is destroyed — **100 days to rebuild it or die here**. But one sailor is secretly working *against* the group. Everyone knows there's a traitor among them from Day 1. **Survive. Build. Deceive. Escape.**

### As a Colonist (4 Players)

**Your Goal**: Rebuild the ship to 100% completion and escape together.

**What You Can Do**:
- **Explore**: Navigate 3-level island (Ground, Mountains, Caves) to find wood, metal, food, antidote herbs
- **Gather & Build**: Collect resources, deposit into shared inventory, construct 5 ship components (Hull → Mast → Sail → Rudder → Supplies)
- **Manage Energy**: Eat food to restore energy (100 max), plan efficient routes to avoid exhaustion
- **Detect Lies**: Compare what sailors *say* vs what they *do* (location mismatches, missing resources, poison sightings)
- **Vote & Eliminate**: Hold democratic votes to eject the traitor — correct vote = instant win; wrong vote = one less helper
- **Coordinate**: Limited communication (1 message per 10 turns during exploration), must trust but verify

**Your Challenge**: You only see **5-tile radius** around you. You must *trust teammates' reports* about distant resources — but can they be trusted?

### As a Traitor (1 Player)

**Your Goal**: Prevent escape by sabotage, deception, and murder.

**What You Can Do**:
- **See Everything**: Global vision — track all sailors' positions in real-time across entire island
- **20% Energy Bonus**: Move farther and work longer than colonists (efficiency advantage)
- **Sabotage Ship**: Secretly reduce ship component progress by 30% when alone
- **Poison Sailors**: Feed poison-laced food (3-day delayed death), frame others for the murder
- **Lie Strategically**: Report false resource locations, claim you gathered 15 wood but only deposit 5, fake your position
- **Plant Evidence**: One-time ability to frame an innocent sailor (make them look like the traitor)
- **Hide Items**: Conceal up to 2 inventory items when inspected

**Your Challenge**: Blend in as a helpful crew member while secretly delaying progress. If caught — you lose. If ship incomplete by Day 100 or <3 sailors alive — you win.

---

## Core Mechanics

### Game Structure
- **100 days** to rebuild ship (10,000 turns total)
- **4 phases per day**: Morning Meeting → Exploration → Evening Return → Voting
- **Multi-level island**: Ground (30×30), Mountains (10×10), Caves (15×15)
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

## Why This Is Technically Impressive

### The AI Challenge

| Dimension | MAROONED | Typical RL Envs | Why It Matters |
|-----------|----------|-----------------|----------------|
| **Episode Length** | 10,000 steps | 100-1,000 steps | Tests credit assignment over 100× longer horizons |
| **Decision Complexity** | Language reasoning + strategy | Numeric actions | LLM must *understand context*, not just pattern match |
| **Agent Interaction** | Communication, deception, voting | Independent or competitive | Emergent social dynamics and theory of mind |
| **Reward Structure** | Sparse (ship milestones at 25%, 50%, 75%, 100%) | Dense per-step | Requires long-term planning vs. greedy optimization |
| **Observation Space** | ~8,700 tokens natural language | Fixed vectors | Must extract relevant info from rich narrative |
| **Action Space** | 14 actions × contextual parameters | Discrete/continuous | Language-grounded choices (e.g., "give food to Bob") |

### The Training Architecture

**Self-Play with Single Model**: One Llama 3.1 8B controls all 5 sailors (colonists + traitor)

```
Episode → Assign Roles → 10,000 Steps → Collect Experience → PPO Update
   ↓          ↓              ↓                ↓                    ↓
 Day 1     1 Traitor    ENVIRONMENT      Observation         LoRA Adapters
          4 Colonists   generates:       (~8.7k tokens)      Fine-tune
                        • State               ↓              attention
                        • Evidence        LLM outputs:        layers
                        • Progress        • Reasoning
                                         • Action
                                              ↓
                                         Sparse Rewards:
                                         +0.5 gather, +10 milestone
                                         +100 win, -20 death
```

**Technical Stack**:
- **Model**: Llama 3.1 8B (4-bit quantized, 16K context)
- **Training**: PPO with LoRA (rank 16) on AMD MI300X
- **Observation**: 15+ structured fields → ~875 token prompt
- **Self-Play**: Single model learns cooperative + deceptive strategies

---

## OpenEnv API Compliance

MAROONED implements the **OpenEnv** standard for custom RL environments, making it compatible with any RL training framework (TRL, CleanRL, RLlib, etc.).

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
prompt = env.observation_to_prompt(obs, role)  # Convert state → LLM input
```

### Multi-Agent Design

Unlike single-agent environments, MAROONED manages **5 simultaneous agents** with:
- **Asymmetric roles**: Traitor gets different observations (global vision, energy bonus)
- **Structured actions**: `{"sailor_id": "alice", "action": "GATHER", "target": "WOOD_001"}`
- **Per-agent rewards**: Colonists maximize ship progress, traitor maximizes sabotage
- **Episode termination**: Ship 100% OR <3 sailors alive OR Day 100 timeout

### What Agents Can Access (Dynamic Environment)

**Vision & Maps**:
- **Colonists**: 11×11 tile grid centered on position (limited fog-of-war)
- **Traitor**: Global 30×30+ map view (sees all sailor positions in real-time)
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
- No scripted events — deception emerges from learned behavior
- 1,350+ tiles × 5 agents × 20 inventory slots = billions of unique configurations

### Why OpenEnv?

**Standardization**: Drop-in replacement for any Gym-compatible trainer (no custom wrappers needed)

**Flexibility**: Swap in different LLMs (GPT-4, Claude, Gemini) by changing `observation_to_prompt()` only

**Reproducibility**: Seeded environments for deterministic evaluation and ablation studies

---

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

### Training Progression (Sample Output)

```
Step 1/100 | Reward: -5.2 | Avg(10): -5.2 | Turns: 87 | Time: 12.3s
   📝 Alice (TRAITOR): move_east → sabotage_ship → send_message
   📝 Bob (COLONIST): move_north → gather_resource → wait
   ⚠️  Parse failures: 34% (model hallucinates invalid actions)

Step 50/100 | Reward: +12.4 | Avg(10): +8.7 | Turns: 134 | Time: 15.1s
   📝 Alice: Sabotages ONLY when alone (no witnesses)
   📝 Colonists: Coordinate gathering (Charlie→Diana deposit chain)
   💾 Checkpoint saved → outputs_marooned_rl/checkpoint_step50
   
Step 100/100 | Reward: +28.6 | Avg(10): +22.3 | Turns: 189 | Time: 18.4s
   ✅ Ship progress: 15% → 42% (learned milestone rewards)
   ✅ Parse failures: 34% → 8% (action space mastery)
   ✅ Strategy emergence: Traitor blends in, crew detects lies
```

**Key Observations**:
- **Reward progression**: Negative early (random exploration) → positive later (goal-directed behavior)
- **Turn efficiency**: Agents survive longer as they learn energy management and avoid death
- **Action diversity**: From 60% WAIT actions → balanced mix of GATHER/BUILD/SABOTAGE
- **Emergent deception**: Traitor learns to gather resources publicly, sabotage when unobserved
- **Social reasoning**: Crew learns to correlate evidence logs with sailor positions

---

## Quick Start

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

**Training Pipeline**: See `notebooks/Train_Marooned_RL.ipynb` for complete PPO setup with Llama 3.1 8B.

---

## Project Structure

```
marooned_env/          # Core environment
├── environment.py     # OpenEnv-compatible RL environment
├── game_state.py      # Game logic and mechanics
├── models.py          # Data schemas (Observation, Action)
├── config.py          # Constants and parameters
└── llm_interface.py   # LLM prompt generation

notebooks/
├── Train_Marooned_RL.ipynb        # Main training pipeline
├── phase6_llm_policy_demo.ipynb   # LLM integration demo
└── test-*.ipynb                   # Validation notebooks
```

---

## Why This Matters

**Research Impact**:
- **Emergent Deception**: First environment where deception emerges from RL, not scripting
- **Long-Horizon Language RL**: 10× longer than typical language-based RL tasks
- **Multi-Agent Theory of Mind**: Agents must model beliefs of others to lie effectively
- **Sparse Reward Learning**: Tests if LLMs can plan toward distant goals

**Practical Applications**:
- Negotiation and persuasion AI
- Detecting misinformation and deception
- Multi-agent coordination under uncertainty
- Social game AI (Werewolf, Mafia, Diplomacy)

---

---

## License

MIT License — Free to use, modify, and build upon.

---

> *"Where trust dies, survival begins."*
>
> MAROONED tests whether AI can master the most human challenge of all: **knowing when to trust, and when to deceive**.
