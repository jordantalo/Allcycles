# Variables
COMPOSE = docker compose

# Default target
help:
	@echo "Available commands:"
	@echo "  make build   - Build the Docker image"
	@echo "  make up      - Run the ETL pipeline inside the container"
	@echo "  make re      - Rebuild the image and rerun the pipeline"
	@echo "  make logs    - Tail the container logs"
	@echo "  make down    - Stop and remove containers"
	@echo "  make debug   - Run the local CSV debug export script"
	@echo "  make clean   - Remove cache files and raw/debug data"

all: up

# Run pipeline
up:
	$(COMPOSE) up --build

# View logs
logs:
	$(COMPOSE) logs -f

# Stop containers
down:
	$(COMPOSE) down

# Clean build caches and generated data
clean:
	$(COMPOSE) down -v

fclean: clean
		docker system prune -af

re: fclean all

console:
	$(COMPOSE) exec web_app bash

.PHONY: help build up down re logs clean debug
