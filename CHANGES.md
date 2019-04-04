Changelog
=========

1.0.5 - 2019-04-03
------------------

- Fix an issue where a broken command's traceback would not be emitted - https://github.com/click-contrib/click-plugins/issues/25

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
