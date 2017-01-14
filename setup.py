#!/usr/bin/env python


"""Setup script for click-plugins"""


import codecs
import itertools as it
import os

from setuptools import find_packages
from setuptools import setup


with codecs.open('README.rst', encoding='utf-8') as f:
    long_desc = f.read().strip()


def parse_dunder_line(string):

    """Take a line like:

        "__version__ = '0.0.8'"

    and turn it into a tuple:

        ('__version__', '0.0.8')

    Not very fault tolerant.
    """

    # Split the line and remove outside quotes
    variable, value = (s.strip() for s in string.split('=')[:2])
    value = value[1:-1].strip()
    return variable, value


with open(os.path.join('click_plugins', '__init__.py')) as f:
    dunders = dict(map(
        parse_dunder_line, filter(lambda l: l.strip().startswith('__'), f)))
    version = dunders['__version__']
    author = dunders['__author__']
    email = dunders['__email__']
    source = dunders['__source__']


extras_require = {
    'test': [
        'pytest>=3.0',
        'pytest-cov',
    ]
}
extras_require['all'] = list(it.chain(*extras_require.values()))


setup(
    name='click-plugins',
    author=author,
    author_email=email,
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    description="An extension module for click to enable registering CLI "
                "commands via setuptools entry-points.",
    extras_require=extras_require,
    include_package_data=True,
    install_requires=['click>=3.0'],
    keywords='click plugin setuptools entry-point',
    license="New BSD",
    long_description=long_desc,
    packages=find_packages(exclude=['tests.*', 'tests']),
    url=source,
    version=version,
    zip_safe=True
)
