import logging
import sys
import httpx
from config import NODE_ADDRESSES

# Local DHT storage for this peer
local_dht = {}  # Each peer has its own subset of topics
message_storage = {}  # Store messages for each topic
subscriptions = {}  # Store subscriptions for each topic

peer_id = sys.argv[2]  # Binary string ID of the peer node

async def create_topic(topic, data=None):
    local_dht[topic] = data
    logging.info(f"Created topic '{topic}' at node {peer_id}")
    return {"status": "Success", "message": f"Topic '{topic}' created at node {peer_id}"}

async def delete_topic(topic):
    if topic in local_dht:
        del local_dht[topic]
        if topic in message_storage:
            del message_storage[topic]
        logging.info(f"Deleted topic '{topic}' at node {peer_id}")
        return {"status": "Success", "message": f"Topic '{topic}' deleted."}
    else:
        logging.warning(f"Attempted to delete non-existent topic '{topic}' at node {peer_id}")
        return {"status": "Error", "message": "Topic not found."}

async def publish_message(topic, message):
    if topic not in message_storage:
        message_storage[topic] = []
    message_storage[topic].append(message)
    logging.info(f"Published message to topic '{topic}' at node {peer_id}")
    return {"status": "Success", "message": f"Message published to topic '{topic}'"}

async def pull_messages(topic):
    messages = message_storage.get(topic, [])
    logging.info(f"Pulled messages for topic '{topic}' at node {peer_id}: {messages}")
    return {"status": "Success", "messages": messages}

async def query_topic(topic):
    if topic in local_dht:
        logging.info(f"Queried topic '{topic}' found at node {peer_id}")
        return {"status": "Success", "node": peer_id}
    else:
        logging.warning(f"Queried topic '{topic}' not found at node {peer_id}")
        return {"status": "Error", "message": "Topic not found."}

async def subscribe(topic):
    """Subscribes to a topic."""
    if topic not in subscriptions:
        subscriptions[topic] = []
    if peer_id not in subscriptions[topic]:
        subscriptions[topic].append(peer_id)  # Add this peer to the subscription list
    logging.info(f"Node {peer_id} subscribed to topic '{topic}'")
    return {"status": "Success", "message": f"Subscribed to topic '{topic}'"}

async def forward_request(target_node, endpoint, data):
    """Forward a request to the specified node address."""
    node_address = NODE_ADDRESSES.get(target_node)
    if not node_address:
        logging.error(f"Node address for {target_node} not found.")
        return {"status": "Error", "message": "Target node not found."}

    url = f"{node_address}/{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to forward request to {node_address}: {e}")
        return {"status": "Error", "message": "Failed to forward request to target node."}
