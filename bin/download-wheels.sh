#!/usr/bin/env bash

export PYTHON_VERSION="3.12"

grep -v "eventlet\|flask" < pip-tools/requirements.in | xargs -I {} \
  python3 -m pip download {} \
  --platform linux_x86_64 \
  --only-binary=:all: \
  --python-version "$PYTHON_VERSION"

# download flask
python3 -m pip download flask \
  --platform manylinux_2_17_x86_64 \
  --platform linux_x86_64 --only-binary=:all: \
  --python-version "$PYTHON_VERSION"

# download eventlet
python3 -m pip download eventlet \
  --only-binary=:all: \
  --platform none \
  --platform manylinux_2_17_x86_64 \
  --python-version "$PYTHON_VERSION"
