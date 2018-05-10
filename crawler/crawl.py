#!/usr/bin/env python3.4

"""A simple web crawler -- main driver program."""

# TODO:
# - Add arguments to specify TLS settings (e.g. cert/key files).

import aiohttp
import argparse
import asyncio
import logging
import sys

from crawler import crawling
from crawler import reporting


ARGS = argparse.ArgumentParser(description="Web crawler")
ARGS.add_argument(
    '--iocp', action='store_true', dest='iocp',
    default=False, help='Use IOCP event loop (Windows only)')
ARGS.add_argument(
    '--select', action='store_true', dest='select',
    default=False, help='Use Select event loop instead of default')
ARGS.add_argument(
    'roots', nargs='*',
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
    '--log_out', metavar='FILE',
    help='Log the output to a file instead of sys.stdout')

def fix_url(url):
    """Prefix a schema-less URL with http://."""
    if '://' not in url:
        url = 'http://' + url
    return url

async def run_crawler(loop, roots, exclude, strict, max_redirect, max_tries,
        max_tasks, file=None):
    async with aiohttp.ClientSession(loop=loop) as session:
        crawler = crawling.Crawler(roots,
                                   session,
                                   exclude=exclude,
                                   strict=strict,
                                   max_redirect=max_redirect,
                                   max_tries=max_tries,
                                   max_tasks=max_tasks)
        await crawler.crawl()
        reporting.report(crawler, file=file)

def main():
    """Main program.

    Parse arguments, set up event loop, run crawler, print report.
    """
    args = ARGS.parse_args()
    if not args.roots:
        print('Use --help for command line help')
        return

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

    if args.log_out:
        f = open(args.log_out, 'w')
    else:
        f = None

    roots = {fix_url(root) for root in args.roots}
    try:
        loop.run_until_complete(run_crawler(
                                            loop,
                                            roots,
                                            args.exclude,
                                            args.strict,
                                            args.max_redirect,
                                            args.max_tries,
                                            args.max_tasks,
                                            file=f
                                            ))
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
