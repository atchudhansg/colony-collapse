# `notebooks/` — Development & Training Documentation

**Phase-by-phase development notebooks showing environment evolution from basic mechanics to full RL training.** Organized chronologically through 7 phases, each notebook validates specific subsystems before integration.

---

## Phase Structure

### Phase 0: Bootstrap
- Core data models, config constants, environment skeleton
- **No notebooks** (infrastructure only)

### Phase 1: Core Simulation
**Goal**: Single-sailor sandbox with navigation, gathering, ship building

**Notebooks**:
- `phase1_core_simulation.ipynb` — Full mechanics validation (movement, energy, resources, construction)
- `test-maps.ipynb` — Map generation (3 levels, terrain, stairs)
- `test-resources.ipynb` — Resource spawning and gathering
- `test-ship-building.ipynb` — Construction system (5 components, dependencies)

### Phase 2: Multi-Agent
**Goal**: Extend to 5 sailors with turn rotation and coordination

**Notebooks**:
- `phase2_multi_sailor.ipynb` — 5-agent mechanics (turn scheduler, observations, cooperative building)

### Phase 3: Deception
**Goal**: Hidden roles, sabotage, poison, evidence, voting

**Notebooks**:
- `test-phase3-traitor.ipynb` — Asymmetric roles (sabotage, poison, evidence logs, global vision, voting)

### Phase 4: Reward Engineering
**Goal**: RL reward structure (incremental, milestone, terminal)

**Notebooks**:
- `test-phase4-rewards.ipynb` — Reward validation (colonist vs traitor incentives, balance testing)

### Phase 5: OpenEnv API
**Goal**: Standard Gym interface compliance

**Notebooks**:
- `test-phase5-openenv.ipynb` — API contract (`reset()`, `step()`, observations, actions, termination)

### Phase 6: LLM Integration
**Goal**: Natural language control via LLM prompts

**Notebooks**:
- `phase6_llm_policy_demo.ipynb` — LLM gameplay (prompt generation, action parsing, fallback handling)
- `test-inference.ipynb` — Llama 3.1 8B baseline evaluation (~8,700 token prompts)
- `dynamic_environment_demo.ipynb` — Temporal dynamics (day/turn progression, phase transitions)

### Phase 7: RL Training
**Goal**: PPO training with self-play

**Notebooks**:
- **`Train_Marooned_RL.ipynb`** — **[PRIMARY SUBMISSION]** Complete training pipeline:
  - Llama 3.1 8B with LoRA (rank 16, BF16)
  - AMD MI300X optimizations (ROCm, Flash Attention)
  - Self-play architecture (1 model controls all 5 sailors)
  - 100 training steps demonstrated (~30-60 min)

---

## Quick Reference

| Task | Notebook |
|------|----------|
| **Understand basic mechanics** | `phase1_core_simulation.ipynb` |
| **See multi-agent coordination** | `phase2_multi_sailor.ipynb` |
| **Test deception/traitor** | `test-phase3-traitor.ipynb` |
| **Debug map generation** | `test-maps.ipynb` |
| **Validate rewards** | `test-phase4-rewards.ipynb` |
| **Check OpenEnv compliance** | `test-phase5-openenv.ipynb` |
| **Baseline LLM performance** | `test-inference.ipynb` |
| **Run RL training** | `Train_Marooned_RL.ipynb` |

---

## Training Results (Phase 7)

**Untrained Baseline**:
- Average reward: 0-5 per turn
- Random exploration, no coordination
- Parse failures: 34% (hallucinates invalid actions)

**After 100 Training Steps**:
- Average reward: 22.3 per turn
- Strategic gathering → deposit → build sequences
- Parse failures: 8% (action space mastery)
- Ship progress: 15% → 42% (milestone learning)
- Emergent deception: Traitor sabotages only when alone

---

## Development Workflow

1. **Modify** environment code in `/marooned_env/`
2. **Validate** with phase-specific notebook:
   - Map changes → `test-maps.ipynb`
   - Traitor mechanics → `test-phase3-traitor.ipynb`
   - Rewards → `test-phase4-rewards.ipynb`
3. **Verify** OpenEnv compliance → `test-phase5-openenv.ipynb`
4. **Train** with `Train_Marooned_RL.ipynb`

---

> **Incremental development philosophy**: Each phase builds on previous phases without breaking earlier functionality. Test notebooks validate subsystems independently before integration.

