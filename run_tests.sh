#!/bin/bash
PYTHON=python
export PYTHONPATH=.:./src

$PYTHON src/beatbox/tests/test_beatbox.py
$PYTHON src/beatbox/tests/test_pythonClient.py
