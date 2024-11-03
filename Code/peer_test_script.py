import asyncio
import httpx
import time
import subprocess
import os
import platform
import signal

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

# Base topic name
BASE_TOPIC_NAME = "test_topic"
MESSAGE = "Hello, Distributed World!"

def generate_unique_topic_name(peer_id):
    return f"{BASE_TOPIC_NAME}_{peer_id}"


async def create_topic(peer_url, topic):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{peer_url}/create_topic", json={"topic": topic})
        print(f"Create Topic: {response.json()}")


async def delete_topic(peer_url, topic):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{peer_url}/delete_topic", json={"topic": topic})
        print(f"Delete Topic: {response.json()}")


async def publish_message(peer_url, topic, message):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{peer_url}/publish_message", json={"topic": topic, "message": message})
        print(f"Publish Message: {response.json()}")


async def subscribe(peer_url, topic):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{peer_url}/subscribe", json={"topic": topic})
        print(f"Subscribe: {response.json()}")


async def pull_messages(peer_url, topic):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{peer_url}/pull_messages", json={"topic": topic})
        print(f"Pull Messages: {response.json()}")


async def main():
    # Set up concurrent tasks
    tasks = []
    for peer_id, peer_url in NODE_ADDRESSES.items():
        unique_topic_name = generate_unique_topic_name(peer_id)

        # Create topics concurrently
        tasks.append(create_topic(peer_url, unique_topic_name))

        # Simultaneously subscribe to the unique topic
        tasks.append(subscribe(peer_url, unique_topic_name))

        # Simultaneously publish messages to the unique topic
        tasks.append(publish_message(peer_url, unique_topic_name, MESSAGE))

    # Run all create, subscribe, and publish tasks concurrently
    await asyncio.gather(*tasks)

    # Pull messages after some time to ensure messages are available
    pull_tasks = [pull_messages(peer_url, generate_unique_topic_name(peer_id)) for peer_id, peer_url in NODE_ADDRESSES.items()]
    await asyncio.gather(*pull_tasks)

    # Clean up by deleting the topic concurrently
    delete_tasks = [delete_topic(peer_url, generate_unique_topic_name(peer_id)) for peer_id, peer_url in NODE_ADDRESSES.items()]
    await asyncio.gather(*delete_tasks)


# Function to kill peer processes based on OS
def kill_peer_processes():
    current_os = platform.system()
    if current_os == "Linux":
        # Use lsof to find and kill the peer processes
        subprocess.run("lsof -t -i :5000-5007 | xargs kill", shell=True)
    elif current_os == "Windows":
        # For Windows, we will use taskkill; here we find process IDs
        for port in range(5000, 5008):
            subprocess.run(f"for /f \"tokens=5\" %i in ('netstat -ano ^| findstr :{port}') do taskkill /PID %i /F", shell=True)
    else:
        print("Unsupported OS for killing processes.")


# Run the test script
if __name__ == "__main__":
    # Run the run.sh script to start peer nodes
    print("Starting peer nodes...")
    subprocess.Popen(["bash", "run.sh"])  # Start the peer nodes in the background

    # Give some time for the peer nodes to initialize
    time.sleep(5)  # Wait for the nodes to be ready; adjust if needed

    print("Starting test script...")
    asyncio.run(main())

    # Kill the peer nodes processes after testing
    print("Stopping peer nodes...")
    kill_peer_processes()
    print("Peer nodes stopped.")
