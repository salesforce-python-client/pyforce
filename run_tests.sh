#!/bin/bash
PYTHON=python
export PYTHONPATH=.:./src

$PYTHON pyforce/tests/test_xmlclient.py
$PYTHON pyforce/tests/test_python_client.py
