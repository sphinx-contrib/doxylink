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
        if latest_file_changed > tagfile_changed:
            recreate = True
        else:
            recreate = False

    if recreate:
        subprocess.call('doxygen', cwd=basedir)

    return tagfile


def test_parse_tag_file(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    from pprint import pprint
    pprint(mapping)

    assert 'my_lib.h' in mapping
    assert 'my_lib.h::my_func' in mapping
    assert '()' in mapping['my_lib.h::my_func']['arglist']
    assert len(mapping['my_lib.h::my_func']['arglist']) == 5
    assert 'my_namespace' in mapping
    assert 'my_namespace::MyClass' in mapping
    assert 'my_lib.h::MY_MACRO' in mapping
    assert 'ClassesGroup' in mapping


def test_find_url_piecewise(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    assert 'my_namespace' in doxylink.find_url_piecewise(mapping, 'my_namespace')
    assert 'my_namespace::MyClass' in doxylink.find_url_piecewise(mapping, 'my_namespace::MyClass')
    assert 'my_namespace::MyClass' in doxylink.find_url_piecewise(mapping, 'MyClass')
    assert 'MyClass' in doxylink.find_url_piecewise(mapping, 'MyClass')

    assert len(doxylink.find_url_piecewise(mapping, 'MyClass')) == 2

    assert 'my_lib.h::MY_MACRO' in doxylink.find_url_piecewise(mapping, 'my_lib.h::MY_MACRO')
    assert 'my_lib.h::MY_MACRO' in doxylink.find_url_piecewise(mapping, 'MY_MACRO')

    assert 'ClassesGroup' in doxylink.find_url_piecewise(mapping, 'ClassesGroup')


def test_return_from_mapping(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    mapping_entry = mapping['my_lib.h::my_func']
    assert doxylink.return_from_mapping(mapping_entry)
    assert doxylink.return_from_mapping(mapping_entry, '()')
    assert doxylink.return_from_mapping(mapping_entry, '(int)')
    assert doxylink.return_from_mapping(mapping_entry, '(float)')
    with pytest.raises(LookupError):
        print(doxylink.return_from_mapping(mapping_entry, '(double)'))


def test_find_url2(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    assert doxylink.find_url2(mapping, 'MyClass')['file'] == 'classMyClass.html'
