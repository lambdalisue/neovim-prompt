from curses import ascii
from collections import abc

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from prompt.keystroke import Keystroke
from prompt.keymap import Keymap, Definition


def test_Definition_parse(nvim):
    lhs = Keystroke.parse(nvim, '<C-H>')
    rhs = Keystroke.parse(nvim, '<BS>')

    d = Definition.parse(nvim, [lhs, rhs])
    assert d == Definition(lhs, rhs)

    d = Definition.parse(nvim, [lhs, rhs, 'noremap'])
    assert d == Definition(lhs, rhs, noremap=True)

    d = Definition.parse(nvim, [lhs, rhs, 'nowait'])
    assert d == Definition(lhs, rhs, nowait=True)

    d = Definition.parse(nvim, [lhs, rhs, 'noremap nowait'])
    assert d == Definition(lhs, rhs, True, True)

    d = Definition.parse(nvim, ['<C-H>', '<BS>'])
    assert d == Definition(lhs, rhs)

    d = Definition.parse(nvim, ['<C-H>', '<BS>', 'noremap'])
    assert d == Definition(lhs, rhs, noremap=True)

    d = Definition.parse(nvim, ['<C-H>', '<BS>', 'nowait'])
    assert d == Definition(lhs, rhs, nowait=True)

    d = Definition.parse(nvim, ['<C-H>', '<BS>', 'noremap nowait'])
    assert d == Definition(lhs, rhs, True, True)

    with pytest.raises(AttributeError):
        Definition.parse(nvim, [lhs, rhs, '', ''])

    with pytest.raises(AttributeError):
        Definition.parse(nvim, [lhs, rhs, 'unknown'])


def test_Keymap_property():
    keymap = Keymap()


def test_keymap_register(nvim):
    lhs = Keystroke.parse(nvim, '<C-H>')
    rhs = Keystroke.parse(nvim, '<BS>')
    keymap = Keymap()
    keymap.register(Definition(lhs, rhs))
    assert keymap.registry[lhs] == Definition(lhs, rhs)

    keymap.register(Definition(lhs, rhs, True))
    assert keymap.registry[lhs] == Definition(lhs, rhs, True)

    keymap.register(Definition(lhs, rhs, True, True))
    assert keymap.registry[lhs] == Definition(lhs, rhs, True, True)


def test_keymap_register_from_rule(nvim):
    lhs = Keystroke.parse(nvim, '<C-H>')
    rhs = Keystroke.parse(nvim, '<BS>')
    keymap = Keymap()
    keymap.register_from_rule(nvim, ('<C-H>', '<BS>'))
    assert keymap.registry[lhs] == Definition(lhs, rhs, False, False)

    keymap.register_from_rule(nvim, ('<C-H>', '<BS>', 'noremap'))
    assert keymap.registry[lhs] == Definition(lhs, rhs, True, False)

    keymap.register_from_rule(nvim, ('<C-H>', '<BS>', 'noremap nowait'))
    assert keymap.registry[lhs] == Definition(lhs, rhs, True, True)


def test_keymap_register_from_rules(nvim):
    lhs1 = Keystroke.parse(nvim, '<C-H>')
    lhs2 = Keystroke.parse(nvim, '<C-D>')
    lhs3 = Keystroke.parse(nvim, '<C-M>')
    rhs1 = Keystroke.parse(nvim, '<BS>')
    rhs2 = Keystroke.parse(nvim, '<DEL>')
    rhs3 = Keystroke.parse(nvim, '<CR>')

    keymap = Keymap()
    keymap.register_from_rules(nvim, [
        ('<C-H>', '<BS>'),
        ('<C-D>', '<DEL>', 'noremap'),
        ('<C-M>', '<CR>', 'noremap nowait'),
    ])
    assert keymap.registry[lhs1] == Definition(lhs1, rhs1, False, False)
    assert keymap.registry[lhs2] == Definition(lhs2, rhs2, True, False)
    assert keymap.registry[lhs3] == Definition(lhs3, rhs3, True, True)

    # It can overwrite
    keymap.register_from_rules(nvim, [
        ('<C-H>', '<BS>', 'noremap nowait'),
        ('<C-D>', '<DEL>', 'nowait'),
        ('<C-M>', '<CR>'),
    ])
    assert keymap.registry[lhs1] == Definition(lhs1, rhs1, True, True)
    assert keymap.registry[lhs2] == Definition(lhs2, rhs2, False, True)
    assert keymap.registry[lhs3] == Definition(lhs3, rhs3, False, False)


def test_keymap_filter(nvim):
    lhs1 = Keystroke.parse(nvim, '<C-X><C-F>')
    lhs2 = Keystroke.parse(nvim, '<C-X><C-B>')
    lhs3 = Keystroke.parse(nvim, '<C-A>')
    keymap = Keymap()
    keymap.register_from_rule(nvim, ('<C-X><C-F>', '<A>'))
    keymap.register_from_rule(nvim, ('<C-X><C-B>', '<B>'))
    keymap.register_from_rule(nvim, ('<C-A>', '<C>'))

    assert keymap.filter(Keystroke.parse(nvim, '')) == sorted((
        Definition(lhs3, Keystroke.parse(nvim, '<C>'), False, False),
        Definition(lhs1, Keystroke.parse(nvim, '<A>'), False, False),
        Definition(lhs2, Keystroke.parse(nvim, '<B>'), False, False),
    ))

    assert keymap.filter(Keystroke.parse(nvim, '<C-X>')) == sorted((
        Definition(lhs1, Keystroke.parse(nvim, '<A>'), False, False),
        Definition(lhs2, Keystroke.parse(nvim, '<B>'), False, False),
    ))

    assert keymap.filter(Keystroke.parse(nvim, '<C-X><C-F>')) == sorted((
        Definition(lhs1, Keystroke.parse(nvim, '<A>'), False, False),
    ))


def test_keymap_resolve(nvim):
    lhs1 = Keystroke.parse(nvim, '<C-X><C-F>')
    lhs2 = Keystroke.parse(nvim, '<C-X><C-B>')
    lhs3 = Keystroke.parse(nvim, '<C-A>')
    keymap = Keymap()
    keymap.register_from_rule(nvim, ('<C-X><C-F>', '<A>'))
    keymap.register_from_rule(nvim, ('<C-X><C-B>', '<B>'))
    keymap.register_from_rule(nvim, ('<C-A>', '<C>'))

    assert keymap.resolve(Keystroke.parse(nvim, '')) is None
    assert keymap.resolve(Keystroke.parse(nvim, '<C-A>')) == \
        Keystroke.parse(nvim, '<C>')
    assert keymap.resolve(Keystroke.parse(nvim, '<C-X>')) is None
    assert keymap.resolve(Keystroke.parse(nvim, '<C-X><C-F>')) == \
        Keystroke.parse(nvim, '<A>')

    # remap
    keymap.register_from_rule(nvim, ('<B>', '<D>'))
    assert keymap.resolve(Keystroke.parse(nvim, '<C-X><C-B>')) == \
        Keystroke.parse(nvim, '<D>')
    # noremap
    keymap.register_from_rule(nvim, ('<C-X><C-B>', '<B>', 'noremap'))
    assert keymap.resolve(Keystroke.parse(nvim, '<C-X><C-B>')) == \
        Keystroke.parse(nvim, '<B>')

    keymap.register_from_rule(nvim, ('<C-Y><C-K>', '<E>'))
    assert keymap.resolve(Keystroke.parse(nvim, '<C-Y>')) is None


def test_keymap_harvest_timeout(nvim):
    nvim.options = {
        'timeout': True,
        'timeoutlen': 1000,
        'encoding': 'utf-8',
    }
    timeoutlen = timedelta(milliseconds=nvim.options['timeoutlen'])

    now = datetime.now()
    with patch('prompt.keymap.datetime') as m1:
        keymap = Keymap()
        keymap.register_from_rules(nvim, [
            ('<C-H>', '<prompt:CH>', 'noremap'),
            ('<C-H><C-H>', '<prompt:CHCH>', 'noremap'),
        ])

        # Keypress within timeoutlen
        def side_effect(*args):
            yield ord('\x08')   # ^H
            m1.now.return_value += timedelta(milliseconds=999)
            yield 0
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call = MagicMock()
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CHCH>')
        with pytest.raises(StopIteration):
            nvim.call()

        # Keypress after timeoutlen
        def side_effect(*args):
            yield ord('\x08')   # ^H
            m1.now.return_value += timedelta(milliseconds=1000)
            yield 0
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CH>')
        assert nvim.call() == ord('\x08')   # residual

        # Timeout without keypress
        def side_effect(*args):
            m1.now.return_value += timedelta(milliseconds=1000)
            yield 0
            yield ord('\x08')   # ^H
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CHCH>')
        with pytest.raises(StopIteration):
            nvim.call()

        # Keypress within timeoutlen but with nowait
        keymap.register_from_rules(nvim, [
            ('<C-H>', '<prompt:CH>', 'noremap nowait'),
            ('<C-H><C-H>', '<prompt:CHCH>', 'noremap'),
        ])
        def side_effect(*args):
            yield ord('\x08')   # ^H
            m1.now.return_value += timedelta(milliseconds=999)
            yield 0
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call = MagicMock()
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CH>')
        assert nvim.call() == 0   # residual
        assert nvim.call() == ord('\x08')   # residual


def test_keymap_harvest_notimeout(nvim):
    nvim.options = {
        'timeout': False,
        'timeoutlen': 1000,
        'encoding': 'utf-8',
    }
    timeoutlen = None

    now = datetime.now()
    with patch('prompt.keymap.datetime') as m1:
        keymap = Keymap()
        keymap.register_from_rules(nvim, [
            ('<C-H>', '<prompt:CH>', 'noremap'),
            ('<C-H><C-H>', '<prompt:CHCH>', 'noremap'),
        ])

        # Keypress after timeoutlen
        def side_effect(*args):
            yield ord('\x08')   # ^H
            m1.now.return_value += timedelta(milliseconds=1000)
            yield 0
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call = MagicMock()
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CHCH>')
        with pytest.raises(StopIteration):
            nvim.call()

        # Keypress within timeoutlen but with nowait
        keymap.register_from_rules(nvim, [
            ('<C-H>', '<prompt:CH>', 'noremap nowait'),
            ('<C-H><C-H>', '<prompt:CHCH>', 'noremap'),
        ])
        def side_effect(*args):
            yield ord('\x08')   # ^H
            m1.now.return_value += timedelta(milliseconds=999)
            yield 0
            yield ord('\x08')   # ^H

        m1.now.return_value = now
        nvim.call = MagicMock()
        nvim.call.side_effect = side_effect()

        keystroke = keymap.harvest(nvim, timeoutlen)
        assert keystroke == Keystroke.parse(nvim, '<prompt:CH>')
        assert nvim.call() == 0   # residual
        assert nvim.call() == ord('\x08')   # residual


def test_Keymap_from_rules(nvim):
    lhs1 = Keystroke.parse(nvim, '<C-H>')
    lhs2 = Keystroke.parse(nvim, '<C-D>')
    lhs3 = Keystroke.parse(nvim, '<C-M>')
    rhs1 = Keystroke.parse(nvim, '<BS>')
    rhs2 = Keystroke.parse(nvim, '<DEL>')
    rhs3 = Keystroke.parse(nvim, '<CR>')

    keymap = Keymap.from_rules(nvim, [
        ('<C-H>', '<BS>'),
        ('<C-D>', '<DEL>', 'noremap'),
        ('<C-M>', '<CR>', 'noremap nowait'),
    ])
    assert keymap.registry[lhs1] == Definition(lhs1, rhs1, False, False)
    assert keymap.registry[lhs2] == Definition(lhs2, rhs2, True, False)
    assert keymap.registry[lhs3] == Definition(lhs3, rhs3, True, True)
