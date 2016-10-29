#!/bin/bash
if [[ ! -d 'prompt' ]]; then
  echo 'A "prompt" directory is missing.' >&2
  exit 1
fi
pip install -qr requirements-test.txt
pytest
mypy --silent-imports .
