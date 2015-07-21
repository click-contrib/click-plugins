#!/usr/bin/env python


"""
Setup script for `PrintItBold`
"""


from setuptools import setup


setup(
    name='PrintItBold',
    version='0.1dev0',
    packages=['printit_bold'],
    entry_points='''
        [printit.plugins]
        bold=printit_bold.core:bolddddddddddd
    '''
)
