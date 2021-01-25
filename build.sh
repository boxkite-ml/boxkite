#!/bin/bash

# https://packaging.python.org/tutorials/packaging-projects/

echo "Danger Will Robinson! Will delete your dist directory in 10 seconds"
echo "Press ^C to cancel."
sleep 10

rm -rf dist

python3 setup.py sdist bdist_wheel
