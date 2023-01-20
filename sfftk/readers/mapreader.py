"""
``sfftk.readers.mapreader``
===========================

Ad hoc reader for CCP4 masks

References
----------
The following article is useful as it exposes many internals of map files:

- ftp://ftp.wwpdb.org/pub/emdb/doc/Map-format/current/EMDB_map_format.pdf

"""
import sys

import numpy
from sfftkrw.core import _xrange, _encode

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk'
__date__ = '2016-07-05'


class Map(object):
    """Class to encapsulate a CCP4 mask"""

    def __init__(self, fn, header_only=False, *args, **kwargs):
        """Initialise a Map object

        :param str fn: file name
        :param bool header_only: whether or not (default) to read the data
        """
        self._fn = fn
        self._inverted = False
        with open(fn, 'rb') as f:
            status = self.read(f, header_only=header_only, *args, **kwargs)
        # 0 is good
        assert status == 0

    def write(self, f):
        """Write data to an EMDB Map file

        :param file f: file object
        :return int status: 0 on success; fail otherwise
        """
        import struct

        string = struct.pack('<iii', self._nc, self._nr, self._ns)
        string += struct.pack('<I', self._mode)
        string += struct.pack('<iii', self._ncstart, self._nrstart, self._nsstart)
        string += struct.pack('<iii', self._nx, self._ny, self._nz)
        string += struct.pack('<fff', self._x_length, self._y_length, self._z_length)
        string += struct.pack('<fff', self._alpha, self._beta, self._gamma)
        string += struct.pack('<iii', self._mapc, self._mapr, self._maps)
        string += struct.pack('<fff', self._amin, self._amax, self._amean)
        string += struct.pack('<iii', self._ispg, self._nsymbt, self._lskflg)
        string += struct.pack('<' + 'f' * (9), self._s11, self._s12, self._s13, self._s21, self._s22, self._s23,
                              self._s31, self._s32, self._s33)
        string += struct.pack('<fff', self._t1, self._t2, self._t3)
        string += struct.pack('<15i', *self._extra)
        # string += struct.pack('<4c', self._map)
        # convert to bytes
        string += _encode(self._map, 'utf-8')
        string += _encode(self._machst, 'utf-8')
        string += struct.pack('<f', self._rms)

        # if inverted we will add one more label
        if self._inverted:
            string += struct.pack('<i', self._nlabl + 1)
        else:
            string += struct.pack('<i', self._nlabl)

        for i in range(self._nlabl):
            len_label = len(self.__getattribute__('_label_%s' % i))
            encoding = _encode(self.__getattribute__('_label_{}'.format(i)), 'utf-8')
            string += encoding
            # pack the remaining space
            string += struct.pack('<{}x'.format(80 - len_label))

        if self._inverted:
            from datetime import datetime
            d = datetime.now()
            string += _encode("{:<56}{:>24}".format(
                "sfftk: inverted intensities",
                d.strftime("%d-%b-%y  %H:%M:%S     ")
            ), 'utf-8')

        # pad up to full header of 1024 bytes
        try:
            assert 1024 - len(string) >= 0
        except AssertionError:
            raise ValueError("Header is too long")

        string += struct.pack(
            '<' + str(1024 - len(string)) + 'x')  # dodgy line because we may need to move one byte forward or back

        string += struct.pack('<' + self._voxel_type * self._voxel_count, *tuple(self._voxels))

        f.write(string)
        f.flush()

        return 0

    def read(self, f, header_only=False):
        """Read data from an EMDB Map mask

        :param file f: file object
        :param bool header_only: only read the header [default: False]
        :return int status: 0 on success; fail otherwise
        """
        import struct

        # source: ftp://ftp.ebi.ac.uk/pub/databases/emdb/doc/Map-format/current/EMDB_map_format.pdf
        # number of columns (fastest changing), rows, sections (slowest changing)
        self._nc, self._nr, self._ns = struct.unpack('<iii', f.read(12))
        # voxel datatype
        self._mode = struct.unpack('<I', f.read(4))[0]
        # position of first column, first row, and first section (voxel grid units)
        self._ncstart, self._nrstart, self._nsstart = struct.unpack('<iii', f.read(12))
        # intervals per unit cell repeat along X,Y Z
        self._nx, self._ny, self._nz = struct.unpack('<iii', f.read(12))
        # Unit Cell repeats along X, Y, Z In Ångstroms
        self._x_length, self._y_length, self._z_length = struct.unpack('<fff', f.read(12))
        # Unit Cell angles (degrees)
        self._alpha, self._beta, self._gamma = struct.unpack('<fff', f.read(12))
        # relationship of X,Y,Z axes to columns, rows, sections
        self._mapc, self._mapr, self._maps = struct.unpack('<iii', f.read(12))
        # Minimum, maximum, average density
        self._amin, self._amax, self._amean = struct.unpack('<fff', f.read(12))
        # space group #
        # number of bytes in symmetry table (multiple of 80)
        # flag for skew matrix
        self._ispg, self._nsymbt, self._lskflg = struct.unpack('<iii', f.read(12))
        # skew matrix-S11, S12, S13, S21, S22, S23, S31, S32, S33
        self._s11, self._s12, self._s13, self._s21, self._s22, self._s23, self._s31, self._s32, self._s33 = struct.unpack(
            '<' + 'f' * (9), f.read(9 * 4))
        # skew translation-T1, T2, T3
        self._t1, self._t2, self._t3 = struct.unpack('<fff', f.read(12))
        # user-defined metadata
        self._extra = struct.unpack('<15i', f.read(15 * 4))
        # MRC/CCP4 MAP format identifier
        self._map = struct.unpack('<4s', f.read(4))[0].decode('utf-8')
        # machine stamp
        self._machst = struct.unpack('<4s', f.read(4))[0].decode('utf-8')
        # Density root-mean-square deviation
        self._rms = struct.unpack('<f', f.read(4))[0]
        # number of labels
        self._nlabl = struct.unpack('<i', f.read(4))[0]
        # Up to 10 user-defined labels
        for i in range(int(self._nlabl)):
            self.__setattr__(
                '_label_{}'.format(i),
                struct.unpack('<80s', f.read(80))[0].decode('utf-8').rstrip(' ')
            )

        # jump to the beginning of data
        if f.tell() <= 1024:
            f.seek(1024)
        else:
            raise ValueError("Current byte position in file (%s) is past end of header (1024)" % f.tell())

        if self._mode == 0:
            self._voxel_type = 'b'
            self._voxel_size = 1
        elif self._mode == 1:
            self._voxel_type = 'h'
            self._voxel_size = 2
        elif self._mode == 2:
            self._voxel_type = 'f'
            self._voxel_size = 4
        elif self._mode == 3:
            raise ValueError("No support for complex signed integer Fourier maps")
        elif self._mode == 4:
            raise ValueError("No support for complex floating point Fourier maps")

        # exit here for header only read
        if header_only:
            self._voxel_values = set()
            self._voxel_array = None
            return 0

        #         import math

        self._voxel_count = self._nc * self._nr * self._ns
        self._voxels = struct.unpack('<' + self._voxel_type * self._voxel_count,
                                     f.read(self._voxel_count * self._voxel_size))
        self._voxel_values = set(self._voxels)

        import numpy

        if self._voxel_type == 'b':
            data_type = numpy.int8
        elif self._voxel_type == 'h':
            data_type = numpy.int16
        elif self._voxel_type == 'f':
            data_type = numpy.float32

        self._voxel_array = numpy.array(self._voxels, dtype=data_type)
        self._voxel_array.shape = self._ns, self._nr, self._nc

        # we are done reading; let's make sure we are at the end

        current_position = f.tell()  # where are we in the file
        from os import SEEK_END
        f.seek(0, SEEK_END)
        final_position = f.tell()  # where the end really is

        # ensure we are the end
        if current_position != final_position:
            raise ValueError("There is still some data (%s bytes) to read: current_position = %s; end_position = %s" % (
                final_position - current_position, current_position, final_position))

        return 0

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            string = """\
            \rCols, rows, sections:
            \r    {0}, {1}, {2}
            \rMode: {3}
            \rStart col, row, sections:
            \r    {4}, {5}, {6}
            \rX, Y, Z:
            \r    {7}, {8}, {9}
            \rLengths X, Y, Z (ångström):
            \r    {10}, {11}, {12}
            \r\U000003b1, \U000003b2, \U000003b3:
            \r    {13}, {14}, {15}
            \rMap cols, rows, sections:
            \r    {16}, {17}, {18}
            \rDensity min, max, mean:
            \r    {19}, {20}, {21}
            \rSpace group: {22}
            \rBytes in symmetry table: {23}
            \rSkew matrix flag: {24}
            \rSkew matrix:
            \r    {25} {26} {27}
            \r    {28} {29} {30}
            \r    {31} {32} {33}
            \rSkew translation:
            \r    {34}
            \r    {35}
            \r    {36}
            \rExtra: {37}
            \rMap: {38}
            \rMach-stamp: {39}
            \rRMS: {40}
            \rLabel count: {41}
            \r""".format(
                self._nc, self._nr, self._ns,
                self._mode,
                self._ncstart, self._nrstart, self._nsstart,
                self._nx, self._ny, self._nz,
                self._x_length, self._y_length, self._z_length,
                self._alpha, self._beta, self._gamma,
                self._mapc, self._mapr, self._maps,
                self._amin, self._amax, self._amean,
                self._ispg,
                self._nsymbt,
                self._lskflg,
                self._s11, self._s12, self._s13, self._s21, self._s22, self._s23, self._s31, self._s32, self._s33,
                self._t1, self._t2, self._t3,
                self._extra,
                self._map,
                self._machst,
                self._rms,
                self._nlabl
            )
            if int(self._nlabl) > 0:
                for i in _xrange(int(self._nlabl)):
                    string += """\
                    \rLabel {0}:\
                    \r    {1}
                    \r""".format(i, self.__getattribute__('_label_%s' % i))

            return string
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            string = """\
            \rCols, rows, sections:
            \r    {0}, {1}, {2}
            \rMode: {3}
            \rStart col, row, sections:
            \r    {4}, {5}, {6}
            \rX, Y, Z:
            \r    {7}, {8}, {9}
            \rLengths X, Y, Z (ångström):
            \r    {10}, {11}, {12}
            \r\U000003b1, \U000003b2, \U000003b3:
            \r    {13}, {14}, {15}
            \rMap cols, rows, sections:
            \r    {16}, {17}, {18}
            \rDensity min, max, mean:
            \r    {19}, {20}, {21}
            \rSpace group: {22}
            \rBytes in symmetry table: {23}
            \rSkew matrix flag: {24}
            \rSkew matrix:
            \r    {25} {26} {27}
            \r    {28} {29} {30}
            \r    {31} {32} {33}
            \rSkew translation:
            \r    {34}
            \r    {35}
            \r    {36}
            \rExtra: {37}
            \rMap: {38}
            \rMach-stamp: {39}
            \rRMS: {40}
            \rLabel count: {41}
            \r""".format(
                self._nc, self._nr, self._ns,
                self._mode,
                self._ncstart, self._nrstart, self._nsstart,
                self._nx, self._ny, self._nz,
                self._x_length, self._y_length, self._z_length,
                self._alpha, self._beta, self._gamma,
                self._mapc, self._mapr, self._maps,
                self._amin, self._amax, self._amean,
                self._ispg,
                self._nsymbt,
                self._lskflg,
                self._s11, self._s12, self._s13, self._s21, self._s22, self._s23, self._s31, self._s32, self._s33,
                self._t1, self._t2, self._t3,
                self._extra,
                self._map,
                self._machst,
                self._rms,
                self._nlabl
            )
            if int(self._nlabl) > 0:
                for i in _xrange(int(self._nlabl)):
                    string += """\
                    \rLabel {0}:\
                    \r    {1}
                    \r""".format(i, self.__getattribute__('_label_%s' % i))

            return string

    def __repr__(self):
        return "<class '%s'>" % self.__class__

    @property
    def voxels(self):
        """The voxel mask"""
        return self._voxel_array

    @property
    def is_mask(self):
        """Determine if this is a mask or not

        :return bool status: mask or not
        """
        if len(self._voxel_values) == 2 and 0.0 in self._voxel_values:
            return True
        else:
            return False

    def fix_mask(self, mask_value=1.0, voxel_values_threshold=3):
        """Try to fix this mask

        A mask should have only two voxel values: some non-zero value (usually 1) and zero (0) for masked-out regions.
        Sometimes the process of manipulating the mask (e.g. volume rotation) relies on interpolation, which
        converts a mask to have more than two voxel values. This function attempts to fix that provided that
        the number of voxel values is not greater than `voxel_value_threshold`.

        :param float mask_value: the mask value
        :param int voxel_values_threshold: the maxmimum number of voxel values permitted in fixing the mask
        """
        assert voxel_values_threshold > 2  # no need to fix a proper mask (value of 2)

        # round values
        import numpy
        self._voxel_array = numpy.around(self._voxel_array, decimals=1)
        self._voxel_values = set(self._voxel_array.flatten().tolist())

        if len(self._voxel_values) > voxel_values_threshold:
            raise ValueError("Unfixable mask: too many values ({0:,}) > {1}!".format(len(self._voxel_values),
                                                                                     voxel_values_threshold))
        else:
            for value in self._voxel_values:
                if value != 0.0:  # only modify masked regions
                    self._voxel_array = (self._voxel_array == value) * mask_value

        # reset voxel_values list
        self._voxel_values = set(self._voxel_array.flatten().tolist())

    def invert(self):
        """Invert the map file (mask or not)"""
        x_prime = (self._voxel_array - self._amin) / (self._amax - self._amin)
        #         self._voxel_array = 1 - x_prime
        self._voxel_array = self._amin + (1 - x_prime) * (self._amax - self._amin)
        #
        #         self._voxel_array = self._amax + self._amin -
        self._amin = self._voxel_array.min()
        self._amax = self._voxel_array.max()
        self._amean = self._voxel_array.mean()

        self._voxels = self._voxel_array.flatten().tolist()
        self._inverted = True

    @property
    def labels(self):
        """A string of labels found in the CCP4 mask file"""
        label_list = list()
        for i in _xrange(self._nlabl):
            label_list.append(getattr(self, "_label_{}".format(i)))
        return "\n".join(label_list)

    @property
    def skew_matrix_data(self):
        """Skew matrix data as a space-separated string"""
        return " ".join(map(repr,
                            [
                                self._s11, self._s12, self._s13,
                                self._s21, self._s22, self._s23,
                                self._s31, self._s32, self._s33,
                            ])
                        )

    @property
    def skew_matrix(self):
        """Skew matrix as a numpy array"""
        return numpy.array([
            self._s11, self._s12, self._s13,
            self._s21, self._s22, self._s23,
            self._s31, self._s32, self._s33,
        ]).reshape(3, 3)

    @property
    def skew_translation_data(self):
        """Skew translation as a space-separated string"""
        return " ".join(map(repr, [self._t1, self._t2, self._t3]))

    @property
    def skew_translation(self):
        """Skew translation as a numpy array"""
        return numpy.array([self._t1, self._t2, self._t3]).reshape(3, 1)

    @property
    def ijk_to_xyz_transform_data(self):
        x_size = self._x_length / self._nc
        y_size = self._y_length / self._nr
        z_size = self._z_length / self._ns
        return " ".join(map(repr, [
            x_size, 0., 0., self._ncstart * self._x_length / self._nc,
            0., y_size, 0., self._nrstart * self._y_length / self._nr,
            0., 0., z_size, self._nsstart * self._z_length / self._ns,
        ]))

    @property
    def ijk_to_xyz_transform(self):
        x_size = self._x_length / self._nc
        y_size = self._y_length / self._nr
        z_size = self._z_length / self._ns
        return numpy.array([
            x_size, 0., 0., self._ncstart * self._x_length / self._nc,
            0., y_size, 0., self._nrstart * self._y_length / self._nr,
            0., 0., z_size, self._nsstart * self._z_length / self._ns,
        ]).reshape(3, 4)


def get_data(fn, inverted=False, *args, **kwargs):
    """Get structured data from EMDB Map file

    :param str fn: map filename
    :param bool inverted: should we invert the histogram or not (default)?
    :return: map object
    :rtype: :py:class:`sfftk.readers.mapreader.Map`
    """
    my_map = Map(fn, *args, **kwargs)

    if inverted:
        my_map.invert()

    return my_map


def compute_transform(fn, header_only=True):
    """Compute the transform that connects the image to physical space

    :param str fn: map filename
    :param bool header_only: only read the header if `True`
    :return: a 3x4 transformation matrix
    :rtype: :py:class:`numpy.ndarray`
    """
    my_map = Map(fn, header_only=header_only)
    transform = numpy.zeros((3, 4))
    s_x = my_map._x_length / my_map._nc
    s_y = my_map._y_length / my_map._nr
    s_z = my_map._z_length / my_map._ns
    t_x = my_map._ncstart * s_x
    t_y = my_map._nrstart * s_y
    t_z = my_map._nsstart * s_z
    transform[0, 0] = s_x
    transform[1, 1] = s_y
    transform[2, 2] = s_z
    transform[0, 3] = t_x
    transform[1, 3] = t_y
    transform[2, 3] = t_z
    return transform
