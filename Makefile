all: fmt

fmt:
	python -m black .

doctor:
	python -m pip check
	pip list --outdated
