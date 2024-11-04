import subprocess
import time
import requests
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os

INDEXING_SERVER_URL = 'http://localhost:5000'
REQUESTS_PER_API = 1000
TOPIC_COUNT = 1000  # Adjust as needed


def start_indexing_server():
    return subprocess.Popen(['python', 'indexing_server.py'])


def create_topics():
    for i in range(TOPIC_COUNT):
        requests.post(f'{INDEXING_SERVER_URL}/create_topic', json={'topic': f'topic_{i}'})


def benchmark_api(api_name, method, url, data=None):
    start_time = time.time()
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, json=data)
    end_time = time.time()
    return end_time - start_time, response.status_code == 200


def run_benchmark(num_peers):
    apis = [
        ('create_topic', 'POST', f'{INDEXING_SERVER_URL}/create_topic', {'topic': 'new_topic'}),
        ('publish', 'POST', f'{INDEXING_SERVER_URL}/publish', {'topic': 'topic_0', 'message': 'test_message'}),
        ('subscribe', 'POST', f'{INDEXING_SERVER_URL}/subscribe', {'peer_id': 'peer_0', 'topic': 'topic_0'}),
        ('pull_messages', 'POST', f'{INDEXING_SERVER_URL}/pull_messages', {'peer_id': 'peer_0', 'topic': 'topic_0'}),
        ('query_peers', 'GET', f'{INDEXING_SERVER_URL}/query_peers?topic=topic_0', None),
        ('delete_topic', 'DELETE', f'{INDEXING_SERVER_URL}/delete_topic', {'topic': 'topic_to_delete'})
    ]

    results = {api[0]: {'latency': [], 'throughput': []} for api in apis}

    for api_name, method, url, data in apis:
        latencies = []
        successes = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_peers) as executor:
            futures = [executor.submit(benchmark_api, api_name, method, url, data) for _ in range(REQUESTS_PER_API)]

            for future in tqdm(concurrent.futures.as_completed(futures), total=REQUESTS_PER_API,
                               desc=f"Benchmarking {api_name}"):
                latency, success = future.result()
                latencies.append(latency)
                if success:
                    successes += 1

        avg_latency = np.mean(latencies)
        throughput = successes / sum(latencies) if sum(latencies) > 0 else 0
        results[api_name]['latency'].append(avg_latency)
        results[api_name]['throughput'].append(throughput)

    return results


def plot_results(results):
    peer_counts = list(range(1, 101))

    # Create the Images directory if it doesn't exist
    output_dir = '../Out/Images'
    os.makedirs(output_dir, exist_ok=True)

    for api in results.keys():
        plt.figure(figsize=(10, 5))

        plt.plot(peer_counts, results[api]['latency'], label='Latency (s)', color='blue')
        plt.plot(peer_counts, results[api]['throughput'], label='Throughput (req/s)', color='orange')

        plt.title(f'API Performance: {api}')
        plt.xlabel('Number of Peers')
        plt.ylabel('Performance')
        plt.legend()

        plt.tight_layout()

        # Save the figure in the specified directory
        plt.savefig(os.path.join(output_dir, f'{api}_performance.png'))
        plt.show()

def main():
    server_process = start_indexing_server()
    time.sleep(5)  # Allow time for the server to start

    print("Creating topics...")
    create_topics()

    all_results = {api: {'latency': [], 'throughput': []} for api in
                   ['create_topic', 'publish', 'subscribe', 'pull_messages', 'query_peers', 'delete_topic']}

    for num_peers in range(1, 101):
        print(f"\nBenchmarking with {num_peers} peers...")
        results = run_benchmark(num_peers)

        for api in all_results.keys():
            all_results[api]['latency'].append(results[api]['latency'][0])
            all_results[api]['throughput'].append(results[api]['throughput'][0])

    server_process.terminate()

    plot_results(all_results)

    print("\nBenchmark completed. Graphs saved.")


if __name__ == "__main__":
    main()