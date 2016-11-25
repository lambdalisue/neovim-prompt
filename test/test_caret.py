import pytest
from unittest.mock import MagicMock

from prompt.caret import Caret


@pytest.fixture
def prompt():
    prompt = MagicMock()
    prompt.text = ''
    return prompt


def test_locus(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)

    # lower limit
    caret.locus = -1
    assert caret.locus == 0

    # upper limit
    caret.locus = 100
    assert caret.locus == len(prompt.text)


def test_head(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    assert caret.head == 0


def test_lead(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    # The number of leading spaces
    assert caret.lead == 2


def test_tail(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    assert caret.tail == len(prompt.text)


def test_get_backward_text(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    caret.locus = caret.tail
    assert caret.get_backward_text() == '  Hello world!'

    caret.locus = caret.lead
    assert caret.get_backward_text() == '  '

    caret.locus = caret.head
    assert caret.get_backward_text() == ''

    caret.locus = 7
    assert caret.get_backward_text() == '  Hello'


def test_get_selected_text(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    caret.locus = caret.tail
    assert caret.get_selected_text() == ''

    caret.locus = caret.lead
    assert caret.get_selected_text() == 'H'

    caret.locus = caret.head
    assert caret.get_selected_text() == ' '

    caret.locus = 8
    assert caret.get_selected_text() == 'w'


def test_get_forward_text(prompt):
    prompt.text = '  Hello world!'
    caret = Caret(prompt)
    caret.locus = caret.tail
    assert caret.get_forward_text() == ''

    caret.locus = caret.lead
    assert caret.get_forward_text() == 'ello world!'

    caret.locus = caret.head
    assert caret.get_forward_text() == ' Hello world!'

    caret.locus = 7
    assert caret.get_forward_text() == 'world!'
