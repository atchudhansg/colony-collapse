
# MAROONED — Pirate Island Survival Game

### *A Multi-Agent Deception Environment for Reinforcement Learning Research*

> *“Pirates of the Caribbean meets Alice in Borderland meets Among Us.”*
>
> *A sandbox of deception, cooperation, and long-horizon reasoning.*

---

## 1. Overview

**MAROONED** is a novel **multi-agent reinforcement learning (RL)** environment that simulates survival, deception, and trust on a mysterious multi-level island.

Five AI sailors are shipwrecked with a shared mission: gather resources, rebuild their ship, and escape within  **100 in-game days** .

One sailor, however, hides a secret — a **traitor** intent on sabotaging the mission from within.

### Key Features

* **Long-Horizon Planning** – 100 days × 100 turns = 10,000+ sequential decisions.
* **Deception & Detection** – Traitor must lie convincingly; others must infer truth.
* **Language-Based Negotiation** – All communication occurs through natural-language messages.
* **Resource Management** – Explore, forage, craft, and survive cooperatively.
* **Hidden-Role Uncertainty** – Everyone knows a traitor exists, but not who it is.
* **Multi-Layer Map** – Mountain peaks, beach level, and subterranean caves — each with unique resources and risks.

---

## 2. The Island

### 2.1 Topography

```
LEVEL +2 — Mountain Peaks (10×10)
   Rare metals, antidote herbs, low oxygen
   Highest energy cost; harsh but rewarding

LEVEL  0 — Ground / Beach (30×30)
   Central hub for shipbuilding and storage
   Common resources: wood, metal, fruit

LEVEL –1 — Caves (15×15)
   Crystals, mushrooms, fog of war
   Dangerous navigation, limited visibility
```

### 2.2 Resources

| Category           | Examples                   | Purpose                |
| ------------------ | -------------------------- | ---------------------- |
| Building Materials | Wood, Metal, Fibers        | Ship construction      |
| Food               | Apples, Berries, Mushrooms | Restore energy         |
| Medical            | Antidote Herbs             | Cure poisoning         |
| Special            | Crystals, Relics           | Scoring or upgrades    |
| Hazardous          | Poison Tablets             | Traitor sabotage items |

Total poison tablets scattered across map: **18**

---

## 3. The Sailors

### 3.1 Honest Crew (4 Sailors)

* **Objective:** Rebuild the ship to 100% completion.
* **Behavior:** Cooperative, information-sharing, defensive voting.
* **Limitations:** Normal vision range; standard energy expenditure.

### 3.2 Traitor (1 Sailor)

* **Objective:** Prevent escape — by deception, poison, or disruption.
* **Strategy:** Blend in, manipulate dialogue, and delay progress.
* **Unique Traits:**
  * Global vision of all sailor positions.
  * 20% energy efficiency bonus.
  * May *plant evidence* once per game.
  * Can hide up to two inventory items when inspected.

**The crew knows a traitor exists from the beginning.** Suspicion becomes part of survival.

---

## 4. Daily Structure (100 Turns per Day)

Each day follows a recurring social and operational rhythm:

| Phase                       | Turns     | Description                                                                                       |
| --------------------------- | --------- | ------------------------------------------------------------------------------------------------- |
| **Morning Meeting**   | 1 – 15   | All sailors meet at base camp to plan, debate, or call emergency votes.                           |
| **Exploration**       | 16 – 75  | Sailors split up to gather resources across levels. Limited communication (1 message / 10 turns). |
| **Evening Return**    | 76 – 85  | Agents return and deposit materials into the shared inventory.                                    |
| **Discussion & Vote** | 86 – 100 | Evidence is reviewed; a vote may be held to exile a suspected traitor.                            |

---

## 5. Ship Construction

| Component          | Progress % | Required Resources    | Dependency |
| ------------------ | ---------- | --------------------- | ---------- |
| **Hull**     | 30         | 50 wood               | None       |
| **Mast**     | 20         | 30 wood, 20 metal     | Hull       |
| **Sail**     | 25         | 40 plant fibers       | Mast       |
| **Rudder**   | 15         | 15 metal, 10 wood     | Hull       |
| **Supplies** | 10         | 10 apples, 10 berries | None       |

### Construction Rules

* Each component requires **two or more sailors** to collaborate.
* Construction consumes **5 consecutive turns** per section.
* Any sabotage attempt halts building for an entire day.

**Completion (100%) = Victory for the crew.**

---

## 6. Poison and Antidote System

### 6.1 Poison Timeline

```
Day 0 — Poison introduced into victim's food. No visible effects.
Day 1 — Early symptoms: −50% energy regeneration; visible [POISONED] tag.
Day 2 — Severe state: −20 energy/turn; visible [SEVERELY POISONED] tag.
Day 3 — Death. Announcement: “Sailor X died from poisoning.”
```

### 6.2 Antidote Mechanics

* Found only on  **mountain peaks** .
* Must be used within Days 1–2 to be effective.
* Forces moral trade-offs: heal self or save another?

---

## 7. Evidence and Suspicion System

The environment automatically logs suspicious activities, building a **Bayesian evidence model** for social inference.

| Evidence Type               | Example                                      | Strength |
| --------------------------- | -------------------------------------------- | -------- |
| **Poison Collection** | “Eve seen collecting poison tablet.”       | 90       |
| **Ship Sabotage**     | “Mast integrity decreased by 30%.”         | 95       |
| **Death Timeline**    | “Bob died 3 days after Eve gave him food.” | 75       |
| **Location Mismatch** | “Claimed cave, spotted at beach.”          | 50       |
| **Resource Theft**    | “Claimed 15 wood, deposited 3.”            | 45       |

Evidence accumulates over time and is accessible during the daily council vote.

---

## 8. Victory Conditions

| Alignment         | Condition                                                    | Result                    |
| ----------------- | ------------------------------------------------------------ | ------------------------- |
| **Crew**    | Ship fully rebuilt**or**traitor successfully voted out | Sailors escape the island |
| **Traitor** | Crew death, ship incomplete by Day 100, or <3 sailors alive  | Traitor achieves collapse |

### Voting Rules

* A correct vote ends the game immediately (Crew Victory).
* An incorrect vote removes a loyal sailor, continuing the game.
* Multiple votes may occur across different days.

---

## 9. Design Principles

### 9.1 Research Objectives

* Investigate emergent deception and trust in  **language-mediated RL** .
* Explore **long-horizon temporal reasoning** under uncertainty.
* Encourage grounded, interpretable communication between autonomous agents.

### 9.2 Hackathon Evaluation Focus

| Criterion                   | Weight | Description                                                               |
| --------------------------- | ------ | ------------------------------------------------------------------------- |
| **Creativity**        | 50%    | Survival + deception + base-building hybrid; multi-layer map.             |
| **Technical Depth**   | 25%    | Large state space, multi-agent communication, LoRA-tuned language models. |
| **Narrative Quality** | 25%    | Natural storytelling through evidence logs and voting events.             |

---

## 10. Project Structure

```
marooned_env/
├── config.py           # Core constants and balancing parameters
├── models.py           # Data schemas (Observation, Action, Inventory)
├── game_state.py       # Game logic and world tracking
├── environment.py      # OpenEnv-compatible RL environment
└── __init__.py

notebooks/
├── marooned_training.ipynb   # Main training pipeline (Unsloth + TRL)
└── marooned_eval.ipynb       # Replay, visualization, evaluation

docs/
├── README.md                 # Documentation file
├── pitch_outline.md          # Presentation outline for hackathon
└── rules_summary.md          # Quick reference guide

assets/
└── (maps, screenshots, and visualizations)
```

---

## 11. Quick Start Example

```python
from marooned_env import MaroonedEnv

# Initialize environment
env = MaroonedEnv(render_mode="human", seed=42)

# Reset environment to obtain initial observations
observations = env.reset()

# Define example actions for each sailor
actions = {
    "Alice": Action("Alice", ActionType.MOVE_NORTH),
    "Bob":   Action("Bob", ActionType.GATHER_RESOURCE, target_resource_id="WOOD_1"),
    # ... additional sailors
}

obs, rewards, dones, truncated, info = env.step(actions)
```

---

## 12. Implementation Progress

### Phase 0 — Bootstrap (Completed)

* [X] Repository structure defined
* [X] Config constants and balance tables
* [X] Data models implemented
* [X] Game state foundation
* [X] OpenEnv environment skeleton

### Phase 1 — Core Mechanics (Completed)

* [X] Movement and energy system
* [X] Resource collection and inventory logic
* [X] Shipbuilding actions
* [X] Poison mechanics integration

### Phase 2 — Social Layer (Completed)

* [X] Dialogue and communication system
* [X] Evidence tracking and reputation metrics
* [X] Voting and exile resolution
* [X] Traitor ability scripting

### Phase 3 — Training and Evaluation (Pending)

* [X] LLM agent wrapper for policy learning
* [X] PPO/GRPO training loop
* [ ] Evaluation metrics and telemetry
* [ ] Replay and visualization notebooks

---

## 13. Citation

```bibtex
@software{marooned2025,
  title   = {MAROONED: A Multi-Agent Deception Environment for Reinforcement Learning},
  author  = {Your Name},
  year    = {2025},
  note    = {Created for the OpenEnv Hackathon},
  license = {MIT}
}
```

---

## 14. License

**MIT License** — Free to use, modify, and build upon.

Attribution appreciated.

---

## 15. Closing Note

> *“Built with algorithms, suspicion, and a touch of salt air.”*
>
> MAROONED aims to push the limits of multi-agent reasoning — where trust, deception,
>
> and cooperation emerge not from rules, but from survival instincts encoded in learning itself.
