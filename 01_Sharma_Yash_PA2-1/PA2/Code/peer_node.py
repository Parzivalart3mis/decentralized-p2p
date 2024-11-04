import requests
from flask import Flask, request, jsonify
import logging
from datetime import datetime
import sys
import os

app = Flask(__name__)

# Suppress Flask's default logging messages
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

INDEXING_SERVER_URL = 'http://localhost:5000'

# Set up logging
log_dir = '../Out/Logs'  # Updated log directory
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Setup logging for the peer node
peer_id = sys.argv[2]  # Peer ID from command-line argument
port = int(sys.argv[1])  # Port from command-line argument

log_filename = f"{peer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_path = os.path.join(log_dir, log_filename)  # Full path to the log file
logging.basicConfig(filename=log_path, level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Log the start of the peer node
logging.info(f"Peer node {peer_id} started")

@app.route('/create_topic', methods=['POST'])
def create_topic():
    data = request.json
    topic = data['topic']

    # Request the indexing server to create the topic
    response = requests.post(f'{INDEXING_SERVER_URL}/create_topic',
                             json={'topic': topic})
    if response.status_code == 200:
        logging.info(f"Created topic '{topic}'")
        return jsonify({"message": f"Topic '{topic}' created successfully."}), 200
    else:
        return jsonify({"message": response.json()["message"]}), response.status_code

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    topic = data['topic']
    message = data['message']

    # Notify the indexing server
    response = requests.post(f'{INDEXING_SERVER_URL}/publish', json={'topic': topic, 'message': message})
    if response.status_code == 200:
        logging.info(f"Published message '{message}' to topic '{topic}'.")
        return jsonify({"message": f"Message '{message}' published to topic '{topic}'."}), 200
    else:
        return jsonify({"message": response.json()["message"]}), response.status_code

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    topic = data['topic']

    # Register with the indexing server
    response = requests.post(f'{INDEXING_SERVER_URL}/subscribe', json={'peer_id': peer_id, 'topic': topic})
    if response.status_code == 200:
        logging.info(f"Peer '{peer_id}' subscribed to topic '{topic}'.")
        return jsonify({"message": f"Peer '{peer_id}' subscribed to topic '{topic}'."}), 200
    else:
        return jsonify({"message": response.json()["message"]}), response.status_code

@app.route('/pull_messages', methods=['POST'])
def pull_messages():
    data = request.json
    topic = data['topic']

    # Pull messages from the indexing server
    response = requests.post(f'{INDEXING_SERVER_URL}/pull_messages', json={'peer_id': peer_id, 'topic': topic})
    if response.status_code == 200:
        messages = response.json().get("messages", [])
        logging.info(f"Peer '{peer_id}' pulled messages from topic '{topic}': {messages}")
        return jsonify({"messages": messages}), 200
    else:
        return jsonify({"message": response.json()["message"]}), response.status_code

@app.route('/delete_topic', methods=['DELETE'])
def delete_topic():
    data = request.json
    topic = data['topic']

    # Request the indexing server to delete the topic
    response = requests.delete(f'{INDEXING_SERVER_URL}/delete_topic', json={'topic': topic})
    if response.status_code == 200:
        logging.info(f"Deleted topic '{topic}' from peer '{peer_id}'")
        return jsonify({"message": f"Topic '{topic}' deleted successfully."}), 200
    else:
        return jsonify({"message": response.json()["message"]}), response.status_code

@app.route('/exit_peer', methods=['POST'])
def exit_peer():
    requests.post(f'{INDEXING_SERVER_URL}/unregister_peer_node', json={'peer_id': peer_id})
    logging.info(f"Peer node {peer_id} unregistered and exiting.")
    return jsonify({"message": "Peer node unregistered and exiting."}), 200

if __name__ == '__main__':
    # Register with the indexing server initially
    requests.post(f'{INDEXING_SERVER_URL}/register_peer_node', json={'peer_id': peer_id})
    logging.info(f"Peer node {peer_id} registered with the indexing server.")
    app.run(port=port, threaded=True)