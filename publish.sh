#!/bin/bash

# See https://packaging.python.org/tutorials/packaging-projects/
source .env
python3 -m twine upload dist/*
