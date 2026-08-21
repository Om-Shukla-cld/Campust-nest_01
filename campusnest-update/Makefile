# Convenience targets — see README.md for the full guide.
PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: setup run test seed reset-db docker-up docker-down

setup:            ## create venv + install backend deps
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -r backend/requirements.txt
	@test -f backend/.env || cp backend/.env.example backend/.env
	@echo "✔ backend ready — run: make run"

run:              ## start API on :8000 with auto-reload (SQLite by default)
	$(BIN)/uvicorn backend.main:app --reload --port 8000

test:             ## run smoke tests
	$(BIN)/pytest backend/tests -q

seed:             ## seed demo data if DB is empty
	$(BIN)/python -m backend.seed

reset-db:         ## drop & re-seed the database
	$(BIN)/python -m backend.seed --reset

docker-up:        ## API + PostgreSQL via docker compose
	docker compose up --build

docker-down:
	docker compose down -v
