#!/bin/bash
if [[ -d 'prompt' ]]; then
  rm -rf prompt
fi

if [[ -f '../prompt.py' ]]; then
  mkdir prompt
  for file in $(ls -1v ../*.py*); do
    cp $file prompt/
  done
else
  git clone --single-branch --depth 1 \
    https://github.com/lambdalisue/neovim-prompt prompt
fi

. scripts/test.sh
. scripts/docs.sh
