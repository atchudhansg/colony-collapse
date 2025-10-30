# `notebooks/`  Development & Training Documentation

**Phase-by-phase development notebooks showing environment evolution from basic mechanics to full RL training.** Organized chronologically through 7 phases, each notebook validates specific subsystems before integration.

---

## Phase Structure

### Phase 0: Bootstrap
- Core data models, config constants, environment skeleton
- **No notebooks** (infrastructure only)

### Phase 1: Core Simulation
**Goal**: Single-sailor sandbox with navigation, gathering, ship building

**Notebooks**:
- `phase1_core_simulation.ipynb`  Full mechanics validation (movement, energy, resources, construction)
- `test-maps.ipynb`  Map generation (3 levels, terrain, stairs)
- `test-resources.ipynb`  Resource spawning and gathering
- `test-ship-building.ipynb`  Construction system (5 components, dependencies)

### Phase 2: Multi-Agent
**Goal**: Extend to 5 sailors with turn rotation and coordination

**Notebooks**:
- `phase2_multi_sailor.ipynb`  5-agent mechanics (turn scheduler, observations, cooperative building)

### Phase 3: Deception
**Goal**: Hidden roles, sabotage, poison, evidence, voting

**Notebooks**:
- `test-phase3-traitor.ipynb`  Asymmetric roles (sabotage, poison, evidence logs, global vision, voting)

### Phase 4: Reward Engineering
**Goal**: RL reward structure (incremental, milestone, terminal)

**Notebooks**:
- `test-phase4-rewards.ipynb`  Reward validation (colonist vs traitor incentives, balance testing)

### Phase 5: OpenEnv API
**Goal**: Standard Gym interface compliance

**Notebooks**:
- `test-phase5-openenv.ipynb`  API contract (`reset()`, `step()`, observations, actions, termination)

### Phase 6: LLM Integration
**Goal**: Natural language control via LLM prompts

**Notebooks**:
- `phase6_llm_policy_demo.ipynb`  LLM gameplay (prompt generation, action parsing, fallback handling)
- `test-inference.ipynb`  Llama 3.1 8B baseline evaluation (~8,700 token prompts)
- `dynamic_environment_demo.ipynb`  Temporal dynamics (day/turn progression, phase transitions)

### Phase 7: RL Training
**Goal**: Teacher-guided learning with SFT corrections

**Notebooks**:
- **`Train_Marooned_RL_Clean.ipynb`**  **[PRIMARY SUBMISSION]** Complete training pipeline:
  - **Student**: Llama 3.1 8B with LoRA (rank 16, BF16)
  - **Teacher**: Mixtral-8x7B-Instruct via vLLM server (OpenAI-compatible API)
  - **Training Strategy**: Real-time validation + periodic SFT (no PPO due to API limitations)
  - **Architecture**: Teacher validates student outputs, corrects format errors, provides process penalties
  - **SFT Passes**: Every 10-25 steps when corrections  10
  - AMD MI300X optimizations (ROCm, Flash Attention)
  - Self-play architecture (1 model controls all 5 sailors)
  - Visualization support (game state rendering during training)

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
| **Run RL training** | `Train_Marooned_RL_Clean.ipynb` |

---

## Training Strategy (Phase 7)

### Teacher-Guided Learning Architecture

**Problem**: Untrained LLMs struggle with action format (30-40% parse failures), wasting training episodes learning syntax instead of strategy.

**Solution**: Use a separate teacher model (Mixtral-8x7B via vLLM) to validate and correct student outputs in real-time:

```
Student (Llama 3.1 8B)  Generates action
    
Teacher (vLLM Mixtral-8x7B)  Validates + Corrects + Critiques
    
Environment  Executes corrected action
    
Student receives: env_reward + process_penalty (-0.5 to -1.0 for errors)
    
Collect corrections: (student_wrong, teacher_correct + critique)
    
Every 10-25 steps: SFT pass on corrections  Clear dataset  Continue
```

**Expected Results**:
- Parse failures: 30-40%  <5% after first SFT pass
- Faster convergence: Student focuses on strategy, not syntax
- Better final policies: Less time wasted on format debugging

### Training Results

**Untrained Baseline**:
- Average reward: Negative (random exploration, frequent deaths)
- Parse failures: 30-40% (invalid action formats)
- No coordination between sailors

**After Teacher-Guided Training**:
- Parse failures: <5% (teacher corrections embedded via SFT)
- Strategic behavior emerges faster (gathering  depositing  building chains)
- Traitor learns to blend in (sabotage only when unobserved)
- Crew learns to correlate evidence with sailor positions

---

## Development Workflow

1. **Modify** environment code in `/marooned_env/`
2. **Validate** with phase-specific notebook:
   - Map changes  `test-maps.ipynb`
   - Traitor mechanics  `test-phase3-traitor.ipynb`
   - Rewards  `test-phase4-rewards.ipynb`
3. **Verify** OpenEnv compliance  `test-phase5-openenv.ipynb`
4. **Train** with `Train_Marooned_RL_Clean.ipynb`

### Updated Teacher Model Setup

**Start vLLM teacher server**:
```bash
vllm serve mistralai/Mixtral-8x7B-Instruct-v0.1 \
  --port 8000 \
  --gpu-memory-utilization 0.65 \
  --max-model-len 8192 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 512 \
  --dtype bfloat16 \
  --tensor-parallel-size 1 \
  --tokenizer-mode mistral \
  --disable-log-stats
```

**Verify server**:
```bash
curl http://localhost:8000/v1/models
# Should return: {"data": [{"id": "mistralai/Mistral-7B-Instruct-v0.3", ...}]}
```

3. **Run training**: Open `Train_Marooned_RL_Clean.ipynb` and execute all cells
