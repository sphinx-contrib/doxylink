Welcome to sphinxcontrib-doxylink's documentation
=================================================

Doxylink is a Sphinx extension to link to external Doxygen API documentation.

It allows you to specify C++ symbols and it will convert them into links to the HTML page of their Doxygen documentation.

.. toctree::
    :hidden:

    api

Usage
-----

You use Doxylink like:

.. code-block:: rst

    :polyvox:`PolyVox::Volume`
    You use :qtogre:`QtOgre::Log` to log events for the user.
    :polyvox:`PolyVox::Array::operator[]`

Where :rst:role:`polyvox` and :rst:role:`qtogre` roles are defined by the :confval:`doxylink` configuration value.

Like any interpreted text role in Sphinx, if you want to display different text to what you searched for, you can include some angle brackets ``<...>``.
In this case, the text inside the angle brackets will be used to match up with Doxygen and the part in front will be displayed to the user:

.. code-block:: rst

    :polyvox:`Array <PolyVox::Array>`.
    :polyvox:`tidyUpMemory <tidyUpMemory(int)>` will reduce memory usage.

.. note::
    In C++, it is common that classes and functions will be templated and so will have angle brackets themselves.
    For example, the C++ class:

    .. code-block:: c++

        PolyVox::Array<0,ElementType>

    would be naively linked to with Doxylink with:

    .. code-block:: rst

        :polyvox:`PolyVox::Array<0,ElementType>`

    but that would result in Sphinx parsing it as you wanting to search for ``0,ElementType`` and display ``PolyVox::Array`` as the text to the user.
    To avoid this misparsing you must escape the opening ``<`` by prepending it with a ``\``:

    .. code-block:: rst

        :polyvox:`PolyVox::Array\<0,ElementType>`

    If you want to use templated symbols inside the angle brackets like:

    .. code-block:: rst

        :polyvox:`Array <PolyVox::Array<0,ElementType>>`

    then that will work without having to escape anything.

Namespaces, classes etc.
^^^^^^^^^^^^^^^^^^^^^^^^

For non-functions (i.e. namespaces, classes, enums, variables) you simply pass in the name of the symbol.
If you pass in a partial symbol, e.g. ```Volume``` when you have a symbol in C++ called ``PolyVox::Utils::Volume`` then it would be able to match it as long as there is no ambiguity (e.g. with another symbol called ``PolyVox::Old::Volume``).
If there is ambiguity then simply enter the fully qualified name like:

.. code-block:: rst

    :polyvox:`PolyVox::Utils::Volume` or :polyvox:`PolyVox::Utils::Volume <Volume>`

Functions
^^^^^^^^^

For functions there is more to be considered due to C++'s ability to overload a function with multiple signatures.
If you want to link to a function and either that function is not overloaded or you don't care which version of it you link to, you can simply give the name of the function with no parentheses:

.. code-block:: rst

    :polyvox:`PolyVox::Volume::getVoxelAt`

Depending on whether you have set the :confval:`add_function_parentheses` configuration value, Doxylink will automatically add on parentheses to that it will be printed as ``PolyVox::Volume::getVoxelAt()``.

If you want to link to a specific version of the function, you must provide the correct signature.
For a requested signature to match on in the tag file, it must exactly match a number of features:

- The types must be correct, including all qualifiers, e.g. ``unsigned const int``
- You must include any pointer or reference labeling, e.g. ``char*``, ``const QString &`` or ``int **``
- You must include whether the function is const, e.g. ``getx() const``

The argument list is not whitespace sensitive (any more than C++ is anyway) and the names of the arguments and their default values are ignored so the following are all considered equivalent:

.. code-block:: rst

    :myapi:`foo( const QString & text, bool recalc, bool redraw = true )`
    :myapi:`foo(const QString &foo, bool recalc, bool redraw = true )`
    :myapi:`foo( const QString& text, bool recalc, bool redraw )`
    :myapi:`foo(const QString&,bool,bool)`

When making a match, Doxylink splits up the requested string into the function symbol and the argument list.
If it finds a match for the function symbol part but not for the argument list then it will return a link to any one of the function versions.

Files
^^^^^

You can also link directly to a header or source file by giving the name of the file:

.. code-block:: rst

    :myapi:`main.cpp`
    :myapi:`MainWindow.h`

Setup
-----

When generating your Doxygen documentation, you need to instruct it to create a 'tag' file.
This is an XML file which contains the mapping between symbols and HTML files.
To make Doxygen create this file ensure that you have a line like:

.. code-block:: ini

    GENERATE_TAGFILE = PolyVox.tag

in your ``Doxyfile``.

Configuration values
--------------------

.. confval:: doxylink

    The environment is set up with a dictionary that maps the interpreted text role, which must be lower-case,
    to a tuple with at most three elements, of which the third is optional:

    - The path to the Doxygen tag file, which can be:

      - absolute,
      - relative to the location where `sphinx-build` is executed,
      - a URL so that the file will be downloaded first.

    - The path to the root of HTML documentation, which can be:

      - absolute
      - relative to `Sphinx' output directory`_.

    - The filename of a Doxygen pdf file, to be used when Sphinx uses the LaTeX builder.
      Otherwise, the second element of the tuple will be used to link to.

    .. code-block:: python

        doxylink = {
            'polyvox' : ('/home/matt/PolyVox.tag', '/home/matt/PolyVox/html/', 'polyvox_doxygen.pdf'),
            'qtogre' : ('/home/matt/QtOgre.tag', '/home/matt/QtOgre/html/', 'qtogre_doxygen.pdf'),
        }

    .. note::

        The links in your pdf document to your Doxygen pdf file(s) may not work (properly) in a browser or a basic
        PDF-reader. They should work in Adobe Reader for example.

.. _`Sphinx' output directory`: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.outdir

.. confval:: add_function_parentheses

    A boolean that decides whether parentheses are appended to function and method role text. Default is ``True``.

.. confval:: doxylink_pdf_files

    Doxylink can be configured to download remote Doxygen pdf files or copy them from a local location.
    You should use the output file name as the third
    element of the value of the ``doxylink`` dictionary **and** as key in the ``doxylink_pdf_files`` dictionary,
    which should contain the URL to the remote location or local location as value.
    If the pdf file already exists locally in Sphinx' output directory, it will not be downloaded or overwritten.

    .. code-block:: python

        doxylink_pdf_files = {
            'polyvox_doxygen.pdf': url_to_remote_doxygen_pdf,
            'qtogre_doxygen.pdf': '/home/matt/qtogre/doxygen.pdf',
        }

.. confval:: doxylink_parse_error_ignore_regexes

    A list of regular expressions that can be used to ignore specific errors reported from the parser.
    Default is ``[]``. This is useful if you have a lot of errors that you know are not important.
    For example, you may want to ignore errors related to a specific namespace.
    The regular expression is matched against the error message using Python's
    `re.search <https://docs.python.org/3/library/re.html#re.search>`_ function.

Bug reports
-----------

If you find any errors, bugs, crashes etc. then please raise an issue `on GitHub <https://github.com/sphinx-contrib/doxylink/issues/new>`_.
If there is a crash please include the backtrace and log returned by Sphinx.
If you have a bug, particularly with Doxylink not being able to parse a function, please send the tag file so tat I can reproduce and fix it.

:requires: Python 3.4

.. todo::

    Parallelise the calls to normalise() in parse_tag_file() using multiprocessing.
    Set up a pool of processes and pass in a queue of strings.
    Non-function calls will be done in the same way as present.
    For function calls, build up the information into a list of tuples, convert it into an appropriate Queue format and run it.
    Maybe even a multiprocessing.Pool.map could do the job.

:copyright: Copyright 2022 by Matt Williams
:license: BSD, see LICENSE for details.
