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

