.PHONY: install install-frontend install-backend dev-frontend dev-backend embeddings pull-projects test test-frontend test-backend

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

# After editing backend/content/afdal.*.md or the project catalog: recompute
# the passages' embeddings, then commit backend/content/embeddings.json.
embeddings:
	cd backend && poetry run python scripts/build_embeddings.py

# Before editing projects locally: copy the online catalog (including admin
# edits) and its images into the repository, so a push starts from it.
pull-projects:
	cd backend && poetry run python scripts/pull_projects.py

test: test-backend test-frontend

test-backend:
	cd backend && poetry run pytest

test-frontend:
	cd frontend && npm run build
