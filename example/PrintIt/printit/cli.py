"""
Commandline interface for PrintIt
"""


from importlib.metadata import entry_points

import click
import click_plugins
from click_plugins import with_plugins


@with_plugins(entry_points(group='printit.plugins'))
@click.group()
def cli():

    """
    Format and print file contents.

    \b
    For example:
    \b
        $ cat README.rst | printit lower
    """


@cli.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
def upper(infile, outfile):

    """
    Convert to upper case.
    """

    for line in infile:
        outfile.write(line.upper())


@cli.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
def lower(infile, outfile):

    """
    Convert to lower case.
    """

    for line in infile:
        outfile.write(line.lower())
