.PHONY: install install-frontend install-backend dev-frontend dev-backend test test-frontend test-backend

install: install-frontend install-backend

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && poetry install

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && poetry run uvicorn app.main:app --reload --port 8000

# Run in two terminals: `make dev-backend` and `make dev-frontend`.

test: test-backend test-frontend

test-backend:
	cd backend && poetry run pytest

test-frontend:
	cd frontend && npm run build
