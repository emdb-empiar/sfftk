# -*- coding: utf-8 -*-
# map.py
"""
User-facing reader classes
"""
from __future__ import division

__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2016-11-09"


import os.path
import inspect
from base import Segmentation, Header, Segment, Annotation, Volume
from .. import schema
from ..readers import mapreader 


class MapVolume(Volume):
    def __init__(self, segmentation, *args, **kwargs):
        self._segmentation = segmentation
        self.voxels = segmentation._segmentation.voxels
        
    def convert(self, *args, **kwargs):
        volume = schema.SFFThreeDVolume()

        # make file
        hdf5_fn = "".join(self._segmentation._fn.split('.')[:-1]) + '.hdf'
        
        volume.file = os.path.basename(os.path.abspath(hdf5_fn))
        volume.format = "MRC"
        
        # write hdf5 contents file
        import h5py
                        
        with h5py.File(hdf5_fn, 'w') as f:
            # mask dataset in root group
            _ = f.create_dataset("mask", data=self.voxels)
        
        return volume


class MapAnnotation(Annotation):
    @property
    def description(self):
        return None
    @property
    def colour(self):
        return None
    def convert(self):
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.description
        annotation.numberOfInstances = 1
        import random
        from warnings import warn
        red, green, blue = random.random(), random.random(), random.random()
        warn("Colour not defined for mask segments. Setting colour to random RGB value of {}".format((red, green, blue)))
        
        colour = schema.SFFColour()
        colour.rgba = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
            )
        return annotation, colour


class MapSegment(Segment):
    def __init__(self, segmentation):
        self._segmentation = segmentation
    @property
    def annotation(self):
        return MapAnnotation()
    @property
    def volume(self):
        return MapVolume(self._segmentation)
    def convert(self):
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        segment.volume = self.volume.convert()
        return segment
    
    
class MapHeader(Header):
    def __init__(self, segmentation):
        self._segmentation = segmentation._segmentation
        for attr in dir(self._segmentation):
            if attr[:2] == "__" or attr[:1] == "_":
                continue
            if inspect.ismethod(getattr(self._segmentation, attr)):
                continue
            if attr == "voxels": # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._segmentation, attr))


class MapSegmentation(Segmentation):
    """``MapSegmentation`` reader"""
    def __init__(self, fn, *args, **kwargs):
        """Initialise the MapSegmentation reader"""
        self._fn = fn   
        
        # set the segmentation attribute
        self._segmentation = mapreader.get_data(fn)
    """
    :TODO: document attributes and methods of readers
    """
    @property
    def header(self):
        return MapHeader(self)
    @property
    def segments(self): # only one segment 
        return [MapSegment(self)]
    def convert(self, *args, **kwargs):
        segmentation = schema.SFFSegmentation()
        
        segmentation.name = self.header.name
                
        # software
        segmentation.software = schema.SFFSoftware(
            name="Undefined",
            version="Undefined",
            processingDetails='None'
            )
        segmentation.filePath = os.path.dirname(os.path.abspath(self._fn))
        segmentation.primaryDescriptor = "threeDVolume"
                
        # transforms
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=3,
                data=self.header.skew_matrix_data,
                )
            )
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=1,
                data=self.header.skew_translation_data,
                )
            )
        
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
            segments.add_segment(segment)
        
        # finally pack everything together
        segmentation.segments = segments
        
        if 'details' in kwargs:
            segmentation.details = kwargs['details']
        return segmentation
