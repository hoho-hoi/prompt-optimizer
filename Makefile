.PHONY: test lint format clean help setup

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy src tests

format:
	uv run ruff format .

setup:
	uv sync --dev

clean:
	rm -rf scratch/*
	@echo "Cleaned scratch directory."

help:
	@echo "Available commands:"
	@echo "  make test    - Run tests"
	@echo "  make lint    - Run linters"
	@echo "  make format  - Format code"
	@echo "  make setup   - Install dependencies"
	@echo "  make clean   - Clean artifacts"