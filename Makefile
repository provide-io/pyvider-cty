# pyvider-cty Makefile

.PHONY: help
help: ## Show this help message
	@echo "pyvider-cty Build System"
	@echo "========================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

.PHONY: test
test: ## Run tests
	uv run pytest tests/

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest --cov=pyvider.cty --cov-report=term-missing --cov-report=html tests/

.PHONY: lint
lint: ## Run linting
	uv run ruff check src/ tests/ scripts/

.PHONY: format
format: ## Format code
	uv run ruff format src/ tests/ scripts/

.PHONY: memray
memray: ## Run memray memory stress tests (all subsystems)
	@mkdir -p memray-output
	uv run python scripts/memray/run_memray_stress.py

.PHONY: memray-analyze
memray-analyze: ## Analyze memray results and generate report + flamegraphs
	uv run python scripts/memray/memray_analysis.py

.PHONY: memray-flamegraph
memray-flamegraph: ## Generate flamegraphs from memray binaries
	@for f in memray-output/memray_*.bin; do \
		[ -f "$$f" ] || continue; \
		echo "Processing $$(basename $$f)..."; \
		uv run memray flamegraph "$$f" -o "$${f%.bin}_flamegraph.html" 2>/dev/null || true; \
	done
