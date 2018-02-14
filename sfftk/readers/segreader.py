# -*- coding: utf-8 -*-
'''
sfftk.readers.segreader
========================

Ad hoc reader for Segger files
'''
from __future__ import division

import os


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-01"
__updated__ = '2018-02-14'


def get_root(region_parent_zip, region_id):
    '''
    Return the penultimate `parent_id` for any `region_id`.
    
    The penultimate parent is one layer below the root (0).
    The set of penultimate parents are the distinct regions contained in the segmentation.
    They correspond to putative functional regions.

    :param tuple region_parent_zip: a list of 2-tuples of `region_ids` and `parent_ids`
    :param int region_id: the `region_id` whose root parent_id is sought
    :return int parent_id: the corresponding penultimate `parent_id` (one step below the root - value of `0`)    
    '''
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
    '''Encapsulation of a Segger segmentation'''
    def __init__(self, fn, *args, **kwargs):
        '''Initialiser of Segger Segmentation objects'''

        import h5py  # only import
        self._fn = fn
        '''
        :TODO: args and kwargs
        '''
        self._seg_handler = h5py.File(fn, *args, **kwargs)
        # region/parent ids
        self._region_ids = self._seg_handler['region_ids'].value
        self._parent_ids = self._seg_handler['parent_ids'].value
        self._zipped_region_parent_ids = zip(self._region_ids, self._parent_ids)
        self._region_parent_dict = dict(self._zipped_region_parent_ids)
        # colours
        self._region_colours = self._seg_handler['region_colors'].value
        self._region_colours_dict = dict(zip(self._region_ids, self._region_colours))
        self._parent_region_dict = dict()
        for r, p in self._zipped_region_parent_ids:
            if p not in self._parent_region_dict:
                self._parent_region_dict[p] = [r]
            else:
                self._parent_region_dict[p] += [r]
        self._parent_region_dict[0] = self.root_parent_ids
    @property
    def header(self):
        '''Collate group-level attributes in a dictionary'''
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
        '''File path'''
        return os.path.dirname(os.path.abspath(self._fn))
    @property
    def file_name(self):
        '''File name'''
        return os.path.basename(os.path.abspath(self._fn))
    @property
    def name(self):
        '''Name of the segmentation'''
        return self._seg_handler.attrs['name']
    @property
    def format(self):
        '''Format of the segmentation'''
        return self._seg_handler.attrs['format']
    @property
    def format_version(self):
        '''Format version'''
        return self._seg_handler.attrs['format_version']
    @property
    def ijk_to_xyz_transform(self):
        '''Image-to-physical space transform'''
        return self._seg_handler.attrs['ijk_to_xyz_transform']
    @property
    def map_level(self):
        '''Map level (contour level)'''
        '''
        :TODO: verify if this is the contour level
        '''
        return self._seg_handler.attrs['map_level']
    @property
    def map_path(self):
        '''Path to map file'''
        return self._seg_handler.attrs['map_path']
    @property
    def map_size(self):
        '''Map dimensions (I, J, K)'''
        '''
        :TODO: is the I, J, K notation correct?
        '''
        return self._seg_handler.attrs['map_size']
    @property
    def region_ids(self):
        '''An iterable of region_ids'''
        return self._region_ids
    @property
    def parent_ids(self):
        '''A dictionary of region_ids to parent_ids'''
        return self._parent_ids
    @property
    def root_parent_ids(self):
        '''The '''
        _root_parent_ids = filter(lambda r: r[1] == 0, self._zipped_region_parent_ids)
        return map(lambda r: r[0], _root_parent_ids)
    @property
    def region_colours(self):
        '''A dictionary of region_ids to region_colors'''
        return self._region_colours_dict
    def get_parent_id(self, region_id):
        '''Provides the parent_id given a region_id'''
        try:
            return self._region_parent_dict[region_id]
        except KeyError:
            raise ValueError("Unknown region of id {}".format(region_id))
    def get_region_ids(self, parent_id):
        '''Provides the regions_ids associated with a parent_id'''
        try:
            return self._parent_region_dict[parent_id]
        except KeyError:
            raise ValueError("Unknow parent of id {}".format(parent_id))
    @property
    def mask(self):
        '''The mask (TM)'''
        return self._seg_handler['mask']
    @property
    def ref_points(self):
        '''A dictionary of region_ids to ref_points'''
        return dict(zip(self._seg_handler['region_ids'], self._seg_handler['ref_points']))
    @property
    def smoothing_levels(self):
        '''A dictionary of region_ids to smoothing_levels'''
        return dict(zip(self._seg_handler['region_ids'], self._seg_handler['smoothing_levels']))
    @property
    def descriptions(self):
        '''Returns a dictionary of descriptions for each region'''
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
    '''Gets segmentation data from a Segger file'''
    return SeggerSegmentation(fn, *args, **kwargs)
