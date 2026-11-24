.PHONY: help install dev dev-backend dev-frontend lint typecheck test build verify clean

help:
	@echo "ReturnZero AI - Development Commands"
	@echo "====================================="
	@echo "make install       - Install backend and frontend dependencies"
	@echo "make dev           - Run backend and frontend concurrently"
	@echo "make dev-backend   - Run FastAPI backend with uvicorn reload"
	@echo "make dev-frontend  - Run Next.js frontend dev server"
	@echo "make lint          - Run ruff on backend and eslint on frontend"
	@echo "make typecheck     - Run mypy --strict on backend and tsc on frontend"
	@echo "make test          - Run pytest with coverage and vitest"
	@echo "make build         - Run next build on frontend"
	@echo "make verify        - Run full verification suite (lint, typecheck, test, build, guards)"
	@echo "make clean         - Remove cache files, build artifacts, and databases"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend on :8000 and frontend on :3000..."
	make -j 2 dev-backend dev-frontend

lint:
	cd backend && python -m ruff check . && python -m ruff format --check .
	cd frontend && npm run lint

typecheck:
	cd backend && python -m mypy --strict app && python -m mypy tests
	cd frontend && npx tsc --noEmit

test:
	cd backend && python -m pytest tests/ --cov=app --cov-report=term-missing
	cd frontend && npm run test

build:
	cd frontend && npm run build

verify: lint typecheck test build
	python scripts/check_claims.py
	python scripts/smoke_test.py
	@echo "All verification gates PASSED!"

clean:
	rm -rf frontend/.next frontend/dist backend/__pycache__ backend/*/__pycache__ backend/*/*/__pycache__ backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/coverage.xml returnzero.db
