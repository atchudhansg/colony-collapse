dont# 🏴‍☠️ MAROONED - Quick Rules Reference

Fast lookup guide for game mechanics.

---

## ⏰ TIME STRUCTURE

- **Total Duration**: 100 days
- **Turns per Day**: 100
- **Total Decisions**: ~10,000 turns

### Daily Phases

| Phase | Turns | Location | Purpose |
|-------|-------|----------|---------|
| **Morning** | 1-15 | Base Camp | Strategy meeting, voting |
| **Exploration** | 16-75 | Anywhere | Gather resources, explore |
| **Evening Return** | 76-85 | → Base Camp | Deposit items |
| **Discussion** | 86-100 | Base Camp | Review evidence, vote |

---

## 🗺️ MAP LEVELS

| Level | Size | Energy Cost | Key Resources |
|-------|------|-------------|---------------|
| **Mountain (+2)** | 10×10 | -3 to climb up | Antidote herbs, special metal |
| **Ground (0)** | 30×30 | -1 per tile | Wood, metal, food |
| **Cave (-1)** | 15×15 | -1 to climb down | Crystals, mushrooms, rare wood |

**Vision Radius**: 5 tiles (3 in caves, 2 in fog)

---

## ⚡ ENERGY SYSTEM

- **Starting**: 100/100
- **Walking**: -1 per tile
- **Climbing UP**: -3 per level
- **Climbing DOWN**: -1 per level
- **Gathering**: -5 per action
- **Building**: -3 per turn

### Daily Changes
- **Ate food**: +10 energy
- **No food**: -20 energy
- **Poisoned (severe)**: -20 per turn

### Death
- **Energy = 0**: Death by starvation/exhaustion

---

## 📦 RESOURCES

### Building Materials
| Resource | Use | Locations |
|----------|-----|-----------|
| **Wood** | Hull, mast, rudder, sail | Ground (50), Cave (15) |
| **Metal** | Mast, rudder | Ground (30), Cave (20), Mountain (15) |
| **Plant Fiber** | Sail | Ground (35) |

### Food (Energy Restoration)
| Food | Energy | Locations |
|------|--------|-----------|
| **Apple** | +15 | Ground (25), Mountain (10) |
| **Berry** | +10 | Ground (40), Mountain (10) |
| **Mushroom** | +8 | Cave (30) |

### Special Items
| Item | Use | Locations |
|------|-----|-----------|
| **Antidote Herb** | Cure poison | Mountain (8) |
| **Poison Tablet** | Kill sailor | All levels (18 total) |
| **Crystal** | Special/trade | Cave (20) |

---

## 🚢 SHIP COMPONENTS

| Component | % of Ship | Requirements | Prerequisite |
|-----------|-----------|--------------|--------------|
| **Hull** | 30% | 50 wood | None |
| **Mast** | 20% | 30 wood + 20 metal | Hull complete |
| **Sail** | 25% | 40 plant fiber | Mast complete |
| **Rudder** | 15% | 15 metal + 10 wood | Hull complete |
| **Supplies** | 10% | 10 apples + 10 berries | None |

**Building Rules:**
- Need 2+ sailors at ship site
- Takes 5 consecutive turns per component
- Total = 100% to escape

---

## ☠️ POISON MECHANICS

### Timeline
```
Day 0: Consume poison (unknowingly)
Day 1: Early symptoms (-50% energy regen)
Day 2: Severe symptoms (-20 energy/turn)
Day 3: DEATH (if no antidote)
```

### Cure Window
- Antidote works during Days 1-2
- After Day 3: too late, sailor dies
- Antidote is rare (only 8 on mountain)

### Evidence
- System tracks who gave food to whom
- "Bob received food from Eve on Day 3"
- "Bob died from poisoning on Day 5"
- Timeline correlation = strong evidence

---

## 🎒 INVENTORY

### Personal Backpack
- **Capacity**: 20 items
- **Privacy**: Only owner sees contents
- **Inspection**: Can be asked to show (can refuse)

### Common Inventory (Base Camp)
- **Capacity**: Unlimited
- **Visibility**: Everyone sees contents
- **Access**: Anyone can deposit/withdraw

### Depositing
- Must be at base camp
- Automatically shown to all sailors
- Mismatch = evidence of theft

---

## 🎭 SAILOR ROLES

### 4 Honest Sailors
**Goal**: Build ship to 100% OR eliminate traitor

**Abilities**:
- Standard energy costs
- Limited vision (5-tile radius)
- Can see others in range

### 1 Traitor
**Goal**: Prevent ship completion

**Special Abilities**:
- **Enhanced Vision**: See all sailor positions (always)
- **Energy Efficiency**: 20% less energy cost
- **Frame Power**: Plant evidence once per game
- **Hide Items**: Conceal 2 items when showing backpack

**Sabotage Methods**:
- Collect poison, give as "food"
- Lie about locations/resources
- Hoard resources instead of depositing
- Damage completed ship components
- Misdirect team to wrong areas

---

## 🔍 EVIDENCE TYPES

| Type | Example | Strength |
|------|---------|----------|
| **Poison Collection** | Caught picking up poison tablet | 90/100 |
| **Ship Sabotage** | Damaging completed hull | 95/100 |
| **Death Timeline** | Gave food 3 days before poison death | 75/100 |
| **Location Mismatch** | Said cave, seen at beach | 50/100 |
| **Resource Theft** | Found 15 wood, deposited 3 | 45/100 |
| **False Info** | Said area empty, others found lots | 30/100 |

Auto-logged by system, visible to all sailors.

---

## 🗳️ VOTING

### Rules
- Can vote during **Morning** or **Discussion** phases
- Need majority (3/5, then 2/4, etc.)
- Most votes → eliminated
- Role revealed after elimination

### Outcomes
- **Traitor eliminated**: Sailors win immediately
- **Honest eliminated**: Game continues (fewer workers)
- **No majority**: No elimination

### Strategy
- Wrong votes weaken team (fewer sailors to build)
- Can vote multiple times across days
- Balance evidence vs. urgency

---

## 🏆 WIN CONDITIONS

### Sailors Win
✅ Ship reaches 100% completion  
✅ Traitor correctly voted out

### Traitor Wins
✅ All honest sailors dead  
✅ Day 100 reached, ship <100%  
✅ Fewer than 3 sailors alive (can't complete ship)

---

## 🎮 KEY ACTION TYPES

### Movement
- `MOVE_NORTH/SOUTH/EAST/WEST`: Walk one tile
- `CLIMB_UP/CLIMB_DOWN`: Change levels (at stairs)

### Resources
- `GATHER_RESOURCE`: Pick up resource at location
- `DEPOSIT_ITEM`: Put items in common inventory
- `GIVE_ITEM`: Transfer to adjacent sailor
- `EAT_FOOD`: Consume food for energy

### Ship
- `BUILD_SHIP`: Contribute to ship (need 2+ sailors)

### Social
- `SEND_MESSAGE`: Broadcast or direct message
- `CALL_SOS`: Emergency help request
- `CALL_VOTE`: Initiate elimination vote
- `VOTE`: Cast vote for accused sailor
- `SHOW_BACKPACK`: Reveal inventory (or refuse)

### Special
- `USE_ANTIDOTE`: Cure poison on self/other
- `FRAME_SAILOR`: Plant evidence (traitor only, 1×)
- `SABOTAGE_SHIP`: Damage component (traitor only)

### Passive
- `WAIT`: Do nothing this turn

---

## 📊 VICTORY TIERS (Scoring)

### Sailors

| Tier | Points | Requirements |
|------|--------|--------------|
| **Complete** | 100 | Ship done, all 4 alive, traitor caught by Day 30 |
| **Strong** | 75 | Ship done, 3 alive, traitor caught by Day 60 |
| **Narrow** | 50 | Ship done, 2 alive |
| **Pyrrhic** | 25 | Traitor caught but ship only 60-80% |

### Traitor

| Tier | Points | Requirements |
|------|--------|--------------|
| **Complete** | 100 | All sailors dead, never suspected |
| **Strong** | 75 | Day 100, ship <50%, 2+ killed |
| **Narrow** | 50 | Day 100, ship 50-80%, 1 killed |
| **Lucky** | 25 | Survived wrong vote, ship incomplete |

---

## 💡 QUICK TIPS

### For Honest Sailors
- ✅ Travel in pairs to verify claims
- ✅ Cross-reference location reports
- ✅ Track who gave food to whom
- ✅ Stockpile antidotes early
- ✅ Build evidence case before voting

### For Traitor
- ⚠️ Lie about locations (but not TOO obviously)
- ⚠️ Collect poison when alone
- ⚠️ Respond to SOS with poison disguised as food
- ⚠️ Blame others for discrepancies
- ⚠️ Hoard key resources (wood/metal)
- ⚠️ Don't be the first to accuse (looks suspicious)

---

## 🔧 CONFIG CONSTANTS

Quick reference for key numbers:

```python
TOTAL_SAILORS = 5
TRAITOR_COUNT = 1
MAX_DAYS = 100
TURNS_PER_DAY = 100

INITIAL_ENERGY = 100
BACKPACK_CAPACITY = 20
SPATIAL_VIEW_RADIUS = 5
POISON_DEATH_DAY = 3

MIN_SAILORS_TO_BUILD = 2
MIN_SAILORS_TO_WIN = 3
BUILD_ACTION_TURNS = 5
```

---

**Reference Complete! 🏴‍☠️**
