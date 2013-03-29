#!/bin/bash
PYTHON=python
export PYTHONPATH=.:./src

$PYTHON src/pyforce/tests/test_xmlclient.py
$PYTHON src/pyforce/tests/test_python_client.py
