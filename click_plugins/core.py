"""Core components for ``click_plugins``.

See ``with_plugins()``.
"""


import click

import os
import sys
import traceback


def with_plugins(plugins):

    """Decorator for loading plugins.

    Each entry point must point to a ``click.Command()`` object. An entry
    point producing an exception during loading will be wrapped in a
    ``BrokenCommand()``.

    >>> from pkg_resources import iter_entry_points
    >>> import click
    >>> from click_plugins import with_plugins
    >>>
    >>> @with_plugins(iter_entry_points('entry_point.name'))
    >>> @click.group()
    >>> def cli():
    ...     '''Commandline interface for something.'''
    >>>
    >>> @cli.command()
    >>> @click.argument('arg')
    >>> def subcommand(arg):
    ...     '''A subcommand for something else'''

    :param iterable plugins:
        Of ``pkg_resources.EntryPoint()`` objects.

    :rtype click.Group:
    """

    def decorator(group):
        if not isinstance(group, click.Group):
            raise TypeError("Plugins can only be attached to an instance of click.Group()")

        for entry_point in plugins or ():
            try:
                group.add_command(entry_point.load())
            except Exception:
                # Catch this so a busted plugin doesn't take down the CLI.
                # Handled by registering a dummy command that does nothing
                # other than explain the error.
                group.add_command(BrokenCommand(entry_point.name))

        return group

    return decorator


class BrokenCommand(click.Command):

    """Represents a plugin ``click.Command()`` that failed to load.

    Can be executed just like a ``click.Command()``, but prints information
    for debugging and exits with an error code.
    """

    def __init__(self, name):

        """
        :param str name:
            Entry point name.
        """

        click.Command.__init__(self, name)

        util_name = os.path.basename(sys.argv and sys.argv[0] or __file__)

        if os.environ.get('CLICK_PLUGINS_HONESTLY'):  # pragma no cover
            icon = u'\U0001F4A9'
        else:
            icon = u'\u2020'

        self.help = (
            "\nWarning: entry point could not be loaded. Contact "
            "its author for help.\n\n\b\n"
            + traceback.format_exc())
        self.short_help = (
            icon + " Warning: could not load plugin. See `%s %s --help`."
            % (util_name, self.name))

    def invoke(self, ctx):

        """Print traceback and debugging message.

        :param click.Context ctx:
            Active context.
        """

        click.echo(self.help, color=ctx.color)
        ctx.exit(1)

    def parse_args(self, ctx, args):

        """Pass arguments along without parsing.

        :param click.Context ctx:
            Active context.
        :param list args:
            List of command line arguments.
        """

        # Do not attempt to parse these arguments. We do not know why the
        # entry point failed to load, but it is reasonable to assume that
        # argument parsing will not work. Ultimately the goal is to get the
        # 'Command.invoke()' method (overloaded in this class) to execute
        # and provide the user with a bit of debugging information.

        return args
