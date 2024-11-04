# Name of the virtual environment folder
VENV := venv

# Detect the operating system
OS := $(shell uname -s)

# Define activation command based on the OS
ifeq ($(OS),Linux)
    ACTIVATE := source $(VENV)/bin/activate
else ifeq ($(OS),Darwin) # macOS
    ACTIVATE := source $(VENV)/bin/activate
else ifeq ($(OS),Windows_NT) # Windows
    ACTIVATE := $(VENV)\Scripts\activate
endif

# Create virtual environment
$(VENV)/bin/activate:
	python3 -m venv $(VENV)

# Install all dependencies from requirements.txt
install: $(VENV)/bin/activate
	$(ACTIVATE) && pip install -r requirements.txt

# Freeze dependencies to requirements.txt
freeze:
	$(ACTIVATE) && pip freeze > requirements.txt

# Clean the environment
clean:
	rm -rf $(VENV)

# Help message
help:
	@echo "Available commands:"
	@echo "  install: Install dependencies from requirements.txt"
	@echo "  freeze: Freeze the installed packages to requirements.txt"
	@echo "  clean: Remove the virtual environment"
	@echo "  help: Show this help message"
