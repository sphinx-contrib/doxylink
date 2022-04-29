#!/bin/bash
# SPDX-FileCopyrightText: © 2022 Matt Williams <matt@milliams.com>
# SPDX-License-Identifier: BSD

set -euo pipefail
IFS=$'\n\t'

version_spec=${1:-}

if [[ -z "${version_spec}" ]]
  then
    echo "This script must be called with an argument of the version number or a \"bump spec\"."
    echo "See \`poetry version --help\`"
    echo "For example, pass in \"patch\", \"minor\" or \"major\" to bump that segment."
    exit 1
fi

if ! git diff-index --quiet HEAD -- pyproject.toml
  then
    echo "There are uncomitted changes to \`pyproject.toml\`."
    echo "Commit or restore them before continuing."
    exit 1
fi

if ! git diff --cached --quiet
  then
    echo "There are uncomitted changes in the staging area."
    echo "Commit or restore them before continuing."
    exit 1
fi

if ! poetry build -q
  then
    echo "Poetry build failed:"
    poetry build
fi

echo "Are you sure you want to release the next ${version_spec} version?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit 1;;
    esac
done

# Bump version in pyproject.toml
poetry version "${version_spec}"
new_version=$(poetry version --short)
git add pyproject.toml

date=$(date --iso-8601)
sed --in-place "s/__version__ = \".*\"/__version__ = \"${new_version}\"/" sphinxcontrib/doxylink/__init__.py
git add sphinxcontrib/doxylink/__init__.py
sed --in-place "s/## \[Unreleased\]/## [Unreleased]\\n\\n## [${new_version}] - ${date}/" CHANGELOG.md
git add CHANGELOG.md

git commit -m "Update to version ${new_version}"
git tag "${new_version}"
git push --atomic --tags origin HEAD
