#########
Changelog
#########

2.0 - TBD
=========

Final release. Repository now serves as a reference implementation, and
contains a file that users may vendor in order to use ``click-plugins``.

* Convert ``click_plugins/`` to a single ``click_plugins.py`` file. Users may
  copy this file into their project to use ``click-plugins``.
* Drop Travis-CI and optionally use `Tox <https://tox.wiki>`_ for a full test
  matrix. This project is winding down and no longer needs a CI system.

1.1.1.2 - 2025-06-24
====================

- Add a clear note stating that the package is no longer maintained, but the library can be vendored.

1.1.1.1 - 2025-06-24
====================

- Mark the project as inactive.

1.1.1 - 2019-04-04
==================

* Fixed a version mismatch in ``click_plugins/__init__.py``. See ``1.1``.

1.1 - 2019-04-04
================

* `#25 <https://github.com/click-contrib/click-plugins/issues/25>`_ - Fix an
  issue where a broken command's traceback would not be emitted.
* `#28 <https://github.com/click-contrib/click-plugins/pull/28>`_ - Bump
  required click version to ``click>=4``.
* `#28 <https://github.com/click-contrib/click-plugins/pull/28>`_ - Runs Travis
  tests for the latest release of ``click`` versions ``>=4,<8``
  (approximately).

1.0.4 - 2018-09-15
==================

* `#9 <https://github.com/click-contrib/click-plugins/issues/19>`_ - Preemptive
  fix for a breaking change in ``click`` v7. CLI command names generated from
  functions with underscores will have dashes instead of underscores.


1.0.3 - 2016-01-05
==================

* Include tests in ``MANIFEST.in``. See further discussion in
  `#8 <https://github.com/click-contrib/click-plugins/pull/8>`_.


1.0.2 - 2015-09-23
------------------

* General packaging and Travis-CI improvements.
* `#8 <https://github.com/click-contrib/click-plugins/pull/8>`_ - Don't
  include tests in ``MANIFEST.in``


1.0.1 - 2015-08-20
==================

* `#5 <https://github.com/click-contrib/click-plugins/pull/5>`_ - Fixed a typo
  in an error message.


1.0 - 2015-07-20
================

- Initial release.
