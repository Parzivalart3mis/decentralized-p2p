# DHT P2P System

This is a Distributed Hash Table (DHT) Peer-to-Peer (P2P) system implemented using a hypercube topology.

## Prerequisites

- Python 3.7 or higher
- Make

## Setup

1. Create a virtual environment and install dependencies:

```
make venv
make install
```

## Running the System

### 1. Deploy Peer Nodes

To start all peer nodes: \
`make deploy` \
This command runs the `deploy_nodes.sh` script, which starts 8 peer nodes on ports 5000-5007.

### 2. Run Tests 

To run all tests: \
`make run_tests`\
This will run both the benchmark test and the peer test.

To run tests individually:
- Benchmark test: `make run_benchmark`
- Peer test: `make run_peer_test`

### 3. Clean Up

To stop all peer nodes and clean up the environment: \
`make clean`

## System Overview

This DHT P2P system consists of 8 nodes arranged in a 3-dimensional hypercube topology. Each node is identified by a 3-bit binary ID (000 to 111) and runs on a separate port (5000 to 5007).

### Key Components

1. **Peer Nodes**: Implemented in `main.py`, each node can create topics, publish messages, subscribe to topics, and query the DHT.

2. **DHT Implementation**: The `dht.py` file contains the core DHT functionality, including topic storage and message routing.

3. **API**: The system provides RESTful APIs for creating topics, publishing messages, subscribing to topics, and querying the DHT.

4. **Benchmarking**: The `test_script_benchmark.py` file measures system performance in terms of latency and throughput for varying numbers of topics.

5. **Peer Testing**: The `test_script_peer.py` file tests the functionality of peer interactions, including topic creation, message publishing, and subscription.

## Running Experiments

The benchmark script (`test_script_benchmark.py`) runs experiments with varying numbers of topics (from 1 to 1000, in steps of 100) and measures.
- Average latency
- Throughput (operations per second)

Results are plotted and saved in the `../Out/Images` directory.

## Make Commands

- `make all`: Set up the environment, install dependencies, and run all tests
- `make venv`: Create a virtual environment
- `make install`: Install dependencies
- `make run_benchmark`: Run the benchmark test
- `make run_peer_test`: Run the peer test
- `make run_tests`: Run both benchmark and peer tests
- `make deploy`: Deploy all peer nodes
- `make clean`: Clean up the environment and stop all peer nodes

## Troubleshooting

If you encounter issues with peer nodes not stopping properly:

1. Check running processes: `ps aux | grep python`
2. Manually kill processes if needed: `kill -9 <PID>`

For Windows users, use the Task Manager to end Python processes if they don't stop automatically.



This README provides a comprehensive guide for users to set up, run, and understand the DHT P2P system. It includes all the make commands and gives a high-level overview of the system components and functionality. Users can follow these steps to deploy the nodes, run tests, and clean up the environment.
