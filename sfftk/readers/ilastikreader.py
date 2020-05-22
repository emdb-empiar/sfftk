# -*- coding: utf-8 -*-
"""
``sfftk.readers.ilastikreader``
===========================

Ad hoc reader for ilastik segmentation files
"""
import h5py
import numpy
class IlastikSegmentation(object):
    """Encapsulation of an Ilastik segmentation"""
    def __init__(self, fn, dataset_name=u'exported_data', axis_order='zyxc', *args, **kwargs):
        self._fn = fn
        self._axis_order = axis_order
        with h5py.File(fn, 'r') as h:
            self._data = h[dataset_name][()][:,:,:,0]
        # segment_ids
        indices_set = set(numpy.unique(self._data))
        self._segment_ids = list(indices_set.difference({0}))  # do not include '0' as a label

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
