PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PY := PYTHONPATH=src $(VENV)/bin/python
IMAGE := gasp
ARGS ?=

.PHONY: all build install run test lint clean docker-clean build docker-run help

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(PIP) install -r requirements.txt -r requirements-dev.txt

lint:
	$(PY) -m ruff check src/

test:
	$(PY) -m pytest tests/ -v

run:
	$(PY) -m gasp $(ARGS)

# FOR DOCKER
build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -v $(PWD)/data:/app/data $(IMAGE) $(ARGS)

clean:
	rm -rf $(VENV) __pycache__ src/gasp/__pycache__


docker-clean:
	docker rmi $(IMAGE)


help:
	@echo "make setup                       - create venv and install deps"
	@echo "make run ARGS='...'              - run locally"
	@echo "make test                        - run tests"
	@echo "make lint                        - lint Python code"
	@echo "make build                       - build Docker image"
	@echo "make docker-run ARGS='...'       - run in Docker"
	@echo "make clean                       - remove build artifacts"
	@echo "make docker-clean                - remove Docker image"
	@echo ""
	@echo "Example:"
	@echo "  make run ARGS='kernel.cu --gpu b200 --verbose'"
	@echo "  make docker-run ARGS='data/kernel.cu --gpu b200'"