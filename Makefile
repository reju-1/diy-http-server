# Define virtual environment paths
ENTRY_POINT := src/server.py

# Default target
.DEFAULT_GOAL := help


run:  ## Run server
	python $(ENTRY_POINT)


clean:  ## Clean Python cache and temporary files
	find src/ -type d -name '__pycache__' -exec rm -r {} + -o -name '*.pyc' -delete -o -name '*.pyo' -delete


help:  ## Show all available targets
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
