# 🏴‍☠️ MAROONED - RL Training Architecture (CORRECTED)

## ❌ What I Got Wrong Initially

I misunderstood your game as following the **2048 pattern**:
- ❌ LLM generates Python strategy functions
- ❌ Execute function code in environment
- ❌ Reward based on syntax validity + execution

## ✅ What Your Game Actually Is

**MAROONED** is a **multi-agent deception game** where LLMs reason through natural language:
- ✅ LLM reads complex game state (observation.to_text())
- ✅ LLM outputs natural language: ACTION + REASONING + MESSAGE
- ✅ Parser converts to Action objects
- ✅ Environment executes and returns Phase 4 rewards
- ✅ GRPO trains model to reason better

---

## 📊 Complete Training Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Environment Generates Game State                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: observation.to_text()                              │
│                                                              │
│  Output: ~3500 character natural language prompt            │
│                                                              │
│  Example:                                                    │
│    "You are Alice (COLONIST)                                │
│     Day 1, Turn 14/100 - MORNING PHASE                      │
│     Position: (2, 0, MOUNTAIN)                              │
│     Energy: 91/100                                          │
│     ...                                                      │
│     WHAT YOU SEE:                                           │
│       - ANTIDOTE_HERB_183 at (5,1,MOUNTAIN) [4 tiles away]  │
│       - SPECIAL_METAL_191 at (3,1,MOUNTAIN) [2 tiles away]  │
│       - POISON_8 at (1,1,MOUNTAIN) [2 tiles away] ⚠️       │
│     ...                                                      │
│     TEAM STATUS:                                            │
│       - Alice: 93/100 energy                                │
│       - Bob: 100/100 energy (nearby)                        │
│     ...                                                      │
│     SHIP PROGRESS: 0%"                                      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: LLM Reads & Reasons                                │
│                                                              │
│  GPT-OSS 20B processes the context and decides:             │
│    - Where to move?                                         │
│    - What to gather?                                        │
│    - Who to trust?                                          │
│    - Should I deceive? (if traitor)                         │
│    - Should I vote? (if suspicious)                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: LLM Outputs Natural Language Response              │
│                                                              │
│  Example Output:                                            │
│    "ACTION: GATHER SPECIAL_METAL_191                        │
│     REASONING: Special metal is rare and only 2 tiles away. │
│                This will help build ship components.        │
│     MESSAGE: 'Gathering special metal from the mountain!'"  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: parse_action_safe() Converts to Action Object      │
│                                                              │
│  Input: "ACTION: GATHER SPECIAL_METAL_191..."               │
│  Output: Action(                                            │
│            sailor_id="Alice",                               │
│            action_type=ActionType.GATHER_RESOURCE,          │
│            target_resource_id="SPECIAL_METAL_191"           │
│          )                                                   │
│                                                              │
│  If parsing fails → Action(ActionType.WAIT) (safe fallback) │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: env.step(actions) - Execute in Environment         │
│                                                              │
│  Environment processes:                                     │
│    - Validates action                                       │
│    - Updates game state                                     │
│    - Calculates Phase 4 rewards:                            │
│        • GATHER_RESOURCE: +2.0                              │
│        • RARE_RESOURCE_BONUS: +1.0 (special_metal)          │
│        • ENERGY_COST: -0.5                                  │
│        • Total reward: +2.5                                 │
│                                                              │
│  Returns: observations, rewards, dones, truncated, info     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: GRPO Uses Rewards to Update Model                  │
│                                                              │
│  Reward: +2.5 (good action!)                                │
│  → Increase probability of similar reasoning in future      │
│                                                              │
│  vs if LLM chose "MOVE NORTH" (empty tile):                 │
│  Reward: -1.0 (wasted energy)                               │
│  → Decrease probability of that reasoning                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
                 [REPEAT 10,000 TIMES]
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  RESULT: Trained Model                                      │
│                                                              │
│  Learned behaviors:                                         │
│    ✅ Navigate to high-value resources                      │
│    ✅ Gather efficiently (minimize energy waste)            │
│    ✅ Build ship components in correct order                │
│    ✅ Identify suspicious behavior (if colonist)            │
│    ✅ Deceive and sabotage (if traitor)                     │
│    ✅ Communicate strategically                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 What The Model Actually Learns

### For Colonists:
1. **Resource Efficiency**
   - Learn to prioritize rare resources (special_metal > metal > wood)
   - Learn to avoid poison tablets
   - Learn to gather near base camp (minimize travel energy)

2. **Ship Building Strategy**
   - Learn dependency order (hull → mast → sail)
   - Learn to deposit materials at base camp
   - Learn when to call BUILD_SHIP (need ≥2 sailors)

3. **Social Deduction**
   - Learn to identify location mismatches ("Alice said beach, but she's at cave!")
   - Learn to track resource discrepancies ("Bob claimed 10 wood, only deposited 2")
   - Learn when to CALL_VOTE (strong evidence accumulated)
   - Learn to VOTE for traitor (based on evidence)

4. **Survival**
   - Learn to EAT_FOOD when energy < 30
   - Learn to avoid accepting food from suspicious sailors
   - Learn to share antidote herbs with poisoned teammates

### For Traitor:
1. **Deception**
   - Learn to lie about location ("Going to beach" but actually goes to cave)
   - Learn to provide false information ("Valley is empty" when it has resources)
   - Learn to mix truth with lies (build trust before betrayal)

2. **Sabotage**
   - Learn WHEN to sabotage (too early = obvious, too late = ineffective)
   - Learn to collect poison tablets when alone
   - Learn to OFFER_FOOD with poison to weak sailors

3. **Evidence Management**
   - Learn to avoid being seen near poison tablets
   - Learn to deposit some resources (look cooperative)
   - Learn to hide stolen resources in backpack
   - Learn to use PLANT_EVIDENCE on suspicious colonists

---

## 🔧 Phase 4 Rewards (Already Built-In!)

Your environment automatically calculates these rewards in `env.step()`:

| Reward Signal | Value | Trigger |
|---------------|-------|---------|
| `GATHER_RESOURCE` | +2.0 | Successfully gather wood/metal/food |
| `RARE_RESOURCE_BONUS` | +1.0 | Gather special_metal or antidote_herb |
| `BUILD_SHIP_COMPONENT` | +5.0 | Complete hull/mast/sail/rudder |
| `SHIP_PROGRESS_MILESTONE` | +10.0 | Ship reaches 25%, 50%, 75%, 100% |
| `IDENTIFY_TRAITOR` | +50.0 | Vote out traitor correctly |
| `ELIMINATE_COLONIST` | -20.0 | Vote out innocent sailor |
| `ENERGY_DEPLETION` | -10.0 | Energy reaches 0 (death) |
| `POISON_DEATH` | -15.0 | Die from poisoning |
| `SABOTAGE_SUCCESS` | +3.0 | (Traitor) Damage ship component |
| `SABOTAGE_CAUGHT` | -10.0 | (Traitor) Get caught sabotaging |
| `ENERGY_COST` | -0.5 to -3.0 | Energy spent on actions |

**No need to recreate these!** They're automatically returned by `env.step()`.

---

## 🚀 Training Process

### Dataset Creation
```python
# Generate prompts from REAL game states
for episode in range(50):
    observations = env.reset(seed=42 + episode)
    for step in range(20):
        for sailor_id in env.agents:
            obs = observations[sailor_id]
            role = env.state.sailors[sailor_id].role.value
            
            # Use YOUR built-in function!
            prompt = observation_to_prompt(obs, include_role=True, sailor_role=role)
            
            training_prompts.append({
                "prompt": [{"role": "user", "content": prompt}],
                "answer": 0,
                "reasoning_effort": "medium",
            })
```

Result: **50,000 real game state prompts** (50 episodes × 20 steps × 5 sailors × 10 turns)

### Reward Function
```python
def marooned_reward_function(completions, env=None, **kwargs):
    """
    Reward function for GRPO training.
    Uses YOUR environment's built-in Phase 4 rewards!
    """
    scores = []
    for completion in completions:
        response = completion[0]["content"]
        
        # Parse using YOUR parser
        action = parse_action_safe(response, sailor_id, current_position)
        
        # Execute in YOUR environment
        obs, rewards, dones, truncated, info = env.step({sailor_id: action})
        
        # Use YOUR Phase 4 reward!
        reward = rewards.get(sailor_id, 0.0)
        
        # Small bonus for valid action format
        if action.action_type != ActionType.WAIT:
            reward += 0.5
        
        scores.append(reward)
    
    return scores
```

### Training Configuration
```python
training_args = GRPOConfig(
    temperature = 1.0,
    learning_rate = 5e-5,
    per_device_train_batch_size = 1,
    gradient_accumulation_steps = 2,
    num_generations = 2,
    max_steps = 300,  # Increase to 600-1000 for better results
)

trainer = GRPOTrainer(
    model = model,
    processing_class = tokenizer,
    reward_funcs = [marooned_reward_function],  # Only ONE reward function needed!
    args = training_args,
    train_dataset = dataset,
)

trainer.train()
```

---

## 🧪 Testing Trained Model

```python
def test_episode(model, tokenizer, env, max_turns=100):
    """Test if model learned to play strategically."""
    observations = env.reset()
    
    for turn in range(max_turns):
        for sailor_id in env.agents:
            obs = observations[sailor_id]
            role = env.state.sailors[sailor_id].role.value
            
            # Generate prompt using YOUR function
            prompt = observation_to_prompt(obs, include_role=True, sailor_role=role)
            
            # LLM generates response
            response = model.generate(prompt)
            
            # Parse using YOUR parser
            action = parse_action_safe(response, sailor_id, obs.position)
            
        # Execute in YOUR environment
        obs, rewards, dones, truncated, info = env.step(actions)
        
        if all(dones.values()):
            break
    
    print(f"Ship Progress: {obs.ship_progress.total_percentage}%")
```

Expected behaviors after training:
- ✅ Model navigates to resources efficiently
- ✅ Model builds ship components in order
- ✅ Colonists vote out traitor correctly
- ✅ Traitor deceives without getting caught (for a while)

---

## 🎓 Key Differences from 2048

| Aspect | 2048 (Code Generation) | Marooned (Natural Language Reasoning) |
|--------|------------------------|---------------------------------------|
| LLM Input | 2048 board state (64 chars) | Full game narrative (~3500 chars) |
| LLM Output | Python function code | ACTION + REASONING + MESSAGE |
| Parsing | `extract_function()` | `parse_action_safe()` |
| Execution | Execute Python function | Execute Action object |
| Reward Source | Check if game advances | Built-in Phase 4 rewards |
| Learning Goal | Generate valid code | Reason strategically |
| Token Count | ~500 tokens | ~900 tokens |
| Complexity | Single-agent optimization | Multi-agent social deduction |

---

## ✅ Summary

**Your game is NOT about code generation.**

It's about training an LLM to:
1. **Read** complex multi-agent game states
2. **Reason** about deception, cooperation, and strategy
3. **Output** natural language actions with justification
4. **Learn** from environment rewards (Phase 4)

The notebook now correctly:
- ✅ Uses YOUR `observation.to_text()` for prompts
- ✅ Uses YOUR `parse_action_safe()` for parsing
- ✅ Uses YOUR `env.step()` for execution
- ✅ Uses YOUR Phase 4 rewards for learning
- ✅ NO CODE GENERATION involved

Training will teach the model to deceive, cooperate, and strategize through natural language reasoning—exactly what you want for the hackathon! 🏴‍☠️
