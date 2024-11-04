from flask import Flask, request, jsonify
import logging
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)

# Suppress Flask's default logging messages
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

# Store active peer nodes and their topics
global_topics = {}  # Global topic message storage
peer_nodes = {}  # Stores which topics each peer is subscribed to
peer_queues = defaultdict(lambda: defaultdict(list))  # Per-peer message queues

# Set up logging
log_dir = '../Out/Logs'  # Updated log directory
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Setup logging for the indexing server
log_filename = f"indexing_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_path = os.path.join(log_dir, log_filename)  # Full path to the log file
logging.basicConfig(filename=log_path, level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

@app.route('/register_peer_node', methods=['POST'])
def register_peer_node():
    data = request.json
    peer_id = data['peer_id']
    peer_nodes[peer_id] = []  # Initialize with empty topics list
    logging.info(f"Peer node '{peer_id}' registered.")
    return jsonify({"message": "Peer node registered successfully."}), 200

@app.route('/unregister_peer_node', methods=['POST'])
def unregister_peer_node():
    data = request.json
    peer_id = data['peer_id']
    peer_nodes.pop(peer_id, None)
    peer_queues.pop(peer_id, None)
    logging.info(f"Peer node '{peer_id}' unregistered.")
    return jsonify({"message": "Peer node unregistered."}), 200

@app.route('/create_topic', methods=['POST'])
def create_topic():
    data = request.json
    topic = data['topic']

    # Initialize the global topic list
    global_topics[topic] = []  # Initialize a list for storing messages
    logging.info(f"Topic '{topic}' created.")
    return jsonify({"message": f"Topic '{topic}' created successfully."}), 200

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    topic = data['topic']
    message = data['message']

    if topic in global_topics:
        # Add the message to the global topic list
        global_topics[topic].append(message)
        # Add the message to each subscribed peer's queue
        for peer_id in peer_nodes:
            if topic in peer_nodes[peer_id]:
                peer_queues[peer_id][topic].append(message)
        logging.info(f"Published message '{message}' to topic '{topic}'.")
        return jsonify({"message": f"Message '{message}' published to topic '{topic}'."}), 200
    logging.warning(f"Tried to publish to non-existent topic '{topic}'.")
    return jsonify({"message": "Topic not found."}), 404

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    peer_id = data['peer_id']
    topic = data['topic']

    if peer_id not in peer_nodes:
        return jsonify({"message": f"Peer node '{peer_id}' is not registered."}), 400

    if topic not in global_topics:
        return jsonify({"message": "Topic not found."}), 404

    # Register the peer to the topic
    peer_nodes[peer_id].append(topic)
    logging.info(f"Peer '{peer_id}' subscribed to topic '{topic}'.")
    return jsonify({"message": f"Peer '{peer_id}' subscribed to topic '{topic}'."}), 200

@app.route('/pull_messages', methods=['POST'])
def pull_messages():
    data = request.json
    peer_id = data['peer_id']
    topic = data['topic']

    if peer_id not in peer_nodes:
        return jsonify({"message": f"Peer node '{peer_id}' is not registered."}), 400

    if topic not in global_topics:
        return jsonify({"message": "Topic not found."}), 404

    # Retrieve messages for the subscribed topic from the peer's queue
    messages = peer_queues[peer_id][topic]
    logging.info(f"Peer '{peer_id}' pulled messages from topic '{topic}': {messages}")

    # Clear messages from this peer's queue for this topic
    peer_queues[peer_id][topic] = []

    return jsonify({"messages": messages}), 200

@app.route('/query_peers', methods=['GET'])
def query_peers():
    topic = request.args.get('topic')

    if topic not in global_topics:
        return jsonify({"message": "Topic not found."}), 404

    # Find all peers subscribed to this topic
    peers_subscribed = [peer_id for peer_id, topics in peer_nodes.items() if topic in topics]

    logging.info(f"Peers subscribed to topic '{topic}': {peers_subscribed}")
    return jsonify({"peers": peers_subscribed}), 200

@app.route('/delete_topic', methods=['DELETE'])
def delete_topic():
    data = request.json
    topic = data['topic']

    if topic not in global_topics:
        return jsonify({"message": "Topic not found."}), 404

    # Remove the topic from the global topics
    global_topics.pop(topic)

    # Remove the topic from all peers' subscriptions and queues
    for peer_id in peer_nodes:
        if topic in peer_nodes[peer_id]:
            peer_nodes[peer_id].remove(topic)
        if topic in peer_queues[peer_id]:
            del peer_queues[peer_id][topic]

    logging.info(f"Deleted topic '{topic}' and notified all peers.")
    return jsonify({"message": f"Topic '{topic}' deleted successfully."}), 200

if __name__ == '__main__':
    app.run(port=5000, threaded=True)