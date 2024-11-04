import random
import string

NODE_ADDRESSES = {
    "000": "http://127.0.0.1:5000",
    "001": "http://127.0.0.1:5001",
    "010": "http://127.0.0.1:5002",
    "011": "http://127.0.0.1:5003",
    "100": "http://127.0.0.1:5004",
    "101": "http://127.0.0.1:5005",
    "110": "http://127.0.0.1:5006",
    "111": "http://127.0.0.1:5007",
}

NUM_TOPICS = 10000  # Total topics to generate
NODE_COUNT = len(NODE_ADDRESSES)


# Function to generate unique topic names
def generate_topic_name(peer_id):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"test_topic_{peer_id}_{random_string}"


# Function to hash topic names to node IDs
def hash_topic_to_node(topic_name):
    index = int(hash(topic_name)) % NODE_COUNT
    # Get the node ID based on the calculated index
    return list(NODE_ADDRESSES.keys())[index]


# Track topic distribution
topic_distribution = {node: 0 for node in NODE_ADDRESSES.keys()}

# Generate topics and assign them to nodes
for _ in range(NUM_TOPICS):
    peer_id = random.choice(list(NODE_ADDRESSES.keys()))  # Randomly select a peer_id
    topic_name = generate_topic_name(peer_id)
    assigned_node = hash_topic_to_node(topic_name)

    # Count the topic for the assigned node
    topic_distribution[assigned_node] += 1

# Print the results
print("Topic distribution across nodes:")
for node, count in topic_distribution.items():
    print(f"Node {node}: {count} topics")
