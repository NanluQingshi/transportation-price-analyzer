.PHONY: dev lint fmt typecheck test migrate

dev:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

lint:
	uv run ruff check src && uv run ruff format --check src

fmt:
	uv run ruff format src && uv run ruff check --fix src

typecheck:
	uv run mypy src

test:
	uv run pytest

migrate:
	uv run alembic upgrade head
