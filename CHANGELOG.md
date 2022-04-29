<!---
SPDX-FileCopyrightText: © 2022 Matt Williams <matt@milliams.com>
SPDX-License-Identifier: BSD
-->

# Changelog

## [Unreleased]

## [1.11.2] - 2022-04-28
### Fixed
- Add support for sphinx parallel read/write [PR #37]

## [1.11.1] - 2021-11-15
### Fixed
- Only link to Doxygen's PDF output when Sphinx uses the latex format [PR #36]

## [1.11] - 2021-09-22
### Added
- Add feature to download remote and copy local pdf files [PR #35]

## [1.10] - 2021-09-10
### Fixed
- Fix links to files in Doxygen's PDF output [PR #34]

## [1.9] - 2021-09-02
### Added
- Add support for linking to Doxygen's PDF output [PR #32]

## [1.8] - 2021-01-28
### Added
- Add support for pages in addition to files [PR #25]
- Add volatile as qualifier [PR #26]

## [1.7] - 2021-01-11
### Added
- Add support for argument packs in C++11 [PR #20]
- Add support for linking to remote tag files [issue #12]
- Add support for multiple tag files with the same name [PR #27]

## [1.6.1] - 2019-04-27
### Fixed
- Fix for deprecated `app.info()` [PR #23]

## [1.6] - 2018-07-22
### Added
- Add support for linking to Doxygen groups [issue #11].
- Add possibility to link to #DEFINE macros.
### Fixed
- Do a better job of parsing compound fundamental types.
- Rewrite internals to a more structured style.
- Fix error in namespace resolution.

## [1.5] - 2017-12-09
### Fixed
- Fix #6: convert dict_values to list before indexing [Stein Heselmans]
- fix parsing for C++11 functions with specifiers () final, () override or () = default [Elco Jacobs]

## [1.4] - 2017-12-04
### Removed
- Remove Python 2 compatibility
### Fix
- Add bug fix from Stein Heselmans to force the qualifier to be a single string

## [1.3] - 2012-09-13
### Fixed
- Add fix from Matthias Tuma from Shark3 to allow friend declarations inside classes.

## [1.2] - 2011-11-03
### Added
- Add Python 3 support

## [1.1] - 2011-02-19
### Added
- Add support for linking directly to struct definitions.
- Allow to link to functions etc. which are in a header/source file but not a member of a class.

## [1.0] - 2010-12-14
### Added
- New Dependency: PyParsing (http://pyparsing.wikispaces.com/)
- Completely new tag file parsing system. Allows for function overloading.
  The parsed results are cached to speed things up.
- Full usage documentation. Build with `sphinx-build -W -b html doc html`.
### Fixed
- Fix problem with mixed slashes when building on Windows.

## [0.4] - 2010-08-15
### Added
- Allow URLs as base paths for the HTML links.
### Fixed
- Don't append parentheses if the user has provided them already in their query.

## [0.3] - 2010-08-10
### Added
- Only parse the tag file once per run. This should increase the speed.
- Automatically add parentheses to functions if the `add_function_parentheses` config variable is set.

## [0.2] - 2010-07-31
### Added
- When a target cannot be found, make the node an `inline` node so there's no link created.
### Fixed
- No longer require a trailing slash on the `doxylink` config variable HTML link path.
- Allow doxylinks to work correctly when created from a documentation subdirectory.

## [0.1] - 2010-07-22
### Added
- Initial release
