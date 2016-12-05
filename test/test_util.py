import re
from unittest.mock import MagicMock, patch
from neovim import attach
import pytest
import prompt.util as util


def test_ensure_bytes(nvim):
    assert isinstance(util.ensure_bytes(nvim, 'foo'), bytes)
    assert isinstance(util.ensure_bytes(nvim, b'foo'), bytes)


def test_ensure_str(nvim):
    assert isinstance(util.ensure_str(nvim, 'foo'), str)
    assert isinstance(util.ensure_str(nvim, b'foo'), str)


def test_int2char(nvim):
    assert util.int2char(nvim, 97) == 'a'
    assert util.int2char(nvim, 12354) == 'あ'

    with patch('prompt.util.get_encoding') as get_encoding:
        get_encoding.return_value = 'sjis'

        def nr2char(fname: str, code: int):
            b = code.to_bytes(2, byteorder='big')
            return b.decode('sjis')

        nvim.call = MagicMock()
        nvim.call.side_effect = nr2char
        code = int.from_bytes(b'\x82\x60', byteorder='big')
        assert util.int2char(nvim, code) == 'Ａ'


def test_int2repr(nvim):
    assert util.int2repr(nvim, 97) == 'a'
    assert util.int2repr(nvim, 12354) == 'あ'
    assert util.int2repr(nvim, b'\x80kb') == '<BS>'


def test_getchar(nvim):
    nvim.error = Exception
    nvim.call = MagicMock()
    nvim.call.return_value = 97
    assert util.getchar(nvim) == 97

    nvim.call.return_value = b'a'
    assert util.getchar(nvim) == b'a'

    nvim.call.return_value = 'a'
    assert util.getchar(nvim) == b'a'

    nvim.call.return_value = 0x03
    with pytest.raises(KeyboardInterrupt):
        util.getchar(nvim)

    nvim.call.side_effect = Exception("b'Keyboard interrupt'")
    with pytest.raises(KeyboardInterrupt):
        util.getchar(nvim)

    nvim.call.side_effect = Exception
    with pytest.raises(Exception):
        util.getchar(nvim)


def test_build_keyword_pattern_set():
    nvim = attach('child', argv=["nvim", "--embed"])

    nvim.current.buffer.options['iskeyword'] = 'A-Z,^C-Z,#,@-@,^'
    pattern_set = util.build_keyword_pattern_set(nvim)
    pattern = re.compile(pattern_set.pattern)
    inverse = re.compile(pattern_set.inverse)
    assert pattern_set is util.build_keyword_pattern_set(nvim)
    assert pattern.match('A')
    assert pattern.match('B')
    assert not pattern.match('C')
    assert not pattern.match('D')
    assert pattern.match('#')
    assert pattern.match('@')
    assert pattern.match('^')
    assert not pattern.match('!')
    assert not pattern.match('-')

    assert not inverse.match('A')
    assert not inverse.match('B')
    assert inverse.match('C')
    assert inverse.match('D')
    assert not inverse.match('#')
    assert not inverse.match('@')
    assert not inverse.match('^')
    assert inverse.match('!')
    assert inverse.match('-')

    nvim.current.buffer.options['iskeyword'] = '1-255,^A-C,^^,^!'
    pattern_set = util.build_keyword_pattern_set(nvim)
    pattern = re.compile(pattern_set.pattern)
    inverse = re.compile(pattern_set.inverse)
    assert pattern_set is util.build_keyword_pattern_set(nvim)
    assert not pattern.match('A')
    assert not pattern.match('B')
    assert not pattern.match('C')
    assert pattern.match('D')
    assert pattern.match('#')
    assert pattern.match('@')
    assert not pattern.match('^')
    assert not pattern.match('!')
    assert pattern.match('-')

    assert inverse.match('A')
    assert inverse.match('B')
    assert inverse.match('C')
    assert not inverse.match('D')
    assert not inverse.match('#')
    assert not inverse.match('@')
    assert inverse.match('^')
    assert inverse.match('!')
    assert not inverse.match('-')


def test_Singleton():

    class Dummy(metaclass=util.Singleton):
        pass

    assert Dummy() is Dummy()
