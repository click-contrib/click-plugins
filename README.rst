click-plugins
=============

A method for registering plugins on command line interfaces built with
`click`_.


History
-------

This project was originally distributed as the `click-plugins <https://pypi.org/project/click-plugins/>`_
package via the Python Package Index. That package still exists, but will not
be updated. Instead, users should vendor files from this repository in order
to use ``click-plugins``. See `click_plugins.rst`_ for more
information.

This project is no longer actively maintained, but has been structured for
maximum longevity. It has no dependencies aside from `click`_, and does not
offer any mechanism for building a package. Users are free to vendor, and
modify as needed in accordance with the license. Users are also free to build
their own package.

Users may want to treat this project as a reference for their own
implementation.


Vendoring
~~~~~~~~~

Users interested in vendoring ``click-plugins`` should consider adding the
files listed below to their project.

* `click_plugins.py`_ - Core library file. Required.
* `click_plugins_tests.py`_ - Tests for `click_plugins.py`. Not required, but
  can be integrated into an application's test suite.
* `click_plugins.rst`_ - Documentation for `click_plugins.py`_. Not required,
  but can be integrated into a project's documentation.
* `click_plugins.html`_ - An HTML versin of `click_plugins.rst`_. The version
  in this repository is manually generated, and may be out of sync with
  `click_plugins.rst`_. It is included for convenience for users who cannot
  easily render reStructuredText as HTML.

Users are responsible for any adjustments required to satisfy their project's
typing, linting, and code style requirements.


Testing
~~~~~~~

Tests are built and executed using Python's builtin `unittest <https://docs.python.org/3/library/unittest.html>`_
library.

.. code-block::

    $ python -m unittest click_plugins_tests.py

`tox <https://tox.wiki>`_ (see `tox.ini <tox.ini>`_) can be used to test
multiple versions of Python and `click`_. The goal is to support as many
versions of Python and `click`_ as reasonably possible, including versions
that are potentially no longer
officially supported by Python Software Foundation or the `click`_ maintainers.
Versions that have reached end of life and and are difficult to support may be
dropped.


Documentation
~~~~~~~~~~~~~

This project uses `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_,
but users who do not support this markup language will not be able to process
`click_plugins.rst`_ when building documentation. Most
users can probably support a HTML file, which can be rendered with:

.. code-block:: console

    $ docutils click_plugins.rst click_plugins.html


Release
~~~~~~~

* Consider bumping the version in `click_plugins.py <click_plugins.py>`_ based
  on the magnitude of the change.
* Build and check in a new version of the documentation.
* Update `CHANGES.rst <CHANGES.rst>`_.


.. _click: https://palletsprojects.com/projects/click/
.. _click_plugins.py: click_plugins.py
.. _click_plugins_tests.py: click_plugins_tests.py
.. _click_plugins.rst: click_plugins.rst
.. _click_plugins.html: click_plugins.html
