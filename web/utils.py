import cgi
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


lenient_host = lambda host: ''.join(host.split('.')[-2:])

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

def parse_header(resp):
    '''
    https://docs.python.org/3.6/library/cgi.html#cgi.parse_header
    '''
    content_type = resp.headers.get('content-type')
    pdict = {}
    if content_type:
        content_type, pdict = cgi.parse_header(content_type)
    return content_type, pdict
