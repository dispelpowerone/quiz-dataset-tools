all: mypy fmt test

mypy:
	uv run mypy quiz_dataset_tools

fmt:
	uv run black quiz_dataset_tools tests

install:
	uv run pip install .

test:
	TQDM_DISABLE=1 uv run python -m unittest discover tests/

doctor:
	uv run pip check
	uv run pip list --outdated

server:
	uv run uvicorn quiz_dataset_tools.server.main:app --host 0.0.0.0
