import asyncio
import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import uvicorn
import requests  # Import requests for forwarding requests

# Define the FastAPI app
app = FastAPI()

# Constants for hypercube configuration
NUM_NODES = 8  # Assume 3D hypercube with 8 nodes
HYPERCUBE_DIMENSIONS = 3  # Dimensions of hypercube

# Initialize peer settings
peer_id = sys.argv[2]  # Binary string ID of the peer node
port = int(sys.argv[1])  # Port number for this peer node

# Directory setup for logging
log_dir = './Out/Logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_filename = f"{peer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_path = os.path.join(log_dir, log_filename)
logging.basicConfig(filename=log_path, level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Local DHT storage for this peer
local_dht = {}  # Each peer has its own subset of topics
message_storage = {}  # Store messages for each topic

# Define request models using Pydantic
class CreateTopicRequest(BaseModel):
    topic: str

class SubscribeRequest(BaseModel):
    topic: str

class PublishMessageRequest(BaseModel):
    topic: str
    message: str

class PullMessagesRequest(BaseModel):
    topic: str

class QueryTopicRequest(BaseModel):
    topic: str

class DeleteTopicRequest(BaseModel):
    topic: str

# Helper function to calculate hash of a topic for DHT
def hash_topic(topic):
    return int(hashlib.sha256(topic.encode()).hexdigest(), 16) % NUM_NODES

# Forward request function
async def forward_request(target_node, endpoint, data):
    """Forward request to the correct target node in the hypercube network."""
    target_port = 5000 + int(target_node, 2)  # Assuming node ports follow a pattern
    url = f"http://localhost:{target_port}/{endpoint}"
    try:
        response = requests.post(url, json=data)
        return response.json()  # Return the response from the target node
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to forward request to node {target_node}: {e}")
        raise HTTPException(status_code=500, detail="Failed to forward request")

# Hypercube neighbor calculation
def get_neighbors(peer_id):
    neighbors = []
    for i in range(HYPERCUBE_DIMENSIONS):
        neighbor_id = list(peer_id)
        neighbor_id[i] = '1' if neighbor_id[i] == '0' else '0'
        neighbors.append(''.join(neighbor_id))
    return neighbors

# Separate functions for each action
async def handle_create_topic(topic, data=None):
    local_dht[topic] = data
    logging.info(f"Created topic '{topic}' at node {peer_id}")
    return {"status": "Success", "message": f"Topic '{topic}' created at node {peer_id}"}

async def handle_subscribe(topic):
    logging.info(f"Node {peer_id} subscribed to topic '{topic}'")
    return {"status": "Success", "message": f"Subscribed to topic '{topic}'"}

async def handle_publish_message(topic, message):
    message_storage.setdefault(topic, []).append(message)
    logging.info(f"Published message to topic '{topic}' at node {peer_id}")
    return {"status": "Success", "message": f"Message published to topic '{topic}'"}

async def handle_pull_messages(topic):
    messages = message_storage.get(topic, [])
    logging.info(f"Pulled messages for topic '{topic}' at node {peer_id}: {messages}")
    return {"status": "Success", "messages": messages}

async def handle_query_topic(topic):
    if topic in local_dht:
        logging.info(f"Queried topic '{topic}' found at node {peer_id}")
        return {"status": "Success", "node": peer_id}
    else:
        return "Topic not found."

async def handle_delete_topic(topic):
    if topic in local_dht:
        del local_dht[topic]
        if topic in message_storage:
            del message_storage[topic]
        logging.info(f"Deleted topic '{topic}' at node {peer_id}")
        return {"status": "Success", "message": f"Topic '{topic}' deleted."}
    else:
        return "Topic not found."

# API to create a new topic
@app.post("/create_topic")
async def create_topic(request: CreateTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await handle_create_topic(topic, {})
    else:
        # Forward request to the target node
        return await forward_request(target_node, "create_topic", request.dict())

# API to subscribe to a topic
@app.post("/subscribe")
async def subscribe(request: SubscribeRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await handle_subscribe(topic)
    else:
        return await forward_request(target_node, "subscribe", request.dict())

# API to publish a message to a topic
@app.post("/publish_message")
async def publish_message(request: PublishMessageRequest):
    topic = request.topic
    message = request.message
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await handle_publish_message(topic, message)
    else:
        return await forward_request(target_node, "publish_message", request.dict())

# API to pull messages from a topic
@app.post("/pull_messages")
async def pull_messages(request: PullMessagesRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await handle_pull_messages(topic)
    else:
        return await forward_request(target_node, "pull_messages", request.dict())

# API to query a topic
@app.post("/query_topic")
async def query_topic(request: QueryTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        response = await handle_query_topic(topic)
        if response == "Topic not found.":
            raise HTTPException(status_code=404, detail="Topic not found.")
        return response
    else:
        return await forward_request(target_node, "query_topic", request.dict())

# API to delete a topic
@app.post("/delete_topic")
async def delete_topic(request: DeleteTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        response = await handle_delete_topic(topic)
        if response == "Topic not found.":
            raise HTTPException(status_code=404, detail="Topic not found.")
        return response
    else:
        return await forward_request(target_node, "delete_topic", request.dict())

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
