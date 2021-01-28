Release checklist
=================

- Update version number in `sphinxcontrib/doxylink/__init__.py`.
- Update date in CHANGES.rst and make sure new features and bug fixes are mentioned.
- Commit sources with updated version numbers `git commit`.
- Tag new version `git tag 1.1` (or whatever the version is).
- Travis CI will upload new version to PyPI (alternatively use `python setup.py sdist upload`).
