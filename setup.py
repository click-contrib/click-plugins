#!/usr/bin/env python


"""
Setup script for click-plugins
"""


import codecs
import os

from setuptools import find_packages
from setuptools import setup


with codecs.open('README.rst', encoding='utf-8') as f:
    long_desc = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('click_plugins', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break


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
        'Programming Language :: Python :: 3',
    ],
    description="An extension module for click to enable registering CLI commands "
                "via setuptools entry-points.",
    extras_require={
        'dev': [
            'pytest>=3.6',
            'pytest-cov',
            'wheel',
            'coveralls'
        ],
    },
    include_package_data=True,
    install_requires=['click>=4.0'],
    keywords='click plugin setuptools entry-point',
    license="New BSD",
    long_description=long_desc,
    packages=find_packages(exclude=['tests.*', 'tests']),
    url=source,
    version=version,
    zip_safe=True
)
