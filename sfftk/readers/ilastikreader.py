"""
``sfftk.readers.ilastikreader``
===========================

Ad hoc reader for ilastik segmentation files
"""
import h5py
import numpy


class IlastikSegmentation(object):
    """Encapsulation of an Ilastik segmentation"""

    def __init__(self, fn, dataset_name='exported_data', axis_order='zyxc', *args, **kwargs):
        self._fn = fn
        self._axis_order = axis_order
        self._dataset_name = dataset_name
        with h5py.File(fn, 'r') as h:
            self._size = h[dataset_name].size  # number of voxels
            self._dtype = h[dataset_name].dtype  # the data type of each voxel
            self._data = h[dataset_name][()][:, :, :, 0].astype(int)
            self._shape = self._data.shape  # we don't use the shape provided directly
            self._len = h[dataset_name].len()  # the size of the first axis (usually z)
            # some attributes
            self._axistags = h[dataset_name].attrs['axistags']
            self._display_mode = h[dataset_name].attrs['display_mode']
            self._drange = h[dataset_name].attrs['drange']
        # segment_ids
        indices_set = set(numpy.unique(self._data))
        self._segment_ids = list(indices_set.difference({0}))  # do not include '0' as a label

    @property
    def num_voxels(self):
        return self._size

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return self._shape

    @property
    def num_images(self):
        return self._len

    @property
    def filename(self):
        return self._fn

    @property
    def data(self):
        return self._data

    @property
    def segment_ids(self):
        return self._segment_ids

    @property
    def segment_count(self):
        return len(self._segment_ids)


def get_data(fn, *args, **kwargs):
    return IlastikSegmentation(fn, *args, **kwargs)
