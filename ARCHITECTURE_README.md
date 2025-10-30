### MAROONED Architecture Diagram 
```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: TRAINING LAYER                                          │
│ (Python Notebooks)                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Student LLM         Environment       Teacher LLM              │
│ (Llama 3.1 8B) → (MaroonedEnv) → (Mixtral-8x7B)               │
│                      ↓                                          │
│               Every 10-25 Steps                                 │
│                      ↓                                          │
│          training_logger.log_turn()                            │
│                      ↓                                          │
│          POST /api/training/turn (JSON)                        │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: DATA LAYER                                              │
│ (Flask API + Database)                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────────────┐ ┌──────────────────────┐              │
│ │ Flask API Server     │ │ Data Storage         │              │
│ │ (localhost:5000)     │ │                      │              │
│ ├──────────────────────┤ ├──────────────────────┤              │
│ │ POST /training/*     │→│ SQLite Database      │              │
│ │ GET /episodes/*      │↔│ (data/episodes.db)   │              │
│ │ GET /training/*      │↔│ + JSON Backup        │              │
│ └──────────────────────┘ │ (data/episodes/)     │              │
│                          └──────────────────────┘              │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: VISUALIZATION LAYER                                     │
│ (Web Browser)                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ GET /api/episodes/latest → simulation.js                       │
│                      ↓                                          │
│            Canvas Rendering                                     │
│                      ↓                                          │
│       - Animated Agent Movement                                 │
│       - Ship Building Progress                                  │
│       - Voting Phase Dialogue                                   │
│       - Real-time Game State                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```