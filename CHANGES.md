Changelog
=========

1.1.1 - 2019-04-04
------------------

- Fixed a version mismatch in `click_plugins/__init__.py`  See `1.1`.

1.1 - 2019-04-04
----------------

- Fix an issue where a broken command's traceback would not be emitted - https://github.com/click-contrib/click-plugins/issues/25
- Bump required click version to `click>=4` - https://github.com/click-contrib/click-plugins/pull/28
- Runs Travis tests for the latest release of click versions 4 -> 7 - https://github.com/click-contrib/click-plugins/pull/28

1.0.4 - 2018-09-15
------------------

- Preemptive fix for a breaking change in Click v7.  CLI command names generated from functions with underscores will have dashes instead of underscores.  See https://github.com/click-contrib/click-plugins/issues/19.


1.0.3 - 2016-01-05
------------------

- Include tests in MANIFEST.in - See further discussion in #8


1.0.2 - 2015-09-23
------------------

- General packaging and Travis-CI improvements.
- Don't include tests in MANIFEST.in - #8


1.0.1 - 2015-08-20
------------------

- Fixed a typo in an error message - #5


1.0 - 2015-07-20
----------------

- Initial release.
