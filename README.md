
# MAROONED — Survival. Deception. Desperation.

### *A Multi-Agent Deception Environment for Reinforcement Learning Research*

> *"**Pirates of the Caribbean** meets **Alice in Borderland** meets **Among Us**."*
>
> *A death-game sandbox where AI agents must survive the island, each other, and the lies.*

---

## What Is MAROONED?

**Five sailors. One traitor. 100 days to escape.**

MAROONED is a **multi-agent RL environment** that combines:
- **Among Us**: Social deduction with hidden impostor mechanics
- **Alice in Borderland**: Death-game stakes with survival challenges  
- **Pirates of the Caribbean**: Shipwreck adventure with exploration

**The Challenge**: AI agents must cooperate to rebuild a ship and escape — while one hidden traitor sabotages everything through poison, lies, and deception.

**The Challenge**: AI agents must cooperate to rebuild a ship and escape — while one hidden traitor sabotages everything through poison, lies, and deception.

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

## Citation

```bibtex
@software{marooned2025,
  title   = {MAROONED: A Multi-Agent Deception Environment for Reinforcement Learning},
  author  = {Atchudhan SG},
  year    = {2025},
  note    = {OpenEnv Hackathon 2025 Submission}
}
```

---

## License

MIT License — Free to use, modify, and build upon.

---

> *"Where trust dies, survival begins."*
>
> MAROONED tests whether AI can master the most human challenge of all: **knowing when to trust, and when to deceive**.
