import os
import sys
import pytest
from unittest.mock import MagicMock

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)


@pytest.fixture
def nvim():
    nvim = MagicMock(spec='neovim.Nvim')
    nvim.call = MagicMock(return_value=0)
    nvim.options = {
        'encoding': 'utf-8',
    }
    return nvim


@pytest.fixture
def prompt(nvim):
    from prompt.prompt import Prompt
    return Prompt(nvim)
