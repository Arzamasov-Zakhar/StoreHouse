format:
	poetry run isort .
	poetry run black .

tests: tests_python

check:
	poetry run isort . --check
	poetry run flake8 src/
	poetry run black . --check
	poetry run mypy src/
	poetry run mypy tests/

tests_python:
	poetry run pytest -vv --cov-report xml --cov src tests
