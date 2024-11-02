import asyncio
import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib

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

# Define request models using Pydantic
class PublishRequest(BaseModel):
    topic: str
    data: str

class SubscribeRequest(BaseModel):
    topic: str

class QueryRequest(BaseModel):
    topic: str

# Helper function to calculate hash of a topic for DHT
def hash_topic(topic):
    return int(hashlib.sha256(topic.encode()).hexdigest(), 16) % NUM_NODES

# Hypercube neighbor calculation
def get_neighbors(peer_id):
    neighbors = []
    for i in range(HYPERCUBE_DIMENSIONS):
        neighbor_id = list(peer_id)
        neighbor_id[i] = '1' if neighbor_id[i] == '0' else '0'
        neighbors.append(''.join(neighbor_id))
    return neighbors

# Route requests across the hypercube
async def route_request(action, topic, data=None, target_node=None):
    visited = set()  # Tracks visited nodes
    queue = [(peer_id, 0)]
    while queue:
        current_node, dist = queue.pop(0)
        if current_node == target_node:
            if action == 'publish':
                local_dht[topic] = data
                logging.info(f"Routed 'publish' for topic '{topic}' to node {target_node}")
            elif action in ('subscribe', 'query'):
                data = local_dht.get(topic, "Topic not found.")
                logging.info(f"Routed '{action}' for topic '{topic}' to node {target_node}")
            return data
        visited.add(current_node)
        for neighbor in get_neighbors(current_node):
            if neighbor not in visited:
                queue.append((neighbor, dist + 1))
    return "Topic not found."

# API to publish a topic
@app.post("/publish")
async def publish(request: PublishRequest):
    topic = request.topic
    data = request.data
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        local_dht[topic] = data
        logging.info(f"Stored topic '{topic}' locally.")
        return {"status": "Success", "message": f"Published topic '{topic}'."}
    else:
        await route_request('publish', topic, data, target_node)
        return {"status": "Success", "message": f"Published topic '{topic}' to node {target_node}."}

# API to subscribe to a topic
@app.post("/subscribe")
async def subscribe(request: SubscribeRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        data = local_dht.get(topic, "Topic not found.")
        logging.info(f"Retrieved subscription data for topic '{topic}' locally.")
    else:
        data = await route_request('subscribe', topic, target_node=target_node)
    return {"status": "Success", "data": data}

# API to query a topic
@app.post("/query")
async def query(request: QueryRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        data = local_dht.get(topic, "Topic not found.")
        logging.info(f"Queried data for topic '{topic}' locally.")
    else:
        data = await route_request('query', topic, target_node=target_node)
    return {"status": "Success", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
