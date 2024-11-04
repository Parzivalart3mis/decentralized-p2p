import time
import hashlib
import random
import string

def hash_topic(topic, num_nodes):
    return int(hashlib.sha256(topic.encode()).hexdigest(), 16) % num_nodes

def experiment_hash_time_cost(num_topics=10000, num_nodes=8):
    topics = [''.join(random.choices(string.ascii_letters + string.digits, k=10)) for _ in range(num_topics)]
    total_time = 0

    for topic in topics:
        start_time = time.perf_counter()
        target_node = hash_topic(topic, num_nodes)
        end_time = time.perf_counter()
        total_time += (end_time - start_time)

    average_time = total_time / num_topics
    print(f"Average time per hash computation: {average_time:.10f} seconds")

experiment_hash_time_cost()
