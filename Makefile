.PHONY: build up down logs migrate makemigrations superuser shell devUp reset-db reset-db-force

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

reset-db:
	@printf "This will remove the Postgres Docker volume and recreate the DB. Continue? (y/N): " ; read ans ; \
	if [ "$$ans" != "y" ]; then echo "Aborting reset-db." ; exit 1 ; fi ; \
	docker compose down -v ; \
	docker compose up -d --build ; \
	docker compose ps

# Non-interactive forced reset (use with care)
reset-db-force:
	docker compose down -v
	docker compose up -d --build
	docker compose ps