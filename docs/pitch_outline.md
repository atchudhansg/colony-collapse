# 🎬 MAROONED - Hackathon Pitch Outline

**Duration**: 5 minutes  
**Goal**: Convince judges this is creative, technically excellent, and tells a great story

---

## 📊 SLIDE 1: TITLE (10 seconds)

```
🏴‍☠️ MAROONED
A Multi-Agent Deception Environment

[Dramatic image: Island map with 5 sailor icons, one glowing red]

Tagline: "Pirates of the Caribbean meets Alice in Borderland meets Among Us"
```

**Script**: "Imagine 5 AI sailors shipwrecked on a mysterious island. They have 100 days to rebuild their ship and escape. But one of them is a traitor trying to sabotage everything."

---

## 📊 SLIDE 2: THE PROBLEM (30 seconds)

### Current RL Environments Are Limited

**Existing Problems:**
- ❌ Short-horizon tasks (thousands of steps, not hundreds of thousands)
- ❌ Simple spatial environments (flat grids)
- ❌ No deception mechanics (everyone cooperates or competes openly)
- ❌ Limited natural language interaction

**What's Missing:**
- Complex social dynamics
- Long-term strategic planning
- Trust and betrayal
- Detective work through evidence

**Script**: "Most RL environments focus on short-term goals in simple spaces. We wanted something that requires strategic planning over months, social deception, and detective reasoning - all through natural language."

---

## 📊 SLIDE 3: THE GAME MECHANICS (60 seconds)

### Three Core Systems

```
┌─────────────────────┐
│   🗺️ EXPLORATION    │
│  - 3D multi-level   │
│  - Mountains/Caves  │
│  - Resource gathering│
└─────────────────────┘
         ↓
┌─────────────────────┐
│   🚢 COOPERATION    │
│  - Build ship       │
│  - Share resources  │
│  - Survive together │
└─────────────────────┘
         ↓
┌─────────────────────┐
│   🎭 DECEPTION      │
│  - Hidden traitor   │
│  - Poison mechanics │
│  - Evidence system  │
└─────────────────────┘
```

**Key Features:**
1. **100 days × 100 turns = 10,000+ decisions** (long-horizon RL)
2. **Multi-level 3D island** (mountains, ground, caves)
3. **Gradual poison death** (3-day timeline, curable with antidote)
4. **Evidence logging** (tracks lies, suspicious behavior)
5. **Natural language** (all communication is text-based)

**Script**: "The game combines three challenges. First, exploration - a 3D island with different resource distributions at each level. Second, cooperation - you need to work together to build components of a ship. Third, deception - one AI is secretly sabotaging while trying to avoid detection."

---

## 📊 SLIDE 4: DEMO GAMEPLAY (90 seconds)

### Story Example: The Death of Bob

**Day 3:**
- Bob's energy critical (15/100)
- Calls SOS: "Help! I'm at Beach-South, starving!"
- Eve responds: "I'll bring you food!"

**Day 5:**
- Bob shows early symptoms: [POISONED]
- Evidence log updates: "Bob received food from Eve on Day 3"

**Day 7:**
- Bob's symptoms severe: Energy dropping 20/turn
- Alice: "Someone poisoned Bob! Who gave him food?"
- Eve: "I gave him berries! Maybe they were bad?"
- Charlie: "I saw Eve near the poison tablets on Day 2..."

**Day 8:**
- Emergency vote called
- 4 votes → Eve eliminated
- Role revealed: **TRAITOR**
- Remaining sailors complete ship on Day 68
- **SAILORS WIN**

**Visual**: Show actual game replay with:
- Island map with sailor positions
- Evidence log screenshots
- Chat messages between AIs
- Ship progress bar growing

**Script**: "Let me show you how a game actually plays out. On Day 3, Bob is starving and calls for help. Eve, the traitor, brings him 'food' - but it's actually poison. Bob doesn't know yet. Two days later, symptoms appear. The other AIs notice the timeline matches. They call a vote, catch the traitor, and successfully escape."

---

## 📊 SLIDE 5: TECHNICAL HIGHLIGHTS (45 seconds)

### Why This is Hard

**State Space Complexity:**
```python
Observation includes:
- 3D position (x, y, level)
- Energy (0-100)
- Backpack inventory (20 slots)
- Spatial view (5-tile radius)
- All sailors' public status
- Evidence log (growing over time)
- Message history
- Ship progress
- Shared knowledge map
```

**Action Space:**
- 30+ action types (movement, gathering, building, communication, voting)
- Context-dependent validity
- Cooperative constraints (building needs 2+ sailors)

**Emergent Behaviors:**
- Traitor must learn to:
  - Lie convincingly about locations
  - Misdirect team away from good resources
  - Poison without getting caught
  - Deflect suspicion onto others

- Honest sailors must learn to:
  - Cross-reference claims with observations
  - Build evidence cases
  - Balance trust vs. paranoia
  - Coordinate despite traitor interference

**Script**: "From a technical perspective, the state space is massive - tracking 3D positions, inventories, energy, evidence, and conversation history. The action space has 30+ types with complex dependencies. Most importantly, AIs must learn emergent deceptive and detective behaviors purely from rewards."

---

## 📊 SLIDE 6: INNOVATION POINTS (30 seconds)

### Hackathon Criteria Checkboxes

✅ **Creativity (50 pts):**
- First RL environment combining survival + social deception + base building
- Multi-level 3D exploration
- Gradual poison mechanics
- Evidence-based detective work

✅ **Technical Excellence (25 pts):**
- Long-horizon RL (10K+ steps)
- Language-based multi-agent coordination
- Hidden information asymmetry
- Complex state dependencies

✅ **Storytelling (25 pts):**
- Pirates/survival theme
- Natural narrative emergence
- Evidence logs read like mysteries
- Dramatic moments (poison reveals, votes)

✅ **Bonus Criteria:**
- ✓ Long horizon
- ✓ Model vs Model (traitor vs sailors)
- ✓ Multiple island configurations
- ✓ New environment (built from scratch)

**Script**: "We hit all the hackathon criteria. Maximum creativity - nothing like this exists. Strong technical challenge - long-horizon planning with deception. Incredible storytelling - every game generates a unique narrative."

---

## 📊 SLIDE 7: RESULTS (IF TRAINED) (45 seconds)

### Training Results

**Metrics:**
- Win rate (Sailors vs Traitor)
- Average survival time
- Ship completion percentage
- Evidence detection accuracy
- Successful deception rate

**Interesting Learned Behaviors:**

Example findings:
- "Traitor learned to volunteer for solo missions to hide resource theft"
- "Honest sailors learned to travel in pairs after Day 20 to verify claims"
- "Antidote hoarding emerged as optimal strategy"
- "Traitors learned to poison early, deflect late"

**Failure Cases:**
- "Sometimes honest sailors voted each other out in paranoia"
- "Traitor occasionally self-reported by accident in long conversations"

**Script**: "In training, we saw fascinating emergent behaviors. Traitors learned to volunteer for solo missions to steal resources without witnesses. Honest sailors learned to travel in pairs to verify each other's claims. We even saw paranoia spirals where honest sailors eliminated each other by mistake."

---

## 📊 SLIDE 8: FUTURE WORK (20 seconds)

### Extensions

**Tier 2 Enhancements:**
- Weather events (storms force meetings, fog reduces vision)
- Inter-sailor trading mechanics
- Footprint tracking (physical evidence of presence)

**Tier 3 Polish:**
- Multi-traitor mode (2 traitors vs 3 sailors)
- Different island layouts
- Ship building mini-games
- Visual renderer (top-down map view)

**Research Applications:**
- Deception detection in LLMs
- Long-horizon planning under uncertainty
- Coalition formation in adversarial settings
- Natural language grounding in complex environments

---

## 📊 SLIDE 9: CLOSING (10 seconds)

```
🏴‍☠️ MAROONED

"5 sailors. 1 traitor. 100 days to escape.
Will they cooperate... or perish?"

[Live demo invitation]

GitHub: [your-repo]
Contact: [your-email]
```

**Script**: "MAROONED is ready to play today. We'd love for you to try it, watch replays, and see if you can spot the traitor. Thank you!"

---

## 🎭 DELIVERY TIPS

### Tone & Energy
- **Enthusiastic but professional**
- Use dramatic pauses during story example
- Show genuine excitement about emergent behaviors
- Don't oversell - let the complexity speak for itself

### Visuals
- Keep slides minimal (more images, less text)
- Use game footage/screenshots heavily
- Show actual evidence logs and chat transcripts
- Animated ship progress bar

### Q&A Preparation

**Expected Questions:**

1. **"How do you handle the huge action space?"**
   - "We use LLMs to parse natural language observations into actions. The model sees: 'You're at the forest. You see wood nearby. Bob is at the beach.' and outputs: 'I'll gather the wood then message Bob to coordinate.'"

2. **"Isn't this just Among Us?"**
   - "Among Us is real-time reflex-based with simple binary tasks. We have long-term resource management, survival mechanics, 3D exploration, and 100-day planning horizons. The deception is one layer of a much deeper strategy game."

3. **"How do you train this?"**
   - "We use LLM-based agents with prompt engineering initially, then fine-tune on successful gameplay trajectories. The reward signal comes from win/loss, ship progress, and survival time."

4. **"What if the traitor is caught on Day 1?"**
   - "That's part of the challenge! The traitor must balance aggression with stealth. If caught early, sailors win but likely haven't gathered enough resources yet. If caught late, more dramatic but ship might be nearly done."

5. **"Computational cost?"**
   - "One full game is ~10K environment steps. With LLM agents, that's ~10K API calls. We batch/cache observations. For training, we use smaller models or distillation from GPT-4 demonstrations."

---

## 📈 SUCCESS METRICS

**You've succeeded if judges:**
- ✅ Say "wow" or lean forward during story example
- ✅ Ask technical questions (shows interest in depth)
- ✅ Mention it could be a research paper
- ✅ Want to play it themselves
- ✅ Compare it favorably to published environments

**Red flags:**
- ❌ Confused about basic mechanics (simplify explanation)
- ❌ "Seems too complex to actually work" (show evidence it runs)
- ❌ "Just like [X]" (emphasize unique combinations)

---

**Good luck! 🏴‍☠️**
