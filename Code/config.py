import sys

# Constants for hypercube configuration
NUM_NODES = 8  # Assume 3D hypercube with 8 nodes
HYPERCUBE_DIMENSIONS = 3  # Dimensions of hypercube
import sys

# Constants for hypercube configuration
NUM_NODES = 8  # Assume 3D hypercube with 8 nodes
HYPERCUBE_DIMENSIONS = 3  # Dimensions of hypercube

# Initialize peer settings
peer_id = sys.argv[2]  # Binary string ID of the peer node
port = int(sys.argv[1])  # Port number for this peer node

# Node addresses configuration for redirection
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

# Note: Adjust these URLs and ports if nodes are distributed across different servers or IPs.

# Initialize peer settings
peer_id = sys.argv[2]  # Binary string ID of the peer node
port = int(sys.argv[1])  # Port number for this peer node

# Node addresses configuration for redirection
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

# Note: Adjust these URLs and ports if nodes are distributed across different servers or IPs.
