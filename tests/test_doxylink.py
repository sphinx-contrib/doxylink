import datetime
import glob
import os
import os.path
import subprocess
import xml.etree.ElementTree as ET

import pytest

from sphinxcontrib.doxylink import doxylink


@pytest.fixture
def examples_tag_file():
    basedir = os.path.join(os.path.dirname(__file__), '../examples')
    extensions = None
    tagfile = None
    with open(os.path.join(basedir, 'Doxyfile')) as doxyfile:
        for line in doxyfile:
            if line.startswith('FILE_PATTERNS'):
                extensions = line.split('=')[1].strip().split(',')
            elif line.startswith('GENERATE_TAGFILE'):
                tagfile_name = line.split('=')[1].strip()
                tagfile = os.path.join(basedir, tagfile_name)
    if None in [extensions, tagfile]:
        raise RuntimeError('Could not find FILE_PATTERNS or GENERATE_TAGFILE in Doxyfile')
    matches = []
    for extension in extensions:
        m = glob.glob(os.path.join(basedir, extension))
        matches.extend(m)

    if not os.path.isfile(tagfile):
        recreate = True
    else:
        latest_file_changed = max([datetime.datetime.fromtimestamp(os.stat(f).st_mtime) for f in matches])
        tagfile_changed = datetime.datetime.fromtimestamp(os.stat(tagfile).st_mtime)
        print(latest_file_changed)
        print(tagfile_changed)
        if latest_file_changed > tagfile_changed:
            recreate = True
        else:
            recreate = False

    if recreate:
        subprocess.call('doxygen', cwd=basedir)

    return tagfile


def test_function_present(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)
    assert 'my_lib.h' in mapping
    assert 'my_lib.h::my_func' in mapping
    assert '()' in mapping['my_lib.h::my_func']['arglist']
