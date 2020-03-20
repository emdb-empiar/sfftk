``sfftk.readers`` package
-------------------------

.. note::

    - Each module in this package implements an *ad hoc* reader for a particular file type. The naming convention is ``<ext>reader``, where ``<ext>`` is a short and unique description for that file format, typically (but not exclusively) the file extension for the file format e.g. ``am`` for AmiraMesh hence ``amreader`` module. By *ad hoc* we mean that the module is designed to conform to the data model of the file format. The :py:mod:`formats` package adapts the *ad hocness* to that of EMDB-SFF data model.
    - Each module should implement at top-level function `get_data` that takes a string filename and ``*args``, ``**kwargs`` and returns an object representing a segmentation from the relevant file format.


AmiraMesh reader
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.amreader
    :members:
    :show-inheritance:

SuRVoS reader
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.survosreader
    :members:
    :show-inheritance:

CCP4 mask reader
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.mapreader
    :members:
    :show-inheritance:

IMOD reader
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.modreader
    :members:
    :show-inheritance:

Segger reader
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.segreader
    :members:
    :show-inheritance:

Stereolithography
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.stlreader
    :members:
    :show-inheritance:

Amira HyperSurface reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: sfftk.readers.surfreader
    :members:
    :show-inheritance:
