#!/bin/sh
set -e
cd $(dirname $(cd $(dirname $0); pwd))
pwd

if [ -d "prompt" ]; then
  rm -rf prompt
fi

ROOT=$(dirname $(pwd))

if [ -e "$ROOT/prompt.py" ]; then
  mkdir prompt
  for file in $(ls -1v $ROOT/*.py); do
    cp $file prompt/
  done
  for file in $(ls -1v $ROOT/*.pyi); do
    cp $file prompt/
  done
else
  git clone --single-branch --depth 1 \
    https://github.com/lambdalisue/neovim-prompt prompt
fi
pip install -qr requirements-test.txt
pytest
mypy --silent-imports .
