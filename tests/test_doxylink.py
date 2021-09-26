import datetime
import glob
import os
import os.path
import subprocess
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

import pytest
from testfixtures import LogCapture

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


@pytest.mark.parametrize('symbol, expected_matches', [
    ('my_namespace', {'my_namespace'}),
    ('my_namespace::MyClass', {'my_namespace::MyClass'}),
    ('MyClass', {'my_namespace::MyClass', 'my_namespace::MyClass::MyClass', 'MyClass', 'MyClass::MyClass'}),
    ('my_lib.h::MY_MACRO', {'my_lib.h::MY_MACRO'}),
    ('MY_MACRO', {'my_lib.h::MY_MACRO'}),
    ('my_namespace::MyClass::my_method', {'my_namespace::MyClass::my_method'}),
    ('MyClass::my_method', {'my_namespace::MyClass::my_method'}),
    ('ClassesGroup', {'ClassesGroup'}),
])
def test_find_url_piecewise(examples_tag_file, symbol, expected_matches):
    tag_file = ET.parse(examples_tag_file)
    mapping = doxylink.parse_tag_file(tag_file)

    matches = doxylink.match_piecewise(mapping.keys(), symbol)
    assert expected_matches == matches
    assert matches.issubset(mapping.keys())

@pytest.mark.parametrize('str_to_validate, expected', [
    ('http://example.com', True),
    ('https://example.com/sub', True),
    ('http://1.1.1.1', True),
    ('http://1.1.1.1/sub', True),
    ('http://localhost', True),
    ('ftp://example.com', True),
    ('example', False),
    ('http_dir', False),
    ('http://1.2.3', False),
])
def test_is_url(str_to_validate, expected):
    result = doxylink.is_url(str_to_validate)
    assert result == expected


@pytest.mark.parametrize('values, out_rootdir, out_pdf', [
    (['doxygen/project.tag', 'https://example.com'], 'https://example.com', ''),
    (['doxygen/project.tag', 'https://example.com', ''], 'https://example.com', ''),
    (['doxygen/project.tag', 'doxygen.pdf'], '', 'doxygen.pdf'),
    (['doxygen/project.tag', 'https://example.com', 'doxygen.pdf'], 'https://example.com', 'doxygen.pdf'),
])
def test_extract_configuration_pass(values, out_rootdir, out_pdf):
    tag_filename, rootdir, pdf_filename = doxylink.extract_configuration(values)
    assert rootdir == out_rootdir
    assert pdf_filename == out_pdf


@pytest.mark.parametrize('values', [
    (['doxygen/project.tag']),
    (['doxygen/project.tag', 'https://example.com', 'doxygen.pdf', 'fail']),
])
def test_extract_configuration_fail(values):
    with pytest.raises(ValueError):
        doxylink.extract_configuration(values)


@pytest.mark.parametrize('tag_filename, rootdir, pdf_filename, builder', [
    ('doxygen/project.tag', 'https://example.com', '', 'html'),
    ('doxygen/project.tag', '', 'doxygen.pdf', 'latex'),
    ('doxygen/project.tag', 'html/doxygen', 'doxygen.pdf', 'latex'),
])
def test_process_configuration_pass(tag_filename, rootdir, pdf_filename, builder):
    app = MagicMock()
    app.builder.format = builder
    with LogCapture() as l:
        doxylink.process_configuration(app, tag_filename, rootdir, pdf_filename)
    l.check()


@pytest.mark.parametrize('rootdir, pdf_filename, builder, msg', [
    ('', 'doxygen.pdf', 'html',
     "Linking from HTML to Doxygen pdf ('doxygen.pdf') is not supported. "
     "Consider setting the root directory of Doxygen's HTML output as value instead."),
    ('https://example.com', '', 'latex',
     "Linking from PDF to remote Doxygen html is not supported yet; got 'https://example.com'."
     "Consider linking to a Doxygen pdf file instead as third element of the tuple in the `doxylink` config variable."),
    ('html/doxygen', '', 'latex',
     "Linking from PDF to local Doxygen html is not possible; got 'html/doxygen'."
     "Consider linking to a Doxygen pdf file instead as third element of the tuple in the `doxylink` config variable."),
])
def test_process_configuration_warn(rootdir, pdf_filename, builder, msg):
    app = MagicMock()
    app.builder.format = builder
    with LogCapture() as l:
        doxylink.process_configuration(app, 'doxygen/project.tag', rootdir, pdf_filename)
    l.check(('sphinx.sphinxcontrib.doxylink.doxylink', 'WARNING', msg))
