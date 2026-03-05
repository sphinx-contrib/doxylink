import os
from pathlib import Path
import pytest
import subprocess
import sys
import re
from typing import Iterable

_CXX_SOURCE = """
namespace primary {

/// Test function.
void TestFunction();

/// Function that appears in two namespaces.
void AmbiguousFunction();

/// Global variable.
extern int global_var;

/// Ambiguous variable.
extern int ambiguous_var;

/// Test class.
class TestClass {
public:
  /// Method.
  void method();
};

/// Test struct.
struct TestStruct {
  /// Member.
  int member;
};

/// Test class template.
template <typename T>
class TestTemplate {
public:
  /// Test template method.
  void init();
};

/// Test function template.
template <typename T>
void FunctionTemplate(T param);

/// Variable template.
template <class T>
constexpr T variable_template = T(3.14);

}  // namespace primary

namespace secondary {

/// Function with the same name in a different namespace.
void AmbiguousFunction();

/// Ambiguous variable in a different namespace.
extern int ambiguous_var;

}  // namespace secondary

/// Simple macro.
#define SIMPLE_MACRO 42

/// A function-like macro.
#define FUNCTION_LIKE_MACRO(int x, int y);


"""

_CXX_NAMES = (
    ("primary", "TestFunction"),
    ("primary", "AmbiguousFunction"),
    ("primary", "global_var"),
    ("primary", "TestClass"),
    ("primary::TestClass", "method"),
    ("primary", "TestStruct"),
    ("primary::TestStruct", "member"),
    ("primary", "TestTemplate"),
    ("primary::TestTemplate", "init"),
    ("primary", "FunctionTemplate"),
    ("primary", "variable_template"),
    ("primary", "ambiguous_var"),
    ("secondary", "TestFunction"),
    ("secondary", "ambiguous_var"),
    (None, "SIMPLE_MACRO"),
    (None, "FUNCTION_LIKE_MACRO"),
)

# Assert that all names above are present in _CXX_SOURCE
assert all(name in _CXX_SOURCE for _, name in _CXX_NAMES)


@pytest.fixture
def doxylink_setup(tmp_path: Path) -> Path:
    """Sets up a Sphinx project with Doxygen output for Doxylink tests."""
    # Set up directories
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    src_dir = project_dir / "src"
    src_dir.mkdir()

    docs_dir = project_dir / "docs"
    docs_dir.mkdir()

    # Create C++ source file
    header_file = src_dir / "test.h"
    header_file.write_text(_CXX_SOURCE, encoding="utf-8")

    # Create Doxyfile
    doxyfile = docs_dir / "Doxyfile"
    doxyfile.write_text(
        f"""
PROJECT_NAME = "Test Project"
OUTPUT_DIRECTORY = {docs_dir / "doxygen_out"}
GENERATE_TAGFILE = {docs_dir / "test.tag"}
GENERATE_XML = YES
GENERATE_HTML = YES
INPUT = {src_dir}
QUIET = YES
EXTRACT_ALL = YES
""",
        encoding="utf-8",
    )

    # Run Doxygen
    subprocess.check_call(["doxygen", str(doxyfile)], cwd=docs_dir)

    # Verify tag file exists
    tag_file = docs_dir / "test.tag"
    assert tag_file.exists()
    tag_content = tag_file.read_text(encoding="utf-8")
    for ns, name in _CXX_NAMES:
        assert name in tag_content, f"Tag file does not contain '{name}': {tag_content}"

    # Create Sphinx conf.py
    conf_py = docs_dir / "conf.py"
    # We point 'html' to the doxygen html output relative to the sphinx output
    # Since sphinx output will be in docs_dir/_build/html, and doxygen is in docs_dir/doxygen_out/html
    # The relative path from _build/html to doxygen_out/html is ../../doxygen_out/html
    conf_py.write_text(
        f"""
extensions = ['sphinxcontrib.doxylink']
doxylink = {{
    'test': ('{tag_file.resolve()}', '../../doxygen_out/html'),
}}
master_doc = 'index'
""",
        encoding="utf-8",
    )

    return docs_dir


def run_sphinx(
    docs_dir: Path,
    out_dir: Path,
    extra_args: Iterable[str] = (),
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Runs Sphinx and returns the result."""
    cmd = [sys.executable, "-m", "sphinx", "-b", "html", *extra_args, ".", str(out_dir)]
    return subprocess.run(
        cmd, cwd=docs_dir, capture_output=True, text=True, check=check
    )


def test_doxylink_valid_links(doxylink_setup: Path) -> None:
    """Tests that valid Doxylink links are generated."""
    docs_dir = doxylink_setup

    # Create index.rst
    index_rst = docs_dir / "index.rst"
    rst_lines = [
        "Test Document",
        "=============",
        "",
    ]
    for ns, name in _CXX_NAMES:
        qualified_name = f"{ns}::{name}" if ns else name
        rst_lines.append(f"Link to {name}: :test:`{qualified_name}`")

    index_rst.write_text("\n".join(rst_lines) + "\n", encoding="utf-8")

    # Run Sphinx
    build_dir = docs_dir / "_build"
    run_sphinx(docs_dir, build_dir / "html")

    # Verify generated HTML
    index_html = build_dir / "html" / "index.html"
    content = index_html.read_text(encoding="utf-8")

    # Helper to verify link exists
    def verify_link(text: str, symbol: str) -> None:
        # Look for <a ... href="...doxygen_out/html/..." ...>...symbol...</a>
        pattern = rf'<a\s+[^>]*href="[^"]*doxygen_out/html/[^"]*"[^>]*>.*?{re.escape(symbol)}.*?</a>'
        assert re.search(
            pattern, text, re.DOTALL
        ), f"Could not find link for symbol '{symbol}'"

    for ns, name in _CXX_NAMES:
        verify_link(content, name)
