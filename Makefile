.PHONY: run test cover lint format docker

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

test:
	pytest -q

cover:
	pytest --cov=app --cov-report term-missing

lint:
	ruff check .
	black --check .

format:
	black .

docker:
	docker build -t jwks-server-py:local .
