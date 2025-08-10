.PHONY: help install-dev format lint

help: ## 📋 Show available targets and current settings
	@echo "✨ PlomTTS Home Assistant Integration 🗣️"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install-dev: ## 🔧 Install dev tools (linter, testing, type stubs)
	pip install -r requirements-dev.txt

format: ## ✨ Format code with black and isort
	@echo "✨ Formatting code..."
	black .
	isort .
	@echo "✅ Code formatted"

lint: ## 🎨 Run comprehensive linting checks
	@echo "🎨 Running linting checks..."
	black --check .
	isort --check-only .
	mypy .
	@echo "✅ All linting checks complete"
