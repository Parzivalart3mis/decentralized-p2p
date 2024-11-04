import subprocess
import time
import requests


def start_flask_app(script, port, peer_id=None):
    if peer_id:
        return subprocess.Popen(['python', script, str(port), peer_id])
    else:
        return subprocess.Popen(['python', script, str(port)])


def test_api(url, method='GET', data=None):
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, json=data)
        return response.status_code == 200, response.json()
    except requests.RequestException:
        return False, None


def pull_messages_with_retry(url, topic, max_retries=3):
    for _ in range(max_retries):
        success, response = test_api(f'{url}/pull_messages', 'POST', {'topic': topic})
        if success and response.get('messages'):
            return True, response
        time.sleep(1)  # Wait for 1 second before retrying
    return False, None


def main():
    # Start the indexing server on port 5000
    indexing_server = start_flask_app('indexing_server.py', 5000)

    # Start a single peer node on port 5001
    peer_node = start_flask_app('peer_node.py', 5001, 'peer1')

    # Allow some time for the applications to start
    time.sleep(5)

    # Ensure the processes are running
    running = [indexing_server.pid, peer_node.pid]
    print('Running process IDs:', running)

    # Test APIs
    indexing_server_url = 'http://localhost:5000'
    peer_url = 'http://localhost:5001'

    # Test create_topic
    topic = 'test_topic'
    assert test_api(f'{peer_url}/create_topic', 'POST', {'topic': topic})[0], "Create topic failed"
    print("Create topic successful")

    # Test subscribe (before publishing)
    assert test_api(f'{peer_url}/subscribe', 'POST', {'topic': topic})[0], "Subscribe failed for peer1"
    print("Subscribe successful for peer1")

    # Test publish
    message = 'Message from peer1'
    assert test_api(f'{peer_url}/publish', 'POST', {'topic': topic, 'message': message})[0], "Publish failed for peer1"
    print("Publish successful for peer1")

    # Allow some time for message processing
    time.sleep(2)

    # Test pull_messages with retry
    success, response = pull_messages_with_retry(peer_url, topic)
    assert success, "Pull messages failed for peer1"
    print(f"Pull messages successful for peer1. Messages: {response['messages']}")

    # Test query_peers
    assert test_api(f'{indexing_server_url}/query_peers?topic={topic}')[0], "Query peers failed"
    print("Query peers successful")

    # Test delete_topic
    assert test_api(f'{peer_url}/delete_topic', 'DELETE', {'topic': topic})[0], "Delete topic failed"
    print("Delete topic successful")

    # Test exit_peer
    assert test_api(f'{peer_url}/exit_peer', 'POST')[0], "Exit peer failed"
    print(f"Exit peer successful for {peer_url}")

    # Clean up processes
    indexing_server.terminate()
    peer_node.terminate()

    print("All tests completed successfully!")


if __name__ == "__main__":
    main()
