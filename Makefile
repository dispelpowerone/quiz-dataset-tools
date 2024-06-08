all: mypy fmt install test

mypy:
	python3 -m mypy quiz_dataset_tools

fmt:
	python3 -m black quiz_dataset_tools tests

install:
	python3 -m pip install .

test:
	python3 -m unittest discover tests/

doctor:
	python3 -m pip check
	python3 -m pip list --outdated

server:
	uvicorn quiz_dataset_tools.server.main:app --host 0.0.0.0
