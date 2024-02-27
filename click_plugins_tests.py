from collections import defaultdict
import configparser
import importlib.metadata
from io import StringIO
import os
import sys
import unittest
from unittest import mock

import click
from click.testing import CliRunner

from click_plugins import _module, with_plugins


###############################################################################
# CLI Commands

# These commands are later registered as entry points, and then loaded. They
# must exist in


EP_NO_EXIST_KEY = 'no_exist'
EP_NO_EXIST_VALUE = 'click_plugins_tests:__no__exist__'


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

    def __init__(self, valid, invalid, extra_group):

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
        self.extra_group = extra_group

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
            cfg.set(section, EP_NO_EXIST_KEY, EP_NO_EXIST_VALUE)

        if self.extra_group:
            section = 'extra_entry_point_group'
            cfg.add_section(section)
            cfg.set(
                section, 'extra_entry_point_key', 'extra_entry_point_value')

        with StringIO() as f:
            cfg.write(f)
            f.seek(0)
            text = f.read()

        return text.strip()


###############################################################################
# Tests


def mock_entry_points(**params):

    """Load a fixed set of entry points without a package.

    ``click-plugins`` needs to exercise loading plugins, but managing a
    one or more additional packages for testing this machinery is complicated.
    Instead, this function mocks enough of the packaging machinery to present
    a set of valid ``importlib.metadata.EntryPoint()`` objects.

    :param **kwargs params:
        Keyword arguments. See ``importlib.metadata.entry_points()``.

    :rtype importlib.metadata.EntryPoints or tuple:

    :returns:
        Python 3.8 returns a ``tuple()`` of ``EntryPoint()`` objects. Other
        versions of Python return a ``importlib.metadata.EntryPoints()``
        object.
    """

    # This code is unfortunately a bit complicated. Different versions of
    # Python have subtly different APIs. Hopefully Python 3.12 has provided
    # stability. Some versions are more complete than others. Notably, Python
    # 3.8 only supports the 'group' parameter.

    if (3, 8) <= sys.version_info <= (3, 9) and params:
        raise RuntimeError(
            f"'entry_points()' on Python 3.8 and 3.9 does not accept"
            f" parameters"
        )

    dist = VirtualDistribution(valid=True, invalid=True, extra_group=True)
    virtual_eps = dist.entry_points

    if sys.version_info >= (3, 12):
        eps = importlib.metadata.EntryPoints(virtual_eps)
        eps = eps.select(**params)

    elif sys.version_info >= (3, 10):
        from importlib.metadata import SelectableGroups
        eps = SelectableGroups.load(virtual_eps)
        if params:
            eps = eps.select(**params)

    elif sys.version_info >= (3, 8):

        # Based on the CPython v3.10.13 source code. Ultimately a 'tuple()'
        # of 'EntryPoint()' objects is returned.
        #   Lib/importlib/metadata.py

        by_group = defaultdict(list)
        for e in virtual_eps:
            by_group[e.group].append(e)

        return dict(by_group)

    else:
        raise RuntimeError(
            f'unsupported Python: {".".join(map(str, sys.version_info[:3]))}')

    return eps


def mock_entry_points_from_group(group):

    """Shim for an API difference in older versions of Python."""

    if sys.version_info >= (3, 10):
        all_entry_points = mock_entry_points(group=group)

    else:
        all_entry_points = mock_entry_points()
        all_entry_points = all_entry_points[group]

    return all_entry_points


class TestLoad(unittest.TestCase):

    """Ensures plugins can be properly loaded."""

    mapping = {
        'click_plugins_tests.valid': (cmd1.name, cmd2.name),
        'click_plugins_tests.invalid': (EP_NO_EXIST_KEY, )
    }

    def test_EntryPoint(self):

        """Load a plugin from a single ``EntryPoint()`` object."""

        for group, expected_keys in self.mapping.items():
            entry_points = mock_entry_points_from_group(group)
            for ep, key in zip(entry_points, expected_keys):

                @with_plugins(ep)
                @click.group()
                def group():
                    """test_load_EntryPoint"""

                self.assertEqual((key, ), tuple(group.commands.keys()))

    def test_EntryPoint_objects(self):

        """Load plugins from an iterable of ``EntryPoint()`` objects."""

        for group, expected_keys in self.mapping.items():

            @with_plugins(mock_entry_points_from_group(group))
            @click.group()
            def group():
                """test_load_EntryPoint"""

            self.assertEqual(expected_keys, tuple(group.commands.keys()))

    @mock.patch("importlib.metadata.entry_points")
    def test_entry_point_group_name(self, patched):

        """Load plugins from an entry points group name."""

        patched.side_effect = mock_entry_points

        for group, expected_keys in self.mapping.items():

            @with_plugins(group)
            @click.group()
            def group():
                """test_load_entry_point_name"""

            self.assertEqual(expected_keys, tuple(group.commands.keys()))


class Tests(unittest.TestCase):

    def setUp(self):

        """Setup plugins and baseline CLI groups."""

        # 'click' test runner.
        self.runner = CliRunner()

        valid_dist = VirtualDistribution(
            valid=True, invalid=False, extra_group=False)
        invalid_dist = VirtualDistribution(
            valid=False, invalid=True, extra_group=False)

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

    @mock.patch('importlib.metadata.entry_points', mock_entry_points)
    def test_registered(self):

        """Ensure the test plugins are properly registered.

        If this test fails something about the overall test setup is not
        correct.
        """

        for group in (
                'click_plugins_tests.valid', 'click_plugins_tests.invalid'):
            eps = mock_entry_points_from_group(group)
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
                    f"ERROR: entry point '{_module(ep)}:{ep.name}' could"
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

    @mock.patch("importlib.metadata.entry_points")
    def test_with_plugins_stacked(self, patched):

        """Multiple ``@with_plugins()``."""

        patched.side_effect = mock_entry_points

        @with_plugins("click_plugins_tests.valid")
        @with_plugins("click_plugins_tests.invalid")
        @click.group()
        def group():
            """test_with_plugins_stacked"""

        self.assertEqual(
            sorted(group.commands.keys()), ['cmd1', 'cmd2', 'no_exist'])


if __name__ == '__main__':
    unittest.main()
