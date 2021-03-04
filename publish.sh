#!/bin/bash

# See https://packaging.python.org/tutorials/packaging-projects/
source .env
pip install twine==3.3.0
python3 -m twine upload dist/*
