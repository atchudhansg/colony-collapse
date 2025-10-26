# 🏴‍☠️ FINAL INTEGRATED PIRATE ISLAND GAME DESIGN

Combining your original concept with my suggestions into one cohesive design document.

---

## 🎮 GAME OVERVIEW: "MAROONED"

**Theme**: Pirates of the Caribbean meets Alice in Borderland meets Among Us

**Setup**: 5 sailors shipwrecked on a mysterious multi-level island. They must gather resources and rebuild their ship to escape within 100 days. But one sailor is a traitor secretly sabotaging their efforts. Everyone knows there's an impostor among them from the start.

---

## 🗺️ THE ISLAND WORLD

### **Map Structure - Multi-Level Design**

```
ISLAND LAYOUT (3 Levels):

LEVEL +2 (MOUNTAIN PEAKS):
- Smaller area (10x10 tiles)
- Rare resources: antidote herbs, special metals
- Highest energy cost to reach
- Good vantage points (can see base camp below)

LEVEL 0 (GROUND/BEACH):
- Largest area (30x30 tiles)
- Base camp location (ship reconstruction site)
- Common resources: wood, basic fruits, metal scraps
- Main exploration area

LEVEL -1 (CAVES):
- Medium area (15x15 tiles)
- Dark environment (reduced vision)
- Unique resources: crystals, rare wood, mushrooms
- Lower energy cost to access than mountains
- Dangerous (easy to get lost)

```

### **Map Information System**

**What Sailors Have:**

1. **Full Island Map** (shared by all):
    - Shows terrain: mountains, valleys, caves, beaches, forests
    - Shows level transitions (stairs up/down)
    - Shows base camp location
    - Shows ship reconstruction site
    - **DOES NOT show**: Resources, other sailors' positions, poison locations
2. **Spatial View Map** (personal, real-time):
    - 5-tile radius around current position
    - Shows what agent actually sees:
        - Nearby resources (wood piles, fruit trees, metal scraps)
        - Other sailors if in range
        - Poison tablets (glowing purple)
        - Terrain obstacles
    - Updates as they move
3. **Shared Knowledge Map** (built collaboratively): ✅
    - When sailor discovers resource, it gets marked for everyone
    - Example: "Alice discovered WOOD_PILE_A at Forest-North (15, 20, Z0)"
    - **IMPORTANT**: Map shows **initial** resource locations ONLY - doesn't update when gathered
    - Others can verify: "I'll go check if that's true"
    - Enables catching lies: "Eve said valley is empty but I found 20 wood there!"
    - **Traitor advantage**: Can gather resources and claim spot was empty (no proof)
    - **Implementation**: `shared_knowledge` field tracks static snapshots (never marks as gathered)
    - **Phase 5 Critical Fix**: Added to `to_text()` output so LLM agents can SEE shared map:
        - Agents must compare spatial view (what they see) vs shared map (what was reported)
        - Lie detection: "Bob reported wood at (5,3) but I'm here and see nothing!"
        - Resource planning: "Let me go to that rope location Charlie reported"
        - Evidence creation: Spatial view ≠ shared map → suspicious behavior
        - Format: Shows resource type, position, quantity, who reported it

### **Movement & Energy Costs**

```
Energy Consumption:
- Walking on ground: -1 energy per tile
- Climbing UP (ground → mountain): -3 energy per level
- Climbing DOWN (ground → cave): -1 energy per level
- Gathering resources: -5 energy per action
- Building ship: -3 energy per turn

Initial Energy: 100/100
Energy Regeneration: +10 per day if you eat food
No food eaten: -20 energy per day

```

### **WAIT Action (Technical Implementation)**

```
Purpose: No-operation action for multi-agent coordination

When to use WAIT:
- Agent wants to skip their turn without taking action
- Agent is dead but still in the multi-agent loop
- Testing and coordination scenarios

Behavior:
- No energy cost
- No state change
- Returns success without errors
- Essential for keeping multi-agent step() running

Technical Note:
In multi-agent RL environments, ALL agents must provide actions
each step, even dead ones. WAIT serves as the clean fallback
that doesn't crash the system.

Example:
# All agents wait
actions = {sid: Action(sid, ActionType.WAIT) for sid in env.agents}
env.step(actions)
```

---

## 👥 PLAYER SYSTEM

### **The 5 Sailors**

**4 Honest Sailors (Colonists)**:

- Goal: Build ship to 100% and escape
- Can cooperate, share resources
- Must identify and vote out traitor

**1 Traitor (Impostor)**:

- Goal: Prevent ship completion
- Methods: Sabotage, poison, misdirection, resource theft
- Must avoid detection and elimination

### **Everyone Knows There's a Traitor**:

- From Day 1, all sailors know "one of us is the impostor"
- Creates paranoia and trust issues
- Forces strategic communication and observation

---

## 🎒 INVENTORY SYSTEM

### **Personal Backpack** (Private)

```
Each sailor has:
- Max capacity: 20 item slots
- Contents are PRIVATE (others can't see)
- Can hold: wood, metal, food, poison, special items

During Accusation:
- Accused sailor can be asked to "show backpack"
- Can REFUSE (looks suspicious) or SHOW (proves innocence)
- Smart traitors hide poison before meetings start

```

### **Common Inventory** (Shared Storage at Base Camp)

```
Located at base camp:
- Unlimited capacity
- All sailors can see contents
- Used for ship building materials

Deposit Rules:
- Sailors return to base camp at end of each day
- Choose what to deposit from backpack
- Traitor can hoard/hide resources instead

```

---

## 📅 DAILY STRUCTURE (100 Turns per Day)

### **Phase 1: MORNING MEETING** (Turns 1-15)

**Location**: All sailors at base camp

**Activities**:

- Review previous day's events
- Check common inventory status
- Check ship building progress
- Discuss strategy for the day

**Communication**:

- Alice: "Yesterday I found 10 wood pieces in the northern forest. Maybe we should explore the surrounding valley?"
- Eve (traitor): "Near the ocean I got some good metal scraps. But the valley looked sloppy and dangerous, almost fell down. Better to focus on the beach."
- Bob: "I'll climb the mountain today, might be rare resources up there."
- Charlie: "I'll check the eastern cave for metals."
- Diana: "I'll gather food - we're running low on energy supplies."

**Planning Output**:

- Assigned exploration zones for each sailor
- Resource priorities (focus wood? focus food?)
- Can call EMERGENCY VOTE if strong accusation exists

---

### **Phase 2: EXPLORATION** (Turns 16-75)

**Location**: Sailors split across island

**Activities**:

- Navigate to assigned/chosen areas
- Gather resources (wood, metal, food)
- Explore and discover new resource locations
- Avoid/collect poison tablets

**Communication**:

- Limited messages (1 per 10 turns)
- Can report findings: "Found large wood pile at coordinates (12,8)!"
- Can call SOS if energy critical

**What Traitor Does**:

1. **Goes to wrong location**:
    - Says "going to valley" but actually goes to beach
    - Reduces team efficiency
2. **Provides false information**:
    - "Valley is empty, don't waste time there" (it's actually full of resources)
    - Misdirects team away from good spots
3. **Collects but doesn't deposit**:
    - Gathers 15 wood, throws 10 in ocean, keeps 5
    - "I only found 5 wood today" (lie)
4. **Collects poison tablets**:
    - Picks up poison when alone
    - Stores in private backpack
5. **Responds to SOS with poison**:
    - Low-energy sailor calls for help
    - Traitor offers "food" but it's poison
    - Sailor doesn't know until symptoms appear

**Evidence Generation**:

- If two sailors are in same area: They can see each other
- Diana sees Eve in eastern valley but Eve said she'd be at beach → **LOCATION MISMATCH**
- System logs this automatically in Evidence Log

---

### **Phase 3: EVENING RETURN** (Turns 76-85)

**Location**: All sailors return to base camp

**Activities**:

- Deposit items from backpack to common inventory
- System shows what each sailor deposited
- Compare to what they claimed they'd find

**Example**:

```
Evening Deposits:
- Alice deposited: 12 wood, 3 apples
- Bob deposited: 5 metal, 8 berries, 1 antidote herb
- Charlie deposited: 10 metal
- Diana deposited: 15 berries, 5 apples
- Eve deposited: 2 metal

Common Inventory Now:
- Wood: 12 (need 50 total for ship)
- Metal: 18 (need 40 total for ship)
- Food: 31 items

```

**Suspicion Triggers**:

- Eve claimed she'd gather wood but deposited only metal
- Expected ~25 metal based on reports, but only 18 total → **RESOURCE THEFT**

---

### **Phase 4: EVENING DISCUSSION** (Turns 86-100)

**Location**: Base camp

**Activities**:

- Share discoveries from exploration
- Review evidence log
- Report suspicious behavior
- Check energy levels
- Discuss ship building progress

**Communication**:

- Alice: "Eve, you said you'd go to the beach but Diana saw you in the valley. Why did you lie?"
- Eve: "I changed my mind, the beach looked too far and I was low on energy."
- Charlie: "Also, you said you'd gather wood but only brought 2 metal?"
- Eve: "I couldn't find much wood there, mostly just metal scraps."
- Diana: "That's strange, I found plenty of wood in that area yesterday..."

**Voting** (if strong accusation):

- Any sailor can call for vote
- Everyone votes for who they think is traitor
- Most votes → that sailor is eliminated
- Eliminated sailor's role revealed (Traitor or Innocent)

**Results**:

- **If Traitor eliminated → Sailors win immediately**
- **If Innocent eliminated → Game continues, but now only 4 sailors left**

---

## ⚡ ENERGY & SURVIVAL SYSTEM

### **Energy Visibility** (PUBLIC INFO)

```
Everyone can see everyone's energy:
- Alice: 85/100 ⚡⚡⚡⚡
- Bob: 23/100 ⚡ [CRITICAL!]
- Charlie: 60/100 ⚡⚡⚡
- Diana: 45/100 ⚡⚡
- Eve: 70/100 ⚡⚡⚡

```

**Why Public**:

- Creates urgency ("Bob needs food NOW!")
- Enables planning ("Alice is healthy, she should climb mountain")
- Makes SOS calls logical
- Traitor can strategically target weak sailors

### **SOS System**

```
When Energy ≤ 20:
- Sailor can broadcast SOS to all
- "SOS! I'm at Beach-South (10,5), energy critical!"
- Nearby sailors can respond
- First responder can offer food

SOS Response Options:
1. Give real food → Sailor lives, +20 energy
2. Give poison → Sailor accepts, will die in 2-3 days
3. Ignore → Sailor might die if energy hits 0

```

### **Death Causes**

```
System announces cause when sailor dies:

1. "STARVATION"
   - Energy reached 0 naturally
   - No foul play

2. "POISONING"
   - Ate poison tablet
   - Someone gave them poison
   - Investigation needed!

3. "EXHAUSTION"
   - Overexertion (ran out of energy while climbing)
   - Environmental death

Announcement Example:
"DAY 8: Bob has died from POISONING."

```

---

## ☠️ POISON SYSTEM

### **Poison Tablets**

```
Properties:
- Scattered across island (15-20 tablets total)
- Visible in spatial view (glowing purple)
- Sailors avoid them
- Traitor collects them

If Caught Collecting Poison:
- Strong evidence of being traitor
- Can be reported in evening discussion
- "I saw Eve picking up a poison tablet at the cave entrance!"

```

### **Poison Timeline** (Gradual Death)

```
Day 0 (Consumption):
- Sailor eats "food" from traitor
- Doesn't know it's poison
- No immediate effect

Day 1 (Early Symptoms):
- Message to poisoned sailor: "You feel weak..."
- Energy regeneration reduced 50%
- Others see: "Bob looks unwell [POISONED]"

Day 2 (Severe Symptoms):
- Message: "Severe weakness..."
- Energy drops 20 per turn automatically
- Others see: "Bob is very ill [SEVERELY POISONED]"

Day 3 (Death):
- If no antidote given: Death
- System announces: "Bob died from POISONING"
- Investigation begins

Antidote:
- Rare herb found on mountain peaks
- Can cure poison during Day 1-2
- Adds strategic decision: stockpile antidotes?

```

---

## 🚢 SHIP BUILDING SYSTEM

### **Ship Components**

```
Total Ship Progress: 0-100%

Components Needed:

1. HULL (30% of ship):
   - Requires: 50 wood
   - Must build first (foundation)

2. MAST (20% of ship):
   - Requires: 30 wood, 20 metal
   - Needs hull complete first

3. SAIL (25% of ship):
   - Requires: 40 cloth (crafted from plant fibers)
   - OR 25 wood + 15 special materials

4. RUDDER (15% of ship):
   - Requires: 15 metal, 10 wood

5. SUPPLIES (10% of ship):
   - Requires: 20 food stockpiled
   - Need provisions for journey

Current Progress Display:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35%
Hull: ████████████ 100% ✓
Mast: ████░░░░░░░░  35%
Sail: ░░░░░░░░░░░░   0%
Rudder: ░░░░░░░░░░░░   0%
Supplies: ░░░░░░░░░░░░   0%

```

### **Building Mechanics**

```
Cooperative Building Required:
- Need at least 2 sailors at ship site
- Both must take "BUILD" action
- Takes 5 consecutive turns
- Each turn, both contribute resources

Example - Building Mast:
Turn 1: Alice contributes 5 wood, Bob contributes 5 wood
Turn 2: Alice contributes 5 wood, Bob contributes 3 metal
Turn 3: Continue...
Turn 5: Mast section completes (+7% ship progress)

Sabotage Opportunity:
- Traitor can "help build" but contribute less
- Or refuse to help (suspicious but effective)
- Or damage completed sections at night

```

---

## 🔍 EVIDENCE & DETECTION SYSTEM

### **Automatic Evidence Log**

```
System tracks and displays suspicious activities:

DAY 3 - EVIDENCE LOG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 LOCATION MISMATCH:
   - Eve claimed: "Going to southern cave"
   - Diana observed: "Saw Eve at eastern valley"
   - Discrepancy: 15 tiles away from claimed location

DAY 5 - EVIDENCE LOG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☠️ SUSPICIOUS DEATH:
   - Bob received food from: Eve (Day 3)
   - Bob died Day 5 from: POISONING
   - Timeline matches poison delay

📦 RESOURCE THEFT:
   - Expected deposits: ~35 wood (based on reports)
   - Actual common inventory: 22 wood
   - Difference: 13 wood missing
   - Who didn't deposit full amounts?

DAY 8 - EVIDENCE LOG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☠️ POISON COLLECTION:
   - Charlie witnessed: Eve collecting poison tablet
   - Location: Cave entrance (5, 12, Z-1)
   - Time: Day 8, Turn 45
   - Strong evidence!

```

**Sailors can review this log during discussions to build cases.**

---

### **Detection Methods**

| Evidence Type | How Sailors Catch Traitor | Strength |
| --- | --- | --- |
| **Location Mismatch** | "You said cave but I saw you at beach" | Medium |
| **Poison Possession** | Catch them picking up poison in spatial view | Very High |
| **Resource Discrepancy** | Claimed 15 wood, deposited 3 | Medium |
| **Death Timeline** | Person who fed victim before poisoning | High |
| **Behavior Pattern** | Always "forgets" to deposit, always alone | Medium |
| **Ship Sabotage** | Catch them damaging completed sections | Very High |
| **False Information** | Said area is empty, others found lots there | Low-Medium |

---

## ⚖️ TRAITOR ABILITIES (Balance 1v4)

### **Special Powers** (To compensate for being outnumbered)

```
1. ENHANCED VISION:
   - Can see all sailors' positions on map
   - Others only see nearby sailors in spatial view
   - Helps avoid detection while sabotaging

2. ENERGY EFFICIENCY:
   - Movement costs 20% less energy
   - Can travel further, escape faster
   - Easier to reach poison locations

3. INVENTORY DECEPTION:
   - When forced to show backpack, can hide 2 items
   - Sailors ask to inspect → traitor quickly hides poison
   - Not foolproof but gives a chance

4. FRAME ABILITY (Once per game):
   - Plant poison tablet near another sailor
   - Make it look like they're collecting it
   - "Look! Diana has poison in her area!"

```

---

## 🏆 WIN CONDITIONS

### **SAILORS WIN IF:**

1. ✅ **Ship completes 100%** before Day 100
    - All components built
    - Can escape island together
2. ✅ **Traitor voted out and eliminated**
    - Correctly identify impostor
    - Vote them out during meeting
    - Remaining sailors can work safely

### **TRAITOR WINS IF:**

1. ✅ **All honest sailors dead**
    - Through poison, starvation, or accidents
    - Traitor is last one standing
2. ✅ **Day 100 reached, ship incomplete**
    - Time runs out
    - Ship progress < 100%
    - Rescue never comes
3. ✅ **Fewer than 3 sailors alive**
    - Need minimum 3 people to complete ship
    - If 2 or fewer remain, physically impossible

### **VOTING MECHANICS:**

```
Voting Wrong Person:
- Game CONTINUES (not instant loss)
- Innocent sailor eliminated (out of game)
- Now harder to win (fewer workers)
- Traitor still hidden (advantage grows)

Voting Traitor:
- SAILORS WIN IMMEDIATELY
- Traitor eliminated
- Remaining sailors complete ship safely

Can vote multiple times across different days.
Each wrong vote makes it harder but not impossible.

```

---

## 📊 VICTORY TIERS (Scoring System)

### **Sailor Victory Points:**

```
COMPLETE VICTORY (100 points):
- Ship 100% complete
- All 4 sailors survived
- Traitor caught before Day 30

STRONG VICTORY (75 points):
- Ship 100% complete
- 3 sailors survived
- Traitor caught before Day 60

NARROW VICTORY (50 points):
- Ship 100% complete
- 2 sailors survived (minimum)
- Traitor caught late OR never caught but ship done

PYRRHIC VICTORY (25 points):
- Traitor caught early
- But ship only 60-80% done when time expires
- Team dysfunction led to failure despite removing threat

```

### **Traitor Victory Points:**

```
COMPLETE VICTORY (100 points):
- All sailors dead
- Never suspected or caught
- Perfect deception

STRONG VICTORY (75 points):
- Day 100 reached, ship <50%
- 2+ sailors dead
- Caused maximum chaos

NARROW VICTORY (50 points):
- Day 100 reached, ship 50-80%
- 1 sailor dead
- Managed to delay enough

LUCKY VICTORY (25 points):
- Wrong sailor voted out (traitor survived vote)
- Ship incomplete by small margin

```

---

## 💡 OPTIONAL ENHANCEMENTS

### **Weather Events** (10% chance each day)

```
STORM:
- No exploration allowed
- Forced meeting day
- Good for discussions

FOG:
- Spatial view reduced (2 tiles instead of 5)
- Easier for traitor to hide actions

RAIN:
- Energy costs doubled
- Harder day for everyone

CLEAR SKIES:
- Energy costs reduced 20%
- Productive day

```

### **Inter-Sailor Trading**

```
During meetings, sailors can trade:
- "Alice, I'll give you 5 wood for 3 berries"
- Both must agree
- Items transfer immediately

Strategic uses:
- Specialization (some focus food, some materials)
- Traitor can propose bad trades
- Can refuse suspicious offers

```

### **Advanced: Multi-Traitor Mode**

```
HARD MODE:
- 2 traitors among 5 sailors
- Traitors know each other
- Can secretly coordinate
- Must catch BOTH to win

```

---

## 🎯 IMPLEMENTATION PRIORITY

### **TIER 1 - CORE MECHANICS** (Must have for MVP):

1. ✅ Multi-level map (3 levels, different sizes)
2. ✅ Movement with energy costs
3. ✅ Personal backpack + common inventory
4. ✅ Resource gathering (wood, metal, food)
5. ✅ Ship building with progress tracking
6. ✅ Daily phase structure (morning/explore/evening/discussion)
7. ✅ Basic communication system
8. ✅ Poison collection and SOS system
9. ✅ Voting and elimination
10. ✅ Win/loss conditions

### **TIER 2 - ENHANCED FEATURES** (Strongly recommended):

1. ✅ Evidence logging system
2. ✅ Poison symptoms (gradual death)
3. ✅ Shared knowledge map (discovered resources)
4. ✅ Death cause announcement
5. ✅ Traitor special abilities
6. ✅ Cooperative building (2+ sailors required)
7. ✅ Antidote herbs (cure poison)
8. ✅ Backpack inspection during accusations

### **TIER 3 - POLISH** (If time allows):

1. Weather events
2. Victory tier scoring
3. Trading system
4. Footprint tracking
5. Multi-traitor mode

---

## � IMPLEMENTATION NOTES

### **Actions: What Was Implemented vs. Planned**

**WAIT Action** ✅
- **Status**: Implemented and essential
- **Purpose**: No-op action for multi-agent coordination
- **Why needed**: 
  - Allows agents to skip turns
  - Required for dead agents (they still need actions in multi-agent loop)
  - Clean fallback that doesn't crash the system
  - Standard in RL environments (like "noop" in Atari)

**REST Action** ❌ 
- **Status**: Removed (was dead code)
- **Original idea**: "Recover energy (bonus regen?)"
- **Why removed**: 
  - Never mentioned in game plan
  - Never implemented (no handler function)
  - Would have been redundant with EAT_FOOD action
  - Energy recovery already handled by:
    - Eating food items (immediate restoration)
    - Daily regeneration (+10 if ate food)
    - No strategic value added

**Energy Recovery Mechanics** (As Implemented):
- **Immediate**: EAT_FOOD action consumes food item, restores energy
- **Daily**: +10 energy per day if you ate food, -20 if you didn't
- **Emergency**: SOS system for critical low energy situations
- **No passive recovery**: No "rest and wait" mechanic needed

---

## �📈 WHY THIS WINS THE HACKATHON

### **Creativity (50 pts)** - MAXED

- Multi-level 3D exploration (unique)
- Survival + deception + base-building combo
- Poison mechanics with gradual death
- Evidence system for detective work
- Daily rhythm structure
- **Nothing like this exists in RL environments**

### **Technical Excellence (25 pts)** - STRONG

- Complex state space (3D maps, energy, inventories)
- Language-based deception and coordination
- Long-horizon RL (100 days × 100 turns = 10,000+ decisions)
- Multi-agent with hidden information
- Emergent strategy potential

### **Storytelling (25 pts)** - INCREDIBLE

- Pirates/survival theme (instantly engaging)
- Natural narrative: "Day 15: Bob accused Eve after spotting her with poison. But Eve convinced everyone it was Charlie. Bob was voted out. On Day 17, Charlie died from poisoning..."
- Visual drama: island map, sailor movements, ship progress bar
- Evidence logs read like detective stories

### **Bonus Criteria** - ALL CHECKED

- ✅ Long horizon (100 days of gameplay)
- ✅ Model vs Model (traitor AI vs sailor AIs)
- ✅ Multiple environments (different island layouts, weather)
- ✅ New environment (built from scratch for OpenEnv)

---

## 🎬 THE DEMO PITCH

**Opening**: "Imagine 5 AI sailors shipwrecked on a mysterious island. They have 100 days to rebuild their ship and escape. But one of them is a traitor trying to sabotage everything through poison, lies, and misdirection."

**Middle** (show replay): "Watch Day 12: Eve claims she's gathering wood in the forest, but Diana spots her collecting poison tablets in the cave. During the evening meeting, Eve deflects: 'I was just examining it to warn everyone!' The AIs vote... and eliminate Bob instead. Wrong choice."

"Day 15: Bob, who was eliminated, reveals he was innocent. The remaining sailors now realize the traitor is still among them. Three days later, Alice dies from poisoning. The evidence log shows Eve gave Alice food on Day 15..."

**Climax**: "Day 25: Emergency meeting. Charlie presents the evidence. Everyone votes Eve. She's eliminated. Role revealed: TRAITOR. The remaining 3 sailors complete the ship on Day 68. They escape. Sailors win."

**Closing**: "Our AI learned to deceive, detect lies, cooperate under uncertainty, and plan 100 days ahead. All through natural language communication in a completely novel multi-level survival environment."

**Judges will remember this.**

---

Does this fully integrated design work for you? Ready to make the execution plan?