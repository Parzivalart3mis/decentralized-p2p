import subprocess
import time
import requests
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os


INDEXING_SERVER_URL = 'http://localhost:5000'
REQUESTS_PER_NODE = 1000
TOPIC_COUNT = 1000000  # 1 million topics


def start_indexing_server():
    return subprocess.Popen(['python', 'indexing_server.py'])


def create_topics():
    for i in tqdm(range(TOPIC_COUNT), desc="Creating topics"):
        requests.post(f'{INDEXING_SERVER_URL}/create_topic', json={'topic': f'topic_{i}'})


def query_topic(node_id):
    start_time = time.time()
    topic = f'topic_{np.random.randint(0, TOPIC_COUNT)}'
    response = requests.get(f'{INDEXING_SERVER_URL}/query_peers?topic={topic}')
    end_time = time.time()
    return end_time - start_time


def run_concurrent_queries(num_nodes):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_nodes) as executor:
        futures = []
        for node in range(num_nodes):
            for _ in range(REQUESTS_PER_NODE):
                futures.append(executor.submit(query_topic, node))

        response_times = []
        for future in tqdm(concurrent.futures.as_completed(futures), total=num_nodes * REQUESTS_PER_NODE,
                           desc=f"Querying with {num_nodes} nodes"):
            response_times.append(future.result())

    return np.mean(response_times)


def main():
    server_process = start_indexing_server()
    time.sleep(5)  # Allow time for the server to start

    print("Creating topics...")
    create_topics()

    node_counts = [2, 4, 8]
    avg_response_times = []

    for num_nodes in node_counts:
        print(f"\nTesting with {num_nodes} concurrent nodes...")
        avg_response_time = run_concurrent_queries(num_nodes)
        avg_response_times.append(avg_response_time)
        print(f"Average response time: {avg_response_time:.6f} seconds")

    server_process.terminate()

    # Directory to save the image
    output_dir = '../Out/Images'
    os.makedirs(output_dir, exist_ok=True)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(node_counts, avg_response_times, marker='o')
    plt.title('Average Response Time vs Number of Concurrent Nodes')
    plt.xlabel('Number of Concurrent Nodes')
    plt.ylabel('Average Response Time (seconds)')
    plt.grid(True)

    # Save the figure in the specified directory
    plt.savefig(os.path.join(output_dir, 'response_time_graph.png'))
    plt.show()

    print("\nTest completed. Graph saved as 'response_time_graph.png'")


if __name__ == "__main__":
    main()