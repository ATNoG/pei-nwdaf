.PHONY: env help dev prod down build logs clean producers

help:
	@echo "PEI-NWDAF Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make dev       Start in DEV mode (all ports exposed)"
	@echo "  make prod      Start in PROD mode (only Nginx exposed)"
	@echo "  make down      Stop all services"
	@echo "  make build     Rebuild and start (dev)"
	@echo "  make logs      Follow logs"
	@echo "  make clean     Stop and remove volumes"
	@echo "  make producers Start network producers"

env:
	@if [ ! -f .env ]; then \
		echo "Copying .env.example to .env..."; \
		cp .env.example .env; \
	fi

producers: env
	docker compose -f docker-compose.producers.yml up -d

dev: env
	docker compose up -d

prod: env
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

down:
	docker compose down

build: env
	docker compose up -d --build

logs:
	docker compose logs -f

clean:
	docker compose down -v
	@echo "All services stopped and volumes removed"
