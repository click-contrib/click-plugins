"""Core components for click_plugins"""


import os
import sys
import traceback

import click


def with_plugins(entry_points):

    """A decorator to register external CLI commands to an instance of
    ``click.Group()``.

    Parameters
    ----------
    entry_points : iter
        An iterable producing one ``pkg_resources.EntryPoint()`` per
        iteration.

    Returns
    -------
    click.Group()
    """

    def decorator(group):
        if not isinstance(group, click.Group):
            raise TypeError(
                "Plugins can only be attached to an instance of "
                "'click.Group()'.")

        for ep in entry_points:
            try:
                group.add_command(ep.load())
            except Exception:
                # Catch this so a busted plugin doesn't take down the CLI.
                # Handled by registering a dummy command that does nothing
                # other than explain the error.
                group.add_command(BrokenCommand(ep.name))

        return group

    return decorator


class BrokenCommand(click.Command):

    """Rather than completely crash the CLI when a broken plugin is
    loaded, this class provides a modified help message informing the
    user that the plugin is broken and they should contact the owner.
    If the user executes the plugin or specifies ``--help`` a traceback
    is reported showing the exception the plugin loader encountered.
    """

    def __init__(self, name):

        """Define the special help messages after instantiating a
        ``click.Command()``.

        Parameters
        ----------
        name : str
            For ``click.Command()``.
        """

        click.Command.__init__(self, name)

        if os.environ.get('CLICK_PLUGINS_HONESTLY') == 'TRUE':
            icon = u'\U0001F4A9'
        else:
            icon = u'\u2020'

        # Override the command's short help with a warning message about how
        # the command is not functioning properly
        prog_name = os.path.basename(sys.argv and sys.argv[0] or __file__)
        self.short_help = (
            u"{icon} Warning: could not load plugin.  See: "
            "'$ {prog_name} {name} --help'.".format(
                icon=icon, prog_name=prog_name, name=name))

        # Override the command's long help with the exception traceback.
        # The call to 'traceback.format_exec()' function attempts to
        # access 'Exception.__context__' which doesn't exist on Python
        # 3.3 and 3.4, but appears to exist on 2.7 and >= 3.5.
        if sys.version_info >= (3, 5) or sys.version[:2] == (2, 7):
            tb = traceback.format_exc(chain=True)
        else:
            tb = traceback.format_exc()
        self.help = (
            "\nWarning: entry point could not be loaded. Contact "
            "its author for help.\n\n\b\n".format(os.linesep)
            + tb)

    def invoke(self, ctx):

        """Print the traceback instead of doing nothing.

        Parameters
        ----------
        ctx : click.Context
            CLI context.
        """

        click.echo(self.help, color=ctx.color)
        ctx.exit(1)
