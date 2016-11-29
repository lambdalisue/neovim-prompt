from unittest.mock import MagicMock
import pytest

from prompt.action import Action, DEFAULT_ACTION


@pytest.fixture
def action():
    return DEFAULT_ACTION


def test_Action():
    action = Action()


def test_action_register():
    callback = lambda prompt, params: None
    action = Action()
    action.register('prompt:test', callback)
    assert 'prompt:test' in action.registry
    assert action.registry['prompt:test'] == callback


def test_action_unregister():
    callback = lambda prompt, params: None
    action = Action()
    action.register('prompt:test', callback)
    assert 'prompt:test' in action.registry
    assert action.registry['prompt:test'] == callback

    action.unregister('prompt:test')
    assert 'prompt:test' not in action.registry

    with pytest.raises(KeyError):
        action.unregister('prompt:test')

    action.unregister('prompt:test', fail_silently=True)


def test_action_register_from_rules():
    callback = lambda prompt, params: None
    action = Action()
    action.register_from_rules([
        ('prompt:test1', callback),
        ('prompt:test2', callback),
    ])
    assert 'prompt:test1' in action.registry
    assert 'prompt:test2' in action.registry
    assert action.registry['prompt:test1'] == callback
    assert action.registry['prompt:test2'] == callback


def test_action_call(prompt):
    prompt.text = 'foo'
    callback = lambda prompt, params: prompt.text
    action = Action()
    action.register('prompt:test', callback)
    assert action.call(prompt, 'prompt:test') == 'foo'

    with pytest.raises(AttributeError):
        action.call(prompt, 'prompt:not_a_registered_action')


def test_action_call_with_params(prompt):
    prompt.text = 'foo'
    callback = lambda prompt, params: prompt.text + params
    action = Action()
    action.register('prompt:test', callback)
    assert action.call(prompt, 'prompt:test') == 'foo'
    assert action.call(prompt, 'prompt:test:foo') == 'foofoo'
    assert action.call(prompt, 'prompt:test:foo:foo') == 'foofoo:foo'


def test_Action_from_rules():
    callback = lambda prompt, params: None
    action = Action.from_rules([
        ('prompt:test1', callback),
        ('prompt:test2', callback),
    ])
    assert 'prompt:test1' in action.registry
    assert 'prompt:test2' in action.registry
    assert action.registry['prompt:test1'] == callback
    assert action.registry['prompt:test2'] == callback


def test_accept(prompt, action):
    from prompt.prompt import STATUS_ACCEPT
    assert action.call(prompt, 'prompt:accept') == STATUS_ACCEPT


def test_cancel(prompt, action):
    from prompt.prompt import STATUS_CANCEL
    assert action.call(prompt, 'prompt:cancel') == STATUS_CANCEL


def test_toggle_insert_mode(prompt, action):
    from prompt.prompt import INSERT_MODE_INSERT, INSERT_MODE_REPLACE
    prompt.insert_mode = INSERT_MODE_INSERT
    assert action.call(prompt, 'prompt:toggle_insert_mode') is None
    assert prompt.insert_mode == INSERT_MODE_REPLACE
    assert action.call(prompt, 'prompt:toggle_insert_mode') is None
    assert prompt.insert_mode == INSERT_MODE_INSERT


def test_delete_char_before_caret(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert prompt.text == 'Hell Goodbye'
    assert prompt.caret.locus == 4

    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert prompt.text == ' Goodbye'
    assert prompt.caret.locus == 0

    assert action.call(prompt, 'prompt:delete_char_before_caret') is None
    assert prompt.text == ' Goodbye'
    assert prompt.caret.locus == 0


def test_delete_word_before_caret(prompt, action):

    def mock_call(fname, expr, pat, sub, flags):
        import re
        return re.sub('\w+\s*$', sub, expr)

    prompt.nvim.call = MagicMock()
    prompt.nvim.call.side_effect = mock_call

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_word_before_caret') is None
    assert prompt.text == ' Goodbye'
    assert prompt.caret.locus == 0

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 10
    assert action.call(prompt, 'prompt:delete_word_before_caret') is None
    assert prompt.text == 'Hello bye'
    assert prompt.caret.locus == 6

    prompt.text = 'Hello Goodbye    '
    prompt.caret.locus = 16
    assert action.call(prompt, 'prompt:delete_word_before_caret') is None
    assert prompt.text == 'Hello  '
    assert prompt.caret.locus == 6
    assert action.call(prompt, 'prompt:delete_word_before_caret') is None
    assert prompt.text == ' '
    assert prompt.caret.locus == 0


def test_delete_char_after_caret(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert prompt.text == 'Hello oodbye'
    assert prompt.caret.locus == 5

    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert prompt.text == 'Hello ye'
    assert prompt.caret.locus == 5

    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert action.call(prompt, 'prompt:delete_char_after_caret') is None
    assert prompt.text == 'Hello '
    assert prompt.caret.locus == 5


def test_delete_word_after_caret(prompt, action):

    def mock_call(fname, expr, pat, sub, flags):
        import re
        return re.sub('^\s*\w+', sub, expr)

    prompt.nvim.call = MagicMock()
    prompt.nvim.call.side_effect = mock_call

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_word_after_caret') is None
    assert prompt.text == 'Hello '
    assert prompt.caret.locus == 5

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 10
    assert action.call(prompt, 'prompt:delete_word_after_caret') is None
    assert prompt.text == 'Hello Goodb'
    assert prompt.caret.locus == 10

    prompt.text = 'Hello Goodbye    '
    prompt.caret.locus = 16
    assert action.call(prompt, 'prompt:delete_word_after_caret') is None
    assert prompt.text == 'Hello Goodbye    '
    assert prompt.caret.locus == 16

    prompt.text = '    Hello Goodbye'
    prompt.caret.locus = 2
    assert action.call(prompt, 'prompt:delete_word_after_caret') is None
    assert prompt.text == '    Goodbye'
    assert prompt.caret.locus == 2


def test_delete_char_under_caret(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_char_under_caret') is None
    assert prompt.text == 'HelloGoodbye'
    assert prompt.caret.locus == 5


def test_delete_word_under_caret(prompt, action):

    def mock_call(fname, expr, pat, sub, flags):
        import re
        return re.sub('\w+\s*$', sub, expr)

    prompt.nvim.call = MagicMock()
    prompt.nvim.call.side_effect = mock_call

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_word_under_caret') is None
    assert prompt.text == 'HelloGoodbye'
    assert prompt.caret.locus == 5

    prompt.text = 'Hello   Goodbye'
    prompt.caret.locus = 6
    assert action.call(prompt, 'prompt:delete_word_under_caret') is None
    assert prompt.text == 'HelloGoodbye'
    assert prompt.caret.locus == 5

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 10
    assert action.call(prompt, 'prompt:delete_word_under_caret') is None
    assert prompt.text == 'Hello '
    assert prompt.caret.locus == 6

    prompt.text = 'Hello Goodbye    '
    prompt.caret.locus = 16
    assert action.call(prompt, 'prompt:delete_word_under_caret') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 13
    assert action.call(prompt, 'prompt:delete_word_under_caret') is None
    assert prompt.text == 'Hello '
    assert prompt.caret.locus == 6


def test_delete_text_before_caret(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_text_before_caret') is None
    assert prompt.text == 'Goodbye'
    assert prompt.caret.locus == 0


def test_delete_text_after_caret(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_text_after_caret') is None
    assert prompt.text == 'Hello'
    assert prompt.caret.locus == 5


def test_delete_entire_text(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:delete_entire_text') is None
    assert prompt.text == ''
    assert prompt.caret.locus == 0


def test_move_caret_to_left(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 4

    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert prompt.caret.locus == 0
    assert action.call(prompt, 'prompt:move_caret_to_left') is None
    assert prompt.caret.locus == 0


def test_move_caret_to_one_word_left(prompt, action):

    def mock_call(fname, expr, pat, sub, flags):
        import re
        return re.sub('\w+\s?$', sub, expr)

    prompt.nvim.call = MagicMock()
    prompt.nvim.call.side_effect = mock_call

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_one_word_left') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 0

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 9
    assert action.call(prompt, 'prompt:move_caret_to_one_word_left') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 6

    prompt.text = 'Hello Goodbye    '
    prompt.caret.locus = 16
    assert action.call(prompt, 'prompt:move_caret_to_one_word_left') is None
    assert prompt.text == 'Hello Goodbye    '
    assert prompt.caret.locus == 15
    assert action.call(prompt, 'prompt:move_caret_to_one_word_left') is None
    assert prompt.text == 'Hello Goodbye    '
    assert prompt.caret.locus == 14
    assert action.call(prompt, 'prompt:move_caret_to_one_word_left') is None
    assert prompt.text == 'Hello Goodbye    '
    assert prompt.caret.locus == 6


def test_move_caret_to_left_anchor(prompt, action):
    prompt.nvim.call = MagicMock()
    prompt.nvim.call.return_value = ord('e')
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_left_anchor') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 1

    prompt.nvim.call.return_value = ord('y')
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_left_anchor') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 5


def test_move_caret_to_right(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 6

    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert prompt.caret.locus == 13
    assert action.call(prompt, 'prompt:move_caret_to_right') is None
    assert prompt.caret.locus == 13


def test_move_caret_to_one_word_right(prompt, action):

    def mock_call(fname, expr, pat, sub, flags):
        import re
        return re.sub('^\w+', sub, expr)

    prompt.nvim.call = MagicMock()
    prompt.nvim.call.side_effect = mock_call

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_one_word_right') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 13

    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 2
    assert action.call(prompt, 'prompt:move_caret_to_one_word_right') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 5

    prompt.text = 'Hello   Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_one_word_right') is None
    assert prompt.text == 'Hello   Goodbye'
    assert prompt.caret.locus == 6
    assert action.call(prompt, 'prompt:move_caret_to_one_word_right') is None
    assert prompt.text == 'Hello   Goodbye'
    assert prompt.caret.locus == 7
    assert action.call(prompt, 'prompt:move_caret_to_one_word_right') is None
    assert prompt.text == 'Hello   Goodbye'
    assert prompt.caret.locus == 15


def test_move_caret_to_left_anchor(prompt, action):
    prompt.nvim.call = MagicMock()
    prompt.nvim.call.return_value = ord('y')
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_right_anchor') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 11

    prompt.nvim.call.return_value = ord('H')
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_right_anchor') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 5


def test_move_caret_to_head(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_head') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 0
    assert action.call(prompt, 'prompt:move_caret_to_head') is None
    assert prompt.caret.locus == 0


def test_move_caret_to_lead(prompt, action):
    prompt.text = '    Hello Goodbye'
    prompt.caret.locus = 9
    assert action.call(prompt, 'prompt:move_caret_to_lead') is None
    assert prompt.text == '    Hello Goodbye'
    assert prompt.caret.locus == 4
    assert action.call(prompt, 'prompt:move_caret_to_lead') is None
    assert prompt.caret.locus == 4


def test_move_caret_to_tail(prompt, action):
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:move_caret_to_tail') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 13
    assert action.call(prompt, 'prompt:move_caret_to_tail') is None
    assert prompt.caret.locus == 13


def test_assign_previous_text(prompt, action):
    prompt.history = MagicMock()
    prompt.history.previous.side_effect = [
        'foo', 'bar', 'hoge',
    ]
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:assign_previous_text') is None
    assert prompt.text == 'foo'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_previous_text') is None
    assert prompt.text == 'bar'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_previous_text') is None
    assert prompt.text == 'hoge'
    assert prompt.caret.locus == len(prompt.text)


def test_assign_next_text(prompt, action):
    prompt.history = MagicMock()
    prompt.history.next.side_effect = [
        'foo', 'bar', 'hoge',
    ]
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:assign_next_text') is None
    assert prompt.text == 'foo'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_next_text') is None
    assert prompt.text == 'bar'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_next_text') is None
    assert prompt.text == 'hoge'
    assert prompt.caret.locus == len(prompt.text)


def test_assign_previous_matched_text(prompt, action):
    prompt.history = MagicMock()
    prompt.history.previous_match.side_effect = [
        'foo', 'bar', 'hoge',
    ]
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:assign_previous_matched_text') is None
    assert prompt.text == 'foo'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_previous_matched_text') is None
    assert prompt.text == 'bar'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_previous_matched_text') is None
    assert prompt.text == 'hoge'
    assert prompt.caret.locus == len(prompt.text)


def test_assign_next_matched_text(prompt, action):
    prompt.history = MagicMock()
    prompt.history.next_match.side_effect = [
        'foo', 'bar', 'hoge',
    ]
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:assign_next_matched_text') is None
    assert prompt.text == 'foo'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_next_matched_text') is None
    assert prompt.text == 'bar'
    assert prompt.caret.locus == len(prompt.text)

    assert action.call(prompt, 'prompt:assign_next_matched_text') is None
    assert prompt.text == 'hoge'
    assert prompt.caret.locus == len(prompt.text)


def test_paste_from_register(prompt, action):
    def side_effect(fname, *args):
        if fname == 'getchar':
            return ord('a')
        elif fname == 'getreg':
            return '<%s>' % args[0]

    prompt.nvim.error = Exception
    prompt.nvim.eval = MagicMock()
    prompt.nvim.call = MagicMock()
    prompt.nvim.command = MagicMock()
    prompt.nvim.call.side_effect = side_effect
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:paste_from_register') is None
    assert prompt.text == 'Hello<a> Goodbye'
    assert prompt.caret.locus == 8


def test_paste_from_default_register(prompt, action):
    prompt.nvim.vvars = {
        'register': '*',
    }
    prompt.nvim.call = MagicMock()
    prompt.nvim.command = MagicMock()
    prompt.nvim.call.side_effect = lambda fname, reg: '<%s>' % reg
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:paste_from_default_register') is None
    assert prompt.text == 'Hello<*> Goodbye'
    assert prompt.caret.locus == 8


def test_yank_to_register(prompt, action):
    def side_effect(fname, *args):
        if fname == 'getchar':
            return ord('a')

    prompt.nvim.eval = MagicMock()
    prompt.nvim.call = MagicMock()
    prompt.nvim.command = MagicMock()
    prompt.nvim.call.side_effect = side_effect
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:yank_to_register') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 5
    prompt.nvim.call.assert_called_with('setreg', 'a', 'Hello Goodbye')


def test_yank_to_default_register(prompt, action):
    prompt.nvim.vvars = {
        'register': '*',
    }
    prompt.nvim.call = MagicMock()
    prompt.nvim.command = MagicMock()
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:yank_to_default_register') is None
    assert prompt.text == 'Hello Goodbye'
    assert prompt.caret.locus == 5
    prompt.nvim.call.assert_called_with('setreg', '*', 'Hello Goodbye')


def test_insert_special(prompt, action):
    prompt.nvim.call = MagicMock()
    prompt.nvim.call.return_value = ord('a')
    prompt.nvim.command = MagicMock()
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:insert_special') is None
    assert prompt.text == 'Helloa Goodbye'
    assert prompt.caret.locus == 6

    prompt.nvim.call.return_value = 0x01
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:insert_special') is None
    assert prompt.text == 'Hello\x01 Goodbye'
    assert prompt.caret.locus == 6

    prompt.nvim.call.return_value = b'\x80kb'
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:insert_special') is None
    assert prompt.text == 'Hello\x08 Goodbye'
    assert prompt.caret.locus == 6


def test_insert_digraph(prompt, action):
    from prompt.digraph import Digraph
    # Make sure that digraph is cached
    nvim = prompt.nvim
    nvim.call = MagicMock()
    nvim.call.return_value = 'aa A 00  bb B 01\ncc C 02  ad D 03'
    Digraph().find(nvim, 'a', 'a')
    # ---
    prompt.nvim.call.side_effect = [
        ord('a'),
        ord('a'),
    ]
    prompt.nvim.command = MagicMock()
    prompt.text = 'Hello Goodbye'
    prompt.caret.locus = 5
    assert action.call(prompt, 'prompt:insert_digraph') is None
    assert prompt.text == 'HelloA Goodbye'
    assert prompt.caret.locus == 6
