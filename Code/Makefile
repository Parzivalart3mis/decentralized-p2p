# Makefile for DHT P2P System

# Python interpreter
PYTHON = python3

# Virtual environment
VENV = venv
VENV_BIN = $(VENV)/bin

# Requirements file
REQUIREMENTS = requirements.txt

# Test scripts
BENCHMARK_TEST = test_script_benchmark.py
PEER_TEST = test_script_peer.py

# Deployment script
DEPLOY_SCRIPT = run.sh

# Default target
all: venv install run_tests

# Create virtual environment
venv:
	$(PYTHON) -m venv $(VENV)

# Install dependencies
install: venv
	$(VENV_BIN)/pip install -r $(REQUIREMENTS)

# Run benchmark test
run_benchmark: venv
	$(VENV_BIN)/python $(BENCHMARK_TEST)

# Run peer test
run_peer_test: venv
	$(VENV_BIN)/python $(PEER_TEST)

# Run all tests
run_tests: run_benchmark run_peer_test

# Deploy nodes
deploy:
	./$(DEPLOY_SCRIPT)

# Clean up
clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

.PHONY: all venv install run_benchmark run_peer_test run_tests deploy clean