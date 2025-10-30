### Architecture Diagram

┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: TRAINING LAYER │
│ (Python Notebooks) │
├─────────────────────────────────────────────────────────────────┤
│ │
│ Student LLM Environment Teacher LLM │
│ (Llama 3.1 8B) → (MaroonedEnv) → (Mixtral-8x7B) │
│ ↓ │
│ Every 10-25 Steps │
│ ↓ │
│ training_logger.log_turn() │
│ ↓ │
│ POST /api/training/turn (JSON) │
│ │
└──────────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: DATA LAYER │
│ (Flask API + Database) │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────────┐ ┌──────────────────────┐ │
│ │ Flask API Server │ │ Data Storage │ │
│ │ (localhost:5000) │ │ │ │
│ ├──────────────────────┤ ├──────────────────────┤ │
│ │ POST /training/* │ → │ SQLite Database │ │
│ │ GET /episodes/* │ ↔ │ (data/episodes.db) │ │
│ │ GET /training/* │ ↔ │ + JSON Backup │ │
│ └──────────────────────┘ │ (data/episodes/) │ │
│ └──────────────────────┘ │
│ │
└──────────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: VISUALIZATION LAYER │
│ (Web Browser) │
├─────────────────────────────────────────────────────────────────┤
│ │
│ GET /api/episodes/latest → simulation.js │
│ ↓ │
│ Canvas Rendering │
│ ↓ │
│ - Animated Agent Movement │
│ - Ship Building Progress │
│ - Voting Phase Dialogue │
│ - Real-time Game State │
│ │
└───────────────────────────────────────────────────────────────



### Data Flow: Training to Visualization

**Step 1: Training Capture**
Notebook: log_turn(agent='Alice', action='GATHER_WOOD', reward=0.2)
↓
Flask Endpoint: POST /api/training/turn
↓
Database: INSERT INTO turns (agent, action, reward, ...)
↓
JSON Backup: episode_1.json

text

**Step 2: Frontend Retrieval**
Browser: GET /api/episodes/latest
↓
Flask Response: {episode_id: 1, turns: [...], traitor: 'Charlie', ...}
↓
simulation.js: Parse turns into animation sequence
↓
Display: Replay episode with smooth animations


### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|-----------------|
| **Training** | `training_logger.py` | Hook into notebooks, log game events |
| **API** | `app.py` | REST endpoints, handle HTTP requests |
| **Storage** | `database.py` | SQLite operations, queries, transactions |
| **Models** | `models.py` | Data schemas (Episode, Turn, VotingPhase) |
| **Frontend** | `simulation.js` | Fetch data, animate, render UI |

---
