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


@pytest.mark.parametrize('symbol, file', [
    ('my_func', 'my__lib_8h.html'),
    ('my_func()', 'my__lib_8h.html'),
    ('my_namespace::my_func', 'namespacemy__namespace.html'),
    ('my_lib.h', 'my__lib_8h.html'),
    ('my_lib.h::my_func', 'my__lib_8h.html'),
    ('my_namespace', 'namespacemy__namespace.html'),
    ('my_namespace::MyClass', 'classmy__namespace_1_1MyClass.html'),
    ('my_lib.h::MY_MACRO', 'my__lib_8h.html'),
    ('my_namespace::MyClass::my_method', 'classmy__namespace_1_1MyClass.html'),
    ('ClassesGroup', 'group__ClassesGroup.html'),
])
def test_file_html(examples_tag_file, symbol, file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.SymbolMap(tag_file)

    assert mapping[symbol].file.startswith(file)


@pytest.mark.parametrize('symbol1, symbol2', [
    ('my_func', 'my_lib.h::my_func'),
])
def test_file_equivalent(examples_tag_file, symbol1, symbol2):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.SymbolMap(tag_file)

    assert mapping[symbol1].file == mapping[symbol2].file


@pytest.mark.parametrize('symbol1, symbol2', [
    ('my_func', 'my_namespace::my_func'),
    ('my_func()', 'my_func(int)'),
    ('my_func(float)', 'my_func(int)'),
])
def test_file_different(examples_tag_file, symbol1, symbol2):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.SymbolMap(tag_file)

    assert mapping[symbol1].file != mapping[symbol2].file


def test_parse_tag_file(examples_tag_file):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    assert 'my_lib.h' in mapping
    assert 'my_lib.h::my_func' in mapping
    assert 'my_namespace' in mapping
    assert 'my_namespace::MyClass' in mapping
    assert 'my_lib.h::MY_MACRO' in mapping
    assert 'my_namespace::MyClass::my_method' in mapping
    assert 'ClassesGroup' in mapping


@pytest.mark.parametrize('symbol, matches', [
    ('my_namespace', {'my_namespace'}),
    ('my_namespace::MyClass', {'my_namespace::MyClass'}),
    ('MyClass', {'my_namespace::MyClass', 'my_namespace::MyClass::MyClass', 'MyClass', 'MyClass::MyClass'}),
    ('my_lib.h::MY_MACRO', {'my_lib.h::MY_MACRO'}),
    ('MY_MACRO', {'my_lib.h::MY_MACRO'}),
    ('my_namespace::MyClass::my_method', {'my_namespace::MyClass::my_method'}),
    ('MyClass::my_method', {'my_namespace::MyClass::my_method'}),
    ('ClassesGroup', {'ClassesGroup'}),
])
def test_find_url_piecewise(examples_tag_file, symbol, matches):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    assert matches == doxylink.find_url_piecewise(mapping.keys(), symbol)
