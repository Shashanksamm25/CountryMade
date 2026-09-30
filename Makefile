.PHONY: build up down logs seed lint fmt clean

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

seed:
	docker compose exec app python seed_admin.py

lint:
	ruff check .

fmt:
	ruff format .

clean:
	docker compose down -v --remove-orphans
