import asyncio
import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI
import uvicorn
from api import topics, messages
from logger import setup_logger

# Initialize peer settings
if len(sys.argv) < 3:
    print("Usage: python main.py <port> <peer_id>")
    sys.exit(1)

port = int(sys.argv[1])  # Port number for this peer node
peer_id = sys.argv[2]  # Binary string ID of the peer node

# Setup logger with peer_id
log_path = setup_logger(peer_id)

# Define the FastAPI app
app = FastAPI()

# Set peer_id in the FastAPI app for later use
app.state.peer_id = peer_id

# Include routers
app.include_router(topics.router)
app.include_router(messages.router)

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
