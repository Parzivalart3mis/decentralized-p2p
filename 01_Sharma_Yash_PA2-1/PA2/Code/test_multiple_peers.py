import subprocess
import time
import requests
import random


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

    # Start 3 peer nodes on different ports
    peer_nodes = []
    for i in range(3):
        peer_node = start_flask_app('peer_node.py', 5001 + i, f'peer{i + 1}')
        peer_nodes.append(peer_node)

    # Allow some time for the applications to start
    time.sleep(5)

    # Ensure the processes are running
    running = [indexing_server.pid] + [peer.pid for peer in peer_nodes]
    print('Running process IDs:', running)

    # Test APIs
    indexing_server_url = 'http://localhost:5000'
    peer_urls = [f'http://localhost:{5001 + i}' for i in range(3)]

    # Test create_topic
    topic = 'test_topic'
    assert test_api(f'{peer_urls[0]}/create_topic', 'POST', {'topic': topic})[0], "Create topic failed"
    print("Create topic successful")

    # Test subscribe (before publishing)
    for i, url in enumerate(peer_urls):
        assert test_api(f'{url}/subscribe', 'POST', {'topic': topic})[0], f"Subscribe failed for peer{i + 1}"
        print(f"Subscribe successful for peer{i + 1}")

    # Test publish
    for i, url in enumerate(peer_urls):
        message = f'Message from peer{i + 1}'
        assert test_api(f'{url}/publish', 'POST', {'topic': topic, 'message': message})[
            0], f"Publish failed for peer{i + 1}"
        print(f"Publish successful for peer{i + 1}")

    # Allow some time for message processing
    time.sleep(2)

    # Test pull_messages with retry
    for i, url in enumerate(peer_urls):
        success, response = pull_messages_with_retry(url, topic)
        assert success, f"Pull messages failed for peer{i + 1}"
        print(f"Pull messages successful for peer{i + 1}. Messages: {response['messages']}")

    # Test query_peers
    assert test_api(f'{indexing_server_url}/query_peers?topic={topic}')[0], "Query peers failed"
    print("Query peers successful")

    # Test delete_topic
    assert test_api(f'{peer_urls[0]}/delete_topic', 'DELETE', {'topic': topic})[0], "Delete topic failed"
    print("Delete topic successful")

    # Test exit_peer
    for url in peer_urls:
        assert test_api(f'{url}/exit_peer', 'POST')[0], f"Exit peer failed for {url}"
        print(f"Exit peer successful for {url}")

    # Clean up processes
    indexing_server.terminate()
    for peer in peer_nodes:
        peer.terminate()

    print("All tests completed successfully!")


if __name__ == "__main__":
    main()