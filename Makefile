.PHONY: test lint format clean help setup

# NOTE:
# These targets are safe defaults to prevent CI from failing on a fresh clone.
# Replace the placeholders with stack-specific commands once the toolchain is decided.
# Keep the informational messages so callers know the real work is pending.

test:
	@echo "[INFO] No tests are defined yet. Add your test runner command here."
	@echo "[INFO] Example: pytest tests/ or npm test"

lint:
	@echo "[INFO] No linters are configured yet. Add your lint command here."
	@echo "[INFO] Example: ruff check . or eslint ."

format:
	@echo "[INFO] No formatter is configured yet. Add your format command here."
	@echo "[INFO] Example: ruff format . or prettier --write ."

setup:
	@echo "No setup required or not implemented."

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