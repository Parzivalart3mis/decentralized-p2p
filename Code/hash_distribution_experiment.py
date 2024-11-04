import hashlib
import random
import string
import numpy as np


def hash_topic(topic, num_nodes):
    return int(hashlib.sha256(topic.encode()).hexdigest(), 16) % num_nodes


def experiment_hash_distribution(num_topics=10000, num_nodes=8):
    topics = [''.join(random.choices(string.ascii_letters + string.digits, k=10)) for _ in range(num_topics)]
    node_distribution = {node_id: 0 for node_id in range(num_nodes)}

    # Hash each topic and assign it to a node
    for topic in topics:
        target_node = hash_topic(topic, num_nodes)
        node_distribution[target_node] += 1

    # Analyze the distribution
    counts = list(node_distribution.values())
    average_count = np.mean(counts)
    std_dev = np.std(counts)

    print(f"Distribution of topics across nodes: {node_distribution}")
    print(f"Average topics per node: {average_count}")
    print(f"Standard deviation in topic distribution: {std_dev:.2f}")


experiment_hash_distribution()
