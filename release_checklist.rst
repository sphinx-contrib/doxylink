Release checklist
=================

- Update version number in `doc/conf.py` and `setup.py`.
- Update date in CHANGES.rst and make sure new features and bug fixes are mentioned.
- Commit sources with updated version numbers `git commit`.
- Tag new version `git tag 1.1` (or whatever the version is).
- Upload new version to PyPI `python setup.py sdist upload`
