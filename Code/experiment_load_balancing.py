import asyncio
import random
import logging
import numpy as np
import time
import subprocess
import signal
import platform
from config import NODE_ADDRESSES
from dht import create_topic, forward_request

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_load_balancing(num_topics=100):
    """
    Test the load balancing efficiency by adding multiple topics to the DHT and checking distribution.
    """
    load_distribution = {node_id: 0 for node_id in NODE_ADDRESSES.keys()}

    # Step 1: Create topics on random nodes and track load distribution
    for _ in range(num_topics):
        topic_name = f"load_balancing_test_{random.randint(1, 10000)}"
        selected_node_id = random.choice(list(NODE_ADDRESSES.keys()))

        # Forward a create_topic request to a randomly selected node
        create_response = await forward_request(selected_node_id, "create_topic", {"topic": topic_name})

        if create_response["status"] == "Success":
            load_distribution[selected_node_id] += 1
            logging.info(f"Topic '{topic_name}' created on node {selected_node_id}")
        else:
            logging.warning(f"Failed to create topic '{topic_name}' on node {selected_node_id}")

    # Step 2: Analyze load distribution across nodes
    topic_counts = list(load_distribution.values())
    mean_topics = np.mean(topic_counts)
    std_dev = np.std(topic_counts)

    print(f"Load Balancing Results:\n"
          f"Mean number of topics per node: {mean_topics}\n"
          f"Standard deviation of topics per node: {std_dev}\n"
          f"Topic distribution across nodes: {load_distribution}")

    return {"mean": mean_topics, "std_dev": std_dev, "distribution": load_distribution}

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
    # Run the load balancing test
    results = await test_load_balancing(num_topics=100)
    print(f"Load Balancing Test Results: {results}")

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
