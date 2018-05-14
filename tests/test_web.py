import pytest

from web.utils import UAClient, fix_url


@pytest.mark.skip(reason='Simple inspection function')
def test_UAClient():
    print(type(UAClient.chrome()))
    print(UAClient.ff())
    print(UAClient.ie())
    assert False

@pytest.mark.parametrize('expected, url', [
    ('http://foo.bar', 'foo.bar'),
    ('http://foo.bar', 'http://foo.bar'),
    ('https://foo.bar', 'https://foo.bar'),
])
def test_fix_url(expected, url):
    assert fix_url(url) == expected
