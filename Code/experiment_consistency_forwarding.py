import asyncio
import time
import subprocess
import platform
import random
import signal
import logging
import sys
from config import NODE_ADDRESSES
from dht import create_topic, forward_request, query_topic

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_forwarding_consistency():
    """
    Test the consistency of the request forwarding mechanism by creating topics on random nodes
    and verifying accessibility from other nodes.
    """
    results = {"successful_forwards": 0, "failed_forwards": 0}
    topic_name = "forwarding_test_topic"

    # Step 1: Select a random node to create the topic
    creator_node_id = random.choice(list(NODE_ADDRESSES.keys()))
    logging.info(f"Creating topic '{topic_name}' at node {creator_node_id}")

    # Forward a create_topic request to the chosen node
    create_response = await forward_request(creator_node_id, "create_topic", {"topic": topic_name})

    if create_response["status"] != "Success":
        logging.error("Failed to create topic on the selected node.")
        return results

    # Step 2: Test topic accessibility from other nodes
    for node_id in NODE_ADDRESSES.keys():
        if node_id == creator_node_id:
            continue  # Skip the node that created the topic

        logging.info(f"Node {node_id} querying for topic '{topic_name}' to test forwarding.")
        query_response = await forward_request(node_id, "query_topic", {"topic": topic_name})

        # Check if the topic was found
        if query_response["status"] == "Success":
            results["successful_forwards"] += 1
            logging.info(f"Node {node_id} successfully accessed topic '{topic_name}' through forwarding.")
        else:
            results["failed_forwards"] += 1
            logging.warning(f"Node {node_id} failed to access topic '{topic_name}' through forwarding.")

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
    # Run the consistency forwarding test
    results = await test_forwarding_consistency()
    print(f"Forwarding Consistency Test Results: {results}")


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
