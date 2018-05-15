#!/usr/bin/env python3.4

"""A simple web crawler -- main driver program."""

# TODO:
# - Add arguments to specify TLS settings (e.g. cert/key files).

import aiohttp
import argparse
import asyncio
import logging
import sys

from crawler import crawling, reporting
from web.utils import UAClient, fix_url


def parse_login(s):
    '''
    Return a dict to be utilized as a ClientSession POST data payload from
    parsing (str) `s'.

    Example: s -> 'login=foo:pwd=bar': return {'login': 'foo', 'pwd': 'bar'}
    '''
    payload = {}
    for e in s.split(':'):
        k, v = e.split('=')
        payload[k] = v
    return payload

ARGS = argparse.ArgumentParser(description="Web crawler")
ARGS.add_argument(
    '--iocp', action='store_true', dest='iocp',
    default=False, help='Use IOCP event loop (Windows only)')
ARGS.add_argument(
    '--select', action='store_true', dest='select',
    default=False, help='Use Select event loop instead of default')
ARGS.add_argument(
    'roots', nargs='+',
    default=[], help='Root URL (may be repeated)')
ARGS.add_argument(
    '--max_redirect', action='store', type=int, metavar='N',
    default=10, help='Limit redirection chains (for 301, 302 etc.)')
ARGS.add_argument(
    '--max_tries', action='store', type=int, metavar='N',
    default=4, help='Limit retries on network errors')
ARGS.add_argument(
    '--max_tasks', action='store', type=int, metavar='N',
    default=100, help='Limit concurrent connections')
ARGS.add_argument(
    '--exclude', action='store', metavar='REGEX',
    help='Exclude matching URLs')
ARGS.add_argument(
    '--strict', action='store_true',
    default=True, help='Strict host matching (default)')
ARGS.add_argument(
    '--lenient', action='store_false', dest='strict',
    default=False, help='Lenient host matching')
ARGS.add_argument(
    '-v', '--verbose', action='count', dest='level',
    default=2, help='Verbose logging (repeat for more verbose)')
ARGS.add_argument(
    '-q', '--quiet', action='store_const', const=0, dest='level',
    default=2, help='Only log errors')
ARGS.add_argument(
    '--out', metavar='FILE',
    help='Log the output to a file instead of sys.stdout')
ARGS.add_argument(
    '--login_url', help='URL to login on')
ARGS.add_argument(
    '--login_data', help='Login payload to be POSTed by a ClientSession.' \
        ' Utilize format key=val:key=val (for username and password')

async def run_crawler(*, loop, roots, exclude, strict, max_redirect, max_tries,
        max_tasks, login_url, login_data, file=None):
    headers = {'User-Agent': UAClient.chrome()}
    async with aiohttp.ClientSession(headers=headers,
                                     loop=loop) as session:
        if login_data is not None:
            payload = parse_login(login_data)
            await session.post(login_url, data=payload)
        crawler = crawling.Crawler(
                    roots=roots,
                    session=session,
                    exclude=exclude,
                    strict=strict,
                    max_redirect=max_redirect,
                    max_tries=max_tries,
                    max_tasks=max_tasks)
        await crawler.crawl()
        reporting.report(crawler, file=file)

def main():
    '''
    Main program. Parse arguments, set up event loop, run crawler, print
    report.
    '''
    args = ARGS.parse_args()

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels)-1)])

    if args.iocp:
        from asyncio.windows_events import ProactorEventLoop
        loop = ProactorEventLoop()
        asyncio.set_event_loop(loop)
    elif args.select:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    if args.out:
        f = open(args.out, 'w')
    else:
        f = None

    roots = {fix_url(root) for root in args.roots}
    try:
        loop.run_until_complete(
                run_crawler(
                    loop=loop,
                    roots=roots,
                    exclude=args.exclude,
                    strict=args.strict,
                    max_redirect=args.max_redirect,
                    max_tries=args.max_tries,
                    max_tasks=args.max_tasks,
                    login_url=args.login_url,
                    login_data=args.login_data,
                    file=f))
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nInterrupted\n')
    finally:
        loop.stop()
        loop.run_forever()
        loop.close()
        if f is not None:
            f.close()

if __name__ == '__main__':
    main()
