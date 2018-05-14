from setuptools import setup, find_packages

setup(
        entry_points={
            'console_scripts': [
                'crawl=crawler.crawl:main',
            ],
        },
        name='500lines_crawler',
        packages=find_packages(),
        version='1.0',
)
