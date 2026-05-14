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
		CLUSTER_ID=$$(python3 -c "import uuid,base64;print(base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('='))"); \
		sed -i "s|^KAFKA_CLUSTER_ID=$$|KAFKA_CLUSTER_ID=$$CLUSTER_ID|" .env; \
		echo "  Generated KAFKA_CLUSTER_ID=$$CLUSTER_ID"; \
	fi

producers: env
	docker compose -f docker-compose.producers.yml up -d

dev: env
	DEV_MODE=true docker compose up -d

prod: env
	DEV_MODE=false docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

down:
	docker compose down

dev-build: env
	DEV_MODE=true docker compose up -d --build

prod-build: env
	DEV_MODE=false docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

logs:
	docker compose logs -f


clean:
	@echo "WARNING: This removes ALL Docker volumes and persisted data."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	@echo "All services stopped and volumes removed"
