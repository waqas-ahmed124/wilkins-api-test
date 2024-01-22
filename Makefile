install-dev:
	pip install poetry
	poetry install

migrate: 
	docker compose run app poetry run alembic upgrade head

migration:
	docker compose run app poetry run alembic revision --autogenerate -m "$(message)"
	
format:
	black .

dev: install-dev
	docker compose up --build

clean:
	docker compose stop
	docker compose rm -f
	docker compose down --volumes --remove-orphans
