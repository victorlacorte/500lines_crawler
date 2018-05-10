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
