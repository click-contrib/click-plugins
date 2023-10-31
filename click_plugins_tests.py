import os
import unittest

import click
from click.testing import CliRunner
from pkg_resources import EntryPoint
from pkg_resources import iter_entry_points
from pkg_resources import working_set

from click_plugins import with_plugins


###############################################################################
# CLI Commands

# These commands are later registered as entry points, and then loaded. They
# must exist in

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


###############################################################################
# Shim Entry Point Machinery


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


###############################################################################
# Tests


class TestCase(unittest.TestCase):

    """Includes setup/teardown for registering plugins."""

    def setUp(self):

        """Setup plugins and baseline CLI groups."""

        # 'click' test runner.
        self.runner = CliRunner()

        # Register entry points by manually monkey patching an in-memory
        # object. Somewhat surprisingly, this has worked for a very long time.
        # This 'by_key[...]' bit must reference an external dependency, and is
        # also magic. Effectively this attaches an entrypoint to an existing
        # package. The package must not be part of the stdlib, and probably.
        # 'setuptools' will never register an entrypoint. If it does the
        # 'RuntimeError()' below will be triggered.
        self.working_set_key = 'setuptools'
        dist_info = working_set.by_key[self.working_set_key]
        if hasattr(dist_info, '_ep_map'):
            raise RuntimeError(
                f"'{self.working_set_key}' seems to have registered an entry"
                f" point - refusing to patch"
            )

        dist_info._ep_map = {
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
                    'do_not_exist=broken_plugins:do_not_exist',
                    dist=DistStub())
            }
        }

        # CLI group with valid plugins attached.
        @with_plugins(iter_entry_points('_test_click_plugins.test_plugins'))
        @click.group()
        def good_cli():
            """Good CLI group."""
        self.good_cli = good_cli

        # CLi group with broken plugins attached.
        @with_plugins(iter_entry_points('_test_click_plugins.broken_plugins'))
        @click.group()
        def broken_cli():
            """Broken CLI group."""
        self.broken_cli = broken_cli

    def tearDown(self):
        # This seems to be fine based on the 'pkg_resources' source code.
        # Sketchy, but some form of test isolation is necessary.
        delattr(working_set.by_key[self.working_set_key], '_ep_map')


class Tests(TestCase):

    def test_registered(self):

        """Ensure the test plugins are properly registered.

        If this test fails something about the overall test setup is not
        correct.
        """

        module_names = (
            '_test_click_plugins.test_plugins',
            '_test_click_plugins.broken_plugins'
        )

        for modname in module_names:
            entry_points = list(iter_entry_points(modname))
            self.assertGreater(len(entry_points), 1)

    def test_load_and_run(self):

        """Load functional plugins and execute."""

        # Ensure parent group is functional
        for args in (None, ['--help']):
            parent_result = self.runner.invoke(self.good_cli, args)
            self.assertEqual(0, parent_result.exit_code)

            # When a plugin is broken its help text is replaced and contains
            # an indicator that something is not right. This indicator should
            # *not* be present.
            self.assertNotIn('\u2020 Warning:', parent_result.output)

        # Ensure each plugin executes without error.
        for ep in iter_entry_points('_test_click_plugins.test_plugins'):
            result = self.runner.invoke(self.good_cli, [ep.name, 'something'])
            self.assertEqual(0, result.exit_code)
            self.assertEqual(f'passed{os.linesep}', result.output)

    def test_load_and_run_broken(self):

        """Load broken plugins and execute."""

        # Ensure parent group is functional
        for args in (None, ['--help']):
            parent_result = self.runner.invoke(self.broken_cli, args)
            self.assertEqual(0, parent_result.exit_code)

            # The output from executing the parent command should have an
            # indicator that something is wrong.
            self.assertIn('\u2020 Warning:', parent_result.output)

        # Ensure each plugin fails to execute, and also reports the full
        # traceback when executed with '--help'. Perform this check with and
        # without additional arguments.
        for args in ([], ['-a', 'b']):
            for ep in iter_entry_points('_test_click_plugins.broken_plugins'):
                result = self.runner.invoke(self.broken_cli, [ep.name] + args)
                self.assertEqual(1, result.exit_code)
                self.assertIn('Traceback', result.output)
                msg = (
                    f"ERROR: entry point '{ep.module_name}:{ep.name}' could"
                    f" not be loaded."
                )
                self.assertIn(msg, result.output)

    def test_group_chain(self):

        """Register on subgroup and execute."""

        @self.good_cli.group()
        def subgroup():
            """Subgroup."""

        # The 'subgroup()' is empty, but should not interfere with already
        # registered plugins.
        result = self.runner.invoke(self.good_cli)
        self.assertEqual(0, result.exit_code)
        self.assertIn(subgroup.name, result.output)
        for ep in iter_entry_points('_test_click_plugins.test_plugins'):
            self.assertIn(ep.name, result.output)

        @with_plugins(iter_entry_points('_test_click_plugins.test_plugins'))
        @self.good_cli.group(name='subgroup-with-plugins')
        def subgroup_with_plugins():
            """Subgroup with plugins."""

        # Same as above, but the subgroup also has plugins.
        result = self.runner.invoke(self.good_cli, ['subgroup-with-plugins'])
        self.assertEqual(0, result.exit_code)
        for ep in iter_entry_points('_test_click_plugins.test_plugins'):
            self.assertIn(ep.name, result.output)

        # Execute one of the subgroup's commands
        result = self.runner.invoke(
            self.good_cli, ['subgroup-with-plugins', 'cmd1', 'something'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(f'passed{os.linesep}', result.output)

    def test_exception(self):

        """Only attach plugins to ``click.Group()``."""

        with self.assertRaises(TypeError) as e:
            @with_plugins([])
            @click.command()
            def cli():
                """Broken!"""

        self.assertIn('instance of', str(e.exception))
        self.assertIn('click.Group()', str(e.exception))


if __name__ == '__main__':
    unittest.main()
