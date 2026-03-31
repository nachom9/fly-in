VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

MAIN_FILE = main.py
REQUIREMENTS = requirements.txt

all: banner run

banner:
	@echo "======================================"
	@echo "         Fly-In Drones Simulator      "
	@echo "======================================"

install: $(VENV)/bin/activate

$(VENV)/bin/activate: $(REQUIREMENTS)
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Upgrading pip..."
	@$(PIP) install --upgrade pip
	@echo "Installing requirements..."
	@$(PIP) install -r $(REQUIREMENTS)
	@touch $(VENV)/bin/activate

run: install
	@echo "Running Fly-In Simulator..."
	$(PYTHON) $(MAIN_FILE)

debug: install
	@echo "Running Fly-In Simulator in debug mode..."
	$(PYTHON) -m pdb $(MAIN_FILE)

lint:
	@echo "Running flake8 and mypy..."
	@$(VENV)/bin/flake8 . --exclude venv
	@$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict lint..."
	@$(VENV)/bin/flake8 .
	@$(VENV)/bin/mypy . --strict

clean:
	@echo "Cleaning temporary files and virtual environment..."
	@rm -rf __pycache__ .mypy_cache
	@rm -rf $(VENV)

.PHONY: all banner install run debug clean lint lint-strict