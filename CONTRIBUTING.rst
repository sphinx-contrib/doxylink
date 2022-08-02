Contributing to doxylink
========================

Making releases
---------------

Releases are managed by GitHub Actions.
There is an action called `Release <https://github.com/sphinx-contrib/doxylink/actions/workflows/release.yml>`_ which can be manually triggered.
On that page, you can select "Run workflow" and set the type of release, either "patch", "minor" or "major".
We conform to SemVer so if there have only been bug fixes, use "patch", and if there have been new features use "minor".
