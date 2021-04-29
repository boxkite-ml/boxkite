#!/bin/bash
set -xeuo pipefail
docker build -t quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:dev .
docker push quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:dev
SHA="$(git rev-parse --short HEAD)"
docker tag quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:dev quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:$SHA
docker push quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:$SHA
