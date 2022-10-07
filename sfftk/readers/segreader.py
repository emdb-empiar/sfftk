"""
``sfftk.readers.segreader``
===========================

Ad hoc reader for Segger files"""
import os

import numpy
from sfftkrw.core import _decode, _dict

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-01"
__updated__ = '2018-02-14'


def get_root(region_parent_zip, region_id):
    """
    Return the penultimate `parent_id` for any `region_id`.

    The penultimate parent is one layer below the root (0).
    The set of penultimate parents are the distinct regions contained in the segmentation.
    They correspond to putative functional regions.

    :param tuple region_parent_zip: a list of 2-tuples of `region_ids` and `parent_ids`
    :param int region_id: the `region_id` whose root parent_id is sought
    :return int parent_id: the corresponding penultimate `parent_id` (one step below the root - value of `0`)
    """
    if region_id == 0:
        return 0
    # derive a dictionary of region_id-->parent_id
    region_parent_dict = dict(region_parent_zip)
    # terminate when the ultimate parent is 0
    while region_parent_dict[region_id] != 0:
        # get the parent of the parent
        region_id = region_parent_dict[region_id]
    # this is the penultimate region_id
    parent_id = region_id
    return parent_id


class SeggerSegmentation(object):
    """Encapsulation of a Segger segmentation
    """

    def __init__(self, fn, *args, **kwargs):
        """Initialiser of Segger Segmentation objects"""

        import h5py  # only import
        self._fn = fn
        """
        :TODO: args and kwargs
        """
        self._seg_handler = h5py.File(fn, 'r', *args, **kwargs)
        # region/parent ids
        self._region_ids = self._seg_handler['region_ids'][()].astype(int)
        self._parent_ids = self._seg_handler['parent_ids'][()].astype(int)
        self._zipped_region_parent_ids = list(zip(self._region_ids, self._parent_ids))
        self._region_parent_dict = dict(self._zipped_region_parent_ids)
        # colours
        self._region_colours = self._seg_handler['region_colors'][()].astype(float)
        self._region_colours_dict = dict(zip(self._region_ids, self._region_colours))
        self._parent_region_dict = _dict()
        for r, p in self._zipped_region_parent_ids:
            if p not in self._parent_region_dict:
                self._parent_region_dict[p] = [r]
            else:
                self._parent_region_dict[p] += [r]
        self._parent_region_dict[0] = self.root_parent_ids

    @property
    def header(self):
        """Collate group-level attributes in a dictionary"""
        return {
            'format': self.format,
            'format_version': self.format_version,
            'ijk_to_xyz_transform': self.ijk_to_xyz_transform,
            'map_level': self.map_level,
            'map_path': self.map_path,
            'map_size': self.map_size,
        }

    @property
    def file_path(self):
        """File path"""
        return os.path.dirname(os.path.abspath(self._fn))

    @property
    def file_name(self):
        """
        File name
        """
        return os.path.basename(os.path.abspath(self._fn))

    @property
    def name(self):
        """
        Name of the segmentation
        """
        return _decode(self._seg_handler.attrs['name'], 'utf-8')

    @property
    def format(self):
        """
        Format of the segmentation
        """
        return _decode(self._seg_handler.attrs['format'], 'utf-8')

    @property
    def format_version(self):
        """
        Format version
        """
        return self._seg_handler.attrs['format_version'].astype(int)

    @property
    def ijk_to_xyz_transform(self):
        """Image-to-physical space transform"""
        return self._seg_handler.attrs['ijk_to_xyz_transform'].astype(float)

    @property
    def map_level(self):
        """Map level (contour level)"""
        """
        :TODO: verify if this is the contour level
        """
        return self._seg_handler.attrs['map_level'].astype(float)

    @property
    def map_path(self):
        """Path to map file"""
        return _decode(self._seg_handler.attrs['map_path'], 'utf-8')

    @property
    def map_size(self):
        """Map dimensions (I, J, K)"""
        """
        :TODO: is the I, J, K notation correct?
        """
        try:
            return self._seg_handler.attrs['map_size'].astype(int)
        except KeyError:
            return self._seg_handler['mask'][()].shape

    @property
    def region_ids(self):
        """An iterable of region_ids"""
        return self._region_ids

    @property
    def parent_ids(self):
        """A dictionary of region_ids to parent_ids"""
        return self._parent_ids

    @property
    def root_parent_ids(self):
        """The """
        _root_parent_ids = filter(lambda r: r[1] == 0, self._zipped_region_parent_ids)
        return list(map(lambda r: r[0], _root_parent_ids))

    @property
    def region_colours(self):
        """A dictionary of region_ids to region_colors"""
        return self._region_colours_dict

    def get_parent_id(self, region_id):
        """Provides the parent_id given a region_id"""
        try:
            return self._region_parent_dict[region_id]
        except KeyError:
            raise ValueError("Unknown region of id {}".format(region_id))

    def get_region_ids(self, parent_id):
        """Provides the regions_ids associated with a parent_id"""
        try:
            return self._parent_region_dict[parent_id]
        except KeyError:
            raise ValueError("Unknow parent of id {}".format(parent_id))

    @property
    def mask(self):
        """The mask (TM)"""
        return self._seg_handler['mask'][()]

    def simplify_mask(self, mask, replace=True):
        """Simplify the mask by replacing all `region_ids` with their `root_parent_id`

        The `region_ids` and `parent_ids` are paired from which a tree is inferred. The root
        of this tree is value `0`. `region_ids` that have a corresponding `parent_id` of 0
        are penultimate roots. This method replaces each `region_id` with its penultimate `parent_id`.
        It *simplifies* the volume.

        :param bool replace: if `True` then the returned `mask` will have values; `False` will leave the `mask`
            unchanged (useful for running tests to speed things up)
        :return: `simplified_mask`, `segment_colours`, `segment_ids`
        :rtype: tuple
        """
        simplified_mask = numpy.ndarray(mask.shape, dtype=int)
        simplified_mask[:, :, :] = 0
        # group regions_ids by parent_id
        root_parent_id_group = _dict()
        for r in self.region_ids:
            p = get_root(self._region_parent_dict, r)
            if p not in root_parent_id_group:
                root_parent_id_group[p] = [r]
            else:
                root_parent_id_group[p] += [r]
        if replace:
            # It is vastly faster to use multiple array-wide comparisons than to do
            # comparisons element-wise. Therefore, we generate a string to be executed
            # that will do hundreds of array-wide comparisons at a time.
            # Each comparison is for all region_ids for a parent_id which will
            # then get assigned the parent_id.
            for parent_id, region_id_list in root_parent_id_group.items():
                # check whether any element in the mask has a value == r0 OR r1 ... OR rN
                # e.g. (mask == r0) | (mask == r1) | ... | (mask == rN)
                comp = ' | '.join(['( mask == %s )' % r for r in region_id_list])
                # set those that satisfy the above to have the parent_id
                # Because parent_ids are non-overlapping (i.e. no region_id has two parent_ids)
                # we can do successive summation instead of assignments.
                full_op = 'simplified_mask += (' + comp + ') * %s' % parent_id
                exec(full_op)
        else:
            simplified_mask = mask
        return simplified_mask

        # segment_ids = root_parent_id_group.keys()
        #
        # #     segment_colors = [r_c_zip[s] for s in segment_ids]
        #
        # return simplified_mask, segment_ids

    @property
    def ref_points(self):
        """A dictionary of region_ids to ref_points"""
        return dict(zip(self._seg_handler['region_ids'], self._seg_handler['ref_points']))

    @property
    def smoothing_levels(self):
        """A dictionary of region_ids to smoothing_levels"""
        return dict(zip(self._seg_handler['region_ids'], self._seg_handler['smoothing_levels']))

    @property
    def descriptions(self):
        """
        Returns a dictionary of descriptions for each region
        """
        if 'Description' in self._seg_handler:
            return dict(zip(self._seg_handler['Description/ids'], self._seg_handler['Description/values']))
        else:
            return None

    def __str__(self):
        string = 'Segger Segmentation\n'
        keys = filter(lambda x: x not in ['map_path', 'ijk_to_xyz_transform'], self.header.keys())
        values = [self.header[k] for k in keys]
        holder = "\n".join(['{:<20}:'.format(k) + ' {}' for k in keys])
        string += holder.format(*values)
        return string


def get_data(fn, *args, **kwargs):
    """Gets segmentation data from a Segger file"""
    return SeggerSegmentation(fn, *args, **kwargs)
