"""
sfftk.readers package

Key points
----------

- Each module in this package implements an ad hoc reader for a particular file type. The naming convention is
<ext>reader, where <ext> is a unique extension used by the file. e.g. `am` for AmiraMesh hence `amreader` module.
By ad hoc we mean that the module will be designed in a way most suitable to the file format and should not conform
to some predefined class structure. The formats package is intended to flatten out the ad hocness from this package
by forcing all reader into a predefined class structure.
- Each module should implement at top-level function `get_data` that takes a string filename and ``*args``,
``**kwargs``.
"""
