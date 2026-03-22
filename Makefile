.PHONY: install run dev test lint clean docker-build docker-run help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and download spaCy model
	uv sync
	uv run python -m spacy download en_core_web_sm

run: ## Run the Streamlit web app
	uv run streamlit run src/app.py --server.port 8501

dev: ## Run Streamlit in dev mode with auto-reload
	uv run streamlit run src/app.py --server.port 8501 --server.runOnSave true

test: ## Run tests
	uv run pytest tests/ -v

lint: ## Run ruff linter and formatter check
	uv run ruff check src/
	uv run ruff format --check src/

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

docker-build: ## Build Docker image
	docker build -t sciextract:latest .

docker-run: ## Run Docker container
	docker run --rm -p 8501:8501 --env-file .env sciextract:latest
