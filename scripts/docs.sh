#!/bin/bash
if [[ ! -d 'prompt' ]]; then
  echo 'A "prompt" directory is missing.' >&2
  exit 1
fi
pip install -qr requirements-docs.txt
sphinx-apidoc -f . -o docs
(cd docs; make html)
