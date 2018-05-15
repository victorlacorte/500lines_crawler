'''Read an input file and download all URLs from it.'''

import aiohttp
import asyncio
from asyncio import Queue
import os
import urllib.parse


class Downloader:
    def __init__(self, *, fpath, session, 
                 max_tasks=10, loop=None,
                 chunk_size=1024):
        self.q = Queue(loop=self.loop)
        with open(fpath, 'r') as f:
            for url in f:
                self.q.put_nowait(url)
        self.session = session
        self.loop = loop or asyncio.get_event_loop()
        self.chunk_size = chunk_size

    async def process_url(self, url):
        dirpath, fname = parse_url(url)
        os.makedirs(dirpath, exist_ok=True)
        async with self.session.get(url) as resp:
            # We are blocking over a single file so we can still bypass the
            # whole "IO is blocking" thing, right?
            with open(os.path.join(dirpath, fname), 'wb') as fd:
                while True:
                    chunk = await resp.content.read(self.chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)

    async def work(self):
        """Process queue items forever."""
        try:
            while True:
                url = await self.q.get()
                await self.process_url(url)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    async def download(self):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await self.q.join()
        for w in workers:
            w.cancel()

def parse_url(url):
    '''Return dir and filename components from url.'''
    path = urllib.parse.urlsplit(url).path
    components = path.split('/')[-3:]
    dirpath = '/'.join(components[:2])
    fname = components[-1]
    return dirpath, fname
