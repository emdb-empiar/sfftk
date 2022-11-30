"""
``sfftk.formats.map``
=====================

User-facing reader classes for CCP4/MRC masks.

There are three classes (one of which will be deprecated beginning in ``v0.8.0``).

1 - :py:class:
"""
import inspect
import json
import os
import sys
import warnings

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _xrange
from sfftkrw.core.print_tools import print_date, get_printable_ascii_string

from .base import Segmentation, Header, Segment, Annotation
from ..readers import mapreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-09"
__updated__ = '2018-02-23'


class MapAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, map_obj):
        warnings.warn(
            "please use MaskAnnotation class instead",
            category=PendingDeprecationWarning
        )
        self._map_obj = map_obj
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]

    @property
    def endianness(self):
        if (self._machst[0] == '\x44' and self._machst[1] == '\x41' and self._machst[2] == '\x00' and self._machst[
            3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'D' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'A' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00'):
            return 'little'
        elif self._machst[0] == '\x11' and self._machst[1] == '\x11' and self._machst[2] == '\x00' and \
                self._machst[3] == '\x00':
            return 'big'
        else:
            raise ValueError("MACHST = ", self._machst)

    @property
    def name(self):
        """Segment name (filename since we have a segment per file)"""
        return os.path.basename(self._map_obj._fn)

    @property
    def description(self):
        """Segment description (concat all labels)"""
        desc = ''
        for i in _xrange(self._nlabl):
            desc += get_printable_ascii_string(getattr(self, '_label_{}'.format(i)))
        return desc

    @property
    def colour(self):
        """Segment colour"""
        return None

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        annotation = schema.SFFBiologicalAnnotation()
        annotation.name = self.name
        annotation.number_of_instances = 1
        import random
        red, green, blue = random.random(), random.random(), random.random()
        print_date(
            "Colour not defined for mask segments. Setting colour to random RGB value of {}".format((red, green, blue))
        )
        colour = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
        )
        return annotation, colour


class MapSegment(Segment):
    """Segment class"""

    def __init__(self, map_obj):
        warnings.warn(
            "please use MaskSegment class instead",
            category=PendingDeprecationWarning
        )
        self._map_obj = map_obj

    @property
    def annotation(self):
        """Segment annotation"""
        return MapAnnotation(self._map_obj)

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        lattice = schema.SFFLattice(
            mode=self.annotation.mode,
            endianness=self.annotation.endianness,
            size=schema.SFFVolumeStructure(
                cols=self.annotation.cols,
                rows=self.annotation.rows,
                sections=self.annotation.sections,
            ),
            start=schema.SFFVolumeIndex(
                cols=self.annotation.start_cols,
                rows=self.annotation.start_rows,
                sections=self.annotation.start_sections,
            ),
            data=self._map_obj.voxels,
        )
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=lattice.id,
            value=1.0,
        )
        return segment, lattice


MODE_STRING = {
    0: 'int8',
    1: 'int16',
    2: 'float32',
}


class MapHeader(Header):
    """Class defining the header in a CCP4 file"""

    def __init__(self, segment):
        warnings.warn(
            "please use MaskHeader class instead",
            category=PendingDeprecationWarning
        )
        self._map_obj = segment.annotation._map_obj
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]


class MapSegmentation(Segmentation):
    """Class representing an CCP4/MAP mask segmentation

    .. deprecated:: v0.8.0

        For future versions of ``sfftk``, please use the :py:class:`MaskSegmentation` class for one or more binary masks
        and :py:class:`MergedMaskSegmentation` from merged masks. See also :ref:`merging_masks`.

        A ``PendingDeprecationWarning`` is raised for ``sfftk`` earlier than ``v0.8.0``.

    .. code-block:: python

        from sfftk.formats.map import MapSegmentation
        map_seg = MapSegmentation('file.map')
    """

    def __init__(self, fns, *args, **kwargs):
        """Initialise the MapSegmentation reader"""
        warnings.warn(
            "please use either BinaryMaskSegmentation or MergedMaskSegmentation classes instead",
            category=PendingDeprecationWarning
        )
        self._fns = fns

        # set the segmentation attribute
        self._segments = list()
        cols, rows, sections = 0, 0, 0
        for fi, fn in enumerate(fns):
            self._segments.append(MapSegment(mapreader.get_data(fn, *args, **kwargs)))
            segment_annotation = self._segments[fi].annotation
            if fi == 0:
                cols = segment_annotation.cols
                rows = segment_annotation.rows
                sections = segment_annotation.sections
            else:
                if cols != segment_annotation.cols or rows != segment_annotation.rows or \
                        sections != segment_annotation.sections:
                    print_date("{}: CCP4 mask of dimensions: cols={}, rows={}, sections={}".format(
                        os.path.basename(fn), segment_annotation.cols, segment_annotation.rows,
                        segment_annotation.sections)
                    )
                    print_date("Error: The provided CCP4 masks have different volume dimensions")
                    sys.exit(65)
            print_date("{}: CCP4 mask of dimensions: cols={}, rows={}, sections={}".format(
                os.path.basename(fn), cols, rows, sections)
            )

        # self._map_obj = mapreader.get_data(fn)

    """
    :TODO: document attributes and methods of readers
    """

    @property
    def header(self):
        """Segmentation metadata must be exactly as in one segment"""
        return MapHeader(self.segments[0])

    @property
    def segments(self):  # only one segment
        """The segments in this segmentation"""
        return self._segments
        # return [MapSegment(self)]

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "CCP4 mask segmentation"
        # software
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Unspecified",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details
            )
        )
        segmentation.primary_descriptor = "three_d_volume"

        segmentation.bounding_box = schema.SFFBoundingBox(
            xmax=self.header.x_length,
            ymax=self.header.y_length,
            zmax=self.header.z_length,
        )

        # transforms
        segmentation.transform_list = schema.SFFTransformList()

        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(self.header.ijk_to_xyz_transform)
            )

        segment_list = schema.SFFSegmentList()
        lattice_list = schema.SFFLatticeList()
        for s in self.segments:
            segment, lattice = s.convert()
            segment_list.append(segment)
            lattice_list.append(lattice)

        # finally pack everything together
        segmentation.segment_list = segment_list
        segmentation.lattice_list = lattice_list

        segmentation.details = details
        return segmentation


class MaskAnnotation(Annotation):
    """Class representing annotation for individual segments"""

    def __init__(self, map_obj, name=None):
        self._map_obj = map_obj
        self._name = name
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]

    @property
    def endianness(self):
        if (self._machst[0] == '\x44' and self._machst[1] == '\x41' and self._machst[2] == '\x00' and self._machst[
            3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'D' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'A' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00'):
            return 'little'
        elif self._machst[0] == '\x11' and self._machst[1] == '\x11' and self._machst[2] == '\x00' and \
                self._machst[3] == '\x00':
            return 'big'
        else:
            raise ValueError("MACHST = ", self._machst)

    @property
    def name(self):
        """Segment name (filename since we have a segment per file)"""
        if self._name is not None:
            return self._name
        return os.path.basename(self._map_obj._fn)

    @property
    def description(self):
        """Segment description (concat all labels)"""
        desc = ''
        for i in _xrange(self._nlabl):
            desc += get_printable_ascii_string(getattr(self, '_label_{}'.format(i)))
        return desc

    @property
    def colour(self):
        """Segment colour"""
        return None

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        annotation = schema.SFFBiologicalAnnotation()
        annotation.name = self.name
        annotation.number_of_instances = 1
        colour = schema.SFFRGBA(
            random_colour=True
        )
        return annotation, colour


class BinaryMaskSegment(Segment):
    """Class representing an individual binary mask segment"""

    def __init__(self, map_obj):
        self._map_obj = map_obj

    @property
    def map_obj(self):
        return self._map_obj

    @property
    def annotation(self):
        """Segment annotation"""
        return MaskAnnotation(self._map_obj)

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        lattice = schema.SFFLattice(
            mode=self.annotation.mode,
            endianness=self.annotation.endianness,
            size=schema.SFFVolumeStructure(
                cols=self.annotation.cols,
                rows=self.annotation.rows,
                sections=self.annotation.sections,
            ),
            start=schema.SFFVolumeIndex(
                cols=self.annotation.start_cols,
                rows=self.annotation.start_rows,
                sections=self.annotation.start_sections,
            ),
            data=self._map_obj.voxels,
        )
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=lattice.id,
            value=1.0,
        )
        return segment, lattice


class MergedMaskSegment(Segment):
    """Class representing an individual segment from a merged mask"""

    def __init__(self, label, parent_label, map_obj, name=None):
        self._label = label
        self._parent_label = parent_label
        self._map_obj = map_obj
        self._name = name

    @property
    def label(self):
        return self._label

    @property
    def parent_label(self):
        return self._parent_label

    @property
    def map_obj(self):
        return self._map_obj

    @property
    def annotation(self):
        """Segment annotation"""
        return MaskAnnotation(self._map_obj, name=self._name)

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment(parent_id=self.parent_label)
        segment.biological_annotation, segment.colour = self.annotation.convert()
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=0,  # always the first lattice
            value=self.label,
        )
        return segment


class MaskHeader(Header):
    """Class representing mask header"""

    def __init__(self, map_obj):
        """Initialise the header of a mask"""
        self._map_obj = map_obj
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]

    @property
    def endianness(self):
        if (self._machst[0] == '\x44' and self._machst[1] == '\x41' and self._machst[2] == '\x00' and self._machst[
            3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'D' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'A' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00'):
            return 'little'
        elif self._machst[0] == '\x11' and self._machst[1] == '\x11' and self._machst[2] == '\x00' and \
                self._machst[3] == '\x00':
            return 'big'
        else:
            raise ValueError("MACHST = ", self._machst)


class BinaryMaskSegmentation(Segmentation):
    """A segmentation consisting of one or more binary masks

    .. warning:: Results in large files

        This class works by compiling a set of binary masks into a single file. The resulting file is much smaller
        than the original individual masks combined at the expense of the compute time required to zip and base64-encode
        the volume data.

        Users are strongly encouraged to first merge all binary masks into a single mask using the :ref:`merging_masks`
        then using the :py:class:`sfftk.formats.map.MergedMaskSegmentation` class instead of this one.

    .. code-block:: python

        from sfftk.formats.map import BinaryMaskSegmentation
        map_seg = BinaryMaskSegmentation('binary_mask.mrc')

    """

    def __init__(self, fns, *args, **kwargs):
        """Initialise a :py:class:`BinaryMaskSegmentation` object"""
        self._fns = fns

        # set the segmentation attribute
        self._segments = list()
        # we will assume that these are homogeneous masks
        for file_index, file in enumerate(self._fns):
            self._segments.append(BinaryMaskSegment(mapreader.get_data(file, *args, **kwargs)))

    @property
    def header(self):
        """The header is all the data from the CCP4/MRC header"""
        return MaskHeader(self.segments[0].map_obj)

    @property
    def segments(self):
        """An iterable of segments"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "CCP4 mask segmentation"
        # software
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Unspecified",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details
            )
        )
        segmentation.primary_descriptor = "three_d_volume"

        segmentation.bounding_box = schema.SFFBoundingBox(
            xmax=self.header.x_length,
            ymax=self.header.y_length,
            zmax=self.header.z_length,
        )

        # transforms
        segmentation.transform_list = schema.SFFTransformList()

        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(self.header.ijk_to_xyz_transform)
            )

        segment_list = schema.SFFSegmentList()
        lattice_list = schema.SFFLatticeList()
        for s in self.segments:
            segment, lattice = s.convert()
            segment_list.append(segment)
            lattice_list.append(lattice)

        # finally pack everything together
        segmentation.segment_list = segment_list
        segmentation.lattice_list = lattice_list

        segmentation.details = details
        return segmentation


class MergedMaskSegmentation(Segmentation):
    """A segmentation constructed from a merged mask derived from multiple binary masks

    .. code-block:: python

        from sfftk.formats.map import MergedMaskSegmentation
        map_seg = MergedMaskSegmentation('merged_mask.mrc', label_tree='merged_mask.json')
    """

    def __init__(self, fn, label_tree="merged_mask.json"):
        """Initialise a :py:class:`BinaryMaskSegmentation` object"""
        self._fn = fn
        self._label_tree_fn = label_tree
        # in this case we have only one lattice (merged_mask.mrc)
        self._map_obj = mapreader.get_data(self._fn)  # there is only one file
        self._segments = list()
        # let's now unpack the labels
        with open(self._label_tree_fn) as f:
            self._mask_metadata = json.load(f)
        # get the mask names by reversing the mask_to_label sub-dict
        label_to_mask = {_label: _mask for _mask, _label in self._mask_metadata['mask_to_label'].items()}
        for label, parent_label in self._mask_metadata['label_tree'].items():
            if isinstance(parent_label, int):
                self._segments.append(
                    MergedMaskSegment(int(label), parent_label, self._map_obj, name=label_to_mask[int(label)])
                )
            elif isinstance(parent_label, list):
                l1, l2 = parent_label
                name = f"Overlapping region between mask with label {l1} and {l2}"
                # we will only store one parent even though this label is associated with two parents
                # we can work out the other parent by subtracting the parent_id from the label_id=segment_id
                # in this way, we can completely reconstruct the label tree from which we can,
                # in principle, completely reconstruct the original binary masks
                self._segments.append(
                    MergedMaskSegment(int(label), max(parent_label), self._map_obj, name=name)
                )

    @property
    def map_obj(self):
        return self._map_obj

    @property
    def header(self):
        """The header is all the data from the CCP4/MRC header"""
        return MaskHeader(self.map_obj)

    @property
    def segments(self):
        """An iterable of segments"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "Merged CCP4 mask segmentation"
        # software
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Unspecified",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details
            )
        )
        segmentation.primary_descriptor = "three_d_volume"

        segmentation.bounding_box = schema.SFFBoundingBox(
            xmax=self.header.x_length,
            ymax=self.header.y_length,
            zmax=self.header.z_length,
        )

        # transforms
        segmentation.transform_list = schema.SFFTransformList()

        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(self.header.ijk_to_xyz_transform)
            )

        segment_list = schema.SFFSegmentList()
        lattice_list = schema.SFFLatticeList()
        lattice_list.append(
            schema.SFFLattice(
                mode=self.header.mode,
                endianness=self.header.endianness,
                size=schema.SFFVolumeStructure(
                    cols=self.header.cols,
                    rows=self.header.rows,
                    sections=self.header.sections,
                ),
                start=schema.SFFVolumeIndex(
                    cols=self.header.start_cols,
                    rows=self.header.start_rows,
                    sections=self.header.start_sections,
                ),
                data=self._map_obj.voxels,
            )
        )
        for s in self.segments:
            segment = s.convert()
            segment_list.append(segment)

        # finally pack everything together
        segmentation.segment_list = segment_list
        segmentation.lattice_list = lattice_list

        segmentation.details = details
        return segmentation
