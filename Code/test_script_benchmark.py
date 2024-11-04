import asyncio
import httpx
import time
import subprocess
import os
import platform
import random
import string
import matplotlib.pyplot as plt
import signal
import sys

# Define the plotting directory
PLOTTING_DIR = "../Out/Images"
if not os.path.exists(PLOTTING_DIR):
    os.makedirs(PLOTTING_DIR)

# Assuming NODE_ADDRESSES matches the port each peer is running on
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

# Benchmarking settings
MAX_TOPICS = 10  # Run tests from 1 to MAX_TOPICS topics

# Generate a unique topic name
def generate_topic_name(peer_id):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"test_topic_{peer_id}_{random_string}"

async def perform_operations(peer_id, peer_url, topic_name):
    async with httpx.AsyncClient() as client:
        # Step 1: Create Topic
        await client.post(f"{peer_url}/create_topic", json={"topic": topic_name})

        # Step 2: Publish Message
        message = "Hello, Distributed World!"
        await client.post(f"{peer_url}/publish_message", json={"topic": topic_name, "message": message})

        # Step 3: Subscribe All Nodes
        for node_id, node_url in NODE_ADDRESSES.items():
            await client.post(f"{node_url}/subscribe", json={"topic": topic_name})

        # Step 4: Pull Messages
        for node_id, node_url in NODE_ADDRESSES.items():
            await client.post(f"{node_url}/pull_messages", json={"topic": topic_name})

        # Step 5: Query Topic
        await client.post(f"{peer_url}/query_topic", json={"topic": topic_name})

        # Step 6: Delete Topic
        await client.post(f"{peer_url}/delete_topic", json={"topic": topic_name})

async def main():
    results_latency = []
    results_throughput = []

    for num_topics in range(1, MAX_TOPICS + 1):
        total_time = 0
        successful_requests = 0

        # Run all operations for `num_topics` unique topics
        for _ in range(num_topics):
            for peer_id, peer_url in NODE_ADDRESSES.items():
                topic_name = generate_topic_name(peer_id)

                # Perform the sequence of operations
                start_time = time.time()
                await perform_operations(peer_id, peer_url, topic_name)
                elapsed_time = time.time() - start_time

                total_time += elapsed_time
                successful_requests += 1

        # Calculate and record metrics for this run
        avg_latency = total_time / successful_requests if successful_requests else 0
        throughput = successful_requests / total_time if total_time > 0 else 0
        results_latency.append(avg_latency)
        results_throughput.append(throughput)

    # Plot results
    plot_results(results_latency, results_throughput)

def plot_results(results_latency, results_throughput):
    # Latency plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, MAX_TOPICS + 1), results_latency, label='Latency')
    plt.title('Average Latency vs Number of Topics')
    plt.xlabel('Number of Topics')
    plt.ylabel('Latency (seconds)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{PLOTTING_DIR}/latency_vs_num_topics.png")
    plt.close()

    # Throughput plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, MAX_TOPICS + 1), results_throughput, label='Throughput')
    plt.title('Throughput vs Number of Topics')
    plt.xlabel('Number of Topics')
    plt.ylabel('Throughput (requests/second)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{PLOTTING_DIR}/throughput_vs_num_topics.png")
    plt.close()

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
