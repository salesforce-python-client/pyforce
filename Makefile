VENV ?= venv
PYTHON ?= python3

.PHONY: default
default: test

$(VENV):
	virtualenv -p $(PYTHON) $(VENV)
	$(VENV)/bin/pip install -r ./requirements-dev.txt

.PHONY: test
test:
	tox

.PHONY: test-py2
test-py2:
	tox -e py27

.PHONY: test-py3
test-py3:
	tox -e py3

.PHONY: install-hooks
install-hooks: $(VENV)
	$(VENV)/bin/pre-commit install --install-hooks

.PHONY: check
check: $(VENV)
	$(VENV)/bin/pre-commit run --all-files

.PHONY: clean
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
