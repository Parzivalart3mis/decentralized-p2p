import asyncio
import random
import logging
import time
import subprocess
import signal
import platform
import sys
from config import NODE_ADDRESSES
from dht import create_topic, delete_topic, query_topic, forward_request

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def simulate_churn(num_rounds=10):
    """
    Simulate node joins and leaves and check data availability.
    """
    results = {"data_available": 0, "data_unavailable": 0}
    topic_name = "churn_test_topic"

    # Step 1: Select a random node to create the topic
    creator_node_id = random.choice(list(NODE_ADDRESSES.keys()))
    logging.info(f"Creating topic '{topic_name}' at node {creator_node_id}")
    create_response = await forward_request(creator_node_id, "create_topic", {"topic": topic_name})

    if create_response["status"] != "Success":
        logging.error("Failed to create topic on the selected node.")
        return results

    # Step 2: Simulate churn
    for round_num in range(1, num_rounds + 1):
        # Randomly select a node to "join" or "leave" the network
        node_id = random.choice(list(NODE_ADDRESSES.keys()))
        operation = random.choice(["join", "leave"])

        if operation == "join":
            logging.info(f"Simulating node {node_id} joining the network (no-op for existing node).")
            # Normally, you'd add new nodes to the DHT, but we'll skip as this is a simulation
        else:
            logging.info(f"Simulating node {node_id} leaving the network (no-op for existing node).")
            # Normally, you'd remove nodes from the DHT, but we'll skip as this is a simulation

        # Query the topic after each join/leave to test availability
        query_response = await forward_request(node_id, "query_topic", {"topic": topic_name})

        # Check if data was available
        if query_response["status"] == "Success":
            results["data_available"] += 1
            logging.info(f"Data for topic '{topic_name}' found by node {node_id} after churn.")
        else:
            results["data_unavailable"] += 1
            logging.warning(f"Data for topic '{topic_name}' unavailable to node {node_id} after churn.")

    return results

# Signal handling for clean shutdown
def signal_handler(sig, frame):
    print("Interrupted! Saving results and exiting...")
    sys.exit(0)

# Kill peer processes
def kill_peer_processes():
    current_os = platform.system()
    if current_os == "Linux":
        subprocess.run("lsof -t -i :5000-5007 | xargs kill", shell=True)
    elif current_os == "Windows":
        for port in range(5000, 5008):
            subprocess.run(f"for /f \"tokens=5\" %i in ('netstat -ano ^| findstr :{port}') do taskkill /PID %i /F", shell=True)
    else:
        print("Unsupported OS for killing processes.")

async def main():
    # Run the network churn test
    results = await simulate_churn(num_rounds=10)
    print(f"Network Churn Test Results: {results}")

# Run the benchmark
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Starting peer nodes...")
    subprocess.Popen(["bash", "run.sh"])  # Start peer nodes in the background
    time.sleep(5)  # Wait for nodes to initialize

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Stopping peer nodes...")
    kill_peer_processes()
    print("Peer nodes stopped.")
