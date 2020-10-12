.PHONY: help clean fmt install prep setup test

help:
	@echo "clean  : Remove auto-created files and directories."
	@echo "fmt    : Autoformat Python code in-place using various tools in sequence."
	@echo "install: Install required third-party Python packages."
	@echo "prep   : Autoformat and run tests."
	@echo "setup  : Install requirements and run tests."
	@echo "test   : Run tests."

clean:
	rm -rf ./.mypy_cache ./.pytest_cache

fmt:
	isort .
	black .
	autopep8 --in-place --aggressive --recursive .

install:
	pip install -U pip wheel
	pip install --use-feature=2020-resolver -U -r ./requirements/install.in -U -r ./requirements/dev.in

prep: fmt test

setup: install test

test:
	black --check .
	vulture --make-whitelist . ./vulture.txt
	pytest
