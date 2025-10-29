..
    This file is part of 'click-plugins' version 2.0: https://github.com/click-contrib/click-plugins


``click-plugins``
=================

Load `click <https://click.palletsprojects.com/>`_ commands from
`entry points <https://docs.python.org/3/library/importlib.metadata.html#entry-points>`_.
Allows a click-based command line interface to load commands from external
packages.

.. contents:: Table of Contents
    :depth: 2


What is a plugin?
-----------------

A plugin is similar to installing and importing a Python package, except the
code conforms to a specific protocol, and is loaded through other means.


Why would I want a plugin?
--------------------------

Library developers providing a command line interface can load plugins to
extend its features by allowing other developers to register additional
commands or groups. This allows for an extensible command line, and a natural
home for commands that aren't a great fit for the primary CLI, but belong in
the broader ecosystem. For example, a plugin might provide a more advanced set
of features, but require additional dependencies.


I am a developer wanting to support plugins on my CLI
-----------------------------------------------------

A `click-plugins <https://pypi.org/project/click-plugins/>`_ package exists on
the Python Package Index. This is an older version that is no longer supported
and will not be updated. Instead, developers should vendor
``click_plugins.py``, and consider vendoring ``click_plugins_tests.py``, and
``click_plugins.rst``. Alternatively, developers are free to use this project
as a reference for their own implementation, or make modifications in
accordance with the license.

Some considerations for vendoring are speed, and packaging. Entrypoints are
known to be slow to load, and some alternative approaches exist at the cost of
additional dependencies, or assumptions about what happens when a plugin fails
to load. Vendoring ``click-plugins`` might include changing the entry point
loading mechanism to one that is more appropriate for your use. Python
packaging can be quite complicated in some cases, and vendoring may require
adjustments for your specific packaging setup.

In order to support loading plugins, developers must document where their
library is looking for entry points. Exactly how to do this varies based on
packaging tooling, but it is supported by `setuptools <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_.
A project may offer several entry points allowing plugins to choose where they
are registered in the CLI. Including the package name in the entrypoint is
good, so an example might look like ``package.plugins`` or
``package.subcommand.plugins``. If ``click-plugins`` offered plugins, it might
want to register them at ``click_plugins.plugins``.

This entry point should be associated with a ``click.Group()`` where the
plugins will live:

.. code-block:: python

    from click
    from click_plugins import with_plugins

    @with_plugins('example.entry.point')
    @click.group('External plugins')
    def group():
        ...


``click_plugins.with_plugins()`` has a docstring describing alternate
invocations.

Some developers use ``click-plugins`` as an easy way to assemble the CLI for
their project in addition to supporting plugins. This approach does work, but
can cause CLI startup to be slow. Developers taking this approach might
consider entry point for the primary CLI, and one for plugins.

Packages offering plugins of the same name will experience collisions.

Support
~~~~~~~

Offering a home for plugins comes with a certain amount of support. The primary
CLI author is likely to sometimes receive bug reports or feature requests for
plugins that are not part of the core project. ``click-plugins`` attempts to
gracefully handle plugins that fail to load, and nudges the user towards the
plugin author, but the plugin origin may at times not be clear. Consider that
your users are primarily interacting with your CLI, but may be experiencing
problems with a plugin, or even a bad interaction between plugins. It may be
worth including a brief description about this in your documentation to help
users report issues to the correct location.


I am a plugin author
--------------------

Register your ``click.Command()`` or ``click.Group()`` as an
`entry point <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_.
The exact mechanism depends on your packaging choices, but for a
``pyproject.toml`` with ``setuptools`` as a backend, it looks like:

.. code-block:: toml

    [tool.setuptools.dynamic]
    entry-points =
        name = library.submodule:object

If ``click_plugins`` had a ``plugins.py`` submodule, it might contain a
plugin structured as the ``click.Command()`` below:

.. code-block:: python

    import click

    @click.command('uppercase')
    def uppercase():
        """Echo stdin in uppercase."""
        with click.get_text_stream('stdin') as f:
            for line in f:
                click.echo(f.upper())

This would be attached to an entry point like:

.. code-block:: toml

    [tool.setuptools.dynamic]
    entry-points =
        bold = click_plugins.plugins:bold


License
-------

New BSD License

Copyright (c) 2015-2025, Kevin D. Wurster, Sean C. Gillies
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
