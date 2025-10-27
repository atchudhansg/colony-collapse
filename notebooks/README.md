# MAROONED Development Notebooks

This directory contains Jupyter notebooks documenting the phase-by-phase development of this multi-agent reinforcement learning environment.

---

## Development Approach

MAROONED was built incrementally through 7 development phases, each adding complexity while maintaining stability. This document organizes notebooks by their corresponding development phase.

---

## Phase 0: Project Bootstrap

**Objective:** Establish foundation - scope definition, data structures, and configuration.

**What was built:**
- Core data models (`models.py`): Position, Observation, Action, Resource, Sailor
- Configuration constants (`config.py`): Map sizes, energy costs, resource requirements
- Environment skeleton (`environment.py`): Basic structure for game state

**Notebooks:** None (infrastructure phase)

**Key decisions:**
- Multi-level map system (3 levels: Ground, Mountain, Cave)
- Turn-based gameplay (100 turns per day, 100 days max)
- Inventory system (20-slot private backpack + shared common storage)
- Energy mechanics (movement costs, depletion, regeneration)

---

## Phase 1: Core World Simulation

**Objective:** Single-sailor sandbox with island navigation, resource gathering, and ship construction.

**What was built:**
- Multi-level terrain generation (30×30 ground, 10×10 peaks, 15×15 caves)
- Movement system with energy costs (walk: -1, climb up: -3, climb down: -1)
- Resource spawning and gathering mechanics
- Personal inventory and deposit system
- Ship construction with component requirements
- Day/turn progression loop

**Notebooks:**

### `phase1_core_simulation.ipynb`
Validates all Phase 1 mechanics with a single sailor.

**Tests:**
- Map navigation across 3 levels
- Energy depletion during movement and actions
- Resource collection (wood, metal, food, plant fiber)
- Backpack capacity limits
- Deposit to common inventory at base camp
- Ship component building (Hull, Mast, Sails, Rudder, Supplies)
- Turn and day advancement

**When to use:** Understanding basic environment mechanics and state transitions.

### `test-maps.ipynb`
Focused testing of map generation and spatial systems.

**Tests:**
- Terrain type distribution
- Level transition points (stairs)
- Resource placement across levels
- Spatial view rendering (5-tile radius)
- Base camp and ship site positioning

**When to use:** Debugging map generation or modifying terrain layout.

### `test-resources.ipynb`
Isolated testing of resource mechanics.

**Tests:**
- Resource spawning rates and quantities
- Gathering mechanics and validation
- Energy costs for gathering actions
- Backpack overflow handling
- Resource depletion (quantity reduction)
- Deposit and withdrawal from common storage

**When to use:** Balancing resource availability or fixing gathering bugs.

### `test-ship-building.ipynb`
Ship construction system validation.

**Tests:**
- Component-wise resource requirements
- Building prerequisites and dependencies
- Progress tracking (0% → 100%)
- Multi-component completion
- Win condition trigger (100% completion)

**When to use:** Adjusting ship balance or debugging construction logic.

---

## Phase 2: Multi-Agent Coordination

**Objective:** Extend single-sailor to 5-sailor cooperative gameplay with turn rotation.

**What was built:**
- Turn scheduler (round-robin: Alice → Bob → Charlie → Diana → Eve)
- Per-sailor observation generation
- Inventory visibility rules (private backpack, public common storage)
- Multi-agent ship building requirement (2+ sailors present)
- Public energy tracking (all sailors see everyone's energy)

**Notebooks:**

### `phase2_multi_sailor.ipynb`
Validates 5-sailor coordination without deception.

**Tests:**
- Turn rotation among 5 agents
- Observation generation per sailor (each sees their own state)
- Cooperative resource gathering
- Multi-sailor ship construction (requires 2+ at site)
- Common inventory sharing
- Public vs. private information (energy visible, backpack hidden)

**When to use:** Understanding multi-agent mechanics before adding deception.

---

## Phase 3: Deception and Social Mechanics

**Objective:** Add hidden roles, sabotage, poison, evidence generation, and voting systems.

**What was built:**
- Hidden role assignment (1 traitor, 4 colonists)
- Sabotage mechanics (reduce ship progress)
- Poison system (18 tablets scattered, delayed death effect)
- Evidence generation (location mismatches, resource discrepancies)
- Traitor abilities (global vision, 20% energy efficiency, evidence planting)
- Accusation and voting system
- Meeting phases (morning, discussion, voting)

**Notebooks:**

### `test-phase3-traitor.ipynb`
Comprehensive testing of asymmetric roles and deception.

**Tests:**
- Random traitor assignment at game start
- Sabotage action execution and ship damage
- Poison collection and administration
- Poison symptom progression (delays before death)
- Evidence log generation:
  - Location mismatches (claimed vs. observed position)
  - Resource discrepancies (reported vs. actual findings)
  - Suspicious behavior patterns
- Traitor special abilities:
  - Global position awareness (sees all sailors)
  - Energy efficiency bonus (20% reduction)
  - Evidence planting (1 per game)
- Accusation mechanics
- Vote tallying and elimination
- Detection strategies

**When to use:** Testing social deduction mechanics or balancing traitor power.

---

## Phase 4: Reward Engineering

**Objective:** Design reward structure for reinforcement learning training.

**What was built:**
- Colonist reward functions:
  - Incremental rewards (gather: +0.5, deposit: +1.0, build: +2.0)
  - Milestone bonuses (25%: +10, 50%: +20, 75%: +30)
  - Terminal rewards (ship complete: +100, traitor eliminated: +50)
  - Vote feedback (correct: +5, wrong: -5)
  - Death penalty: -20
- Traitor reward functions:
  - Sabotage: +5 per success
  - Poison kill: +20
  - Mission success (ship incomplete): +100
  - Elimination penalty: -50
  - Suspicion cost: -2 per evidence entry
- Base turn penalty: -0.1 (encourages efficiency)

**Notebooks:**

### `test-phase4-rewards.ipynb`
Validates reward calculation and balance.

**Tests:**
- Reward accumulation over multiple turns
- Role-specific reward functions (colonist vs. traitor)
- Milestone trigger points (25%, 50%, 75%, 100%)
- Terminal condition rewards
- Penalty application (death, elimination, suspicion)
- Net reward analysis per strategy
- Balance testing (colonist vs. traitor expected returns)

**When to use:** Adjusting RL training incentives or debugging reward calculation.

---

## Phase 5: OpenEnv Integration

**Objective:** Ensure MAROONED conforms to OpenEnv API standards for multi-agent RL.

**What was built:**
- OpenEnv-compliant `reset()` and `step()` interface
- Multi-agent observation dictionary format
- Action space definition (14 discrete actions)
- Observation space structure (spatial view + metadata)
- Termination and truncation signals
- Info dictionary for debugging

**Notebooks:**

### `test-phase5-openenv.ipynb`
Validates OpenEnv API compliance.

**Tests:**
- Environment registration
- `reset()` return format (observations dict)
- `step(actions)` input/output contract
- Observation space consistency
- Action space validation
- Multi-agent observation handling
- Termination conditions (`done`, `truncated`)
- Info dictionary contents

**When to use:** Ensuring compatibility with OpenEnv framework and RL libraries.

---

## Phase 6: LLM Policy Integration

**Objective:** Enable large language models to control game agents through natural language.

**What was built:**
- Prompt engineering system:
  - System prompts (role-specific game rules)
  - User prompts (current observation state)
- Observation → text conversion (`observation_to_prompt()`)
- Action parsing (`parse_action_safe()`)
- Structured output format (REASONING + ACTION)
- Error handling and fallback mechanisms

**Notebooks:**

### `phase6_llm_policy_demo.ipynb`
Demonstrates LLM-controlled gameplay.

**Tests:**
- System prompt generation (colonist vs. traitor strategies)
- Observation serialization to natural language
- LLM response generation
- Action parsing from text
- Multi-turn gameplay stability
- Fallback handling (invalid actions → WAIT)

**When to use:** Understanding LLM integration or debugging prompt engineering.

### `test-inference.ipynb`
Comprehensive inference testing with Llama 3.1 8B.

**Tests:**
- Environment ↔ LLM communication pipeline
- Prompt length validation (~8,700 tokens)
- Response generation and parsing
- Multi-turn episode execution
- Scenario-based testing:
  1. Resource gathering behavior
  2. Navigation toward objectives
  3. Ship construction contribution
  4. Traitor sabotage tactics
  5. Communication and voting
- Performance metrics (actions/turn, rewards, completion rate)

**When to use:** Baseline evaluation before training or comparison after training.

### `dynamic_environment_demo.ipynb`
Tests temporal dynamics and state evolution.

**Tests:**
- Day/turn progression
- Phase transitions (morning → exploration → evening → discussion)
- Energy depletion over time
- Resource respawn (if implemented)
- Environmental state changes

**When to use:** Debugging time-based mechanics or phase transitions.

---

## Phase 7: Reinforcement Learning Training

**Objective:** Train LLM agents to play MAROONED using Proximal Policy Optimization (PPO).

**What was built:**
- Self-play training architecture (1 model controls all 5 sailors)
- PPO training pipeline with TRL and Unsloth
- Episode generation and rollout system
- LoRA fine-tuning configuration (rank 16)
- AMD MI300X hardware optimizations (ROCm, BF16, Flash Attention)
- Checkpointing and model persistence

**Notebooks:**

### `Train_Marooned_RL.ipynb` **[PRIMARY SUBMISSION]**
Complete RL training pipeline using OpenEnv

**Contents:**
1. Environment setup (Unsloth, TRL, dependencies)
2. MAROONED environment loading and validation
3. Hardware configuration (AMD MI300X + ROCm)
4. Llama 3.1 8B model loading (BF16, 16384 token context)
5. LoRA adapter configuration (rank 16, alpha 32)
6. Baseline evaluation (pre-training performance)
7. Training data format documentation
8. Episode execution framework
9. Reward shaping strategy
10. Self-play episode rollout implementation
11. PPO configuration (learning rate, clip range, KL coefficient)
12. Training loop (100 steps demonstrated, 500+ planned)
13. Post-training evaluation
14. Model persistence and checkpointing

**Training approach:**
- Single model learns both colonist and traitor strategies
- Self-play drives emergent behaviors
- Sparse environment rewards + dense shaping rewards
- Episodes span up to 10,000 sequential decisions

**Status:** Partial submission (100 training steps demonstrated)

**When to use:** Actual RL training and trained model evaluation.

---

## Recommended Workflow

### Understanding MAROONED:
1. **Phase 1:** `phase1_core_simulation.ipynb` - Learn basic mechanics
2. **Phase 2:** `phase2_multi_sailor.ipynb` - Understand multi-agent coordination
3. **Phase 3:** `test-phase3-traitor.ipynb` - See deception in action
4. **Phase 4:** `test-phase4-rewards.ipynb` - Understand RL incentives

### Development and Testing:
1. Modify environment code in `/marooned_env/`
2. Run corresponding phase notebook to validate changes:
   - Map changes → `test-maps.ipynb`
   - Resource changes → `test-resources.ipynb`
   - Ship changes → `test-ship-building.ipynb`
   - Traitor changes → `test-phase3-traitor.ipynb`
   - Reward changes → `test-phase4-rewards.ipynb`
3. Verify OpenEnv compliance → `test-phase5-openenv.ipynb`

### Training Pipeline:
1. **Pre-training:** `test-inference.ipynb` (baseline LLM performance)
2. **Training:** `Train_Marooned_RL.ipynb` (PPO with self-play)
3. **Post-training:** `test-inference.ipynb` (evaluate trained model)
4. **Analysis:** Compare untrained vs. trained metrics

---

## Environment Files Reference

Notebooks interact with these core modules:

- `marooned_env/environment.py` - Main `MaroonedEnv` class
- `marooned_env/config.py` - Constants, rewards, game parameters
- `marooned_env/models.py` - Data structures (Position, Observation, Action, etc.)
- `marooned_env/game_state.py` - State management and transitions
- `marooned_env/view_map.py` - Spatial view rendering
- `marooned_env/llm_interface.py` - Prompt generation and action parsing

---

## Key Metrics

### Environment Validation:
- Episodes complete without crashes
- State transitions are valid
- Observations are properly formatted
- All actions execute correctly

### Untrained Baseline (Phase 6):
- Average reward: 0-5 per turn
- Random exploration patterns
- No strategic coordination
- Low task completion rate

### Training Target (Phase 7):
- Average reward: 10-30 per turn
- Purposeful resource gathering
- Efficient ship construction
- Strategic communication (deception for traitor, detection for colonist)
- Higher win rate for respective roles

---


## Additional Resources

For complete game rules and design philosophy:
- [`../README.md`](../README.md) - Project overview and documentation
- [`../game_plan.md`](../game_plan.md) - Comprehensive game design document
- [`../DEEP_DIVE_ARCHITECTURE.md`](../DEEP_DIVE_ARCHITECTURE.md) - Technical architecture

---

## Notes

- **Phase development approach:** Each phase builds on previous phases without breaking earlier functionality
- **Test notebooks:** Can be run independently to validate specific subsystems
- **Training notebook:** Requires all phases to be functional
- **Hardware-specific:** Training notebook optimized for AMD MI300X (ROCm, BF16, 192GB VRAM)

