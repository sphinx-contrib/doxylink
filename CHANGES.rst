()
==

1.7 (Jan 11, 2021)
==================

- Add support for argument packs in C++11 [PR #20]
- Add support for linking to remote tag files [issue #12]
- Add support for multiple tag files with the same name [PR #27]

1.6.1 (Apr 27, 2019)
====================

- Fix for deprecated `app.info()` [PR #23]

1.6 (Jul 22, 2018)
==================

- Add possibility to link to #DEFINE macros.
- Do a better job of parsing compound fundamental types.
- Add support for linking to Doxygen groups [issue #11].
- Rewrite internals to a more structured style.
- Fix error in namespace resolution.

1.5 (Dec 9, 2017)
====================

- Fix #6: convert dict_values to list before indexing [Stein Heselmans]
- fix parsing for C++11 functions with specifiers () final, () override or () = default [Elco Jacobs]

1.4 (Dec 4, 2017)
====================

- Add bug fix from Stein Heselmans to force the qualifier to be a single string
- Remove Python 2 compatibility

1.3 (Sep 13, 2012)
====================

- Add fix from Matthias Tuma from Shark3 to allow friend declarations inside classes.

1.2 (Nov 3, 2011)
====================

- Add Python 3 support

1.1 (Feb 19, 2011)
====================

- Add support for linking directly to struct definitions.
- Allow to link to functions etc. which are in a header/source file but not a member of a class.

1.0 (Dec 14, 2010)
====================

- New Dependency: PyParsing (http://pyparsing.wikispaces.com/)
- Completely new tag file parsing system. Allows for function overloading.
  The parsed results are cached to speed things up.
- Full usage documentation. Build with `sphinx-build -W -b html doc html`.
- Fix problem with mixed slashes when building on Windows.

0.4 (Aug 15, 2010)
====================

- Allow URLs as base paths for the HTML links.
- Don't append parentheses if the user has provided them already in their query.

0.3 (Aug 10, 2010)
====================

- Only parse the tag file once per run. This should increase the speed.
- Automatically add parentheses to functions if the add_function_parentheses config variable is set.

0.2 (Jul 31, 2010)
====================

- When a target cannot be found, make the node an `inline` node so there's no link created.
- No longer require a trailing slash on the `doxylink` config variable HTML link path.
- Allow doxylinks to work correctly when created from a documentation subdirectory.

0.1 (Jul 22, 2010)
==================

- Initial release
