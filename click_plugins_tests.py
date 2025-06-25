from pkg_resources import EntryPoint
from pkg_resources import iter_entry_points
from pkg_resources import working_set

import click
from click.testing import CliRunner
import pytest

from click_plugins import with_plugins


###############################################################################
# 'pytest' fixtures


@pytest.fixture(scope='function')
def runner(request):
    return CliRunner()


###############################################################################
# Register CLI

# A collection of commands and subcommands in various states. Register as
# entry points for loading later.


@click.command()
@click.argument('arg')
def cmd1(arg):
    """Test command 1"""
    click.echo('passed')


@click.command()
@click.argument('arg')
def cmd2(arg):
    """Test command 2"""
    click.echo('passed')


# Manually register plugins in an entry point and put broken plugins in a
# different entry point.

class DistStub(object):

    """Shim for testing.

    This class gets around an exception that is raised when loading an entry
    point. By default, ``entry_point.load()`` sets ``requires=True``, which in
    turn calls ``dist.requires()``. The ``click.group()`` decorator does not
    allow us to change this parameter. Because we are manually registering
    these plugins the ``dist`` attribute is ``None`` so we can just create a
    stub that always returns an empty list since we don't have any
    requirements.  A full ``pkg_resources.Distribution()`` instance is not
    needed because these entry points are not associated with a package.
    """

    def requires(self, *args):
        return []


working_set.by_key['click']._ep_map = {
    '_test_click_plugins.test_plugins': {
        'cmd1': EntryPoint.parse(
            # !! Points to a function in this file !!
            'cmd1=click_plugins_tests:cmd1', dist=DistStub()),
        'cmd2': EntryPoint.parse(
            # !! Points to a function in this file !!
            'cmd2=click_plugins_tests:cmd2', dist=DistStub())
    },
    '_test_click_plugins.broken_plugins': {
        'before': EntryPoint.parse(
            'before=broken_plugins:before', dist=DistStub()),
        'after': EntryPoint.parse(
            'after=broken_plugins:after', dist=DistStub()),
        'do_not_exist': EntryPoint.parse(
            'do_not_exist=broken_plugins:do_not_exist', dist=DistStub())
    }
}


# Main CLI groups - one with good plugins attached and the other broken
@with_plugins(iter_entry_points('_test_click_plugins.test_plugins'))
@click.group()
def good_cli():
    """Good CLI group."""
    pass


@with_plugins(iter_entry_points('_test_click_plugins.broken_plugins'))
@click.group()
def broken_cli():
    """Broken CLI group."""
    pass


###############################################################################
# Tests


def test_registered():
    # Make sure the plugins are properly registered.  If this test fails it
    # means that some of the for loops in other tests may not be executing.
    assert len([ep for ep in iter_entry_points('_test_click_plugins.test_plugins')]) > 1
    assert len([ep for ep in iter_entry_points('_test_click_plugins.broken_plugins')]) > 1


def test_register_and_run(runner):

    result = runner.invoke(good_cli)
    assert result.exit_code == 0

    for ep in iter_entry_points('_test_click_plugins.test_plugins'):
        cmd_result = runner.invoke(good_cli, [ep.name, 'something'])
        assert cmd_result.exit_code == 0
        assert cmd_result.output.strip() == 'passed'


def test_broken_register_and_run(runner):

    result = runner.invoke(broken_cli)
    assert result.exit_code == 0
    assert '\u2020' in result.output

    for ep in iter_entry_points('_test_click_plugins.broken_plugins'):
        cmd_result = runner.invoke(broken_cli, [ep.name])
        assert cmd_result.exit_code != 0
        assert 'Traceback' in cmd_result.output


def test_group_chain(runner):

    # Attach a sub-group to a CLI and get execute it without arguments to make
    # sure both the sub-group and all the parent group's commands are present
    @good_cli.group()
    def sub_cli():
        """Sub CLI."""
        pass

    result = runner.invoke(good_cli)
    assert result.exit_code == 0
    assert sub_cli.name in result.output
    for ep in iter_entry_points('_test_click_plugins.test_plugins'):
        assert ep.name in result.output

    # Same as above but the sub-group has plugins
    @with_plugins(iter_entry_points('_test_click_plugins.test_plugins'))
    @good_cli.group(name='sub-cli-plugins')
    def sub_cli_plugins():
        """Sub CLI with plugins."""
        pass

    result = runner.invoke(good_cli, ['sub-cli-plugins'])
    assert result.exit_code == 0
    for ep in iter_entry_points('_test_click_plugins.test_plugins'):
        assert ep.name in result.output

    # Execute one of the sub-group's commands
    result = runner.invoke(good_cli, ['sub-cli-plugins', 'cmd1', 'something'])
    assert result.exit_code == 0
    assert result.output.strip() == 'passed'


def test_exception():
    # Decorating something that isn't a click.Group() should fail
    with pytest.raises(TypeError):
        @with_plugins([])
        @click.command()
        def cli():
            """Whatever"""


def test_broken_register_and_run_with_help(runner):
    result = runner.invoke(broken_cli)
    assert result.exit_code == 0
    assert '\u2020' in result.output

    for ep in iter_entry_points('_test_click_plugins.broken_plugins'):
        cmd_result = runner.invoke(broken_cli, [ep.name, "--help"])
        msg = (
            f"ERROR: entry point '{ep.module_name}:{ep.name}' could not be"
            f" loaded."
        )
        assert cmd_result.exit_code != 0
        assert cmd_result.output.strip().startswith(msg)
        assert 'Traceback' in cmd_result.output


def test_broken_register_and_run_with_args(runner):
    result = runner.invoke(broken_cli)
    assert result.exit_code == 0
    assert '\u2020' in result.output

    for ep in iter_entry_points('_test_click_plugins.broken_plugins'):
        cmd_result = runner.invoke(broken_cli, [ep.name, "-a", "b"])
        assert cmd_result.exit_code != 0
        assert 'Traceback' in cmd_result.output
