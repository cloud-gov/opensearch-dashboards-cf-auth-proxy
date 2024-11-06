#!/usr/bin/env bash

export PYTHON_VERSION="3.12"

python3 -m pip download -r requirements.txt \
  --platform manylinux_2_17_x86_64 \
  --platform linux_x86_64 \
  --only-binary=:all: \
  --python-version "$PYTHON_VERSION"
