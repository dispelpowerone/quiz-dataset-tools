all: mypy fmt install

mypy:
	#python3 -m mypy driver_test_db

fmt:
	python3 -m black driver_test_db

install:
	python3 -m pip install .

doctor:
	python3 -m pip check
	python3 -m pip list --outdated
