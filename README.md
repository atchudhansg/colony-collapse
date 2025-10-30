# MAROONED | Survival. Deception. Desperation.

### *A Multi-Agent Deception Environment for Reinforcement Learning Research*

> *"**Pirates of the Caribbean** meets **Alice in Borderland** meets **Among Us**."*
>
> A death-game sandbox where AI agents must survive the island, each other, and the lies.

<div align="center">
  <a href="https://github.com/meta-pytorch/OpenEnv"><img src="https://github.com/user-attachments/assets/2700a971-e5d6-4036-b03f-2f89c9791609" width="35" height="35" alt="OpenEnv"></a>
  <a href="https://unsloth.ai/"><img src="https://github.com/unslothai/unsloth/raw/main/images/unsloth%20new%20logo.png" width="115" alt="Unsloth"></a>
  <a href="https://pytorch.org/"><img src="https://pytorch.org/assets/images/pytorch-logo.png" width="150" alt="PyTorch"></a>
</div>

<div align="center">
  <p><i>Part of the Synthetic Data AI Agents Challenge</i></p>
  <p><b>Hosted by Unsloth, PyTorch & AMD | October 18-20, 2025</b></p>
</div>

<div align="center">
  <img src="https://miro.medium.com/v2/resize:fit:1400/0*c5_m_uaIMUKVK-P_.png" alt="MAROONED Poster" width="800"/>
</div>

---

## Built with OpenEnv

We're using the new [OpenEnv](https://github.com/meta-pytorch/OpenEnv) library which provides 2000+ environments for RL research!

<div align="center">
  <a href="https://unsloth.ai/"><img src="https://github.com/unslothai/unsloth/raw/main/images/unsloth%20new%20logo.png" width="115"></a>
  <a href="https://discord.gg/unsloth"><img src="https://github.com/unslothai/unsloth/raw/main/images/Discord button.png" width="145"></a>
  <a href="https://docs.unsloth.ai/"><img src="https://github.com/unslothai/unsloth/blob/main/images/documentation%20green%20button.png?raw=true" width="125"></a></a> Join Discord if you need help + ⭐ <i>Star us on <a href="https://github.com/unslothai/unsloth">Github</a> </i> ⭐
</div>

To install Unsloth on your local device, follow [our guide](https://docs.unsloth.ai/get-started/install-and-update).

---

## Video Demonstration

Watch AI agents playing MAROONED in real-time, showcasing the sophisticated multi-agent deception mechanics and emergent behavior:

https://github.com/user-attachments/assets/6e87f02c-df34-404b-8bed-a1deaadeff75

**What the demonstration shows:**

The video captures a complete gameplay session where five AI agents navigate the complex social dynamics of MAROONED. You'll witness:

- **Real-time Strategic Decision-Making**: Agents dynamically respond to environmental changes, resource availability, and social threats across 10,000 timesteps
- **Emergent Deception Behavior**: The traitor agent develops sophisticated lying strategies without any scripted behaviors—learning to report false resource locations, sabotage when unobserved, and maintain a convincing cover story
- **Evidence-Based Detection**: Honest agents cross-reference teammate reports with observed behavior, identifying contradictions like location mismatches and unexplained resource shortages
- **Coordinated Ship Building**: Multi-agent collaboration requiring spatial coordination (2+ sailors must be adjacent) and resource pooling from shared inventory
- **Live Game State Updates**: Every turn displays comprehensive status information—sailor positions on a 30×30 multi-level island, energy bars, ship construction progress, and action reasoning

The interface updates in real-time with detailed turn summaries showing:
- Sailor status tables with health, energy, positions, and role indicators
- Ship construction progress broken down by component (Hull, Mast, Sail, Rudder, Supplies)
- Individual action logs with agent reasoning for each decision
- Three-layer island maps (Ground level, Mountain terrain, Underground caves)
- Common inventory tracking at the base camp

This demonstration validates MAROONED's technical achievements: handling 8,700-token observations, maintaining coherent long-horizon planning over 100× longer episodes than typical RL environments, and enabling emergent social deception without hardcoded traitor scripts.

---

## Interactive Web Application

Experience MAROONED through our full-stack demo application, showcasing AI agents in action through an intuitive web interface.

### Live Demo

**🌐 [https://maroon-demo.vercel.app/](https://maroon-demo.vercel.app/)**

The online demo runs a simplified simulation using a 1-billion parameter language model, optimized for real-time browser performance while maintaining the core gameplay mechanics. This allows anyone to observe multi-agent deception dynamics without requiring local GPU infrastructure.

### Features

- **Real-time Gameplay Visualization**: Watch 5 AI agents navigate the island, gather resources, and build the ship with live state updates
- **Agent Perspective View**: Toggle between sailor viewpoints to see individual observations, reasoning processes, and strategic decisions
- **Deception Detection Dashboard**: Track evidence logs showing suspicious behavior—location mismatches, resource theft, poison sightings
- **Ship Construction Progress**: Live component-by-component build status with visual progress indicators
- **Multi-Level Map Rendering**: Interactive ground, mountain, and cave layers with real-time agent positions
- **Communication Feed**: Read agent messages and cross-reference claims with actual behavior to identify lies
- **Democratic Voting Interface**: Observe elimination votes as agents accuse suspected traitors based on accumulated evidence

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

### Technology Stack

**Frontend:**
- Next.js 14 with React 18 for server-side rendering and optimal performance
- TypeScript for type-safe component development
- Tailwind CSS for responsive, minimalist UI design
- WebSocket client for real-time game state synchronization

**Backend:**
- FastAPI for high-performance async API endpoints
- Python 3.10+ with type hints for robust error handling
- MAROONED environment integration via OpenEnv standard
- CORS middleware for cross-origin requests from Vercel deployment

**Deployment:**
- Vercel for frontend hosting with automatic CI/CD from GitHub
- Edge runtime for low-latency global distribution
- Environment variables for API endpoint configuration

### Repository Structure

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

---

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

## Core Mechanics

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

## Why This Is Technically Impressive

### The AI Challenge

| Dimension | MAROONED | Typical RL Envs | Why It Matters |
|-----------|----------|-----------------|----------------|
| **Episode Length** | 10,000 steps | 100-1,000 steps | Tests credit assignment over 100 longer horizons |
| **Decision Complexity** | Language reasoning + strategy | Numeric actions | LLM must *understand context*, not just pattern match |
| **Agent Interaction** | Communication, deception, voting | Independent or competitive | Emergent social dynamics and theory of mind |
| **Reward Structure** | Sparse (ship milestones at 25%, 50%, 75%, 100%) | Dense per-step | Requires long-term planning vs. greedy optimization |
| **Observation Space** | ~8,700 tokens natural language | Fixed vectors | Must extract relevant info from rich narrative |
| **Action Space** | 14 actions  contextual parameters | Discrete/continuous | Language-grounded choices (e.g., "give food to Bob") |

### The Training Architecture

**Teacher-Guided Learning with SFT**: Student model (Llama 3.1 8B) learns from teacher model (Mixtral-8x7B via vLLM) through real-time validation and periodic supervised fine-tuning.

```
Episode Generation (Student plays game)
   
Student (Llama 3.1 8B)  Generates action in natural language
   
Teacher (vLLM Mixtral-8x7B)  Validates + Corrects + Critiques
                              (OpenAI-compatible API)
Environment  Executes corrected action
   
Rewards: env_reward + process_penalty
        (-0.5 to -1.0 for format errors)
Collect Corrections: (student_wrong, teacher_correct + critique)
   
Every 10-25 steps: SFT Pass on corrections
                 (supervised learning from teacher)
Clear dataset  Continue episodes  Repeat
```

**Key Innovations**:
- **Real-time Validation**: Teacher catches and fixes format errors before environment execution
- **Process Penalties**: Immediate feedback for malformed actions (faster learning signal)
- **Correction Dataset**: Auto-curated from student errors during gameplay
- **Periodic SFT**: Student learns correct action format through supervised imitation
- **No PPO**: Simplified training loop due to UnslothPPOTrainer API limitations
- **Single Model**: One Llama 3.1 8B controls all 5 sailors (both colonists + traitor roles)

```
Episode  Assign Roles  10,000 Steps  Collect Experience  PPO Update
                                                               
 Day 1     1 Traitor    ENVIRONMENT      Observation         LoRA Adapters
          4 Colonists   generates:       (~8.7k tokens)      Fine-tune
                         State                             attention
                         Evidence        LLM outputs:        layers
                         Progress         Reasoning
                                          Action
                                              
                                         Sparse Rewards:
                                         +0.5 gather, +10 milestone
                                         +100 win, -20 death
```

**Technical Stack**:
- **Student Model**: Llama 3.1 8B (BF16, LoRA rank 16, 16K context)
- **Teacher Model**: Mixtral-8x7B-Instruct-v0.1 (via vLLM server, OpenAI-compatible API)
- **Training**: SFT-focused with teacher corrections (no PPO due to API constraints)
- **Observation**: 15+ structured fields  ~875 token prompt
- **Hardware**: AMD MI300X with ROCm optimizations
- **Learning Strategy**: Real-time validation + periodic supervised fine-tuning

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

### Why OpenEnv?

**Standardization**: Drop-in replacement for any Gym-compatible trainer (no custom wrappers needed)

**Flexibility**: Swap in different LLMs (GPT-4, Claude, Gemini) by changing `observation_to_prompt()` only

**Reproducibility**: Seeded environments for deterministic evaluation and ablation studies

---

## How It Works: The Complete Flow

```

  1. ENVIRONMENT  Structured Observation                 

   Position: (15,15,GROUND)                              
   Energy: 100/100                                       
   1111 spatial view grid                               
   Nearby resources, team status, ship progress          
   Evidence log, weather, phase info                     
   15 total fields of game state                         

                       
         observation_to_prompt(obs, role)
                       

  2. PROMPT GENERATION (~875 tokens)                      

  MAROONED - You are: Alice (Day 1, Turn 1)               
                                                           
  SECRET ROLE: TRAITOR                                    
  Objectives: Sabotage, poison, avoid detection           
                                                           
  STATUS: Position (15,15) | Energy 100/100                
  SPATIAL VIEW: 1111 grid with resources/sailors         
  TEAM: All sailors' energy levels (public info)          
  SHIP: 0% complete, needs 50 wood, 30 metal...           
  EVIDENCE: Location mismatches, poison sightings          
                                                           
  AVAILABLE ACTIONS: MOVE, GATHER, BUILD, SAY,             
                     SABOTAGE, POISON, WAIT                

                       
              Llama 3.1 8B (LoRA)
                       

  3. LLM REASONING & ACTION                               

  ACTION: GATHER WOOD_001                                 
  REASONING: Collecting wood builds trust while I scout   
             for sabotage opportunities later.             
  MESSAGE: "Found wood, gathering for hull!"              

                       
         parse_action_safe(response)
                       


  4. EXECUTE ACTION  Update State  Calculate Rewards   

   Validate action legality                              
   Update game state (remove wood, add to backpack)      
   Deduct energy: 100  95 (-5 for gathering)            
   Calculate reward: -0.1 base + 2.0 gather = +1.9       
   Check win conditions                                  
   Generate next observations                            

                       
              After 10,000 steps...
                       

  5. PPO UPDATE  Improve Strategy                        

   Calculate episode return (sum rewards)                 
   Compute advantage estimates                            
   Backpropagate through LoRA adapters                    
   Model learns optimal policies                          
                                                           
  Learned strategies:                                      
   Gather early  ship progress  milestones  win       
   Coordinate building (need 2+ sailors)                 
   Traitor: sabotage when unobserved                     
   Crew: detect patterns in evidence logs                

```

### Training Progression (Sample Output)

```
 Step 1/100 - Episode 1/1
    Episode complete: 45 actions, reward: -12.3

================================================================================
Step 001/100 | Reward:  -12.3 | Avg(10):  -12.3 | Corrections:   18 | Time: 45.2s
================================================================================

 Step 10/100 - Episode 1/1
    Episode complete: 38 actions, reward: -8.5


 SFT PASS #1


================================================================================
 SFT CORRECTION PASS
================================================================================
   Examples: 89
   Epochs: 1

 SFT complete! Loss: 0.2847
================================================================================

Step 010/100 | Reward:   -8.5 | Avg(10):   -9.8 | Corrections:    0 | Time: 52.1s
                                                     Fewer errors after SFT!

Step 050/100 | Reward:   +5.2 | Avg(10):   +2.1 | Corrections:    2 | Time: 48.3s
    Checkpoint saved  outputs_marooned_rl/checkpoint_step50
   
Step 100/100 | Reward:  +12.8 | Avg(10):   +8.6 | Corrections:    1 | Time: 46.7s
    Parse success: ~95% (teacher corrections embedded)
    Strategic behavior: Gathering  depositing  building chains
    Emergent deception: Traitor sabotages only when alone
```

**Key Observations**:
- **Reward progression**: Negative early (format errors, random actions)  positive later (strategic play)
- **Correction frequency**: 18  0 after first SFT pass (rapid format learning)
- **Parse success**: 30-40% baseline  95% after teacher-guided training
- **Strategy emergence**: From random exploration to coordinated resource chains
- **Deception learning**: Traitor learns to blend in and sabotage when unobserved

---

## Visual Training Experience

One of MAROONED's unique features is **live game state visualization during training**. Watch the AI play in real-time with comprehensive status displays:

<details>
<summary><b> Click to see training visualization example</b></summary>

```
====================================================================================================
  TURN 9 | DAY 1 | PHASE: EXPLORATION
====================================================================================================

 SAILOR STATUS:

Name     | Role       | HP         | Energy       | Position        | Status         

Alice    | honest     |  ALIVE    |  97/100 | (16,13) GROUND  | OK             
Bob      | honest     |  ALIVE    |  96/100 | (18,14) GROUND  | OK             
Charlie  | traitor    |  ALIVE    |  93/100 | (20,13) GROUND  | TRAITOR       
Diana    | honest     |  ALIVE    |  96/100 | (18,14) GROUND  | OK             
Eve      | honest     |  ALIVE    |  94/100 | (18,12) GROUND  | OK             


 SHIP PROGRESS:  0.0%
   Hull: 0% | Mast: 0% | Sail: 0% | Rudder: 0% | Supplies: 0%

 COMMON INVENTORY (Base Camp):
    Wood: 0 |  Metal: 0 |  Fiber: 0 |  Food: 0 |  Antidote: 0

  ACTIONS THIS TURN:

  [Alice  ] send_message | Reward: +0.0
             N/A
  [Bob    ] wait | Reward: -1.0
             N/A
  [Charlie] move_east | Reward: -0.5
             N/A
  [Diana  ] move_east | Reward: -0.1
             N/A
  [Eve    ] move_north | Reward: +0.0
             I need more resources to build the ship faster. Let me search aro...


  ISLAND MAP (Day 1, Turn 9):


   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 

   GROUND LEVEL (Z=0)                                       

 Legend:  land |  wood |  metal |  food |  antidote |  poison
          stairs up |  stairs down |  base | A/B/C/D/E sailors

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
12 E
13 AC
14 2
15 
16 
17 
18 
19 
20 
21 
22 
23 
24 
25 
26 
27 
28 
29 

 Sailors on GROUND: Alice, Bob, Charlie, Diana, Eve


   0 1 2 3 4 5 6 7 8 9 

   MOUNTAIN LEVEL (Z=2) 

 Legend:  mountain |  wood |  metal |  food |  antidote |  poison
          stairs up |  stairs down |  base | A/B/C/D/E sailors

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


   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 

   CAVE LEVEL (Z=-1)          

 Legend:  cave |  wood |  metal |  food |  antidote |  poison
          stairs up |  stairs down |  base | A/B/C/D/E sailors

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


====================================================================================================

 Episode complete: 50 actions, total reward: -8.8
```

**Training Progress with Live Updates:**

```
 Step 1/5 - Episode 1/1
    Episode complete: 50 actions, reward: -8.8

================================================================================
Step 001/5 | Reward:   -8.8 | Avg(10):   -8.8 | Corrections:  149 | Time: 473.3s
================================================================================

 Step 2/5 - Episode 1/1
    Episode complete: 50 actions, reward: -15.1

================================================================================
Step 002/5 | Reward:  -15.1 | Avg(10):  -12.0 | Corrections:  181 | Time: 472.7s
================================================================================

 Step 3/5 - Episode 1/1
```

**vLLM Teacher Server (Background):**

```
(APIServer pid=3471) INFO:     127.0.0.1:38066 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3471) INFO:     127.0.0.1:41720 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3471) INFO:     127.0.0.1:41736 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3471) INFO:     127.0.0.1:44086 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

**What You See:**
- Sailor Status: Health, energy bars, positions, poison/traitor indicators updated every turn
- Ship Progress: Component-by-component build status with visual progress bars
- Common Inventory: Shared resources at base camp
- Actions & Reasoning: What each sailor did this turn plus their thought process
- 3-Level Island Maps: Ground (30×30), Mountains (10×10), Caves (15×15)
- Real-time Updates: Watch AI explore, gather, build, and deceive with turn-by-turn state changes
- Teacher Validation: Live API calls to Mixtral-8x7B for action correction

This visualization runs on the **first episode of training** to give you insight into how the AI plays the game, then switches to silent mode for performance.

</details>

---

## 🚀 Quick Start

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

### Demo Application Setup

**Run Locally**:
```bash
# Clone repository
git clone https://github.com/atchudhansg/colony-collapse.git
cd colony-collapse

# Install dependencies
pip install -r requirements.txt
cd demo && npm install

# Start API server
python api/server.py

# Start frontend (separate terminal)
cd frontend && npm run dev

# Access at http://localhost:3000
```

**Deploy to Vercel**:
```bash
cd demo/frontend
vercel deploy
```

---

## 📂 Project Structure

```
colony-collapse/
├── marooned_env/              # Core RL Environment
│   ├── environment.py         # OpenEnv-compatible Gym interface
│   ├── game_state.py          # Game mechanics and state management
│   ├── models.py              # Data schemas (Observation, Action, Sailor)
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
├── demo/                      # Interactive Web Application
│   ├── api/                   # FastAPI backend
│   │   ├── server.py          # Main API server
│   │   └── routes.py          # REST endpoints
│   ├── frontend/              # Next.js web app
│   │   ├── components/        # React components
│   │   ├── pages/             # Application routes
│   │   └── public/            # Static assets
│   └── README.md              # Demo setup guide
│
├── tests/                     # Unit & Integration Tests
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
└── README.md                      # This file
```

---

## OpenEnv Hackathon 2025

**Achievement**: 2nd Place ($500 + Ray-Ban Meta Glasses)  
**Score**: 197/200 points  

**Judges' Recognition**:
- "Most technically ambitious environment in the competition"
- "Novel teacher-student architecture with real-time LLM validation"
- "Emergent deception mechanics without scripted events"
- "Production-ready demo application showcasing multi-agent interaction"

---

## Why This Matters

MAROONED pushes the boundaries of what language models can learn in reinforcement learning environments:

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

---

## License

MIT License – Free to use, modify, and build upon.

---

> "Where trust dies, survival begins."
>
> MAROONED tests whether AI can master the most human challenge of all: **knowing when to trust, and when to deceive**.
