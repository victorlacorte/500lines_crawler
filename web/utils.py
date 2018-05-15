import cgi
from datetime import datetime
from email.utils import parsedate
import os

import fake_useragent


class UAClient:
    db_path = 'web/data'
    db_name = 'fakeuseragent%s.json' % fake_useragent.VERSION

    # def __init__(self, path='web/data'):
    #     name = 'fakeuseragent%s.json' % fake_useragent.VERSION
    #     self.ua = fake_useragent.UserAgent(path=os.path.join(path, name))

    @classmethod
    def get_ua(cls, update=False):
        ua = fake_useragent.UserAgent(
                path=os.path.join(cls.db_path, cls.db_name))
        if update:
            ua.update()
        return ua

    @classmethod
    def chrome(cls):
        return cls.get_ua().chrome

    @classmethod
    def ff(cls):
        return cls.get_ua().ff

    @classmethod
    def ie(cls):
        return cls.get_ua().ie


# Pretty sure we need to join on '.' rather than ''
lenient_host = lambda host: '.'.join(host.split('.')[-2:])

# Prefix a schema-less URL with http://
fix_url = lambda url: 'http://' +  url if '://' not in url else url

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
# Permanent redirections:
# 301
# Temporary redirections:
# 302, 303 and 307
# Special redirections:
# 300
# There are other HTTP codes that imply redirections that are missing
# from the comparison tuple.
is_redirect = lambda resp: resp.status in (300, 301, 302, 303, 307)

is_text = lambda content: content in ('text/html', 'application/xml')

def parse_mime_header(resp, name='content-type'):
    '''
    https://docs.python.org/3.6/library/cgi.html#cgi.parse_header
    '''
    h = resp.headers.get(name)
    pdict = {}
    if h:
        h, pdict = cgi.parse_header(h)
    return h, pdict

def parse_http_datetime(s):
    '''
    https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html
    http://code.activestate.com/recipes/577015-parse-http-date-time-string/
    https://docs.python.org/3/library/email.util.html#email.utils.parsedate
    '''
    date = parsedate(s)
    # "Note that indexes 6, 7, and 8 of the result tuple are not usable."
    return datetime(*date[:6]) if date is not None else None
