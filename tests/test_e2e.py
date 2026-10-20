from html.parser import HTMLParser
from pathlib import Path
import pytest
import shutil
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple

# These tests run a real Doxygen, so skip them where it isn't installed.
pytestmark = pytest.mark.skipif(shutil.which("doxygen") is None, reason="doxygen is not installed")

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

/// Function-like macro.
#define FUNCTION_LIKE_MACRO_1(x)

/// Function-like macro.
#define FUNCTION_LIKE_MACRO_2(x, y);

/// Variadic macro.
#define VARIADIC_FUNCTION_LIKE_MACRO_1(...)

/// Variadic macro.
#define VARIADIC_FUNCTION_LIKE_MACRO_2(x, ...)

/// Macro with a keyword as its parameter.
#define MACRO_WITH_KEYWORD_PARAM(enum)
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
    ("secondary", "AmbiguousFunction"),
    ("secondary", "ambiguous_var"),
    (None, "SIMPLE_MACRO"),
    (None, "FUNCTION_LIKE_MACRO_1"),
    (None, "FUNCTION_LIKE_MACRO_2"),
    (None, "VARIADIC_FUNCTION_LIKE_MACRO_1"),
    (None, "VARIADIC_FUNCTION_LIKE_MACRO_2"),
    (None, "MACRO_WITH_KEYWORD_PARAM"),
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


class _LinkCollector(HTMLParser):
    """Collects the (href, text) of every Doxylink link in a page."""

    def __init__(self) -> None:
        super().__init__()
        self.links: List[Tuple[str, str]] = []
        self._current: Optional[List[str]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "a":
            attributes = dict(attrs)
            if "doxylink" in (attributes.get("class") or "").split():
                self._current = [attributes.get("href") or "", ""]

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current[1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            self.links.append((self._current[0], self._current[1]))
            self._current = None


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
    result = run_sphinx(docs_dir, build_dir / "html")

    # An unresolved symbol is only a warning and is rendered as plain text
    assert "Could not find match" not in result.stderr, result.stderr

    # Verify generated HTML
    index_html = build_dir / "html" / "index.html"
    collector = _LinkCollector()
    collector.feed(index_html.read_text(encoding="utf-8"))

    # The text of a link is the symbol as written, plus "()" for functions. It has to match exactly: a link to
    # "primary::TestClass::method()" must not count as a link to "primary::TestClass".
    for ns, name in _CXX_NAMES:
        qualified_name = f"{ns}::{name}" if ns else name
        hrefs = [href for href, text in collector.links if text in (qualified_name, f"{qualified_name}()")]
        assert hrefs, f"Could not find link for symbol '{qualified_name}'"
        assert all("doxygen_out/html/" in href for href in hrefs), hrefs
