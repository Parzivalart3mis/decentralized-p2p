import asyncio
import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import uvicorn

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
class CreateTopicRequest(BaseModel):
    topic: str

class SubscribeRequest(BaseModel):
    topic: str

class PublishRequest(BaseModel):
    topic: str
    data: str

class PullMessagesRequest(BaseModel):
    topic: str

class QueryRequest(BaseModel):
    topic: str

class DeleteTopicRequest(BaseModel):
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
            if action == 'create':
                if topic not in local_dht:
                    local_dht[topic] = []
                    logging.info(f"Created topic '{topic}' at node {target_node}")
                return {"status": "Success", "message": f"Topic '{topic}' created."}
            elif action == 'publish':
                local_dht[topic].append(data)
                logging.info(f"Routed 'publish' for topic '{topic}' to node {target_node}")
            elif action in ('subscribe', 'pull'):
                data = local_dht.get(topic, "Topic not found.")
                logging.info(f"Routed '{action}' for topic '{topic}' to node {target_node}")
            elif action == 'delete':
                if topic in local_dht:
                    del local_dht[topic]
                    logging.info(f"Deleted topic '{topic}' from node {target_node}")
                    return {"status": "Success", "message": f"Topic '{topic}' deleted."}
            return data
        visited.add(current_node)
        for neighbor in get_neighbors(current_node):
            if neighbor not in visited:
                queue.append((neighbor, dist + 1))
    return "Topic not found."

# API to create a topic
@app.post("/create_topic")
async def create_topic(request: CreateTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        if topic not in local_dht:
            local_dht[topic] = []
            logging.info(f"Created topic '{topic}' locally.")
            return {"status": "Success", "message": f"Topic '{topic}' created."}
        else:
            return {"status": "Failed", "message": f"Topic '{topic}' already exists."}
    else:
        return await route_request('create', topic, target_node=target_node)

# API to subscribe to a topic
@app.post("/subscribe")
async def subscribe(request: SubscribeRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        logging.info(f"Subscribed to topic '{topic}' locally.")
        return {"status": "Success", "message": f"Subscribed to topic '{topic}'."}
    else:
        return await route_request('subscribe', topic, target_node=target_node)

# API to publish a message to a topic
@app.post("/publish_message")
async def publish_message(request: PublishRequest):
    topic = request.topic
    data = request.data
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        local_dht[topic].append(data)
        logging.info(f"Published message to topic '{topic}' locally.")
        return {"status": "Success", "message": f"Message published to topic '{topic}'."}
    else:
        await route_request('publish', topic, data, target_node)
        return {"status": "Success", "message": f"Message published to topic '{topic}' at node {target_node}."}

# API to pull messages from a topic
@app.post("/pull_messages")
async def pull_messages(request: PullMessagesRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        messages = local_dht.get(topic, [])
        logging.info(f"Pulled messages from topic '{topic}' locally.")
        return {"status": "Success", "messages": messages}
    else:
        return await route_request('pull', topic, target_node=target_node)

# API to query the location of a topic
@app.post("/query_topic")
async def query_topic(request: QueryRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    logging.info(f"Queried location for topic '{topic}', assigned to node {target_node}.")
    return {"status": "Success", "message": f"Topic '{topic}' is assigned to node {target_node}."}

# API to delete a topic
@app.post("/delete_topic")
async def delete_topic(request: DeleteTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        if topic in local_dht:
            del local_dht[topic]
            logging.info(f"Deleted topic '{topic}' locally.")
            return {"status": "Success", "message": f"Topic '{topic}' deleted."}
        else:
            return {"status": "Failed", "message": f"Topic '{topic}' not found."}
    else:
        return await route_request('delete', topic, target_node=target_node)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
