"""
Add bold styling to `printit`
"""


import click


@click.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
def bold(infile, outfile):

    """
    Make text bold.
    """

    for line in infile:
        click.secho(line, bold=True, file=outfile)
