# `tests/` — Unit Testing & Validation Suite

**Rigorous unit tests and integration tests for production-grade environment validation.** Unlike the exploratory notebooks (which demonstrate features interactively), these tests follow **software engineering best practices** — automated assertions, edge case coverage, and regression prevention.

```
tests/
├── test_env_basic.py                # Core environment initialization
├── test_maps.py                     # Map generation and boundaries
├── test_movement_and_energy.py      # Movement physics and energy costs
├── test_multi_sailor.py             # Multi-agent coordination
├── test_colonists_and_traitors.py   # Reward validation (gather, deposit)
├── phase5_test.py                   # OpenEnv API compliance
├── phase6_test_llm_policy.py        # LLM integration (prompt → action)
└── llm_interface.py                 # Helper functions for LLM tests
```

---

## Tests vs. Notebooks: Key Differences

| Aspect | `notebooks/` (Exploration) | `tests/` (Validation) |
|--------|---------------------------|----------------------|
| **Purpose** | Demonstrate features, visualize outputs | Assert correctness, catch regressions |
| **Execution** | Manual, interactive (run cells as needed) | Automated, pass/fail (CI/CD ready) |
| **Scope** | End-to-end scenarios (full episodes) | Isolated units (single functions) |
| **Style** | Exploratory ("let's see what happens...") | Deterministic ("this MUST equal X") |
| **Failures** | Print warnings, continue execution | Halt immediately with assertion errors |
| **Examples** | "Train agent for 100 steps, plot rewards" | "Energy must drop by exactly 3 after CLIMB_UP" |

**In short**: Notebooks *show* the environment working. Tests *prove* it works correctly.

---

## Test Categories

### Environment Foundation

**`test_env_basic.py`** — Core initialization  
Validates:
- `reset()` returns dict of observations for 5 sailors
- Map dimensions correct (Ground 30×30, Mountains 10×10, Caves 15×15)
- All data structures properly initialized

**`test_maps.py`** — Map generation integrity  
Validates:
- All terrain grids match expected shapes
- Tile coordinates align with grid positions (no offset bugs)
- Stairs/transitions connect different levels correctly
- Boundary tiles (corners, edges) are walkable
- No out-of-bounds indexing errors

### Game Mechanics

**`test_movement_and_energy.py`** — Physics simulation  
Validates:
- Movement actions (`MOVE_NORTH`, `MOVE_SOUTH`, `CLIMB_UP`, etc.) change position
- Energy decreases after movement (walking = -1, climbing up = -3)
- Energy costs scale correctly with terrain difficulty
- Blocked movement doesn't drain energy

**`test_multi_sailor.py`** — Multi-agent interactions  
Validates:
- All 5 sailors can act simultaneously in `step()`
- Actions execute in correct order (no race conditions)
- Sailors can't occupy same tile (collision detection)
- Spatial view updates correctly when sailors move

**`test_colonists_and_traitors.py`** — Reward engineering  
Validates:
- `GATHER_RESOURCE` awards `+2.0` to colonists
- `DEPOSIT_ITEM` at base camp awards `+0.5`
- Traitor receives different rewards for sabotage
- Reward thresholds match config values
- No negative rewards for legal actions

### Integration Tests

**`phase5_test.py`** — OpenEnv API compliance  
Validates:
- Standard Gym interface (`reset()`, `step()`, `render()`)
- Observations match OpenEnv schema
- Actions structured correctly (no raw strings)
- Episode termination signals (done, truncated) work
- Info dict contains required metadata

**`phase6_test_llm_policy.py`** — LLM → Action pipeline  
Validates:
- LLM response parsing (`parse_llm_response()`)
- Safe action extraction (`parse_action_safe()`)
- Action validation (`validate_action()`)
- Malformed LLM outputs handled gracefully (fallback to `WAIT`)
- Integration with environment step loop

---

## Running Tests

**Run all tests**:
```bash
cd tests
python test_env_basic.py
python test_maps.py
python test_movement_and_energy.py
python test_colonists_and_traitors.py
python phase5_test.py
python phase6_test_llm_policy.py
```

**Expected output**:
```
test_env_reset_and_structure Passed
All maps shapes correct.
All level transitions (stairs) are valid and walkable on both ends.
test_movement_causes_energy_drop Passed
Colonist gather and deposit reward test completed.
Phase 5 OpenEnv compliance test passed.
Phase 6 LLM policy flow test passed.
```

---

## Software Engineering Principles

**Unit Testing**: Each test validates a **single responsibility** (map shape, energy cost, reward value) — not entire episodes

**Isolation**: Tests use `reset()` per run — no shared state, no cascading failures

**Deterministic Seeding**: Fixed random seeds (`seed=42`) ensure reproducible results across runs

**Edge Case Coverage**: Boundary validation (corners, stairs, level transitions) catches off-by-one errors

**Regression Prevention**: Once a bug is fixed, a test is added to ensure it never returns

**Integration Testing**: Final tests (`phase5`, `phase6`) validate end-to-end pipelines (LLM → action → step)

---

## Why This Matters

**Prevents Silent Failures**: Environment bugs can corrupt RL training for days before detection  

**Validates Balancing**: Confirms reward values match design intent (ship completion = +100, not +10)  

**Ensures Multi-Agent Correctness**: 5 simultaneous agents create race conditions — tests catch them  

**LLM Safety**: Malformed model outputs (hallucinated actions, invalid coordinates) get sanitized  

**OpenEnv Compliance**: Guarantees compatibility with TRL, CleanRL, RLlib without adapter bugs

---

> **"Trust, but verify."**  
> Every mechanic tested. Every edge case handled. No surprises during training.