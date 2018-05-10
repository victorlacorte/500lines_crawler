from web.utils import UAClient


def test_UAClient():
    ua = UAClient()
    assert ua.chrome()
    assert ua.ff()
    assert ua.ie()
