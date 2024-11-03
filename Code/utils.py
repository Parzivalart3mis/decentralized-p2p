import hashlib
import httpx  # Make sure to have httpx installed for making HTTP requests
import logging
from config import NUM_NODES, HYPERCUBE_DIMENSIONS

# Helper function to calculate hash of a topic for DHT
def hash_topic(topic):
    """Calculates the hash of a topic for consistent node assignment in the DHT."""
    return int(hashlib.sha256(topic.encode()).hexdigest(), 16) % NUM_NODES

# Hypercube neighbor calculation
def get_neighbors(peer_id):
    """Calculates the neighbors of a given peer in the hypercube topology."""
    neighbors = []
    for i in range(HYPERCUBE_DIMENSIONS):
        neighbor_id = list(peer_id)  # Convert peer_id to a list for mutability
        neighbor_id[i] = '1' if neighbor_id[i] == '0' else '0'  # Flip the ith bit
        neighbors.append(''.join(neighbor_id))  # Join back into a string
    return neighbors

# Function to forward requests to the target node
async def forward_request(node_address, path, payload):
    """Forward a request to another node."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{node_address}{path}", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to forward request to {node_address}: {e}")
        return {"status": "Error", "message": "Failed to forward request."}
