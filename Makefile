.PHONY: build up down logs migrate makemigrations superuser shell devUp

devUp:
	docker compose down
	docker compose up -d --build
	docker compose ps

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

superuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose exec backend python manage.py shell