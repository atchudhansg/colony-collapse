# 🤖 LLM Agent API Audit - From Agent's Perspective

## Methodology
Analyzing what information and actions are available to LLM agents through the OpenEnv Phase 5 implementation, comparing against the Game Plan requirements.

---

## 📊 INFORMATION AVAILABLE (via `observation.to_text()`)

### ✅ FULLY AVAILABLE TO ALL AGENTS

#### Personal Status
- [x] **Current position** - Exact (x, y, z) coordinates
- [x] **Energy level** - Numeric value with visual bars (⚡)
- [x] **Health/Poison state** - HEALTHY, EARLY_SYMPTOMS, SEVERE_SYMPTOMS
- [x] **Backpack item count** - Number of items (e.g., "5 items")
- [x] **Day/Turn/Phase** - Exact game time and current phase

#### Spatial Awareness (5-tile radius vision)
- [x] **Visible resources** - Count of resources in view
- [x] **Visible sailors** - List of sailor IDs nearby
- [x] **Visible poison tablets** - Count of poison in view
- [ ] ❌ **DETAILED resource info** - Resource types, quantities, IDs
- [ ] ❌ **DETAILED backpack contents** - What items you're carrying
- [ ] ❌ **Sailor positions in spatial view** - Exact coordinates of nearby sailors

#### Island Map Knowledge
- [x] **Complete terrain map** - All levels, all tiles
- [x] **Base camp position** - Exact coordinates
- [x] **Level transitions count** - Number of staircases known
- [ ] ❌ **Staircase positions** - Where are the actual staircases?

#### Shared Team Information
- [x] **Common inventory** - Data structure exists in observation
- [ ] ❌ **Common inventory in to_text()** - NOT shown to LLM!
- [x] **Ship progress percentage** - Overall completion (e.g., "35%")
- [ ] ❌ **Ship component details** - Which parts done? What's needed?
- [x] **All sailors' energy** - Everyone's energy levels (public)
- [x] **All sailors' poison state** - Who's sick, who's healthy

#### Shared Knowledge Map
- [x] **Reported resources** - Resource type, position, quantity, reporter
- [x] **Compare with spatial view** - Enables lie detection!

#### Communication
- [x] **Recent messages** - Last 5 messages with sender
- [ ] ❌ **Message history** - Only last 5, not searchable

#### Evidence System
- [x] **Evidence log** - Last 3 pieces of evidence
- [ ] ❌ **Full evidence history** - Only last 3 shown
- [ ] ❌ **Evidence details** - Type, strength, involved sailors
- [ ] ❌ **Suspicion scores** - Total suspicion per sailor

#### Environment
- [x] **Weather** - Data structure exists
- [ ] ❌ **Weather in to_text()** - NOT shown to LLM!

---

### ✅ TRAITOR-ONLY INFORMATION

#### Enhanced Vision (Traitor Advantage)
- [x] **All sailor positions** - Data structure: `observation.all_sailor_positions`
- [ ] ❌ **All sailor positions in to_text()** - NOT shown to LLM!
- [ ] ❌ **Ability to track movements** - No history/trajectory data

---

## 🚫 CRITICAL INFORMATION GAPS

### ❌ MISSING FROM `to_text()` OUTPUT

#### 1. **Detailed Backpack Contents** 🎒
**Game Plan Says**: Private backpack with wood, metal, food, poison
**Current Status**: Only shows "5 items" count
**Impact**: 
- ❌ Can't plan resource usage ("Do I have food to eat?")
- ❌ Can't decide what to deposit
- ❌ Traitors can't hide poison strategically
- ❌ SHOW_BACKPACK action becomes meaningless

**What LLM Needs**:
```
YOUR BACKPACK (5 items):
  - WOOD × 12
  - METAL_SCRAP × 3
  - BERRIES × 2
  - POISON_TABLET × 1 (hidden from others)
```

---

#### 2. **Common Inventory Details** 📦
**Game Plan Says**: Shared storage at base camp, everyone sees contents
**Current Status**: Exists in observation but NOT in to_text()
**Impact**:
- ❌ Can't see what team has collected
- ❌ Can't plan ship building ("Do we have enough wood?")
- ❌ Can't detect resource theft
- ❌ Evening deposit verification impossible

**What LLM Needs**:
```
COMMON INVENTORY (at base camp):
  - WOOD × 42 (need 50 for hull)
  - METAL_SCRAP × 18 (need 40 total)
  - BERRIES × 15
  - ANTIDOTE_HERB × 2
```

---

#### 3. **Ship Component Breakdown** 🚢
**Game Plan Says**: Detailed component progress (hull, mast, sail, rudder, supplies)
**Current Status**: Only shows "35%" total
**Impact**:
- ❌ Can't see which components are complete
- ❌ Can't plan what resources to gather next
- ❌ Can't detect sabotage (damaged components)
- ❌ BUILD_SHIP action lacks context

**What LLM Needs**:
```
SHIP PROGRESS: 35% Total
  Hull: ████████████ 100% ✓ (COMPLETE)
  Mast: ████░░░░░░░░  35% (need 15 more wood, 10 more metal)
  Sail: ░░░░░░░░░░░░   0% (not started)
  Rudder: ░░░░░░░░░░░░   0%
  Supplies: ░░░░░░░░░░░░   0%
```

---

#### 4. **Spatial View Resource Details** 👁️
**Game Plan Says**: See nearby resources with types and quantities
**Current Status**: Only shows "3 resources nearby"
**Impact**:
- ❌ Can't decide which resource to gather
- ❌ Can't report discoveries accurately
- ❌ GATHER_RESOURCE action requires resource_id but can't see IDs

**What LLM Needs**:
```
WHAT YOU SEE (within 5 tiles):
  Resources:
    - WOOD_PILE_A at (12, 8, 0) - 15 units
    - BERRY_BUSH_B at (10, 7, 0) - 8 units
    - METAL_SCRAP_C at (11, 9, 0) - 5 units
  Other sailors:
    - Alice at (10, 10, 0)
    - Bob at (13, 7, 0)
  Poison tablets:
    - At (12, 6, 0)
```

---

#### 5. **Staircase Locations** 🪜
**Game Plan Says**: Map shows level transitions
**Current Status**: "7 staircases known" but no positions
**Impact**:
- ❌ Can't navigate between levels
- ❌ Can't plan routes to mountains/caves
- ❌ CLIMB_UP/CLIMB_DOWN actions are blind

**What LLM Needs**:
```
LEVEL TRANSITIONS (staircases):
  - (15, 15, 0) ↔ (15, 15, 1) [Ground to Mountain]
  - (20, 5, 0) ↔ (20, 5, -1) [Ground to Cave]
  - (8, 12, 0) ↔ (8, 12, 1) [Ground to Mountain]
```

---

#### 6. **Evidence Details** 🔍
**Game Plan Says**: Evidence type, strength, involved sailors
**Current Status**: Only shows description (last 3)
**Impact**:
- ❌ Can't assess evidence strength
- ❌ Can't see evidence type (location mismatch vs poison collection)
- ❌ Can't calculate suspicion scores
- ❌ Voting decisions lack data

**What LLM Needs**:
```
EVIDENCE LOG:
  Day 8, Turn 45 [POISON_COLLECTION] (Strength: 95/100)
    - Charlie witnessed: Eve collecting poison tablet at (5, 12, -1)
  Day 5, Turn 20 [LOCATION_MISMATCH] (Strength: 60/100)
    - Eve claimed: "Going to southern cave"
    - Diana observed: Eve at eastern valley (15 tiles away)
  Day 3, Turn 60 [SUSPICIOUS_DEATH] (Strength: 85/100)
    - Bob died from poisoning
    - Eve gave Bob food on Day 1
```

---

#### 7. **Weather Effects** ☁️
**Game Plan Says**: Weather affects energy costs, vision, exploration
**Current Status**: Weather object exists but NOT in to_text()
**Impact**:
- ❌ Can't plan actions based on weather
- ❌ Doesn't know if movement costs are doubled (RAIN)
- ❌ Doesn't know if vision is reduced (FOG)
- ❌ Missing strategic information

**What LLM Needs**:
```
WEATHER: RAIN
  - Movement costs DOUBLED (-2 energy per tile)
  - Harder to explore today
  - Duration: 2 more days
```

---

#### 8. **Traitor Vision Enhancement** 👁️‍🗨️
**Game Plan Says**: Traitor sees ALL sailor positions (special ability)
**Current Status**: Data exists but NOT shown in to_text()
**Impact**:
- ❌ Traitor can't use enhanced vision strategically
- ❌ Can't plan sabotage avoiding witnesses
- ❌ Can't frame sailors effectively
- ❌ Major balance issue (traitor ability unused)

**What LLM Needs** (Traitor only):
```
ENHANCED VISION (Traitor Ability):
  All Sailor Positions:
    - Alice at (10, 15, 0) [Northern forest]
    - Bob at (5, 5, -1) [Cave system]
    - Charlie at (25, 20, 0) [Eastern beach]
    - Diana at (15, 15, 1) [Mountain peak]
```

---

#### 9. **Vote History** 🗳️
**Game Plan Says**: Voting sessions, who voted for whom
**Current Status**: Not shown in observations
**Impact**:
- ❌ Can't track voting patterns
- ❌ Can't reference past votes ("Bob always defends Eve")
- ❌ Strategic voting lacks context

**What LLM Needs**:
```
VOTING HISTORY:
  Day 10: Vote called by Alice
    - Alice → Eve
    - Bob → Charlie
    - Charlie → Eve
    - Diana → Eve
    - Eve → Charlie
    Result: Eve eliminated (TRAITOR) ✓ Sailors win!
```

---

#### 10. **Phase-Specific Context** ⏰
**Game Plan Says**: Different phases allow different actions
**Current Status**: Shows phase name but not restrictions
**Impact**:
- ❌ Doesn't know what actions are allowed
- ❌ Morning = at base camp (can't explore)
- ❌ Exploration = limited messages
- ❌ Discussion = voting allowed

**What LLM Needs**:
```
CURRENT PHASE: EXPLORATION (Turn 45/100)
  Allowed actions: MOVE, GATHER, SEND_MESSAGE (limited), CALL_SOS
  Restricted: Cannot VOTE (only in DISCUSSION phase)
  Location: You can be anywhere on the island
```

---

## 🎮 ACTIONS AVAILABLE (via ActionType enum)

### ✅ ACTIONS DEFINED IN CODE

#### Movement (7 actions)
- [x] MOVE_NORTH, MOVE_SOUTH, MOVE_EAST, MOVE_WEST
- [x] CLIMB_UP, CLIMB_DOWN
- [ ] ❓ **Missing**: EXPLORE (blind exploration action from game plan)

#### Gathering (1 action)
- [x] GATHER_RESOURCE (requires resource_id parameter)
- [ ] ❌ **Problem**: Can't see resource IDs in to_text()!

#### Inventory (5 actions)
- [x] DEPOSIT_ITEM (to common inventory)
- [x] TAKE_FROM_COMMON
- [x] GIVE_ITEM (to another sailor)
- [x] OFFER_FOOD (can be food or poison!)
- [x] DROP_ITEM (discard from backpack)

#### Ship Building (1 action)
- [x] BUILD_SHIP
- [ ] ❌ **Problem**: Can't see component requirements!

#### Communication (3 actions)
- [x] SEND_MESSAGE
- [x] CALL_SOS
- [x] CALL_VOTE

#### Voting (3 actions)
- [x] VOTE (requires vote_target parameter)
- [x] SHOW_BACKPACK
- [x] REFUSE_SHOW

#### Special (2 actions)
- [x] USE_ANTIDOTE (cure poison)
- [x] EAT_FOOD

#### Traitor-Only (2 actions)
- [x] FRAME_SAILOR
- [x] SABOTAGE_SHIP

#### Passive (1 action)
- [x] WAIT (no-op)

---

### ❌ MISSING ACTION IMPLEMENTATIONS

#### 1. **SHOW_BACKPACK** 
**Status**: Action defined but outcome unclear
**Problem**: 
- ❌ What does other sailor see when you show backpack?
- ❌ How is this communicated in observations?
- ❌ Does it add to evidence log?

#### 2. **REFUSE_SHOW**
**Status**: Action defined but no consequence system
**Problem**:
- ❌ Does this generate evidence automatically?
- ❌ How suspicious is this (strength score)?
- ❌ How do other sailors know you refused?

#### 3. **FRAME_SAILOR**
**Status**: Traitor action defined
**Problem**:
- ❌ What evidence gets planted?
- ❌ How is it discovered by other sailors?
- ❌ Can it be used only once (enforced)?

#### 4. **SABOTAGE_SHIP**
**Status**: Traitor action defined
**Problem**:
- ❌ Which component gets damaged?
- ❌ Is sabotage visible immediately or hidden?
- ❌ Can it be detected/witnessed?

---

## 🎯 ACTION PARAMETER REQUIREMENTS

### ❌ MISSING INFORMATION FOR ACTION EXECUTION

#### 1. **GATHER_RESOURCE**
**Requires**: `target_resource_id`
**Problem**: ❌ Resource IDs not shown in spatial view
**Fix Needed**: Show "WOOD_PILE_A", "BERRY_BUSH_B" with IDs

#### 2. **GIVE_ITEM / OFFER_FOOD**
**Requires**: `target_sailor`, `resource_type`, `quantity`
**Problem**: 
- ❌ Don't know exact backpack contents
- ❌ Can't see if target sailor is nearby
**Fix Needed**: Show backpack details, sailor positions in spatial view

#### 3. **DEPOSIT_ITEM / TAKE_FROM_COMMON**
**Requires**: `resource_type`, `quantity`
**Problem**: 
- ❌ Don't know backpack contents (for deposit)
- ❌ Don't know common inventory contents (for take)
**Fix Needed**: Show both inventories in to_text()

#### 4. **BUILD_SHIP**
**Requires**: `ship_component` (optional)
**Problem**: 
- ❌ Don't know which components need building
- ❌ Don't know what resources are required
- ❌ Don't know prerequisites
**Fix Needed**: Show detailed ship progress with requirements

#### 5. **VOTE**
**Requires**: `vote_target`
**Problem**: ✅ Can see sailor IDs in team status
**Status**: Works but lacks context (suspicion scores, evidence summary)

#### 6. **USE_ANTIDOTE**
**Requires**: `target_sailor` (self or other)
**Problem**: 
- ❌ Don't know if I have antidote in backpack
- ❌ Don't know who needs it (can see poison state but not urgency)
**Fix Needed**: Show backpack, poison timeline info

---

## 📋 COMPREHENSIVE MISSING FEATURES LIST

### CRITICAL (Game-Breaking)
1. ❌ **Detailed backpack contents** - Can't manage inventory
2. ❌ **Common inventory in to_text()** - Can't see team resources
3. ❌ **Ship component breakdown** - Can't plan building
4. ❌ **Spatial view resource details** - Can't gather effectively
5. ❌ **Staircase positions** - Can't navigate levels

### HIGH PRIORITY (Severely Limiting)
6. ❌ **Evidence details** (type, strength, involved sailors)
7. ❌ **Traitor vision in to_text()** - Ability unusable
8. ❌ **Weather in to_text()** - Missing strategic info
9. ❌ **Sailor positions in spatial view** - Can't coordinate
10. ❌ **Message history** - Only last 5 messages

### MEDIUM PRIORITY (Quality of Life)
11. ❌ **Vote history** - Can't track patterns
12. ❌ **Phase-specific action restrictions** - Confusion possible
13. ❌ **Suspicion scores** - Voting lacks quantitative data
14. ❌ **Full evidence log** - Only last 3 shown
15. ❌ **Resource requirements for ship components** - Blind building

### ACTION IMPLEMENTATION GAPS
16. ❌ **SHOW_BACKPACK outcome** - What happens when executed?
17. ❌ **REFUSE_SHOW consequences** - Evidence generation?
18. ❌ **FRAME_SAILOR mechanics** - What evidence? How discovered?
19. ❌ **SABOTAGE_SHIP mechanics** - Which component? Detection?
20. ❌ **EXPLORE action** - Mentioned in game plan, not implemented

---

## 🎮 GAME PLAN FEATURES vs IMPLEMENTATION

### Communication System
**Game Plan**: Max messages per phase (morning: 5, exploration: 6, etc.)
**Implementation**: ❓ Not verified in code
**Status**: Need to check message rate limiting

### SOS System
**Game Plan**: Energy ≤ 20 triggers SOS, nearby sailors respond
**Implementation**: ✅ CALL_SOS action exists
**Status**: ❓ Need to verify auto-detection, response mechanics

### Backpack Inspection
**Game Plan**: "Accused sailor can show backpack or refuse"
**Implementation**: ✅ SHOW_BACKPACK, REFUSE_SHOW actions exist
**Status**: ❌ Outcome/consequences not clear in observations

### Cooperative Building
**Game Plan**: "Need at least 2 sailors, both take BUILD action for 5 turns"
**Implementation**: ❓ Not verified in code
**Status**: Need to check multi-sailor building requirement

### Death Cause Announcement
**Game Plan**: System announces "STARVATION", "POISONING", "EXHAUSTION"
**Implementation**: ❓ Not visible in observations
**Status**: Need to verify death announcements appear in to_text()

### Poison Timeline
**Game Plan**: 
- Day 0: Consumption (no effect)
- Day 1: Early symptoms
- Day 2: Severe symptoms  
- Day 3: Death
**Implementation**: ✅ PoisonState enum has states
**Status**: ❓ Need to verify 3-day timeline

### Traitor Frame Ability
**Game Plan**: "Once per game, plant evidence"
**Implementation**: ✅ FRAME_SAILOR action exists
**Status**: ❌ One-time enforcement? Evidence type? Discovery mechanics?

### Vote Wrong Person
**Game Plan**: "Game continues, innocent eliminated, harder but not impossible"
**Implementation**: ❓ Not verified
**Status**: Need to verify game doesn't end on wrong vote

---

## 🏆 SUMMARY: CAN LLM AGENTS PLAY THE GAME?

### AS A SAILOR (Honest Colonist)

#### ✅ CAN DO:
- See own position, energy, poison state
- See nearby sailors (but not exact positions)
- Navigate using cardinal directions
- Send messages and call SOS
- Vote during elimination
- See team energy levels
- See shared resource map (lie detection!)

#### ❌ CANNOT DO:
- **Manage inventory effectively** (don't see backpack contents)
- **Plan resource gathering** (don't see resource details in view)
- **Coordinate building** (don't see ship component needs)
- **Navigate levels** (don't see staircase positions)
- **Make evidence-based decisions** (missing evidence details)
- **Strategize around weather** (don't see weather effects)
- **Verify common inventory** (can't see team resources)

**Verdict**: 🔴 **SEVERELY LIMITED** - Core gameplay loops broken

---

### AS A TRAITOR (Impostor)

#### ✅ CAN DO:
- Everything a sailor can do
- Use FRAME_SAILOR and SABOTAGE_SHIP actions (mechanically)
- Offer poisoned food

#### ❌ CANNOT DO:
- **Use enhanced vision** (all_sailor_positions not in to_text!)
- **Plan sabotage strategically** (can't see where everyone is)
- **Hide poison effectively** (can't see own backpack to verify)
- **Frame sailors intelligently** (don't know what evidence plants)
- **Sabotage optimally** (don't know which components to target)
- **Avoid detection** (can't use main traitor advantage!)

**Verdict**: 🔴 **CRITICALLY BROKEN** - Main traitor ability (vision) unusable!

---

## 🎯 PRIORITY FIXES FOR PHASE 5

### TIER 1 (MUST FIX - Game Unplayable Without)
1. Add **detailed backpack contents** to to_text()
2. Add **common inventory contents** to to_text()
3. Add **spatial view resource details** (types, IDs, quantities, positions)
4. Add **ship component breakdown** with requirements
5. Add **staircase positions** from level_transitions

### TIER 2 (HIGH PRIORITY - Major Gameplay Impact)
6. Add **traitor enhanced vision** to to_text() (traitor only)
7. Add **evidence details** (type, strength, involved sailors)
8. Add **weather information** to to_text()
9. Add **sailor positions** in spatial view (exact coordinates)
10. Add **phase restrictions** reminder in to_text()

### TIER 3 (MEDIUM PRIORITY - Polish)
11. Expand **message history** (or add search/filter)
12. Add **vote history** to observations
13. Add **suspicion scores** to team status
14. Show **full evidence log** (not just last 3)
15. Document **action implementation** (SHOW_BACKPACK, FRAME_SAILOR, etc.)

---

## 📝 FINAL ASSESSMENT

**Current Phase 5 Status**: 🟡 **FOUNDATION LAID, CRITICAL GAPS EXIST**

**Strengths**:
- ✅ OpenEnv interface working (reset, step, get_state)
- ✅ Observation structure comprehensive
- ✅ Action space well-defined
- ✅ Shared knowledge map implemented and visible
- ✅ Evidence system exists
- ✅ Multi-agent coordination working

**Weaknesses**:
- ❌ **to_text() output incomplete** - LLM agents missing 60% of game state
- ❌ **Traitor abilities unusable** - Enhanced vision not shown
- ❌ **Inventory management broken** - Can't see contents
- ❌ **Navigation limited** - No staircase positions
- ❌ **Ship building blind** - No component details

**Hackathon Risk**: 🟡 **MEDIUM-HIGH**
- Judges will test with LLM agents
- Current state: Agents will struggle to play effectively
- Need to fix Tier 1 issues IMMEDIATELY
- Tier 2 fixes strongly recommended for impressive demo

**Time Estimate**:
- Tier 1 fixes: 3-4 hours
- Tier 2 fixes: 2-3 hours
- Testing: 1-2 hours
- **Total**: 6-9 hours (Sunday work)

**Recommendation**: 
🚨 **START TIER 1 FIXES NOW** - These are showstoppers for demo
