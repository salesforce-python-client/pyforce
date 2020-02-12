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

.PHONY: clean
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
