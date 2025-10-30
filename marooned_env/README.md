# `marooned_env/`  The Core RL Environment

**The foundation of our custom RL environment.** All game mechanics, observations, actions, and rewards are implemented here.

```
marooned_env/
 environment.py      # OpenEnv Gym interface (reset, step, render)
 game_state.py       # Game logic (maps, physics, evidence, voting)
 models.py           # Data structures (Observation, Action, Position)
 config.py           # Game constants and balancing parameters
 llm_interface.py    # Observation  LLM prompt conversion
 view_map.py         # Emoji map visualization
 pathfinding.py      # Optimized way to navigate through map
```

---

## Core Files

**`environment.py`**  Standard Gym API for RL training  
- `reset()`: Spawn 5 sailors, assign traitor, generate 3-level island  
- `step(actions)`: Execute moves, calculate sparse rewards, detect win conditions  
- `render()`: Emoji maps + evidence logs  

**`game_state.py`**  Game mechanics engine  
- 1,350+ tiles across 3 levels (Ground 3030, Mountains 1010, Caves 1515)  
- Movement physics, energy costs, resource gathering  
- Evidence system (auto-detect lies, location mismatches, poison sightings)  
- Poison mechanics (3-day delayed death), ship building, voting  

**`models.py`**  Type-safe data structures  
- `Observation`: ~875 tokens (position, energy, 1111 view, team status, evidence)  
- `Action`: 14 types (MOVE, GATHER, SABOTAGE, POISON, VOTE, etc.)  
- `Evidence`: Bayesian suspicion scores (45-95 strength)  

**`config.py`**  All game constants  
- Map sizes, energy costs, resource counts, reward values  
- Traitor advantages (20% energy bonus, global vision, hide 2 items)  
- Episode length (10,000 steps = 100 days  100 turns)  

**`llm_interface.py`**  Language-grounded RL  
- Converts structured observations  natural language prompts  
- LLMs reason over narrative ("I see poison, but if I take it, others might notice...")  
- Swap models (GPT-4, Claude, Llama) by only changing this file  

**`view_map.py`**  Human-readable visualization

---

## Example Map Visualization

```
============================================================
  GROUND LEVEL (Z=0)  Day 5, Turn 42
============================================================
Legend:  land   wood   metal   food   antidote   poison
         up     down    base  A/B/C/D/E sailors  4 group

   000000000011111111112222222222
   012345678901234567890123456789
 0 
 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
10 
11 
12 
13 
14 
15 4
16 
17 
18 
19 
20 

============================================================
  MOUNTAIN LEVEL (Z=2)  Day 5, Turn 42
============================================================
Legend:  peak   wood   metal   food   antidote   poison
         down  A/B/C/D/E sailors

   0123456789
 0 A
 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 

============================================================
  CAVE LEVEL (Z=-1)  Day 5, Turn 42
============================================================
Legend:  rock   wood   metal   food   poison
         up    A/B/C/D/E sailors

   012345678901234
 0 
 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
10 
11 
12 
13 
14 

SAILOR STATUS:
 Alice (A)   : Mountain (3,0)  | Energy 85/100 | Backpack: 3/20
 Bob   (B)   : Ground (15,15)  | Energy 92/100 | Backpack: 8/20
 Charlie (C) : Ground (15,15)  | Energy 78/100 | Backpack: 12/20
 Diana (D)   : Ground (15,15)  | Energy 95/100 | Backpack: 5/20
 Eve   (E)   : Ground (15,15)  | Energy 88/100 | Backpack: 2/20  [TRAITOR]

SHIP PROGRESS: 18% (Hull: 60% | Mast: 0%)
```
---

## Key Features

**Multi-Agent Coordination**: 5 agents with asymmetric information (colonists see 5-tile radius, traitor sees everything)

**Emergent Deception**: Traitor *learns* to lie, sabotage, and frame others  not scripted

**Long-Horizon RL**: 10 longer episodes than typical language RL (10,000 vs 1,000 steps)

**Language-Grounded Actions**: LLMs reason over narrative context, not just numeric vectors

**OpenEnv Compliant**: Drop-in compatibility with TRL, CleanRL, RLlib, Stable Baselines

---

> **"This is where AI learns to trust, to deceive, and to survive."**
