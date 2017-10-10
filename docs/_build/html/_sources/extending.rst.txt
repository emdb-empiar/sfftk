===============
Extending sfftk
===============

Adding A Segmentation File Format
=================================

There are four (4) steps involved.

-  Create a reader

-  Create a format adapter

-  Add test data

-  Write unit tests

Step I: Create a reader
-----------------------

Write a reader module and place it in sfftk.readers package. The reader module may implement a single class that provides a simple API to segmentation files. There is not predefined structure on how to handle reading the file. However, the reader module must implement a `get_data(fn, *args, **kwargs)` function that takes the name of a file as a string. The name of the module should be the extension followed by the word ‘reader’ e.g. for Segger files it is segreader.py.

Step II: Create a format adapter
--------------------------------

Write a format module and place it in the sfftk.formats package. This module adapts the reader in Step II to the schema (EMDB-SFF data model) API. The name of the module must be simply the extension of the file format e.g. for Segger files it is seg.py. The module uses the inherited segmentation parts from the classes defined in sfftk.formats.base module and have names indicating the segmentation format e.g. for Segger seg.py has a SeggerSegmentation class that inherits from the generic Segmentation class which provides a way to hook functionality required of all custom segmentation representations. This module will then tie the segmentation file format API defined in readers with the schema (EMDB-SFF data model) API.

Step III: Add test data
-----------------------

Provide an example segmentation file in the sfftk.test_data package.

Step IV: Write tests
--------------------

Write unit tests and add them to the sfftk.unittests.test_formats module. Each format that you add should implement a read and convert test method (respectively called test_<format>_read and test_<format>_convert. See the sfftk.unittests.test_formats module for examples.

Once all this components are in place conversion to XML, HDF5 and JSON should be automatic.

.. code:: bash

    sff convert file.<format> -f sff
    sff convert file.<format> -f hff
    sff convert file.<format> -f json

Also, tests can be run as follows:

.. code:: bash

    sff tests format
    sff test formats
