.PHONY: test

PYPY := $(shell which pypy 2>/dev/null)

default: test

test:
	@echo "testing with python"
	python ./src/pyforce/xmltramp.py
ifdef PYPY
	pypy ./src/pyforce/xmltramp.py
else
	@echo "pypy not installed... skipping test"
endif

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
