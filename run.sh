#!/bin/bash

# Define the number of nodes
NUM_NODES=8

# Base port number for nodes
BASE_PORT=5000

# Run each node in the background
for ((i=0; i<NUM_NODES; i++)); do
    # Convert the index to binary format (3 bits for 8 nodes)
    BINARY_ID=$(printf "%03d" $(bc <<< "obase=2;$i"))
    PORT=$((BASE_PORT + i))

    # Start the FastAPI server for each node
    echo "Starting node $BINARY_ID on port $PORT..."
    python Code/peer_node.py $PORT $BINARY_ID &
done

# Wait for all background jobs to finish
wait

echo "All nodes have been started."
