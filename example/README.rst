Plugin Example
==============

A sample package that loads CLI plugins from another package.


Contents
--------

* ``PrintIt`` - The core package.
* ``PrintItStyle`` - An external plugin for ``PrintIt``'s CLI that adds styling options.
* ``PrintItBold`` - A broken plugin that is should add a command to create bold text, but an error in its ``setup.py`` causes it to not work.


Workflow
--------

From this directory, install the main package (the slash is mandatory):

.. code-block:: console

    $ pip install PrintIt/

And run the commandline utility to see the usage:

.. code-block:: console

    $ printit
    Usage: printit [OPTIONS] COMMAND [ARGS]...

      Format and print file contents.

      For example:

          $ cat README.rst | printit lower

    Options:
      --help  Show this message and exit.

    Commands:
      lower  Convert to lower case.
      upper  Convert to upper case.


Try running ``cat README.rst | printit upper`` to convert this file to upper-case.

The ``PrintItStyle`` directory is an external CLI plugin that is compatible with
``printit``.  In this case ``PrintItStyle`` adds styling options to the ``printit``
utility.

Install it (don't forget the slash):

.. code-block:: console

    $ pip install PrintItStyle/

And get the ``printit`` usage again, now with two additional commands:

.. code-block:: console

    $ printit
    Usage: printit [OPTIONS] COMMAND [ARGS]...

      Format and print file contents.

      For example:

          $ cat README.rst | printit lower

    Options:
      --help  Show this message and exit.

    Commands:
      background  Add a background color.
      color       Add color to text.
      lower       Convert to lower case.
      upper       Convert to upper case.


Broken Plugins
--------------

Plugins that trigger an exception on load are flagged in the usage and the full
traceback can be viewed by executing the command.

Install the included broken plugin, which we expect to give us a bold styling option:

.. code-block:: console

    $ pip install BrokenPlugin/

And look at the ``printit`` usage again - notice the icon next to ``bold``:

.. code-block:: console

    $ printit
    Usage: printit [OPTIONS] COMMAND [ARGS]...

      Format and print file contents.

      For example:

          $ cat README.rst | printit lower

    Options:
      --help  Show this message and exit.

    Commands:
      background  Add a background color.
      bold        † Warning: could not load plugin. See `printit bold --help`.
      color       Add color to text.
      lower       Convert to lower case.
      upper       Convert to upper case.

Executing ``printit bold`` reveals the full traceback:

.. code-block:: console

    $ printit bold

    Warning: entry point could not be loaded. Contact its author for help.

    Traceback (most recent call last):
      File "/Users/wursterk/github/click/venv/lib/python3.4/site-packages/pkg_resources/__init__.py", line 2353, in resolve
        return functools.reduce(getattr, self.attrs, module)
    AttributeError: 'module' object has no attribute 'bolddddddddddd'

    During handling of the above exception, another exception occurred:

    Traceback (most recent call last):
      File "/Users/wursterk/github/click/click/decorators.py", line 145, in decorator
        obj.add_command(entry_point.load())
      File "/Users/wursterk/github/click/venv/lib/python3.4/site-packages/pkg_resources/__init__.py", line 2345, in load
        return self.resolve()
      File "/Users/wursterk/github/click/venv/lib/python3.4/site-packages/pkg_resources/__init__.py", line 2355, in resolve
        raise ImportError(str(exc))
    ImportError: 'module' object has no attribute 'bolddddddddddd'

In this case the error is in the broken plugin's ``setup.py``.  Note the typo
in the ``entry_points`` section.

.. code-block:: python

    from setuptools import setup


    setup(
        name='PrintItBold',
        version='0.1dev0',
        packages=['printit_bold'],
        entry_points='''
            [printit.plugins]
            bold=printit_bold.core:bolddddddddddd
        '''
    )
