import cgi
import os

import fake_useragent


class UAClient:
    def __init__(self, path='web/data'):
        name = 'fakeuseragent%s.json' % fake_useragent.VERSION
        self.ua = fake_useragent.UserAgent(path=os.path.join(path, name))

    def get_ua(self, update=False):
        if update:
            self.ua.update()
        return self.ua

    def chrome(self):
        return self.get_ua().chrome

    def ff(self):
        return self.get_ua().ff

    def ie(self):
        return self.get_ua().ie


def fix_url(url):
    '''Prefix a schema-less URL with http://.'''
    if '://' not in url:
        url = 'http://' + url
    return url

def is_redirect(response):
    '''
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
        Permanent redirections:
          301
        Temporary redirections:
          302, 303 and 307
        Special redirections:
          300
        There are other HTTP codes that imply redirections and are
           not on the comparison tuple.
    '''
    return response.status in (300, 301, 302, 303, 307)

def lenient_host(host):
    parts = host.split('.')[-2:]
    return ''.join(parts)

def parse_header(response):
    '''
    https://docs.python.org/3.6/library/cgi.html#cgi.parse_header
    '''
    content_type = response.headers.get('content-type')
    pdict = {}
    if content_type:
        content_type, pdict = cgi.parse_header(content_type)
    return content_type, pdict

def is_text(content_type):
    return content_type in ('text/html', 'application/xml')
