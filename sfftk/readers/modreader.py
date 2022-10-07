"""
``sfftk.readers.modreader``
===========================

Ad hoc reader for IMOD (`.mod`) files.

`.mod` files are chunk files and loosely follow the Interchange File
Format (IFF). In summary, IFF files consist of a four-byte header
(all caps chunk name e.g. 'IMOD') followed by an integer of
the number of bytes in the chunk. The chunk is then structured
according to the author's design requirements. Not all .mod
chunks follow this convention (e.g. 'OBJT' chunks do not include
the size of the chunk immediately after the chunk ID.

A description of the structure of `.mod` files can be found at
the following URL: https://bio3d.colorado.edu/imod/betaDoc/binspec.html.
This module consists of a set of classes each identified by the respective chunk names. The following patterns are
observed in the design of these classes:

-   The name of the class is the name of the chunk e.g. OBJT class refers to OBJT chunks.

-   All classes have one public method: read(f), which takes a file handle and returns a file handle at the current
    unread position.

-   Some chunks are nested (despite the serial nature of IFF files). Contained chunks are read with public methods
    defined as ``add_<chunk>`` e.g. OBJT objects are containers of CONT objects and therefore have a ``add_cont()``
    method which takes a CONT object as argument. Internally, container objects use (ordered) dictionaries to store
    contained objects.

-   All chunk classes inherit from :py:class:`object` class and have the :py:meth:`object.__repr__()` method
    implemented to print objects of that class.

In addition, there are several useful dictionary constants and functions and classes (flags) that interpret
several fields within chunks.

.. note::

    The order of classes is based on their position in the module. This can be changed if needed.
    The most important classes are :py:class:`.modreader.IMOD`, :py:class:`.modreader.OBJT`,
    :py:class:`.modreader.CONT` and :py:class:`.modreader.MESH`
"""
import os
import struct
import sys

import numpy
from bitarray import bitarray
from sfftkrw.core import _decode, _xrange, _dict_iter_items, _dict_iter_keys, _dict
from sfftkrw.core.print_tools import get_printable_ascii_string

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk'
__date__ = '2015-10-12'
__updated__ = '2018-02-14'

"""
:TODO: unravel VIEW chunk (email from 3dmod authors unclear)
:TODO: list fiels in MESH chunk with -24 markers
:TODO: empty (no field) implementation of OGRP, SKLI and SLAN (class exists but unclear how to nest it)
"""

KEY_WORDS = [
    b'CLIP',
    b'CONT',
    b'COST',
    b'IMAT',
    b'IMOD',
    b'LABL',
    b'MCLP',
    b'MEPA',
    b'MESH',
    b'MEST',
    b'MINX',
    b'MOST',
    b'OBJT',
    b'OBST',
    b'OGRP',
    b'OLBL',
    b'SIZE',
    b'SKLI',
    b'SLAN',
    b'VIEW',
]

# 0 = circle, 1 = none, 2 = square, 3 = triangle, 4 = star
OBJT_SYMBOLS = {
    0: 'circle',
    1: 'none',
    2: 'square',
    3: 'triangle',
    4: 'star',
}

UNITS = _dict({
    - 12: 'pm',
    - 10: 'ångström',
    - 9: 'nm',
    - 6: 'microns',
    - 3: 'mm',
    - 2: 'cm',
    0: 'pixels',
    1: 'm',
    3: 'km',
})

UPPER_ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def angstrom_multiplier(units):
    """
    Determine a multiplier to convert units to angstrom

    .. math::

        1\\textrm{Å} = 10^{-10}\\textrm{m} \\Rightarrow  1\\textrm{m} = 10^{10}\\textrm{Å}

    Consider some generic unit *U* with a power of 10

    .. math::

        1\\textrm{U} = 10^x \\textrm{m} \\Rightarrow 1\\textrm{m} = 10^{-x}\\textrm{U}

    We need a unit factor that relates Å to *U*. Dividing both expressions for :math:`1\\textrm{m}`

    .. math::

        \\begin{aligned}
        1 = \\frac{10^{10}}{10^{-x}} \\textrm{Å per U (Å/U)} = 10^{10 + x} \\textrm{Å/U}
        \\end{aligned}

    To convert *U* to Å we multiply by :math:`10^{10 + x}` Å/U

    Example:
    To convert 3 nm to Å we consider that :math:`x = -9` for nm. So:

    .. math::

        \\begin{align}
        3\\textrm{nm} & = 3\\textrm{nm} \\times 10^{10 + (-9)}\\textrm{Å/nm} \\\\
            & = 3\\textrm{nm} \\times 10^{10 - 9}\\textrm{Å/nm} \\\\
            & = 3\\textrm{nm} \\times 10\\textrm{Å/nm} \\\\
            & = 30\\textrm{Å}
        \\end{align}

    :param int units: the power of ten for the unit e.g. for nm ``units=-9``
    :return: the correct multiplier to convert the given units to angstrom
    :rtype: int
    """
    try:
        assert units in list(_dict_iter_keys(UNITS))
    except AssertionError:
        raise ValueError("invalid units value '{units}'".format(units=units))
    return 10 ** (10 + units)


def find_chunk_length(f):
    """
    Determine the size (in bytes) of the current chunk. Also, return the name of the next chunk.

    Assumes that current position in the file is immediately after the chunk header.

    :param file f: file handle
    :return: the length of the chunk, the next chunk name, the file handle at the next read position
    :rtype: tuple(int, str, file)
    """
    chunk_length = 0
    next_chunk = struct.unpack('>4s', f.read(4))[0]
    while ((next_chunk[0] not in UPPER_ALPHA) or (next_chunk[1] not in UPPER_ALPHA) or (
            next_chunk[2] not in UPPER_ALPHA) or (next_chunk[3] not in UPPER_ALPHA)):
        chunk_length += 1
        f.seek(-3, os.SEEK_CUR)
        next_chunk = struct.unpack('>4s', f.read(4))[0]
    return chunk_length, next_chunk, f


class FLAGS(object):
    """Base class of bit flags"""

    def __init__(self, int_value, num_bytes, endian='little'):
        """Initialiser of ``FLAG`` class

        :param int int_value: the value in base 10
        :param int bytes: the number of bytes to store
        :param str endian: one of `little` or `big`

        Example usage:

        .. code-block:: python

            >>> from sfftk.readers.modreader import FLAGS
            >>> flag = FLAGS(10, 2)
            >>> flag
            0000000000001010
            >>> flag[0]
            False
            >>> flag[1]
            False
            >>> flag[-1]
            False
            >>> flag[-2]
            True
        """
        try:
            assert endian in ['little', 'big']
        except AssertionError:
            raise ValueError("Unknown endianess '%s'" % endian)

        try:
            assert isinstance(int_value, int)
        except AssertionError:
            raise ValueError("Not an int: '%s'" % int_value)

        try:
            assert num_bytes > 0
        except AssertionError:
            raise ValueError("Bytes (%s) should be a positive (>0) integer" % num_bytes)

        self.endian = endian
        self.bytes = num_bytes
        self.bits = self.bytes * 8
        format_string = '{0:0' + str(self.bits) + 'b}'
        try:
            self.bitarray = bitarray(format_string.format(int_value), endian=self.endian)
        except Exception as e:
            raise ValueError(e)

    def __getitem__(self, item):
        return self.bitarray[item]

    def __repr__(self):
        return self.bitarray.to01()


class MODEL_FLAGS(FLAGS):
    """Flags in the MODEL chunk"""

    def __init__(self, *args, **kwargs):
        super(MODEL_FLAGS, self).__init__(*args, **kwargs)


class OBJECT_FLAGS(FLAGS):
    """Flags in the OBJT chunk"""

    def __init__(self, *args, **kwargs):
        super(OBJECT_FLAGS, self).__init__(*args, **kwargs)


class OBJECT_SYM_FLAGS(FLAGS):
    """Additional flags in the OBJT chunk"""

    def __init__(self, *args, **kwargs):
        super(OBJECT_SYM_FLAGS, self).__init__(*args, **kwargs)


class CONTOUR_FLAGS(FLAGS):
    """Flags in the CONT chunk"""

    def __init__(self, *args, **kwargs):
        super(CONTOUR_FLAGS, self).__init__(*args, **kwargs)


class COST_FLAGS(FLAGS):
    """Flags in the COST chunk"""

    def __init__(self, *args, **kwargs):
        super(COST_FLAGS, self).__init__(*args, **kwargs)


class MESH_FLAGS(FLAGS):
    """Flags in the MESH chunk"""

    def __init__(self, *args, **kwargs):
        super(MESH_FLAGS, self).__init__(*args, **kwargs)


class CLIP_FLAGS(FLAGS):
    """Flags in the CLIP chunk"""

    def __init__(self, *args, **kwargs):
        super(CLIP_FLAGS, self).__init__(*args, **kwargs)


class MCLP_FLAGS(FLAGS):
    """Flags in the MCLP chunk"""

    def __init__(self, *args, **kwargs):
        super(MCLP_FLAGS, self).__init__(*args, **kwargs)


class IMAT_FLAGS(FLAGS):
    """
    Flags in the IMAT chunk.
    """

    def __init__(self, *args, **kwargs):
        super(IMAT_FLAGS, self).__init__(*args, **kwargs)


class VIEW_FLAGS(FLAGS):
    """Flags in the VIEW chunk"""

    def __init__(self, *args, **kwargs):
        super(VIEW_FLAGS, self).__init__(*args, **kwargs)


class MEPA_FLAGS(FLAGS):
    """Flags in the MEPA chunk"""

    def __init__(self, *args, **kwargs):
        super(MEPA_FLAGS, self).__init__(*args, **kwargs)


class STORE(object):
    """Generic storage class for models (MOST), objects (OBST), contours (COST), and meshes (MEST)

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f

    def read(self):
        """Read the contents of this chunk"""
        f = self.f
        self.type = struct.unpack('>h', f.read(2))[0]
        self.flags = COST_FLAGS(struct.unpack('>h', f.read(2))[0], 2)
        # bit 1 and 0 (in order)
        if not self.flags[-2] and not self.flags[-1]:  # 0
            self.index = struct.unpack('>i', f.read(4))[0]
        elif not self.flags[-2] and self.flags[-1]:  # 1
            self.index = struct.unpack('>f', f.read(4))[0]
        elif self.flags[-2] and not self.flags[-1]:  # 2
            self.index = struct.unpack('>hh', f.read(4))
        elif self.flags[-2] and self.flags[-1]:  # 3
            self.index = struct.unpack('>bbbb', f.read(4))
        # bit 3 and 2 (in order)
        if not self.flags[-4] and not self.flags[-3]:  # 0
            self.value = struct.unpack('>i', f.read(4))[0]
        elif not self.flags[-4] and self.flags[-3]:  # 1
            self.value = struct.unpack('>f', f.read(4))[0]
        elif self.flags[-4] and not self.flags[-3]:  # 2
            self.value = struct.unpack('>hh', f.read(4))
        elif self.flags[-4] and self.flags[-3]:  # 3
            self.value = struct.unpack('>bbbb', f.read(4))

        return f

    def __repr__(self):
        return "type: %s; flags: %s; index: %s; value: %s\n" % (self.type, self.flags, str(self.index), str(self.value))


class IMOD(object):
    """Class encapsulating the data in an IMOD file

    The top-level of an IMOD file is an IMOD chunk specifying various data members.
    """

    def __init__(self, f):
        self.f = f
        self.isset = False
        self.objts = _dict()
        self.objt_count = 0
        self.current_objt = None
        self.views = _dict()
        self.view_count = 0
        self.mclp = None
        self.minx = None
        self.most = None

    def read(self):
        """Read the IMOD file into an IMOD object

        :FIXME: use zscale to fix sizes
        """
        f = self.f
        self.version = _decode(struct.unpack('>4s', f.read(4))[0], 'utf-8')
        self.name = _decode(get_printable_ascii_string(struct.unpack('>128s', f.read(128))[0]), 'utf-8')
        self.xmax, self.ymax, self.zmax = struct.unpack('>iii', f.read(12))
        self.objsize = struct.unpack('>i', f.read(4))[0]
        self.flags = MODEL_FLAGS(struct.unpack('>I', f.read(4))[0], 4)
        self.drawmode, self.mousemode, self.blacklevel, self.whitelevel = struct.unpack('>iiii', f.read(16))
        self.xoffset, self.yoffset, self.zoffset = struct.unpack('>fff', f.read(12))
        self.xscale, self.yscale, self.zscale = struct.unpack('>fff', f.read(12))
        self.object, self.contour, self.point, self.res, self.thresh = struct.unpack('>iiiii', f.read(20))
        self.pixsize = struct.unpack('>f', f.read(4))[0]
        self.units = struct.unpack('>i', f.read(4))[0]
        self.named_units = UNITS[self.units]
        self.csum = struct.unpack('>i', f.read(4))[0]
        self.alpha, self.beta, self.gamma = struct.unpack('>fff', f.read(12))
        self.isset = True
        return f

    def add_objt(self, objt):
        """Add an OBJT chunk object to this IMOD object"""
        self.objts[self.objt_count] = objt
        self.objt_count += 1
        self.current_objt = self.objts[self.objt_count - 1]

    def add_view(self, view):
        """Add a VIEW chunk object to this IMOD object"""
        self.views[self.view_count] = view
        self.view_count += 1

    @property
    def ijk_to_xyz_transform(self):
        return numpy.array([
            self.pixsize * self.xscale * angstrom_multiplier(self.units), 0., 0., 0.,
            0., self.pixsize * self.yscale * angstrom_multiplier(self.units), 0., 0.,
            0., 0., self.pixsize * self.zscale * angstrom_multiplier(self.units), 0.,
        ]).reshape(3, 4)

    @property
    def x_length(self):
        """The length of X side of the image in angstrom"""
        return self.xmax * self.pixsize * self.xscale * angstrom_multiplier(self.units)

    @property
    def y_length(self):
        """The length of Y side of the image in angstrom"""
        return self.ymax * self.pixsize * self.yscale * angstrom_multiplier(self.units)

    @property
    def z_length(self):
        """The length of Z side of the image in angstrom"""
        return self.zmax * self.pixsize * self.zscale * angstrom_multiplier(self.units)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        string = """\
version:       %s
name:          %s
xmax:          %s
ymax:          %s
zmax:          %s
objsize:       %s
flags:         %s
drawmode:      %s
mousemode:     %s
blacklevel:    %s
whitelevel:    %s
xoffset:       %s
yoffset:       %s
zoffset:       %s
xscale:        %s
yscale:        %s
zscale:        %s
object:        %s
contour:       %s
point:         %s
res:           %s
thresh:        %s
pixsize:       %s
units:         %s (%s)
csum:          %s
alpha:         %s
beta:          %s
gamma:         %s
stored data:
%s""" % (
            self.version, self.name, self.xmax, self.ymax, self.zmax,
            self.objsize, self.flags, self.drawmode, self.mousemode,
            self.blacklevel, self.whitelevel, self.xoffset, self.yoffset,
            self.zoffset, self.xscale, self.yscale, self.zscale, self.object,
            self.contour, self.point, self.res, self.thresh, self.pixsize,
            self.units, self.named_units, self.csum, self.alpha, self.beta, self.gamma, self.most
        )
        return string


class MOST(object):
    """MOST chunk class

    Class encapsulating storage parameters for the top-level :py:class:`sfftk.readers.modreader.IMOD` chunk.

    :param file f: file handle of the IMOD segmentation
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the MOST chunk"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]
        self.store = _dict()
        for i in _xrange(self.bytes // 12):
            store = STORE(f)
            f = store.read()
            self.store[i] = store
        self.isset = True
        return f

    def __repr__(self):
        string = ''
        for i in sorted(self.store.keys()):
            string += self.store[i].__repr__()
        return string


class OBJT(object):
    """OBJT chunk class

    An IMOD file has several :py:class:`sfftk.readers.modreader.OBJT` chunks, each of which contain the data
    either as contours (:py:class:`sfftk.readers.modreader.CONT`) or meshes
    (:py:class:`sfftk.readers.modreader.MESH`). OBJT chunks also contain :py:class:`sfftk.readers.modreader.CLIP`,
    :py:class:`sfftk.readers.modreader.IMAT`, :py:class:`sfftk.readers.modreader.MEPA` and a
    :py:class:`sfftk.readers.modreader.OBST` storage chunk.
    """

    def __init__(self, f):
        self.f = f
        self.isset = False
        self.conts = _dict()
        self.cont_count = 0
        self.current_cont = None
        self.meshes = _dict()
        self.mesh_count = 0
        self.current_mesh = None
        self.clip = None
        self.imat = None
        self.mepa = None
        self.obst = None

    def read(self):
        """Read data from the file to the chunk"""
        f = self.f
        self.name = _decode(get_printable_ascii_string(struct.unpack('>64s', f.read(64))[0]), 'utf-8')
        self.extra = struct.unpack('>16I', f.read(64))[0]  # keep an eye on this
        self.contsize = struct.unpack('>i', f.read(4))[0]
        self.flags = OBJECT_FLAGS(struct.unpack('>I', f.read(4))[0], 4)
        self.axis = struct.unpack('>i', f.read(4))[0]
        self.drawmode = struct.unpack('>i', f.read(4))[0]
        self.red, self.green, self.blue = struct.unpack('>fff', f.read(12))
        self.pdrawsize = struct.unpack('>i', f.read(4))[0]
        self.symbol, self.symsize, self.linewidth2, self.linewidth, self.linesty = struct.unpack('>BBBBB', f.read(5))
        self.symflags = OBJECT_SYM_FLAGS(struct.unpack('>B', f.read(1))[0], 1)
        self.sympad, self.trans = struct.unpack('>BB', f.read(2))
        self.meshsize, self.surfsize = struct.unpack('>ii', f.read(8))
        self.isset = True
        return f

    def add_cont(self, cont):
        """Add a CONT chunk object to this OBJT object"""
        self.conts[self.cont_count] = cont
        self.cont_count += 1
        self.current_cont = self.conts[self.cont_count - 1]

    def add_mesh(self, mesh):
        """Add a MESH chunk object to this OBJT object"""
        self.meshes[self.mesh_count] = mesh
        self.mesh_count += 1
        self.current_mesh = self.meshes[self.mesh_count - 1]

    def __repr__(self):
        string = """\
name:          %s
extra:         %s
contsize:      %s
flags:         %s
axis:          %s
drawmode:      %s
RGB:           (%s, %s, %s)
pdrawsize:     %s
symbol:        %s
symsize:       %s
linewidth2:    %s
linewidth:     %s
linesty:       %s
symflags:      %s
sympad:        %s
trans:         %s
meshsize:      %s
surfsize:      %s
stored data:
%s""" % (
            self.name, self.extra, self.contsize, self.flags,
            self.axis, self.drawmode, self.red, self.green, self.blue,
            self.pdrawsize, self.symbol, self.symsize, self.linewidth2,
            self.linewidth, self.linesty, self.symflags, self.sympad,
            self.trans, self.meshsize, self.surfsize, self.obst
        )
        return string


class OBST(object):
    """OBST chunk class"""

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read data from file to this object"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]
        self.store = _dict()
        for i in _xrange(self.bytes // 12):
            store = STORE(f)
            f = store.read()
            self.store[i] = store
        self.isset = True
        return f

    def __repr__(self):
        string = ''
        for i in sorted(self.store.keys()):
            string += self.store[i].__repr__()
        return string


class CONT(object):
    """CONT chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False
        self.size = None
        self.cost = None

    def read(self):
        """Read the contents of the CONT chunk"""
        f = self.f
        self.psize = struct.unpack('>i', f.read(4))[0]
        self.flags = CONTOUR_FLAGS(struct.unpack('>I', f.read(4))[0], 4)
        self.time, self.surf = struct.unpack('>ii', f.read(8))
        # self.pt is a array of triples
        # first get the array of floats
        # then isolate each frame (0, 1, 2)
        # then zip them all together
        pt = struct.unpack('>' + 'fff' * self.psize, f.read(12 * self.psize))
        pt_x = pt[0::3]
        pt_y = pt[1::3]
        pt_z = pt[2::3]
        self.pt = list(zip(pt_x, pt_y, pt_z))
        self.isset = True
        return f

    def add_size(self, size):
        """Modify the size attribute

        :param size: the size value
        """
        self.size = size

    def __repr__(self):
        string = """\
psize:         %s
flags:         %s
time:          %s
surf:          %s
pt:            %s
size:          %s
stored data:
%s""" % (self.psize, self.flags, self.time, self.surf, self.pt, self.size, self.cost)
        return string


class COST(object):
    """COST chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the COST chunk"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]
        self.store = _dict()
        for i in _xrange(self.bytes // 12):
            store = STORE(f)
            f = store.read()
            self.store[i] = store
        self.isset = True
        return f

    def __repr__(self):
        string = ''
        for i in sorted(self.store.keys()):
            string += self.store[i].__repr__()
        return string


class MESH(object):
    """MESH chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.mest = None
        self.isset = False

    def read(self):
        """Read the contents of the MESH chunk"""
        f = self.f
        self.vsize, self.lsize = struct.unpack('>ii', f.read(8))
        self.flag = MESH_FLAGS(struct.unpack('>I', f.read(4))[0], 4)
        self.time, self.surf = struct.unpack('>hh', f.read(4))
        # self.vert is an array of triples
        # first get the array of floats
        # then isolate each frame (0, 1, 2)
        # then zip them all together
        vert = struct.unpack('>' + 'fff' * self.vsize, f.read(12 * self.vsize))
        vert_x = vert[0::3]
        vert_y = vert[1::3]
        vert_z = vert[2::3]
        self.vert = tuple(zip(vert_x, vert_y, vert_z))
        self.list = struct.unpack('>' + 'i' * self.lsize, f.read(4 * self.lsize))
        self.isset = True
        return f

    def __repr__(self):
        string = """\
vsize:         %s
lsize:         %s
flag:          %s
time:          %s
surf:          %s
vert:          %s
list:          %s
stored data:
%s""" % (self.vsize, self.lsize, self.flag, self.time, self.surf, self.vert, self.list, self.mest)
        return string


class MEST(object):
    """MEST chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the MEST chunk"""
        f = self.f
        self.store = _dict()
        for i in _xrange(self.bytes // 12):
            store = STORE(f)
            f = store.read()
            self.store[i] = store
        self.isset = True
        return f

    def __repr__(self):
        string = ''
        for i in sorted(self.store.keys()):
            string += self.store[i].__repr__()
        return string


class IMAT(object):
    """IMAT chunk class"""

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the IMAT chunk"""
        f = self.f
        self.bytes = struct.unpack('>I', f.read(4))[0]
        self.ambient, self.diffuse, self.specular, self.shininess, self.fillred, self.fillgreen, self.fillblue, \
            self.quality = struct.unpack('>BBBBBBBB', f.read(8))
        self.mat2 = struct.unpack('>I', f.read(4))[0]
        self.valblack, self.valwhite, self.matflags2, self.mat3b3 = struct.unpack('>BBBB', f.read(4))
        self.isset = True
        return f

    def __repr__(self):
        string = """\
bytes:         %s
ambient:       %s
diffuse:       %s
specular:      %s
shininess:     %s
fillred:       %s
fillgreen:     %s
fillblue:      %s
quality:       %s
mat2:          %s
valblack:      %s
valwhite:      %s
matflags2:     %s
mat3b3:        %s""" % (
            self.bytes, self.ambient, self.diffuse, self.specular, self.shininess, self.fillred,
            self.fillgreen, self.fillblue, self.quality, self.mat2, self.valblack,
            self.valwhite, self.matflags2, self.mat3b3
        )
        return string


class SLAN(object):
    """SLAN chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the SLAN chunk"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]
        self.time = struct.unpack('>i', f.read(4))[0]
        self.angles = struct.unpack('>fff', f.read(12))
        self.center = struct.unpack('>fff', f.read(12))
        self.label = get_printable_ascii_string(struct.unpack('>32s', f.read(32))[0])
        return f


class VIEW(object):
    """VIEW chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f, first_view=False):
        self.f = f
        self.isset = False
        self.first_view = first_view

    def read(self):
        """Read the contents of the VIEW chunk"""
        f = self.f
        self.objvsize = struct.unpack('>i', f.read(4))[0]
        if self.first_view:
            self.Objv = struct.unpack('>i', f.read(4))[0]
        else:
            self.Objv = struct.unpack('>%ss' % (self.objvsize), f.read(self.objvsize))[0]
        self.isset = True
        return f

    def __repr__(self):
        if self.first_view:
            string = """\
objvsize:      %s
View:          %s""" % (self.objvsize, self.Objv)
        else:
            string = """\
objvsize:      %s
Objv:          %s""" % (self.objvsize, self.Objv)
        return string


class MINX(object):
    """MINX chunk class

    Model to image transformation
    Documented as 72 bytes but works with 76 bytes

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the MINX chunk"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]  # unknown byte
        self.oscale = struct.unpack('>fff', f.read(12))
        self.otrans = struct.unpack('>fff', f.read(12))
        self.orot = struct.unpack('>fff', f.read(12))
        self.cscale = struct.unpack('>fff', f.read(12))
        self.ctrans = struct.unpack('>fff', f.read(12))
        self.crot = struct.unpack('>fff', f.read(12))
        self.isset = True
        return f

    def __repr__(self):
        string = """\
bytes:         %s
oscale:        %s
otrans:        %s
orot:          %s
cscale:        %s
ctrans:        %s
crot:          %s""" % (
            self.bytes, self.oscale, self.otrans,
            self.orot, self.cscale, self.ctrans, self.crot
        )
        return string


class CLIP(object):
    """CLIP chunk class

    :param file f: file handler for the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the CLIP chunk"""
        f = self.f
        self.count = struct.unpack('>B', f.read(1))[0]
        self.flags = CLIP_FLAGS(struct.unpack('>B', f.read(1))[0], 1)
        self.trans, self.plane = struct.unpack('>BB', f.read(2))
        if self.count == 0:
            count = 1
        else:
            count = self.count
        self.normal = struct.unpack('>fff', f.read(12 * count))
        self.point = struct.unpack('>fff', f.read(12 * count))
        self.something = struct.unpack('>i', f.read(4))[0]
        self.isset = True
        return f

    def __repr__(self):
        string = """\
count:        %s
flags:        %s
trans:        %s
plane:        %s
normal:       %s
point:        %s
something:    %s""" % (self.count, self.flags, self.trans, self.plane, self.normal, self.point, self.something)
        return string


class MCLP(object):
    """MCLP chunk class

    Model clipping plane parameters

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the MCLP chunk"""
        f = self.f
        self.count = struct.unpack('>B', f.read(1))[0]
        self.flags = MCLP_FLAGS(struct.unpack('>B', f.read(1))[0], 1)
        self.trans, self.plane = struct.unpack('>BB', f.read(2))
        if self.count == 0:
            count = 1
        else:
            count = self.count
        self.normal = struct.unpack('>fff', f.read(12 * count))
        self.point = struct.unpack('>fff', f.read(12 * count))
        self.something = struct.unpack('>i', f.read(4))[0]
        self.isset = True
        return f

    def __repr__(self):
        string = """\
count:        %s
flags:        %s
trans:        %s
plane:        %s
normal:       %s
point:        %s
something:    %s""" % (self.count, self.flags, self.trans, self.plane, self.normal, self.point, self.something)
        return string


class MEPA(object):
    """MEPA chunk class

    :param file f: file handle of the IMOD segmentation file
    """

    def __init__(self, f):
        self.f = f
        self.isset = False

    def read(self):
        """Read the contents of the MEPA chunk"""
        f = self.f
        self.bytes = struct.unpack('>i', f.read(4))[0]
        self.flags = MEPA_FLAGS(struct.unpack('>I', f.read(4))[0], 4)
        self.cap, self.passes, self.capSkipNz, self.inczLowRes, self.inczHighRes, self.minz, self.maxz, \
            self.reserved_int = struct.unpack('>8i', f.read(32))
        self.overlaps, self.tubeDiameter, self.xmin, self.xmax, self.ymin, self.ymax, self.tolLowRes, \
            self.tolHighRes, self.flatCrit, self.reserved_float = struct.unpack('>10f', f.read(40))
        self.isset = True
        return f

    def __repr__(self):
        string = """\
bytes:        %s
flags:        %s
cap:          %s
passes:       %s
capSkipNz:    %s
inczLowRes:   %s
inczHighRes:  %s
minz:         %s
maxz:         %s
reserved:     %s
overlaps:     %s
tubeDiameter: %s
xmin:         %s
xmax:         %s
ymin:         %s
ymax:         %s
tolLowRes:    %s
tolHighRes:   %s
flatCrit:     %s
reserved:     %s""" % (
            self.bytes, self.flags, self.cap, self.passes, self.capSkipNz, self.inczLowRes, self.inczHighRes, self.minz,
            self.maxz, self.reserved_int,
            self.overlaps, self.tubeDiameter, self.xmin, self.xmax, self.ymin, self.ymax, self.tolLowRes,
            self.tolHighRes, self.flatCrit, self.reserved_float)
        return string


def get_data(fn):
    """
    Extract chunks from IMOD model file pointed to by the handle f

    :param str fn: name of IMOD file
    :raises ValueError: if it doesn't start with an IMOD chunk
    :raises ValueError: if the file lacks an IEOF chunk
    """
    with open(fn, 'r+b') as f:
        # make sure the file has a 'IEOF' terminal type ID
        # absence of this will mean non-termination
        f.seek(-4, os.SEEK_END)
        chunk_name = _decode(struct.unpack('>4s', f.read(4))[0], 'utf-8')

        if chunk_name == 'IEOF':
            f.seek(0)
        else:
            raise ValueError("Invalid file: missing terminal IEOF; has %s instead" % chunk_name)

        chunk_name = _decode(struct.unpack('>4s', f.read(4))[0], 'utf-8')
        if chunk_name == 'IMOD':
            imod = None
            first_view = True
        else:
            raise ValueError("Invalid file: %s" % chunk_name)

        while chunk_name != 'IEOF':
            if chunk_name == 'IMOD':
                imod = IMOD(f)
                f = imod.read()
            elif chunk_name == 'MOST':
                most = MOST(f)
                f = most.read()
                imod.most = most
            elif chunk_name == 'OBJT':
                objt = OBJT(f)
                f = objt.read()
                imod.add_objt(objt)
            elif chunk_name == 'OGRP':
                # fixme: use print_date
                print("OGRP: skipping data...", file=sys.stderr)
                num_bytes = struct.unpack('>i', f.read(4))[0]
                f.read(num_bytes)
            elif chunk_name == 'OBST':
                obst = OBST(f)
                f = obst.read()
                imod.current_objt.obst = obst
            elif chunk_name == 'CONT':
                cont = CONT(f)
                f = cont.read()
                imod.current_objt.add_cont(cont)
            elif chunk_name == 'COST':
                cost = COST(f)
                f = cost.read()
                imod.current_objt.current_cont.cost = cost
            elif chunk_name == 'SIZE':
                size = struct.unpack('>i' + 'f' * imod.current_objt.current_cont.psize,
                                     f.read(4 * (imod.current_objt.current_cont.psize + 1)))
                imod.current_objt.current_cont.size = size
            elif chunk_name == 'MESH':
                mesh = MESH(f)
                f = mesh.read()
                imod.current_objt.add_mesh(mesh)
            elif chunk_name == 'SKLI':
                # fixme: use print_date
                print("SKLI: skipping data...", file=sys.stderr)
                num_bytes = struct.unpack('>i', f.read(4))[0]
                f.read(num_bytes)
            elif chunk_name == 'MEST':
                mest = MEST(f)
                f = mest.read()
                imod.current_objt.current_mesh.mest = mest
            elif chunk_name == 'CLIP':
                clip = CLIP(f)
                f = clip.read()
                imod.current_objt.clip = clip
            elif chunk_name == 'MCLP':
                mclp = MCLP(f)
                f = mclp.read()
                imod.mclp = mclp
            elif chunk_name == 'IMAT':
                imat = IMAT(f)
                f = imat.read()
                imod.current_objt.imat = imat
            elif chunk_name == 'SLAN':  # the class exists but has not been integrated; need an example of where it occurs
                # fixme: use print_date
                print("SLAN: skipping data...", file=sys.stderr)
                num_bytes = struct.unpack('>i', f.read(4))[0]
                f.read(num_bytes)
            elif chunk_name == 'MEPA':
                mepa = MEPA(f)
                f = mepa.read()
                imod.current_objt.mepa = mepa
            elif chunk_name == 'VIEW':
                if first_view:
                    view = VIEW(f, first_view=first_view)
                    first_view = False
                else:
                    view = VIEW(f)
                f = view.read()
                imod.add_view(view)
            elif chunk_name == 'MINX':
                minx = MINX(f)
                f = minx.read()
                imod.minx = minx
            elif chunk_name == 'OLBL':
                chunk_length, next_chunk = find_chunk_length(f)  # for diagnostics only
                # fixme: use print_date
                print("The chunk {} has a length of {} bytes. The next chunk is {}.".format(
                    chunk_name, chunk_length, next_chunk
                ))
            else:
                # fixme: use print_date
                print("This chunk is %(chunk_name)s." % {'chunk_name': chunk_name})
                chunk_length, next_chunk = find_chunk_length(f)  # for diagnostics only
                # fixme: use print_date
                print("It has a length of %(chunk_length)s bytes." % {'chunk_length': chunk_length})
                # fixme: use print_date
                print("The next chunk is %(next_chunk)s." % {'next_chunk': next_chunk})
                raise ValueError("Unknown chunk named '%s'" % chunk_name)
            # next chunk
            chunk_name = _decode(struct.unpack('>4s', f.read(4))[0], 'utf-8')
            # if isinstance(_chunk_name, _bytes):
            #     chunk_name = _chunk_name.decode('utf-8')
            # else:
            #     chunk_name = _chunk_name

    return imod


def show_chunks(fn):
    """
    Show the sequence and number of chunks pointed to the by file handle f.

    :param str fn: name of IMOD file
    """
    marker_sequence = list()
    seen_view = False
    view_size = 0
    byte = b''
    with open(fn, 'rb') as f:
        while byte != b'IEOF':
            byte = struct.unpack('>4s', f.read(4))[0]
            if byte in KEY_WORDS:  # or (byte[0] in ALPHA and byte[1] in ALPHA and byte[2] in ALPHA and byte[3] in ALPHA):
                marker_sequence.append(byte)
            if byte == b'VIEW':
                seen_view = True
            #                 print "view size = %s" % view_size
            if seen_view:
                view_size += 1

            f.seek(-3, os.SEEK_CUR)  # advance -3 positions back
        marker_sequence.append(byte)  # IEOF

        marker_count = dict(zip(
            KEY_WORDS,
            [0] * len(KEY_WORDS)
        ))
        for i in _xrange(len(marker_sequence) - 1):
            current_marker = marker_sequence[i]
            next_marker = marker_sequence[i + 1]
            if next_marker == current_marker:
                marker_count[current_marker] += 1
            elif next_marker != current_marker:
                marker_count[current_marker] += 1
                # fixme: use print_date
                print(current_marker, marker_count[current_marker])
                #             waiter = raw_input('')
                marker_count[current_marker] = 0
        # print the last one
        # fixme: use print_date
        print(next_marker)

    return


def print_model(fn):
    """Pretty print the IMOD model

    Arguments:
    :param str fn: name of IMOD file
    # :param mod: an object of class IMOD containing all data
    # :type mod: :py:class:`sfftk.readers.modreader.IMOD`
    # :param file output: the name of the output to which data should be sent
    """
    # if output is not sys.stdout:
    #     output_dest = open(output, 'w')
    # else:
    #     output_dest = output

    mod = get_data(fn)
    output_dest = sys.stderr
    # fixme: use print_date
    print("***************************************************************************************", file=output_dest)
    print('IMOD', file=output_dest)
    print(mod, file=output_dest)
    print("***************************************************************************************", file=output_dest)

    for o, O in _dict_iter_items(mod.objts):
        print('OBJT%s' % o, file=output_dest)
        print(O, file=output_dest)
        print("***************************************************************************************",
              file=output_dest)
        for c, C in _dict_iter_items(O.conts):
            print('CONT%s' % c, file=output_dest)
            print(C, file=output_dest)
            print("***************************************************************************************",
                  file=output_dest)
        for m, M in _dict_iter_items(O.meshes):
            print('MESH%s' % m, file=output_dest)
            print(M, file=output_dest)
            print("***************************************************************************************",
                  file=output_dest)
        if O.clip is not None:
            print('CLIP', file=output_dest)
            print(O.clip, file=output_dest)
            print("***************************************************************************************",
                  file=output_dest)
        print('IMAT', file=output_dest)
        print(O.imat, file=output_dest)
        print("***************************************************************************************",
              file=output_dest)
        if O.mepa is not None:
            print('MEPA', file=output_dest)
            print(O.mepa, file=output_dest)
            print("***************************************************************************************",
                  file=output_dest)
    for v, V in _dict_iter_items(mod.views):
        print('VIEW%s' % v, file=output_dest)
        print(V, file=output_dest)
        print("***************************************************************************************",
              file=output_dest)
    print('MINX', file=output_dest)
    print(mod.minx, file=output_dest)
    print("***************************************************************************************", file=output_dest)

    # if output is not sys.stdout:
    #     output_dest.close()

    return
