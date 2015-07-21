#!/usr/bin/env python


"""
Setup script for `PrintIt`
"""


from setuptools import setup


setup(
    name='PrintIt',
    version='0.1dev0',
    packages=['printit'],
    entry_points='''
        [console_scripts]
        printit=printit.cli:cli
    '''
)
