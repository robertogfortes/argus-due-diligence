.PHONY: install run test lint clean setup

setup: install
	cp -n .env.example .env || true
	@echo "\n[ARGUS] Done. Edit .env with your API keys, then run: make run\n"

install:
	pip install -e ".[dev]"

run:
	python -m argus.main

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist/ build/ src/*.egg-info/
	rm -f outputs/*.md outputs/*.json

.DEFAULT_GOAL := help
help:
	@echo "Available targets:"
	@echo "  make setup    — first-time setup (install deps + create .env)"
	@echo "  make install  — install Python dependencies"
	@echo "  make run      — run ARGUS investigation (edit main.py inputs first)"
	@echo "  make test     — run test suite"
	@echo "  make lint     — lint with ruff"
	@echo "  make format   — auto-format with ruff"
	@echo "  make clean    — remove build artifacts and generated outputs"
