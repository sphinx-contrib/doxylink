import xml.etree.ElementTree as ET
from sphinxcontrib.doxylink import doxylink

TEMPLATE_CLASS_WITH_SELF_FRIEND = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<tagfile doxygen_version="1.9.4">
  <compound kind="file">
    <name>base_string.h</name>
    <path>/workspaces/test</path>
    <filename>base__string_8h.html</filename>
    <class kind="class">container::BaseString</class>
    <namespace>container</namespace>
  </compound>
  <compound kind="class">
    <name>container::BaseString</name>
    <filename>classcontainer_1_1_base_string.html</filename>
    <templarg>class T</templarg>
    <templarg>std::size_t N</templarg>
    <member kind="function">
      <type></type>
      <name>BaseString</name>
      <anchorfile>classcontainer_1_1_base_string.html</anchorfile>
      <anchor>e452ce3dc0c4848d8fb5f441311185dc1</anchor>
      <arglist>()</arglist>
    </member>
    <member kind="friend" protection="private">
      <type>friend class</type>
      <name>BaseString</name>
      <anchorfile>classcontainer_1_1_base_string.html</anchorfile>
      <anchor>4f2bed5eca1588cf30324f67c13ca7990</anchor>
      <arglist></arglist>
    </member>
  </compound>
  <compound kind="namespace">
    <name>container</name>
    <filename>namespacecontainer.html</filename>
    <class kind="class">container::BaseString</class>
  </compound>
</tagfile>
"""

def test_doxylink_wont_crash_on_self_friend_template_classes():
    tag_file = ET.ElementTree(ET.fromstring(TEMPLATE_CLASS_WITH_SELF_FRIEND))
    try:
        doxylink.SymbolMap(tag_file)
    except RuntimeError as exc:
        assert False, f"template class with self friend definition raises a Runtime Error: {exc}"


# ``canonicalise_separators()`` maps ``::`` and ``.`` to the same string. That means a
# namespace/member symbol such as ``my_lib::h`` canonicalises to the exact same string
# as a *file* literally named ``my_lib.h`` (both become ``my_lib.h``). This is a known,
# accepted tradeoff (see the docstring of ``canonicalise_separators``): it is an
# admittedly narrow, pre-existing kind of ambiguity that mirrors Doxygen's own reference
# resolution (Doxygen itself treats ``.`` and ``::`` interchangeably), and it only
# arises when a project has a namespace/member combination whose canonicalised name
# collides with a file's name.
#
# This test doesn't assert *which* of the two ambiguous entries wins -- that is
# unspecified and depends on their order in the tag file -- but it pins down that
# a lookup deterministically resolves to *one* of them rather than raising or behaving
# erratically, and it documents the collision for future readers/maintainers.
FILE_NAME_COLLIDES_WITH_MEMBER = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<tagfile>
    <compound kind="file">
        <name>my_lib.h</name>
        <filename>my__lib_8h.html</filename>
    </compound>
    <compound kind="namespace">
        <name>my_lib</name>
        <filename>namespacemy__lib.html</filename>
        <member kind="variable">
            <name>h</name>
            <anchorfile>namespacemy__lib.html</anchorfile>
            <anchor>abc</anchor>
        </member>
    </compound>
</tagfile>
"""


def test_file_name_collides_with_canonicalised_member():
    tag_file = ET.ElementTree(ET.fromstring(FILE_NAME_COLLIDES_WITH_MEMBER))
    mapping = doxylink.SymbolMap(tag_file)

    # Both spellings canonicalise to the same string ('my_lib.h') and so must
    # resolve to the same (single) entry -- whichever it happens to be.
    by_dot = mapping['my_lib.h']
    by_scope = mapping['my_lib::h']
    assert by_dot == by_scope
    assert by_dot.kind in ('file', 'variable')

