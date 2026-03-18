.PHONY: env help up down build logs clean

help:
	@echo "NWDAF Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make env       Generate .env from .env.vms (required before first run)"
	@echo "  make up        Start all services"
	@echo "  make down      Stop all services"
	@echo "  make build     Rebuild and start services"
	@echo "  make logs      Follow logs from all services"
	@echo "  make clean     Stop services and remove volumes"

env:
	@if [ ! -f .env ]; then \
		echo "Error: .env not found. Copy .env.example to .env and configure HOSTS."; \
		exit 1; \
	fi
	@set -a; . ./.env; set +a; envsubst < .env > .env
	@echo ".env generated"

up: env network
	docker compose up -d

down:
	docker compose down

build: env network
	docker compose up -d --build

logs:
	docker compose logs -f

clean:
	docker compose down -v
	@echo "All services stopped and volumes removed"
