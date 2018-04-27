===============
Extending sfftk
===============

.. contents::

Adding A Segmentation File Format
=================================

There are four (4) steps involved.

-  Create a reader

-  Create a format adapter

-  Add test data

-  Write unit tests

Step I: Create a reader
-----------------------

Write a reader module and place it in sfftk.readers package. The reader module may implement a single class that
provides a simple API to segmentation files. There is not predefined structure on how to handle reading the file.
However, the reader module must implement a `get_data(fn, *args, **kwargs)` function that takes the name of a file as a
string. The name of the module should be the extension followed by the word ‘reader’ e.g. for Segger files it is segreader.py.

Step II: Create a format adapter
--------------------------------

Write a format module and place it in the sfftk.formats package. This module adapts the reader in Step II to the schema
(EMDB-SFF data model) API. The name of the module must be simply the extension of the file format e.g. for Segger files
it is seg.py. The module uses the inherited segmentation parts from the classes defined in sfftk.formats.base module
and have names indicating the segmentation format e.g. for Segger seg.py has a SeggerSegmentation class that inherits
from the generic Segmentation class which provides a way to hook functionality required of all custom segmentation
representations. This module will then tie the segmentation file format API defined in readers with the schema
(EMDB-SFF data model) API.

Step III: Add test data
-----------------------

Provide an example segmentation file in the sfftk.test_data package.

Step IV: Write tests
--------------------

Write unit tests and add them to the sfftk.unittests.test_formats module. Each format that you add should implement a
read and convert test method (respectively called test_<format>_read and test_<format>_convert. See the
``sfftk.unittests.test_formats`` module for examples.

Once all this components are in place conversion to XML, HDF5 and JSON should be automatic.

.. code:: bash

    sff convert file.<format> -f sff
    sff convert file.<format> -f hff
    sff convert file.<format> -f json

Also, tests can be run as follows:

.. code:: bash

    sff tests formats
    sff test formats


Adding A Search Resource
=================================

The list of search resources is extensible. Any new search results must fulfil the following criteria:

*   Have a A REST API;

*   Return the result as either JSON or TAB-delimitted text;

Step I: Add the resource description
------------------------------------------------------------------------------------------------

The resource descriptions are contained in :py:mod:`sfftk.notes.__init__.py`. For example, the one for
`OLS <https://www.ebi.ac.uk/ols>`_ is:

.. code-block:: python

    RESOURCE_LIST['ols'] = {
        'name': 'OLS',
        'root_url': 'https://www.ebi.ac.uk/ols/api/',
        'format': 'json',
        'result_path': ['response', 'docs'],
        'result_count': ['response', 'numFound'],
    }

``RESOURCE_LIST`` is a dictionary whose primary key is the lower-case abbreviation of the resource name (``ols`` here).
Each resource's description is a dictionary of:

*   ``name`` - proper abbreviation of the resource's name (``UniProt`` not ``Uniprot``);

*   ``root_url`` - the part of the REST API which is invariant i.e. excluding search parameters;

*   ``format`` - either ``json`` or ``tab``;

*   ``result_path`` - the part of the response data that contains a list of results. In the above example,
    ``response``, ``docs`` are a path to a list element of the JSON where all results are found. If ``format`` is
    ``tab`` set this to ``None``.

*   ``result_count`` - the part of the response data that contains the count of the complete results. Usually only a
    page of all results is returned but it is useful to inform the user of how many results were found. If this is not
    present set it to ``None``.

Step II: Add a handler to return the correct URL
---------------------------------------------------------------------------------------------------------

Modify the :py:class:`sfftk.notes.find.SearchResults.get_url()` method by adding a conditional handler for
the resource that returns the complete search URL (i.e. including the search term and additional options allowed on the
REST API).

The ``if`` statement uses the resource name to identify the resource.

For example, the URL for OLS is generated as follows:

.. code-block:: python

        # ols
        if self.name == 'OLS':
            url = self.root_url + "search?q={}&start={}&rows={}".format(
                self.search_args.search_term,
                self.search_args.start - 1,
                self.search_args.rows,
            )
            if self.search_args.ontology:
                url += "&ontology={}".format(self.search_args.ontology)
            if self.search_args.exact:
                url += "&exact=on"
            if self.search_args.obsoletes:
                url += "&obsoletes=on"

Each of the subsequent ``if`` statements conditionally include additional parameters specified in the command-line
arguments.

Step III: Define how the table is formated
----------------------------------------------------------------------------------------------------------

The :py:meth:`sfftk.notes.find.SearchResource.tabulate()` specifies how to tabulate results from each resource. We use
two classes: :py:class:`sfftk.notes.find.TableField` and :py:class:`sfftk.notes.find.ResultsTable` to do this. Here is
an example for OLS:

.. code-block:: python

        if self._resource.name == 'OLS':
            fields = [
                TableField('index', key='index', pc=5, is_index=True, justify='right'),
                TableField('label', key='label', pc=10),
                TableField('short_form', key='short_form', pc=10, justify='center'),
                TableField('resource', key='ontology_name', pc=5, justify='center'),
                TableField('description', key='description', pc=40, is_iterable=True),
                TableField('iri', key='iri', pc=30),
            ]
            table = ResultsTable(self, fields=fields)

You will need to refer to the resource's REST API documentation to match result fields with table fields.

:py:class:`sfftk.notes.find.TableField` accepts the following arguments:

*   The first (positional) argument is the name of the field and appears in the table header;

*   ``key`` is the official name of the field in the REST API; the :py:class:`sfftk.notes.find.TableField` uses the key
    to extract the row values;

*   Instead of using the ``key`` argument, the user may use ``text`` which will be a fixed value for all rows;

*   ``pc`` is the field width in *percent*; alternatively, use the ``width`` argument to specify how many characters
    wide the field should be;

*   ``is_index`` sets the field to be an index field i.e. to show the row number;

*   ``justify`` can either be ``right``, ``left`` or ``center`` and specifies the field text alignment;

*   ``_format`` specifies a *format string* (a string with with ``{}`` which will replace ``{}`` with the field value.
    This is helpful when creating URLs/IRIs to an accession page e.g.

    .. code-block:: python

         TableField('iri', key='EntryID', _format='https://www.ebi.ac.uk/pdbe/emdb/EMD-{}', pc=30),

    for an EMDB entry page.

Step IV: Write tests and test
------------------------------------------------------------------------------------------------

You will then need to write at least two tests sfin the ``sfftk.unittests.test_notes.TestNotesFindSearchResource`` class:

*   *parser* tests that check that the command-line arguments are correct (see the module for other examples);

*   *get_url* tests that ensure that the URL is correctly formed for all options;

Step IV: Write documentation for the new resource
------------------------------------------------------------------------------------------------

Finally, document the resource in the section :ref:`specifying-the-resource-to-search` by describing the following:

*   the *name* and *link to* the resource in the list of resources;

*   the *keyword* to be passed to the ``-R/--resource`` flag;
