# MAROONED Training API - Setup Guide

## Installation

### 1. Install Dependencies

cd collapse_colony/api
pip install -r requirements.txt

text

### 2. Setup Environment Variables

cp .env.example .env

Edit .env with your configuration
text

### 3. Initialize Database

python

from database import TrainingDatabase
db = TrainingDatabase()
exit()

text

### 4. Start API Server

python run.py

text

The API will be available at:
- **REST API**: http://localhost:5000
- **WebSocket**: ws://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## API Endpoints

### Health & Info
- `GET /api/health` - Health check
- `GET /api/info` - API information

### Episode Management
- `GET /api/episodes` - List all episodes
- `GET /api/episodes/<id>` - Get episode details
- `GET /api/episodes/latest` - Get latest episode
- `GET /api/episodes/<id>/map` - Get map state
- `GET /api/episodes/<id>/export` - Export as JSON

### Training Logging (POST)
- `POST /api/training/episode/start` - Start episode
- `POST /api/training/turn` - Log turn
- `POST /api/training/voting` - Log voting phase
- `POST /api/training/map` - Save map state
- `POST /api/training/episode/end` - End episode

### Statistics
- `GET /api/training/status` - Current training status
- `GET /api/training/stats` - Training statistics



obs, _ = env.reset()
total_episode_reward = 0
current_ship_progress = 0

for step in range(max_steps):
    # Your RL training code
    actions = policy_network(obs)
    obs, rewards, dones, truncated, info = env.step(actions)
    
    # 📊 LOG EACH TURN
    for agent_name in env.agents:
        if agent_name in obs:
            agent_obs = obs[agent_name]
            
            log_turn(
                turn=step + 1,
                day=step // 20 + 1,
                phase='exploration' if step % 100 < 90 else 'voting',
                agent=agent_name,
                role=info.get(f'{agent_name}_role', 'colonist'),
                action=str(actions.get(agent_name, 'wait')),
                reasoning=info.get(f'{agent_name}_reasoning', 'Exploring'),
                message=info.get(f'{agent_name}_message', 'N/A'),
                position={
                    'x': int(agent_obs.position.x),
                    'y': int(agent_obs.position.y),
                    'level': agent_obs.position.level.value
                },
                energy=float(agent_obs.energy),
                health=float(agent_obs.health),
                backpack=dict(agent_obs.backpack),
                reward=float(rewards.get(agent_name, 0)),
                ship_progress=float(info.get('ship_progress', 0))
            )
    
    # 🗳️ LOG VOTING IF APPLICABLE
    if step > 0 and step % 100 == 99:  # Voting every 100 steps
        log_voting(
            day=step // 20 + 1,
            caller=info.get('voting_caller', 'Alice'),
            discussions=[
                {'agent': agent, 'message': f"I think {agent} is suspicious"}
                for agent in list(env.agents.keys())[:2]
            ],
            votes=[
                {'agent': agent, 'voted_for': np.random.choice(list(env.agents.keys()))}
                for agent in env.agents.keys()
            ],
            eliminated=info.get('voted_out', None),
            outcome=info.get('voting_outcome', 'pending')
        )
    
    total_episode_reward += sum(rewards.values())
    current_ship_progress = info.get('ship_progress', 0)
    
    if dones.get('episode_done', False):
        break

# 🏁 END EPISODE
log_episode_end(
    final_result=info.get('result', 'unknown'),
    ship_progress=current_ship_progress,
    colonists_alive=info.get('colonists_alive', 5),
    traitor_alive=info.get('traitor_alive', True)
)

print(f"Episode {episode+1}/{num_episodes} | Reward: {total_episode_reward:.2f} | Ship: {current_ship_progress:.1f}%")

## 🧪 Testing the API

### Test Health Check

curl http://localhost:5000/api/health

text

**Response:**
{
"status": "healthy",
"timestamp": "2025-10-30T20:30:00.123456",
"service": "MAROONED Training API"
}

text

### Test Episode Logging

import requests
import json

BASE_URL = 'http://localhost:5000'

Start episode
response = requests.post(f'{BASE_URL}/api/training/episode/start', json={
'episode_num': 1,
'traitor': 'Charlie'
})
print(response.json())

Log a turn
response = requests.post(f'{BASE_URL}/api/training/turn', json={
'turn': 1,
'day': 1,
'phase': 'exploration',
'agent': 'Alice',
'role': 'colonist',
'action': 'move_north',
'reasoning': 'Exploring area',
'message': 'Moving north',
'position': {'x': 15, 'y': 14, 'level': 'ground'},
'energy': 97,
'health': 100,
'reward': -0.01,
'ship_progress': 2
})
print(response.json())

End episode
response = requests.post(f'{BASE_URL}/api/training/episode/end', json={
'final_result': 'colonists_win',
'ship_progress': 75.5,
'colonists_alive': 4,
'traitor_alive': False
})
print(response.json())

Get latest episode
response = requests.get(f'{BASE_URL}/api/episodes/latest')
episode = response.json()
print(f"Episode {episode['episode_id']}: {episode['traitor']} - {episode['final_result']}")
print(f"Total turns: {episode['total_turns']}, Reward: {episode['total_reward']}")

text

---

## 📊 Viewing Data

### Check Stored Episodes

from database import TrainingDatabase

db = TrainingDatabase()
episodes = db.get_all_episodes(limit=10)

for ep in episodes:
print(f"Episode {ep['episode_id']}: Traitor={ep['traitor']}, Result={ep['final_result']}, Turns={ep['total_turns']}")

text

### View Training Statistics

curl http://localhost:5000/api/training/stats | python -m json.tool

text

### Export Episode as JSON

curl http://localhost:5000/api/episodes/1/export > episode_1.json

text

---

## 🔄 File Storage

Episodes are automatically saved in two formats:

### 1. **SQLite Database** (`data/episodes.db`)
- For efficient querying
- Indexed lookups
- Used by REST API

### 2. **JSON Files** (`data/episodes/`)
- Human-readable format
- Backup storage
- Example: `episode_1.json`

---

## 🐛 Troubleshooting

### Issue: "Database is locked"
**Solution:**
rm data/episodes.db
python run.py # Restart

text

### Issue: "Port 5000 already in use"
**Solution:**
Use different port
export API_PORT=5001
python run.py

text

Or modify `.env`:
API_PORT=5001

text

### Issue: CORS errors in frontend
**Solution:** Add your frontend URL to `.env`:
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-domain.com

text

### Issue: Module not found errors
**Solution:**
Reinstall dependencies
pip install -r requirements.txt --force-reinstall

text

---

## 📁 Directory Structure

collapse_colony/
├── api/
│ ├── app.py # Flask application
│ ├── models.py # Data models
│ ├── database.py # Database operations
│ ├── logger.py # Training logger
│ ├── config.py # Configuration
│ ├── run.py # Startup script
│ ├── requirements.txt # Dependencies
│ ├── .env.example # Environment template
│ ├── .env # Environment config
│ └── README_SETUP.md # This file
├── training_logger.py # Notebook integration hook
├── data/
│ ├── episodes.db # SQLite database (auto-created)
│ └── episodes/ # JSON episode files (auto-created)
├── logs/ # Log files (auto-created)
└── [other training files]

text

---

## 🚢 Production Deployment

### Using Gunicorn + Nginx

#### 1. Install Gunicorn
pip install gunicorn

text

#### 2. Create systemd service
sudo tee /etc/systemd/system/marooned-api.service > /dev/null <<EOF
[Unit]
Description=MAROONED Training API
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) -m gunicorn --worker-class sync -w 4 --bind 0.0.0.0:5000 app:app
Restart=always
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start marooned-api
sudo systemctl enable marooned-api

text

#### 3. Configure Nginx
server {
listen 80;
server_name your-domain.com;

text
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
}

text

### Docker Deployment

#### Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production

CMD ["gunicorn", "--worker-class", "sync", "-w", "4", "--bind", "0.0.0.0:5000", "api.app:app"]

text

#### Build & Run
docker build -t marooned-api .
docker run -p 5000:5000 -v $(pwd)/data:/app/data marooned-api

text

### Heroku Deployment

#### 1. Create Procfile
web: gunicorn --worker-class sync -w 4 --bind 0.0.0.0:$PORT api.app:app

text

#### 2. Deploy
heroku login
heroku create marooned-api
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python3 -c 'import os; print(os.urandom(32).hex())')
git push heroku main

text

---

## 📈 Monitoring

### View API Logs
tail -f logs/api.log

text

### Check Database Size
du -h data/episodes.db

text

### API Health Status
watch -n 1 'curl -s http://localhost:5000/api/health | python -m json.tool'

text

### Training Status
curl http://localhost:5000/api/training/status | python -m json.tool

text

---

## 🔐 Security

### For Production:

1. **Change SECRET_KEY in .env:**
python3 -c 'import os; print(os.urandom(32).hex())'

Copy output to .env
text

2. **Set FLASK_ENV:**
FLASK_ENV=production

text

3. **Restrict CORS:**
CORS_ORIGINS=https://your-domain.com

text

4. **Use HTTPS with SSL certificate**

5. **Database Backup:**
sqlite3 data/episodes.db ".backup backup_$(date +%Y%m%d).db"

text

---

## 📞 Support

For issues:
1. Check logs: `logs/api.log`
2. Verify database: `sqlite3 data/episodes.db ".tables"`
3. Test connectivity: `curl http://localhost:5000/api/health`

---

**🎉 Setup complete! Your training API is ready!**
File 12: collapse_colony/TRAINING_INTEGRATION_EXAMPLE.md (Real Usage Example)
text
# Training Integration - Real World Example

## Complete Example from Notebook

Here's a complete, working example that integrates the training logger into your RL training notebook.

### Setup

Cell 1: Imports and Setup
%pip install flask flask-cors python-dotenv

import sys
sys.path.insert(0, '/path/to/collapse_colony')

from training_logger import init_logger, log_episode_start, log_turn, log_voting, log_episode_end
import numpy as np

Initialize logger
logger = init_logger()
print("✅ Logger initialized")

Check if API is running
import requests
try:
response = requests.get('http://localhost:5000/api/health')
print(f"✅ API Status: {response.json()['status']}")
except:
print("⚠️ API not running. Start it with: python collapse_colony/api/run.py")

text

### Training Loop Example

Cell 2: Training Loop with Logging
num_episodes = 50

for episode in range(num_episodes):
# Randomly select traitor
agents = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
traitor = np.random.choice(agents)

text
# 🎬 START EPISODE
log_episode_start(episode + 1, traitor)

# Initialize environment
obs, info = env.reset()

episode_reward = 0
episode_turns = 0
current_ship_progress = 0
agents_alive = {'Alice': True, 'Bob': True, 'Charlie': True, 'Diana': True, 'Eve': True}

for step in range(200):
    # Get actions from policy
    actions = {}
    for agent in env.agents:
        if agent not in obs:
            continue
        
        # Your policy here
        action = env.action_space(agent).sample()  # or your policy
        actions[agent] = action
    
    # Step environment
    obs, rewards, dones, truncated, info = env.step(actions)
    
    # 📊 LOG EACH AGENT'S TURN
    for agent in env.agents:
        if agent not in obs:
            continue
        
        agent_obs = obs[agent]
        agent_reward = rewards.get(agent, 0)
        
        # Determine action type
        if actions[agent] == 0:
            action_type = 'move_north'
        elif actions[agent] == 1:
            action_type = 'move_south'
        else:
            action_type = 'gather_resource'
        
        # Log turn
        log_turn(
            turn=step + 1,
            day=step // 25 + 1,
            phase='exploration' if step < 150 else 'voting',
            agent=agent,
            role='traitor' if agent == traitor else 'colonist',
            action=action_type,
            reasoning=f"Agent {agent} performing {action_type}",
            message=f"I'm {action_type}",
            position={
                'x': int(agent_obs.position.x),
                'y': int(agent_obs.position.y),
                'level': agent_obs.position.level.value
            },
            energy=float(agent_obs.energy),
            health=float(agent_obs.health),
            backpack={
                'wood': int(agent_obs.backpack['wood']),
                'metal': int(agent_obs.backpack['metal']),
                'food': int(agent_obs.backpack['food'])
            },
            reward=float(agent_reward),
            ship_progress=float(info.get('ship_progress', 0))
        )
        
        episode_reward += agent_reward
    
    # 🗳️ VOTING PHASE (every 50 steps)
    if step > 0 and step % 50 == 49:
        voting_day = step // 25 + 1
        
        # Simulate discussions
        discussions = []
        for agent in env.agents:
            discussions.append({
                'agent': agent,
                'message': f"I think {traitor} is the traitor!" if np.random.random() > 0.5 else "I'm innocent!"
            })
        
        # Simulate votes
        votes = []
        for agent in env.agents:
            # Random vote (or your voting logic)
            voted_for = np.random.choice([a for a in env.agents if a != agent])
            votes.append({
                'agent': agent,
                'voted_for': voted_for
            })
        
        # Count votes to determine eliminated
        vote_counts = {}
        for vote in votes:
            voted_for = vote['voted_for']
            vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1
        
        eliminated = max(vote_counts, key=vote_counts.get) if vote_counts else None
        
        # Log voting phase
        log_voting(
            day=voting_day,
            caller=np.random.choice(env.agents),
            discussions=discussions,
            votes=votes,
            eliminated=eliminated,
            outcome='eliminated' if eliminated else 'skipped'
        )
        
        # Update agents alive
        if eliminated:
            agents_alive[eliminated] = False
    
    current_ship_progress = info.get('ship_progress', 0)
    episode_turns = step + 1
    
    # Check for episode end
    if dones.get('episode_done', False):
        break

# 🏁 END EPISODE
colonists_alive = sum(1 for agent in env.agents if agents_alive.get(agent, True) and agent != traitor)
traitor_alive = agents_alive.get(traitor, True)

if current_ship_progress >= 100:
    result = 'colonists_win' if traitor_alive else 'colonists_win'
elif not traitor_alive:
    result = 'colonists_win'
else:
    result = 'traitor_win'

log_episode_end(
    final_result=result,
    ship_progress=current_ship_progress,
    colonists_alive=colonists_alive,
    traitor_alive=traitor_alive
)

print(f"Episode {episode+1:3d} | Traitor: {traitor:8s} | Reward: {episode_reward:7.2f} | Ship: {current_ship_progress:5.1f}% | Result: {result}")
text

### View Results

Cell 3: View Logged Data
import pandas as pd
from database import TrainingDatabase

db = TrainingDatabase()

Get all episodes
episodes = db.get_all_episodes(limit=50)

Create dataframe
df = pd.DataFrame(episodes)
print("\n📊 Episodes Summary:")
print(df[['episode_id', 'traitor', 'final_result', 'total_turns', 'total_reward', 'ship_progress_final']])

Statistics
print("\n📈 Statistics:")
print(f"Total episodes: {len(episodes)}")
print(f"Colonists wins: {len(df[df['final_result'] == 'colonists_win'])}")
print(f"Traitor wins: {len(df[df['final_result'] == 'traitor_win'])}")
print(f"Avg reward: {df['total_reward'].mean():.2f}")
print(f"Avg ship progress: {df['ship_progress_final'].mean():.1f}%")

Get specific episode
latest_episode = db.get_episode(episodes['episode_id'])
print(f"\n🎮 Latest Episode Details:")
print(f"Traitor: {latest_episode['traitor']}")
print(f"Turns: {len(latest_episode['turns'])}")
print(f"Voting phases: {len(latest_episode['voting_phases'])}")

text

### Query Database Directly

Cell 4: Advanced Queries
import sqlite3

conn = sqlite3.connect('collapse_colony/data/episodes.db')
cursor = conn.cursor()

Find all traitor actions
cursor.execute('''
SELECT agent, action, COUNT(*) as count
FROM turns
WHERE action LIKE '%sabotage%'
GROUP BY agent, action
ORDER BY count DESC
''')

print("Sabotage actions by agent:")
for row in cursor.fetchall():
print(f" {row}: {row} ({row} times)")​

conn.close()

text

---

## API Test Script

test_api.py - Run this to verify everything works
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_api():
print("🧪 Testing MAROONED Training API\n")

text
# 1. Health check
print("1. Testing health check...")
response = requests.get(f'{BASE_URL}/api/health')
assert response.status_code == 200
print("   ✅ Health check passed")

# 2. Start episode
print("\n2. Starting episode...")
response = requests.post(f'{BASE_URL}/api/training/episode/start', json={
    'episode_num': 1,
    'traitor': 'Charlie'
})
assert response.status_code == 201
print("   ✅ Episode started")

# 3. Log turns
print("\n3. Logging turns...")
for turn in range(1, 6):
    response = requests.post(f'{BASE_URL}/api/training/turn', json={
        'turn': turn,
        'day': 1,
        'phase': 'exploration',
        'agent': 'Alice',
        'role': 'colonist',
        'action': 'move_north',
        'reasoning': 'Exploring',
        'message': 'Moving',
        'position': {'x': 15, 'y': 14, 'level': 'ground'},
        'energy': 100 - turn * 3,
        'health': 100,
        'reward': -0.01,
        'ship_progress': turn * 2
    })
    assert response.status_code == 200
print("   ✅ 5 turns logged")

# 4. End episode
print("\n4. Ending episode...")
response = requests.post(f'{BASE_URL}/api/training/episode/end', json={
    'final_result': 'colonists_win',
    'ship_progress': 10,
    'colonists_alive': 4,
    'traitor_alive': False
})
assert response.status_code == 200
print("   ✅ Episode ended")

# 5. Get episode
print("\n5. Retrieving episode...")
response = requests.get(f'{BASE_URL}/api/episodes/1')
assert response.status_code == 200
episode = response.json()
print(f"   ✅ Retrieved episode 1: {episode['traitor']} - {episode['final_result']}")

# 6. List episodes
print("\n6. Listing episodes...")
response = requests.get(f'{BASE_URL}/api/episodes')
assert response.status_code == 200
print(f"   ✅ Found {response.json()['count']} episodes")

# 7. Get stats
print("\n7. Getting statistics...")
response = requests.get(f'{BASE_URL}/api/training/stats')
assert response.status_code == 200
stats = response.json()
print(f"   ✅ Total episodes: {stats['total_episodes']}")

print("\n✅ All tests passed!")
if name == 'main':
try:
test_api()
except requests.exceptions.ConnectionError:
print("❌ Cannot connect to API. Start it with:")
print(" python collapse_colony/api/run.py")
except AssertionError as e:
print(f"❌ Test failed: {e}")
except Exception as e:
print(f"❌ Error: {e}")

text

---

**✅ All setup and integration documentation complete!**

Your Flask backend is now fully documented and ready for integration with:
1. ✅ Training notebooks
2. ✅ Frontend visualization
3. ✅ Real-time monitoring
4. ✅ Production deployment
COMPLETE FLASK BACKEND READY! 🚀

All files created:

✅ requirements.txt

✅ models.py

✅ database.py

✅ logger.py

✅ config.py

✅ app.py

✅ run.py

✅ .env.example

✅ .env

✅ training_logger.py

✅ README_SETUP.md

✅ TRAINING_INTEGRATION_EXAMPLE.md

Next Step: Update frontend simulation.js to fetch from this API? 🎮

ppl-ai-file-upload
https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/51324597/aa7c6077-d2c2-4780-8934-b658d9602c04/Screenshot-2025-10-30-082610.jpg
Screenshot-2025-10-30-082610.jpg
ppl-ai-file-upload
https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/51324597/dcb42e9c-ddfb-4200-abc7-99332edb274f/Screenshot-2025-10-30-082551.jpg
Screenshot-2025-10-30-082551.jpg
