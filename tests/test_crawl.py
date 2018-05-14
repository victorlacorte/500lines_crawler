import pytest

from crawler.crawl import parse_login


@pytest.mark.parametrize('expected, data', [
    (str(dict(foo='bar', baz='baba')), 'foo=bar:baz=baba'),
])
def test_parse_login(expected, data):
    assert str(parse_login(data)) == expected
