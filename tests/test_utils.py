import pytest

from clipmanager.utils import format_title, truncate_lines


@pytest.mark.parametrize('title,expected', [
    ('plain-text', 'plain-text'),
    ('\tplain-text', 'plain-text'),
    ('\nplain-text', '\nplain-text'),
])
def test_format_title(title, expected):
    assert format_title(title) == expected


@pytest.mark.parametrize('title,count,expected', [
    ('line-one', 1, 'line-one'),
    ('line-one', 2, 'line-one'),
    ('line-one\nline-two', 2, 'line-one\nline-two'),
    ('line-one\nline-two\nline-three', 2, 'line-one\nline-two...'),
])
def test_truncate_lines(title, count, expected):
    assert truncate_lines(title, count) == expected
