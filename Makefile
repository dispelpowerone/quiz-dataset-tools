all: mypy fmt install test

mypy:
	python3 -m mypy driver_test_db

fmt:
	python3 -m black driver_test_db tests

install:
	python3 -m pip install .

test:
	python3 -m unittest discover tests/

doctor:
	python3 -m pip check
	python3 -m pip list --outdated
