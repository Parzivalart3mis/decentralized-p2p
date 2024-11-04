#!/bin/bash

# Deployment script for running the Indexing Server and 1 Peer Nodes

# Configurations
INDEXING_SERVER_PORT=5000
PEER1_PORT=5001
VENV_DIR=venv

# Function to check if a port is already in use
check_port() {
  if lsof -i:$1 > /dev/null; then
    echo "Error: Port $1 is already in use."
    exit 1
  fi
}

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Creating one..."
  python3 -m venv $VENV_DIR
fi

echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies if not already installed
if [ ! -f requirements.txt ]; then
  echo "requirements.txt not found. Please ensure it is available."
  exit 1
fi

echo "Installing dependencies..."
pip install -r requirements.txt

# Check ports
check_port $INDEXING_SERVER_PORT
check_port $PEER1_PORT

# Start Indexing Server
echo "Starting Indexing Server on port $INDEXING_SERVER_PORT..."
python3 indexing_server.py &  # Runs in background
INDEXING_SERVER_PID=$!

sleep 2  # Allow the server to initialize

# Start Peer1
echo "Starting Peer1 on port $PEER1_PORT..."
python3 peer_node.py $PEER1_PORT peer1 &  # Runs in background
PEER1_PID=$!

# Wait for a second to ensure all processes are running
sleep 2

# Show running processes
echo "Deployment complete!"
echo "Indexing Server running with PID: $INDEXING_SERVER_PID"
echo "Peer1 running with PID: $PEER1_PID"

# Function to stop all processes
stop_all() {
  echo "Stopping all running processes..."
  kill $INDEXING_SERVER_PID
  kill $PEER1_PID
  echo "All processes stopped."
}

# Trap Ctrl+C (SIGINT) and stop all processes
trap stop_all INT

# Wait for any signal (this keeps the script running to track the processes)
wait
