from setuptools import setup, find_packages

setup(
        name='500lines_crawler',
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'crawl=crawler.crawl:main',
            ],
        },
)
