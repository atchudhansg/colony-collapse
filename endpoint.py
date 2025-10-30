from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api/training-log')
def get_training_log():
    # Read from your training notebook output
    with open('training_log.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)
