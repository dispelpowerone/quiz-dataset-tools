all: mypy fmt

mypy:
	python3 -m mypy driver_test_db

fmt:
	python3 -m black driver_test_db

doctor:
	python3 -m pip check
	python3 -m pip list --outdated
