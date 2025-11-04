.PHONY: help install setup test run docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make setup      - Set up development environment"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run development server"
	@echo "  make docker-up  - Start Docker containers"
	@echo "  make docker-down- Stop Docker containers"
	@echo "  make clean      - Clean temporary files"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && python -m spacy download en_core_web_sm

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

test:
	pytest tests/ -v

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

