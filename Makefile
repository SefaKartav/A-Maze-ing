PYTHON  := python3
CONFIG  := config.txt
MAIN    := a_maze_ing.py

MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

.PHONY: all install run debug lint lint-strict build clean

all: run

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

build:
	$(PYTHON) -m build

clean:
	rm -rf __pycache__ mazegen/__pycache__
	rm -rf .mypy_cache .pytest_cache
	rm -rf build dist *.egg-info
	find . -type f -name "*.pyc" -delete
