import configparser
import importlib.metadata
from io import StringIO
import os
import unittest

import click
from click.testing import CliRunner

from click_plugins import _module_name, with_plugins


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


class VirtualDistribution(importlib.metadata.Distribution):

    """Representation of a package.

    Implements just enough methods to be used in testing. The tests need

    Represents an installed package. Implements just enough methods to be used
    in testing. The tests require ``importlib.metadata.EntryPoint()`` objects,
    and this class provides them. Otherwise, an installed package with entry
    points would be required for testing.
    """

    def __init__(self, valid, invalid):

        """Must set at least one of `valid` or `invalid`.

        Parameters
        ----------
        valid : bool
            Include functional plugins.
        invalid : bool
            Include broken plugins.
        """

        if not valid and not invalid:
            raise RuntimeError(
                f'would not load entry points: {valid=} {invalid=}'
            )

        self.valid = valid
        self.invalid = invalid

    @property
    def name(self):
        return '<virtual distribution for testing>'

    def locate_file(self, path):
        # Base class requires an implementation, but it does not need to
        # be functional.
        raise NotImplementedError

    def read_text(self, filename):

        # Only supports reading 'entry_points.txt'.

        if filename != 'entry_points.txt':
            raise RuntimeError(f'unsupported: {filename=}')

        cfg = configparser.ConfigParser()

        # Add valid plugins. These are expected to work properly.
        if self.valid:
            section = 'click_plugins_tests.valid'
            cfg.add_section(section)
            cfg.set(section, 'cmd1', 'click_plugins_tests:cmd1')
            cfg.set(section, 'cmd2', 'click_plugins_tests:cmd2')

        # Add invalid plugins. Broken in a variety of ways.
        if self.invalid:
            section = 'click_plugins_tests.invalid'
            cfg.add_section(section)
            cfg.set(
                section, 'no_exist', 'click_plugins_tests:__no__exist__')

        with StringIO() as f:
            cfg.write(f)
            f.seek(0)
            text = f.read()

        return text.strip()


###############################################################################
# Tests


class Tests(unittest.TestCase):

    def setUp(self):

        """Setup plugins and baseline CLI groups."""

        # 'click' test runner.
        self.runner = CliRunner()

        valid_dist = VirtualDistribution(valid=True, invalid=False)
        invalid_dist = VirtualDistribution(valid=False, invalid=True)

        self.valid_entry_points = valid_dist.entry_points
        self.invalid_entry_points = invalid_dist.entry_points

        # CLI group with valid plugins attached.
        @with_plugins(self.valid_entry_points)
        @click.group()
        def good_cli():
            """Good CLI group."""
        self.good_cli = good_cli

        # CLi group with broken plugins attached.
        @with_plugins(self.invalid_entry_points)
        @click.group()
        def broken_cli():
            """Broken CLI group."""
        self.broken_cli = broken_cli

    def test_registered(self):

        """Ensure the test plugins are properly registered.

        If this test fails something about the overall test setup is not
        correct.
        """

        for eps in (self.valid_entry_points, self.invalid_entry_points):
            self.assertGreaterEqual(len(eps), 1)

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
        for ep in self.valid_entry_points:
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
            for ep in self.invalid_entry_points:
                result = self.runner.invoke(self.broken_cli, [ep.name] + args)
                self.assertEqual(1, result.exit_code)
                self.assertIn('Traceback', result.output)
                msg = (
                    f"ERROR: entry point '{_module_name(ep)}:{ep.name}' could"
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
        for ep in self.valid_entry_points:
            self.assertIn(ep.name, result.output)

        @with_plugins(self.valid_entry_points)
        @self.good_cli.group(name='subgroup-with-plugins')
        def subgroup_with_plugins():
            """Subgroup with plugins."""

        # Same as above, but the subgroup also has plugins.
        result = self.runner.invoke(self.good_cli, ['subgroup-with-plugins'])
        self.assertEqual(0, result.exit_code)
        for ep in self.valid_entry_points:
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
