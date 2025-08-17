.PHONY: help install lint test run clean

# Use python3 by default, allow overriding
PYTHON ?= python3

help:
	@echo "Commands:"
	@echo "  install         : Install dependencies for development"
	@echo "  install-hooks   : Install pre-commit hooks"
	@echo "  lint            : Run static analysis and formatting checks"
	@echo "  test            : Run tests with pytest"
	@echo "  run             : Run the OSINT CLI tool (e.g., make run ARGS=\"domain --name example.com --all\")"
	@echo "  clean           : Remove temporary files"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .
	@echo "\nDependencies installed. You can now use the 'osint' command."

install-hooks:
	$(PYTHON) -m pip install pre-commit
	pre-commit install

lint:
	@echo "Running linters and type checkers..."
	pre-commit run --all-files

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest

run:
	@echo "Running OSINT Framework..."
	@$(PYTHON) -m osint.app $(ARGS)

clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f .coverage
	rm -rf .pytest_cache
	rm -f osint_cache.sqlite
