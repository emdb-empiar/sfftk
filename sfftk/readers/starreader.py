"""
``sfftk.readers.starreader``
=============================

STAR files are generic data modelling files much in the same way as XML files. RELION uses a particular format of STAR file to store particle data. This module provides several classes to read STAR files: a generic reader and two RELION-specific ones.

In practice, the whole STAR file is loaded into memory during the parsing process. The API we provide enables the user to access the main ways the data is stored in the STAR file: *key-value pairs* and *tables*. This reader is designed only to extract the data from the STAR file and does not attempt to understand STAR file conventions.

Generic STAR files can have any number of key-value pairs and tables. For our use case, we are interested in capturing the relationship between a refined particle (subtomogram average) and a source tomogram. Since each such particle is expressed in terms of its orientation within the tomogram, we need to capture the affine transform that maps the particle to the tomogram.

Therefore, this imposes some constraints on the STAR file:
- The STAR file must have a table with the following columns: ``_rlnCoordinateX``, ``_rlnCoordinateY``, ``_rlnCoordinateZ``, ``_rlnAngleRot``, ``_rlnAngleTilt``, ``_rlnAnglePsi``. These columns represent the position and orientation of the particle in the tomogram.
- The STAR file must reference only one tomogram in the ``_rlnImageName`` column. This is because we are only interested in the relationship between a single particle and a single tomogram. If the STAR file references multiple tomograms, then a prior preparation step will need to be performed to partition the STAR file into multiple files, each referencing a single tomogram. (more on that to come)

For this reason, we distinguish between 'composite' RELION STAR files and 'simple' RELION STAR files. Composite RELION STAR files must be partitioned into simple RELION STAR files before they can be converted into EMDB-SFF files.

Anatomy of a STAR file
----------------------
A STAR file is made up of one or more data blocks.

.. code-block: none

    data_block_1

In the example above, the name of the data block is ``block_1``. The name is optional.

Data is stored in the form of key-value pairs and tables. Key-value pairs are simple and are stored in a dictionary.

.. code-block:: none

    _key value

Tables are designed by the ``loop_`` keyword followed by a sequence of tags/labels each of which is prefixed by an underscore. Each row after the tags/labels is then a row with values for each tag/label.

.. code-block:: none

    loop_
    _atom_site.group_PDB
    _atom_site.id
    _atom_site.type_symbol
    _atom_site.label_atom_id
    _atom_site.label_alt_id
    _atom_site.label_comp_id
    _atom_site.label_asym_id
    _atom_site.label_entity_id
    _atom_site.label_seq_id
    _atom_site.pdbx_PDB_ins_code
    _atom_site.Cartn_x
    _atom_site.Cartn_y
    _atom_site.Cartn_z
    _atom_site.occupancy
    _atom_site.B_iso_or_equiv
    _atom_site.pdbx_formal_charge
    _atom_site.auth_seq_id
    _atom_site.auth_comp_id
    _atom_site.auth_asym_id
    _atom_site.auth_atom_id
    _atom_site.pdbx_PDB_model_num
    ATOM   1    N N   . LYS A 1 7   ? 12.364  -13.639 8.445   1.00 54.67  ? 527 LYS A N   1
    ATOM   2    C CA  . LYS A 1 7   ? 11.119  -12.888 8.550   1.00 49.59  ? 527 LYS A CA  1
    ATOM   3    C C   . LYS A 1 7   ? 9.961   -13.651 7.926   1.00 44.77  ? 527 LYS A C   1
    ATOM   4    O O   . LYS A 1 7   ? 9.055   -14.126 8.617   1.00 49.39  ? 527 LYS A O   1
    ATOM   5    C CB  . LYS A 1 7   ? 11.255  -11.538 7.841   1.00 49.41  ? 527 LYS A CB  1
    ATOM   6    C CG  . LYS A 1 7   ? 10.169  -10.531 8.174   1.00 53.16  ? 527 LYS A CG  1
    ATOM   7    C CD  . LYS A 1 7   ? 10.523  -9.771  9.432   1.00 59.71  ? 527 LYS A CD  1
    ATOM   8    C CE  . LYS A 1 7   ? 11.779  -8.947  9.195   1.00 63.60  ? 527 LYS A CE  1
    ATOM   9    N NZ  . LYS A 1 7   ? 12.353  -8.381  10.443  1.00 64.85  ? 527 LYS A NZ  1
    ATOM   10   N N   . ARG A 1 8   ? 10.011  -13.762 6.603   1.00 40.03  ? 528 ARG A N   1

All values are treated as strings.

RELION STAR files
-----------------
These adhere to the following conventions (https://relion.readthedocs.io/en/latest/Reference/Conventions.html#star-format):
- Euler angle convention used is ZYZ
- The coordinate system is right-handed with positive rotations being anticlockwise/counterclockwise
- ``_rlnCoordinateX``, ``_rlnCoordinateY``, ``_rlnCoordinateZ`` are tomogram PIXEL positions
- ``_rlnAngleRot``, ``_rlnAngleTilt``, ``_rlnAnglePsi`` are angles in DEGREES
    - The first rotation is called ``rlnAngleRot`` and is around the Z-axis;
    - The second rotation is called ``rlnAngleTilt`` and is around the new Y-axis;
    - The third rotation is called ``rlnAnglePsi`` and is around the new Z axis;
- If present ``_rlnOriginXAngstrom`` and ``_rlnOriginYAngstrom`` are in ANGSTROMS

API
---
There are two main classes to read STAR files.

#. :py:class:`sfftk.readers.starreader.StarReader`: a generic reader that can parse any STAR file;
#. :py:class:`sfftk.readers.starreader.RelionStarReader`: a reader that can parse RELION STAR files, which validates the constraints described above.

Both readers provide the same API. The examples below use the generic reader but the same applies to the RELION reader.

First, users must instantiate the reader:

.. code-block:: python

    star_reader = StarReader()

Then, users must parse the file:

.. code-block:: python

    star_reader.parse('file.star')

The reader will then parse the file and store the data in memory. The user can then access the data in the following ways:

#. ``star_reader.keys()``: returns a list of key-value pairs;

    .. code-block:: python

        print(star_reader.keys) # show key-value pairs
        print(star_reader.keys['key']) # get the value for the given key

#. ``star_reader.tables``: returns a dictionary of tables where the key is the name of the table and the value is a ``sfftk.readers.starreader.StarTable`` object. By default, we automatically infer the type of the values in the table. If the user wishes to disable this behaviour, they can pass ``infer_types=False`` to the ``parse`` method.

    .. code-block:: python

        print(star_reader.tables) # print the list of tables
        print(star_reader.tables['_atom_site'] # the name of a table is name of the label prefix (separated by a period)
        print(star_reader.tables['_atom_site'].columns) # print the columns in the table
        print(star_reader.tables['_atom_site'][0]) # print the first row in the table
        print(star_reader.tables['_atom_site'][0][4]) # print the fifth column in the first row

    .. note:: RELION STAR files

        For RELION STAR files, the name of the table is ``_rln``.

        .. code-block:: python

            print(star_reader.tables['_rln'])

        Additionally, each row can be converted into an affine transform matrix using the ``to_affine_transform`` method:

        .. code-block:: python

            print(star_reader.tables['_rln'][0].to_affine_transform()) # print the affine transform matrix for the first row
            print(star_reader.tables['_rln'][0].to_affine_transform(axes="ZXZ")) # change the orientation convention
            print(star_reader.tables['_rln'][0].to_affine_transform(degrees=False)) # use radians instead of degrees

"""

import re
import sys

import numpy as np
from gemmi import cif
from scipy.spatial.transform import Rotation

FLOAT_RE1 = r"^[+-]?\d*[.]\d*([eE][+-]?\d+)?$"
FLOAT_RE2 = r"^[+-]?\d+[.]\d*([eE][+-]?\d+)?$"
FLOAT_RE3 = r"^[+-]?\d*[.]\d+([eE][+-]?\d+)?$"
INT_RE = r"^[+-]?\d+$"


def compute_affine_transform(x, y, z, rot, tilt, psi, axes='ZYZ', degrees=True):
    """Compute the affine transform matrix for the given parameters"""
    translation = np.array([x, y, z]).reshape(3, 1)  # 3x1
    print(translation)
    # compute the affine transform matrix
    rotation_matrix = Rotation.from_euler(axes, [rot, tilt, psi], degrees=degrees).as_matrix()
    affine_matrix = np.append(rotation_matrix, translation, axis=1)
    return affine_matrix


def _get_data(fn, *args, **kwargs):
    """Get data from file"""
    doc = cif.read_file(fn)
    block = doc.sole_block()
    print(block, f"name: {block.name}")
    # print(dir(block))
    # print(block.find_loop("_rlnCoordinateX"))
    for item in block:
        print(f"item: {item.loop}")
        for index in range(item.loop.length()):
            print(
                f"x={item.loop.val(index, 2)}; y={item.loop.val(index, 3)}; z={item.loop.val(index, 4)}; rot={item.loop.val(index, 5)}; tilt={item.loop.val(index, 6)}; psi={item.loop.val(index, 7)}")
            print(type(item.loop.val(index, 2)))
            print(
                f"affine matrix:\n{compute_affine_transform(item.loop.val(index, 2), item.loop.val(index, 3), item.loop.val(index, 4), item.loop.val(index, 5), item.loop.val(index, 6), item.loop.val(index, 7))}")
    return doc


def main():
    # fn = "/Users/pkorir/Downloads/80S_Ribosomes_particlesfrom_tomomanstopgapwarpmrm_bin1.star"
    fn = "/Users/pkorir/PycharmProjects/sfftk/sfftk/test_data/segmentations/test_data2.star"
    doc = _get_data(fn)
    print(doc)
    return 0


class StarTableRow:
    """Each row in a star table"""

    def __init__(self, name, loop, values, axes='ZYZ', degrees=True):
        """Initialise the row

        :param str name: the name of the table
        :param cif.Loop loop: the loop object
        :param tuple values: the values in the row
        :param str axes: the axes of rotation
        :param bool degrees: whether the angles are in degrees or radians
        """
        # make sure axes are in upper case
        axes = axes.upper()
        # assertions
        assert isinstance(loop, cif.Loop), "loop must be a cif.Loop object"
        assert 1 <= len(axes) <= 3, "axes must be a string of length 1, 2 or 3"
        assert set('XYZ').issuperset(axes), "axes must be a string of X, Y and/or Z"
        self._name = name
        self._loop = loop
        self._row_data = values
        self._axes = axes
        self._degrees = degrees
        self._fixed_tags = tuple(map(lambda x: x.replace(name, ''), loop.tags))
        self._tagged_values = tuple(zip(self._fixed_tags, values))
        for tag, value in self._tagged_values:
            setattr(self, tag, value)

    def to_affine_transform(self, axes='ZYZ', degrees=True):
        axes = axes.upper()
        assert 1 <= len(axes) <= 3, "axes must be a string of length 1, 2 or 3"
        assert set('XYZ').issuperset(axes), "axes must be a string of X, Y and/or Z"
        if self._name != '_rln':
            raise ValueError(f"Invalid table type: {self.name}; only works on RELION tables")
        x = self.CoordinateX
        y = self.CoordinateY
        z = self.CoordinateZ
        rot = self.AngleRot
        tilt = self.AngleTilt
        psi = self.AnglePsi
        translation = np.array([x, y, z]).reshape(3, 1)  # 3x1
        # compute the affine transform matrix
        if axes != self._axes:
            axes = axes
        else:
            axes = self._axes
        if degrees != self._degrees:
            _degrees = degrees
        else:
            _degrees = self._degrees
        rotation_matrix = Rotation.from_euler(
            axes, [rot, tilt, psi], degrees=_degrees
        ).as_matrix()
        affine_matrix = np.append(rotation_matrix, translation, axis=1)
        return affine_matrix

    def __str__(self):
        """Return a representation of the row"""
        return f"<StarTableRow: {self._tagged_values}>"

    def __repr__(self):
        """Return a representation of the row"""
        return f"StarTableRow(name='{self._name}', loop={self._loop}, *args={self._row_data}>"


class StarTable:
    """A section of tabular data in a star file"""

    def __init__(self, loop, name, infer_types=True, *args, **kwargs):
        self._loop = loop
        self.name = name
        self._infer_types = infer_types
        self._data = list()
        for index in range(0, loop.length() * loop.width(), loop.width()):
            values = self._loop.values[index:index + loop.width()]
            if self._infer_types:
                values = tuple(map(self._infer_float, values))
                values = tuple(map(self._infer_int, values))
            self._data.append(
                StarTableRow(name, loop, values, *args, **kwargs)
            )

    @staticmethod
    def _infer_float(value):
        """Infer the type of the value"""
        try:
            if re.match(FLOAT_RE1, value) and (re.match(FLOAT_RE2, value) or re.match(FLOAT_RE3, value)):
                return float(value)
            return value
        except TypeError:
            return value

    @staticmethod
    def _infer_int(value):
        """Infer the type of the value"""
        try:
            if re.match(INT_RE, value):
                return int(value)
            return value
        except TypeError:
            return value

    @property
    def columns(self):
        """Return the columns in this block"""
        return self._loop.tags

    def __getitem__(self, item):
        """Get rows by index upto length - 1"""
        if isinstance(item, int) or isinstance(item, slice):
            return self._data[item]
        raise TypeError(f"Invalid index type: {type(item)}")

    def __len__(self):
        """Return the number of rows"""
        return self._loop.length()

    def __iter__(self):
        """Iterate over the rows"""
        yield from self._data

    def __str__(self):
        """Return a representation of the table"""
        string = f"<StarTable: {self.name}> with {len(self)} rows and {len(self.columns)} columns"
        string += f"\nColumns:\n"
        for column in self.columns:
            string += f"\t* {column}\n"
        return string


class StarReader:
    """A generic star file reader. The user must specify which fields are required/optional and the reader will then
    assess whether a provided file has the specified field.

    Once the file is parsed, the user can then iterate over the object to get the required data.

    .. code-block:: python

        reader = StarReader()
        reader.parse('my_star_file.star')
        print(reader) # output some information e.g. number of rows, fields, etc.
        print(reader.keys())
        print(reader.tables)
        print(reader.tables['default'])
        print(reader.tables['default'].columns)
        print(reader.tables['name']) # if 'name' exists
        # if no warnings are raised then the file was successfully parsed
        for row in reader.tables: # read from the 'default' table or the only table present
            # do something with the row
            # we drop the leading underscore so as not to imply private variables
            print(row.col1, row.col2, row.col3, row.col4, row.col5, row.col6)

    """

    def __init__(self):
        self._fn = None
        self._doc = None
        self._keys = dict()
        self._tables = dict()

    def parse(self, fn, infer_types=True):
        """Parse the file"""
        self._fn = fn
        self._doc = cif.read_file(str(fn))
        block = self._doc.sole_block()
        for item in block:
            try:  # assume it's a loop; if not it's a pair
                obj = item.loop
                name = self._infer_name(obj)
                # print(f"{name}: {obj.values}")
                if name not in self._tables:
                    self._tables[name] = StarTable(obj, name, infer_types=infer_types)
                else:
                    raise ValueError(f"Duplicate table name: {name}")
                # print(f"item: {obj}; {obj.tags}; {type(item)}")
            except AttributeError:
                obj = item.pair
                if obj is None:
                    continue
                name, value = obj
                # print(f"name: {name}; value: {value}")
                if not self._keys.get(name):
                    self._keys[name] = value
                else:
                    raise ValueError(f"Duplicate key: {name}")
                # print(f"item: {obj}; {type(item)}")

    @staticmethod
    def _infer_name(obj):
        """Infer the name of the table"""
        if obj.tags:
            if obj.tags[0].split('.')[0] == obj.tags[1].split('.')[0]:
                return obj.tags[0].split('.')[0]
            elif obj.tags[0].split('.')[0].startswith('_rln'):
                return '_rln'
        return 'default'

    def keys(self):
        """Return all the keys found in the STAR file"""
        return list(self._keys.keys())

    @property
    def tables(self):
        """Return all the tables in the STAR file"""
        return self._tables

    def __str__(self):
        """Return some information about the file"""
        pass


# class RelionStarReader(StarReader):
#     """Reads a Relion star file and returns a list of affine transform matrices
#
#     .. code-block:: python
#
#         reader = RelionStarReader()
#         reader.parse('my_star_file.star')
#         print(reader) # output some information e.g. number of rows, fields, etc.
#         # if no warnings are raised then the file was successfully parsed
#         for row in reader:
#             # do something with the row
#             # we drop the leading underscore so as not to imply private variables
#             print(row.rlnCoordinateX, row.rlnCoordinateY, row.rlnCoordinateZ, row.rlnAngleRot, row.rlnAngleTilt, row.rlnAnglePsi)
#     """
#     required_fields = [
#         ('_rlnCoordinateX', float),
#         ('_rlnCoordinateY', float),
#         ('_rlnCoordinateZ', float),
#         ('_rlnAngleRot', float),
#         ('_rlnAngleTilt', float),
#         ('_rlnAnglePsi', float),
#         ('_rlnImageName', str),
#         ('_rlnPixelSize', float)
#     ]
#     optional_fields = [
#         ('_rlnOriginXAngstrom', float),
#         ('_rlnOriginYAngstrom', float),
#     ]


def get_data(fn, *args, **kwargs):
    """Return the object with all the required metadata"""
    # todo: implement a way to detect the star dialect
    """
    star_class = detect_required_star_factory(fn)
    star_reader = star_class()
    star_reader.parse(fn)
    """
    relion_star_reader = RelionStarReader()
    relion_star_reader.parse(fn)
    return relion_star_reader


if __name__ == '__main__':
    sys.exit(main())
