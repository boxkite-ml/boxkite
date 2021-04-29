#!/bin/bash
set -xeuo pipefail
docker build -t quay.io/boxkite/boxkite-app:dev .
docker push quay.io/boxkite/boxkite-app:dev
SHA="$(git rev-parse --short HEAD)"
docker tag quay.io/boxkite/boxkite-app:dev quay.io/boxkite/boxkite-app:$SHA
docker push quay.io/boxkite/boxkite-app:$SHA
