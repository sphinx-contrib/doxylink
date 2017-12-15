import datetime
import glob
import io
import os
import os.path
import re
import subprocess
import xml.etree.ElementTree as ET

import pytest
from sphinx.testing.path import path

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


@pytest.fixture
def asw(examples_tag_file):
    """Return a Sphinx app, a status buffer and a warnings buffer"""
    from sphinx.testing.util import SphinxTestApp
    rootdir = path(os.path.dirname(__file__) or '.').abspath()
    example_dir = rootdir / '../examples'
    status, warning = io.StringIO(), io.StringIO()
    confoverrides = {
        'html_theme': 'basic',
        'html_theme_options': {'nosidebar': True},
    }
    this_app = SphinxTestApp('html', example_dir, status=status, warning=warning, confoverrides=confoverrides)
    return this_app, status, warning


def test_sphinx_build(asw):
    app, status, warning = asw
    app.build()
    html = (app.outdir / 'index.html').text()
    print(html)
    assert '<a class="reference external" href="https://example.com/classmy__namespace_1_1MyClass.html">my_namespace::MyClass</a></p>' in html


@pytest.mark.parametrize('input_text, expect_text, expect_uri', [
    (':my_lib:`my_func`', 'my_func()', 'my__lib_8h.html'),
    (':my_lib:`my func <my_func>`', 'my func', 'my__lib_8h.html'),
])
def test_role_function(asw, input_text, expect_text, expect_uri):
    app, status, warning = asw

    match = re.match(r':(\w+):`(.+)`', input_text)

    role_name = match.group(1)
    text = match.group(2)

    finder = doxylink.create_role(app, app.config.doxylink[role_name][0], app.config.doxylink[role_name][1])

    [o], _ = finder(role_name, input_text, text, 1, inliner=None)

    assert len(o.children) == 1, 'The output node should have exactly one child Text node'
    out_text = o.children[0].astext()
    out_refuri = o.attributes['refuri']

    assert out_text == expect_text
    assert out_refuri.startswith(app.config.doxylink[role_name][1]+expect_uri)


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
