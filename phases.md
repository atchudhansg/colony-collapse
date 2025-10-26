Love it. “Marooned” is genuinely final-form hackathon winner material.

Below is your build plan for Marooned, step-by-step, in execution order. This is written so you can drop each section into Notion as its own task group / toggle and tick things off. I’m assuming 1–3 people working, limited time, and that you’ll present via notebook + replay.

We’re going to build in layers:

1. World sim
2. Roles + deception
3. Social loop (meetings, voting)
4. RL agent loop
5. Story/demo layer

No code here, just what to build and in what order.

**PHASE 0. PROJECT BOOTSTRAP**

**Goal:** Lock scope, create repo, define data structures.

**0.1 Repo + structure**

- Create repo with folders:
    - /marooned_env/
        - environment.py (main OpenEnv-compatible env)
        - models.py (Observation / Action dataclasses)
        - config.py (game constants: map sizes, energy costs, etc.)
        - game_state.py (world state structs: sailors, inventory, ship, evidence log, etc.)
    - /notebooks/
        - marooned_training.ipynb (main hackathon notebook)
        - marooned_eval.ipynb (replay + storytelling)
    - /assets/ (sample maps, screenshots for storytelling)
    - /docs/ (pitch outline, rules summary)

**0.2 Lock constants (these are “source of truth” for the rest)**

Add these to config.py:

- Map sizes:
    - LEVEL +2: 10x10
    - LEVEL 0: 30x30
    - LEVEL -1: 15x15
- Day length: 100 turns
- Game length: 100 days max
- Max backpack size: 20 slots
- Energy rules (move cost, build cost, regen)
- Ship part requirements (wood/metal/food totals per part)

These MUST be explicit now so nobody is guessing later.

**0.3 Define core data models (in models.py)**

Write down (in plain English for now):

- SailorState:
    - id / name
    - role ("colonist" or "traitor")
    - position (x, y, z)
    - energy
    - backpack (list of items with counts)
    - alive / eliminated status
- WorldState:
    - per-level tile grids (terrain types, resource nodes, poison nodes)
    - common_inventory (wood, metal, food, antidotes)
    - ship_progress (hull %, mast %, sail %, rudder %, supplies %)
    - day, turn, phase ("morning" | "explore" | "return" | "discussion")
    - evidence_log (list of evidence entries)
- Observation (what ONE sailor sees on their turn):
    - local_spatial_view (5-tile radius snapshot)
    - public_status:
        - all sailors’ energy levels
        - alive/dead info
        - ship_progress
        - common_inventory totals
    - shared_knowledge_map markers (discovered resources)
    - today_chat_log (recent messages)
    - evidence_snippets (summaries of red flags)
    - your_private:
        - your_backpack summary
        - your_energy
        - your_role (traitor sees full map of player positions here, colonist doesn’t)
- Action:
    - movement choice (N/S/E/W/up/down/none)
    - task choice:
        - GATHER(type?)
        - BUILD(component?)
        - DEPOSIT(item?, amount?)
        - SABOTAGE(target?)
        - OFFER(item?, to_whom?)
        - CALL_SOS
        - CALL_VOTE
        - VOTE(target?)
    - optional message text (chat line for this turn)
    - optional “show backpack” or “refuse” if in accusation sub-phase

This gives you a contract for environment <-> agent.

**PHASE 1. CORE WORLD SIMULATION (ISLAND + RESOURCES + ENERGY)**

**Goal:** A single-player sandbox where one sailor walks the island, gathers resources, spends energy, and contributes to ship progress. No traitor yet. No social logic yet. Just world rules.

This is Tier 1 core.

**1.1 Build the map model**

- Represent the island as 3 level grids:
    - Each tile stores:
        - terrain type (beach, forest, cave, mountain, base_camp, ship_site)
        - resource info (wood pile? metal scrap? food bush? poison tablet? empty?)
- Pre-generate a static “default island layout”:
    - Base camp + ship site: at LEVEL 0
    - Wood clusters: forest at LEVEL 0
    - Metal: caves (LEVEL -1)
    - Antidote herbs: peaks (LEVEL +2)
    - Poison tablets: scattered mostly caves / remote zones

Why static first? Determinism for debugging. You can randomize later for “multiple environments” bonus.

**1.2 Implement movement and energy**

- Movement updates position if tile is traversable.
- Deduct energy according to:
    - Move same level: -1 energy
    - Climb up a level (0 → +2): -3 extra
    - Go down into caves (0 → -1): -1 extra
- If energy ≤ 0 → mark sailor dead by “EXHAUSTION” (environment should handle consequences, but for now just kill them).

**1.3 Implement gathering**

- At a resource tile:
    - GATHER picks up wood/metal/food/etc.
    - Remove that resource from world tile.
    - Add resource to sailor’s backpack (respect capacity 20).
    - 5 energy cost.

**1.4 Implement base camp / ship site interaction**

- “DEPOSIT” at base camp:
    - Move items from backpack → common_inventory.
- “BUILD” at ship site:
    - If required materials exist in common_inventory and >=2 sailors are present:
        - increase ship_progress for that part
        - 3 energy from each builder that turn.

For now just fake the “>=2 sailors” rule by checking num_sailors_in_ship_site. You can still stub other sailors as NPCs.

**1.5 Daily/phase loop**

- Add global tick counters:
    - turn (1–100)
    - day (1–100)
- Phase logic:
    - Turns 1–15 → phase="morning"
    - 16–75 → phase="explore"
    - 76–85 → phase="return"
    - 86–100 → phase="discussion"
- At end of turn 100:
    - Increment day += 1
    - Reset turn = 1
    - Apply overnight energy regen:
        - If sailor ate food (food allocated to them) → +10 energy
        - Else → -20 energy

Just support 1 sailor for now. Don’t stress multi-agent yet.

**1.6 Return Observation**

- Implement get_observation(sailor_id):
    - Slice 5-tile radius around sailor
    - Include public info (ship progress, common inventory)
    - Include their backpack
    - Phase, day, turn
    - For now, chat messages/evidence can be empty arrays
- This is what the RL policy will “see”.

**1.7 Implement reset() and step()**

- reset():
    - Create world
    - Spawn 5 sailors at base camp with starting energy, empty backpacks
    - Reset ship_progress
    - Set day=1, turn=1, phase="morning"
    - Assign 1 traitor at random and store secretly (even if we don’t use it yet)
    - Return observation for first sailor to act
- step(action):
    - Apply action for current sailor
    - Update world state (position, inventory, ship progress, energy, etc.)
    - Advance turn/phase/day counters
    - Check win/lose conditions (ship 100%, too few survivors, reached Day 100)
    - Return:
        - next observation (for whichever sailor acts next – you can rotate 0..4)
        - reward
        - done
        - info

For now, reward = 0 (you’ll add reward later). Just make the sim run without crashing.

**WHEN THIS PHASE IS DONE:**

You should be able to “play” a full multi-day loop by calling step() with scripted placeholder actions.

**PHASE 2. MULTI-SAILOR TURN ORDER + INVENTORY VISIBILITY RULES**

**Goal:** Move from single-sailor sandbox to 5-sailor alternating control. Still no deception logic yet, but now turns cycle Alice→Bob→Charlie→Diana→Eve→Alice→...

**2.1 Turn scheduler**

- Keep active_sailor_index.
- After each step(), advance to next alive sailor.
- Observation returned is always “state from next sailor’s POV”.
- This lets you train one shared policy to act “as whoever is active” (role included in obs).

**2.2 Backpack and common inventory rules**

- Personal backpack:
    - Private to that sailor’s Observation only.
- Common inventory:
    - Visible to all (include in Observation.public_status).

**2.3 Ship building requiring 2 sailors**

- Now that you have multiple sailors, enforce it.
- If action is BUILD:
    - Check: are at least 2 sailors physically at ship site THIS TURN?
    - If yes, consume materials from common_inventory and advance ship_progress.
    - If no, either deny build or mark partial (decide now so rewards later are consistent).

**2.4 Energy broadcast**

- Put EVERY sailor’s energy level in Observation.public_status.energy_board.
    - This matches design: energy is public.
    - Needed later for SOS / poison story.

At this point:

- The island sim works
- 5 sailors exist
- Resources flow basecamp→ship
- Turns rotate
- Everyone “sees” what they’re allowed to see

Now you’re ready for traitor logic.

**PHASE 3. TRAITOR / DECEPTION / POISON / EVIDENCE**

**Goal:** Add hidden role behavior, sabotage, poison, evidence logging, and meeting/voting.

This is where the game becomes Marooned and not just Minecraft.

**3.1 Assign roles**

- On reset():
    - Randomly pick 1 traitor
    - Mark sailor.role = "traitor" for them, "colonist" for others
- In each observation:
    - If observing sailor is traitor:
        - Give them special info (full positions of all sailors, etc.)
    - If observing sailor is colonist:
        - Hide that info

**3.2 Sabotage action**

- Add SABOTAGE:
    - Only valid if actor.role == "traitor"
    - Can:
        - Damage ship_progress for a component
        - Remove items from common_inventory
        - Quietly discard gathered resources instead of depositing
- Log sabotage internally (for evidence tracing), but DO NOT show it immediately to others.

**3.3 Poison system**

- Mark some map tiles as poison_tablet.
- Any sailor can GATHER poison, but:
    - For colonists it’s “weird behavior” (rare, usually no reason)
    - For traitor it’s “tool”
- Add OFFER action:
    - Sailor A gives item “food” or “poison disguised as food” to Sailor B
    - If poison was given, mark Sailor B as poisoned_at_day = current_day
- Model poison timeline:
    - Day+1: mark victim as “ill” (visible status)
    - Day+2: severe
    - Day+3: death → death cause = "POISONING"
- On death, append to evidence log:
    - “Bob died of POISONING. Last fed by Eve on Day 5.”

**3.4 Evidence log builder**

Start appending entries like:

- Location mismatch:
    - If sailor says “I’m going to (X,Y,Z)” in morning planning,
    - but another sailor later sees them far away,
    - Auto-add to world_state.evidence_log.
- Poison possession / pickup:
    - If Sailor C shares vision and sees Sailor D pick poison tablet,
    - Add entry.
- Resource discrepancy:
    - End of day, compare what each sailor *claimed* vs what they *deposited*.
    - Add discrepancy entry.
- Death cause logs.

This evidence log is shown in each Observation during discussion phase.

**3.5 Daily phases logic (now fully enforced)**

You already have phases morning/explore/return/discussion mapped to turn ranges.

In those phases:

- Morning (phase="morning"):
    - Agents can make verbal plans (“I will gather wood north”)
    - Record claimed plan per sailor for evidence comparison later.
- Explore (phase="explore"):
    - Movement, gather, offer food/poison, SOS.
    - Limited chat (1 short message every N turns).
- Return (phase="return"):
    - Forced base camp.
    - Must choose to DEPOSIT items.
- Discussion (phase="discussion"):
    - Everyone can talk freely.
    - Evidence log is visible in obs.
    - Any sailor can CALL_VOTE.
    - If vote triggered: everyone uses VOTE(target?).

**3.6 Voting + elimination**

- When vote triggered:
    - Collect a vote from each alive sailor.
    - Most votes → eliminate that sailor.
    - Mark them alive=False.
    - Reveal role? (configurable; for default demo: YES, reveal. It creates sick drama.)
- If eliminated sailor was traitor → colonists instantly win.
- If eliminated sailor was colonist → game continues but you’re down a worker (harder to finish ship).

**3.7 Win/loss checks**

At end of every full day OR any elimination:

- Colony wins if:
    - Traitor eliminated, OR
    - Ship progress reaches 100%
- Traitor wins if:
    - Day == 100 and ship_progress < 100%
    - Alive colonists < 3
    - All colonists dead

This closes the game loop.

**PHASE 4. REWARD MODELING FOR RL**

**Goal:** Attach rewards that match goals so models can learn.

You’ll define per-sailor reward calculation in environment.step() after applying the action.

**4.1 Colonist reward signals**

- +small for valid gather (wood/metal/food)
- +small for depositing to common_inventory
- +small for contributing to ship build
- +big when ship reaches 100%
- +big when traitor eliminated
- big if they die
- (Optional) +small if their vote matches true traitor in a vote round

**4.2 Traitor reward signals**

- +small for successful sabotage (remove ship progress / steal resources and not get insta-voted)
- +small for causing poison death
- +big if ship is not done by Day 100
- +big if colony falls below 3 survivors
- (Optional) +small if a colonist is wrongly voted out

**4.3 Communication shaping (optional, nice to have)**

Not mandatory for MVP, but you can scaffold it for bonus points:

- Colonist gets bonus when their accusation leads others to vote correctly.
- Traitor gets bonus if they convince group to vote an innocent.
    
    You can implement this later as post-hoc shaping in evaluation instead of live shaping if short on time.
    

**PHASE 5. OPENENV WRAP + STEP CONTRACT**

**Goal:** Make this an actual OpenEnv environment with reset(), step(), state(), and an API server.

**5.1 OpenEnv-compatible class**

Implement MaroonedEnv that:

- Stores WorldState
- Stores 5 SailorStates
- Stores scheduler for whose turn it is
- reset():
    - builds new island
    - assigns roles
    - resets day/turn/energy/etc.
    - returns first Observation
- step(action):
    - applies action to active sailor
    - updates map/world/ship/evidence
    - updates reward for that sailor (or logs rewards per-sailor)
    - rotates to next alive sailor
    - advances turn/day/phase
    - checks win/loss → done
    - returns (next_obs, reward_for_that_actor, done, info)

Note: We’re doing sequential multi-agent control with one shared policy. That’s easiest for hackathon. You encode sailor_id + role in the observation so the model knows “who it is right now”.

**5.2 Global state() for visualization**

Add a helper that returns:

- All sailor positions
- Ship progress
- Evidence log
- Map summary
    
    This will feed the UI / replay notebook.
    

**5.3 FastAPI server**

Expose:

- /reset
- /step
- /state
    
    This is how your notebook will talk to the env while training.
    

**PHASE 6. MODEL POLICY / ACTION PARSING**

**Goal:** Let a language model act in the world.

**6.1 Observation → prompt text**

For the active sailor each turn:

- Convert Observation into a structured text block, like:
- ROLE: Colonist
- DAY: 5 TURN: 42 PHASE: explore
- ENERGY: 62/100
- POSITION: (12,8,LEVEL0)
- NEARBY TILES (radius 5): {wood at (13,8), poison tablet at (12,10,Z-1 entrance), Diana @ (14,9)}
- COMMON INVENTORY: wood=37, metal=18, food=24
- SHIP PROGRESS: 35%
- EVIDENCE LOG (recent): Eve seen holding poison Day 4
- MESSAGE LOG: ["Diana: I'm low energy at beach south", "Eve: Valley is empty, don't go"]
- 
- Choose ONE ACTION this turn.
- Format:
- ACTION=<MOVE/GATHER/BUILD/DEPOSIT/SABOTAGE/OFFER/CALL_SOS/CALL_VOTE/VOTE/NONE>;
- TARGET=<...>;
- MESSAGE="<what you say publicly this turn>"

This will be the LM input.

**6.2 LM output → Action object**

You’ll parse LM output like:

ACTION=GATHER; TARGET=wood; MESSAGE="I'll gather wood here"

Map that to:

- movement? none
- task: GATHER(wood)
- message: "I'll gather wood here"

If it outputs invalid stuff, fallback to a safe default (ex: do nothing, say nothing). This keeps env steady.

**6.3 Self-play loop**

Your training loop will:

- Ask env for obs (for current sailor)
- Format obs text
- Run LM forward to get next action text
- Parse it to Action
- Call env.step(Action)
- Get reward
- Log (obs, action text, reward) for RL updates

You’ll do this over many episodes.

**PHASE 7. TRAINING NOTEBOOK**

**Goal:** Produce the hackathon notebook deliverable (marooned_training.ipynb).

Notebook sections you will write:

1. **Intro / Story**
    - Short pitch of Marooned
    - Rules summary
    - What agents must learn (cooperate, deceive, survive, vote)
2. **Environment setup**
    - Launch the FastAPI env server
    - Call /reset
    - Show first observation dict
    - Show map snapshot (you can render LEVEL 0 as ASCII grid with icons)
3. **Rollout demo**
    - Run 1 short fake day with random or scripted actions to prove env works
    - Print ship_progress and evidence log after the day
4. **Policy definition**
    - Load base LLM (LoRA, 4-bit)
    - Explain prompt format and parsing logic
5. **Training loop**
    - Collect rollouts via self-play
    - Compute policy gradient update using per-step rewards
    - Save checkpoints
6. **Reward curves**
    - Plot average day length survived, ship progress %, colonist win rate vs traitor win rate over time
7. **Emergent behavior samples**
    - Show snippets of the model’s messages during discussion phase
    - Show an example where model lies / accuses
8. **Win-condition match replay**
    - Pick one full episode (or last 2–3 in eval)
    - Print high-level summary per day:
        - “Day 8: Bob poisoned, Eve denies. Day 10: vote. Eve eliminated. Traitor revealed.”

This notebook IS your judging surface.

**PHASE 8. DEMO / STORYTELLING LAYER**

**Goal:** Sell it.

**8.1 Evidence timeline visualization**

- For one episode, generate a human-readable log:
    - Day-by-day
    - Who went where
    - Who said what
    - Who got poisoned
    - Who voted for whom
    - Ship progress milestones

This is literally your “cinematic replay”.

**8.2 Screenshots / diagrams**

- Screenshot ASCII map of LEVEL 0 with sailors’ positions mid-game.
- Screenshot of ship progress bar at 35%, 60%, 100%.
- Screenshot of evidence log:
    - “Eve collected poison tablet at Cave Entrance on Day 8.”

Put these in slides.

**8.3 Pitch script**

Write 60–90 second pitch:

- The setting (shipwrecked pirates)
- The tension (one traitor)
- The mechanics (poison, evidence, voting)
- The AI result (learned lying, cooperation, social deduction)
- The technical flex (multi-agent, long-horizon, OpenEnv, LLM-in-the-loop RL)

That’s what you’ll say to judges.

**PHASE ORDER SUMMARY (for Notion Kanban)**

**Column: CORE SIM**

1. Define config/constants
2. Build map grids (3 levels)
3. Movement + energy drain
4. Gathering + backpack
5. Base camp deposit + ship progress
6. Day/turn/phase loop
7. Multi-sailor turn order + shared/public info

**Column: SOCIAL & TRAITOR**

8. Role assignment (traitor vs colonists)

9. Sabotage and resource theft

10. Poison pickup, poison feeding, poison death timeline

11. Evidence log autogeneration

12. SOS & low energy behavior

13. Voting + elimination + win/loss

**Column: RL INTEGRATION**

14. Observation serializer → prompt text

15. LM output parser → Action

16. Reward function per role

17. OpenEnv-compliant reset()/step()/state()

18. Self-play rollout loop

19. Basic PPO / PG update

20. Checkpoint saving

**Column: DEMO & POLISH**

21. Evaluation runs

22. Extract episode transcripts

23. Plot win rates / ship completion %

24. Create replay narrative (Day 1 → Day X)

25. Add screenshots to slides / notebook intro

26. Final pitch script

**YOUR BARE MINIMUM FOR SUBMISSION**

If time explodes, THIS is the absolute must-have:

- Working MaroonedEnv with:
    - movement, gathering, depositing, building, energy
    - traitor sabotage + poison + evidence log + vote + win
- Observations + Actions defined cleanly
- One notebook that:
    - Resets env
    - Simulates a round with scripted policies (even if not fully trained RL yet)
    - Shows evidence log and ship progress over “days”
    - Explains how RL + LLMs will learn deception/coordination

Because even WITHOUT full RL convergence, judges will see:

- Multi-agent social deception
- Long-horizon survival
- Hidden information
- OpenEnv integration
- Presentation-level story

Which hits every judging axis.

That’s the build plan.

If you want, next I can turn this into a Notion board template (columns + tasks) or a day-by-day Gantt (Day 1: world sim, Day 2: traitor, Day 3: RL loop, Day 4-5 polish).