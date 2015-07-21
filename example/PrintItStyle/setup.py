#!/usr/bin/env python


"""
Setup script for `PrintItStyle`
"""


from setuptools import setup


setup(
    name='PrintItStyle',
    version='0.1dev0',
    packages=['printit_style'],
    entry_points='''
        [printit.plugins]
        background=printit_style.core:background
        color=printit_style.core:color
    '''
)
