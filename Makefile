python = python3.12

all: mypy fmt install test

mypy:
	${python} -m mypy quiz_dataset_tools

fmt:
	${python} -m black quiz_dataset_tools tests

install:
	${python} -m pip install .

test:
	TQDM_DISABLE=1 ${python} -m unittest discover tests/

doctor:
	${python} -m pip check
	${python} -m pip list --outdated

server:
	uvicorn quiz_dataset_tools.server.main:app --host 0.0.0.0
