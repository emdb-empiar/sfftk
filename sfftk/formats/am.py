# -*- coding: utf-8 -*-
# am.py
'''
sfftk.formats.am
================

User-facing reader classes for AmiraMesh files

'''
from __future__ import division

import inspect
import os.path

from .. import schema
from ..core.print_tools import print_date
from ..readers import amreader
from .base import Segmentation, Header, Segment, Annotation, Contours, Mesh, Volume

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-10"
__updated__ = '2018-02-23'


'''
:TODO: handle meshes <hxsurface>
'''

class AmiraMeshMesh(Mesh):
    '''Mesh class'''
    def __init__(self):
        self._vertices = None
        self._triangles = None

    @property
    def vertices(self):
        '''Vertices in mesh'''
        return self._vertices

    @property
    def triangles(self):
        '''Triangles in mesh'''
        return self._triangles

    def convert(self):
        '''Convert to :py:class:`sfftk.schema.SFFMesh` object'''
        mesh = schema.SFFMesh()
        vertices = schema.SFFVertexList()
        polygons = schema.SFFPolygonList()
        mesh.vertices = vertices
        mesh.polygons = polygons
        return mesh


class AmiraMeshAnnotation(Annotation):
    '''Annotation class'''
    def __init__(self, material):
        self._material = material

    @property
    def description(self):
        '''Segment description'''
        try:
            return self._material.name
        except AttributeError:
            return None

    @property
    def colour(self):
        '''Segment colour
        
        Colour may or may not exist. Return None if it doesn't and the caller will determine what to do'''
        try:
            colour = self._material.Color
        except AttributeError:
            colour = None
        return colour
#         self.colour_to_material = colour_to_material

    def convert(self):
        '''Convert to :py:class:`sfftk.schema.SFFBiologicalAnnotation` object'''
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.description
        annotation.numberOfInstances = 1
        if self.colour:
            red, green, blue = self.colour
        else:
            import random
            red, green, blue = random.random(), random.random(), random.random()
            print_date("Colour not defined for segment (Material) {}. Setting colour to random RGB value of {}".format(self.description, (red, green, blue)))

        colour = schema.SFFColour()
        colour.rgba = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
            )
        return annotation, colour


class AmiraMeshContours(Contours):
    '''Contour container class'''
    def __init__(self, z_segment):
        self.z_segment = z_segment
    def __iter__(self):
        return iter(self.z_segment)
    def convert(self):
        '''Convert to :py:class:`sfftk.schema.SFFContourList` object'''
        contours = schema.SFFContourList()
        for z, cs in self.z_segment.iteritems():  # for each contour_set at this value of z
            for c in cs:  # for each contour in the contour set (at this value of z)
                contour = schema.SFFContour()
                for x, y in c:  # for each point (x,y) in the contour (at this value of z)
                    # add the point as an SFFContourPoint to the contour (as an SFFContour)
                    contour.add_point(
                        schema.SFFContourPoint(x=x, y=y, z=z)
                        )
                contours.add_contour(contour)  # add the contour to the list of contours (as an SFFContourList)
        return contours


class AmiraMeshVolume(Volume):
    '''Volume container class'''
    def __init__(self, fn, header):
        self._fn = fn
        self._header = header

    def convert(self):
        '''Convert to :py:class:`sfftk.schema.SFFThreeDVolume` object'''
        volume = schema.SFFThreeDVolume()
        # make file
        hdf5_fn = "".join(self._fn.split('.')[:-1]) + '.hdf'
        volume.file = os.path.basename(hdf5_fn)
        volume.format = "Segger"
        return volume


# class AmiraMeshSegment(Segment):
#     '''Segment class'''
#     def __init__(self, header, segment_id, segment):
#         '''Initialiser of AmiraMeshSegment
#
#         :param header: an ``AmiraMeshHeader`` object containing header metadata
#         :type header: AmiraMeshHeader
#         :param int segment_id: the integer identifier for this segment ('Id' in Materials)
#         :param dict segment: dictionary of z value to ``amira.data_streams.ContourSets`` objects (lists of ``amira.data_streams.Contour`` objects)
#         '''
#         self._header = header
#         self.id = segment_id
#         self._segment = segment
#     @property
#     def material(self):
#         '''Material may or may not exist. Return None if it doesn't and the caller will determine what to do'''
#         try: # assume that we have materials defined
#             material = self._header.parameters.Materials[self.id + 1] # Ids are 1-based but in the images are 0-based
#         except AttributeError:
#             material = None
#         return material
#     @property
#     def annotation(self):
#         '''Segment annotation'''
#         return AmiraMeshAnnotation(self.material)
#     @property
#     def contours(self):
#         '''Contours in this segment'''
#         return AmiraMeshContours(self._segment)
#     @property
#     def meshes(self):
#         '''Meshes in this segment'''
#         return None
#     def convert(self):
#         '''Convert to :py:class:`sfftk.schema.SFFSegment` object'''
#         segment = schema.SFFSegment()
#         segment.biologicalAnnotation, segment.colour = self.annotation.convert()
#         segment.contours = self.contours.convert()
#         return segment


class AmiraMeshSegment(Segment):
    '''Segment class'''
    def __init__(self, fn, header, segment_id):
        '''Initialiser of AmiraMeshSegment
         
        :param header: an ``AmiraMeshHeader`` object containing header metadata
        :type header: AmiraMeshHeader
        :param int segment_id: the integer identifier for this segment ('Id' in Materials)
        '''
        self._fn = fn
        self._header = header
        self._segment_id = segment_id

    @property
    def segment_id(self):
        return self._segment_id

    @property
    def material(self):
        '''Material may or may not exist. Return None if it doesn't and the caller will determine what to do'''
        try:  # assume that we have materials defined
            material = self._header.parameters.Materials[self.segment_id]  # Ids are 1-based but in the images are 0-based
        except AttributeError:
            material = None
        return material

    @property
    def annotation(self):
        '''Segment annotation'''
        return AmiraMeshAnnotation(self.material)

    @property
    def volume(self):
        '''The segmentation as a volume'''
        return AmiraMeshVolume(self._fn, self._header)

    def convert(self):
        '''Convert to :py:class:`sfftk.schema.SFFSegment` object'''
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        segment.volume = self.volume.convert()
        return segment


class AmiraMeshHeader(Header):
    '''Header class'''
    def __init__(self, header):
        self._header = header

        for attr in dir(header):
            if attr[:2] == "__":
                continue
            elif inspect.ismethod(getattr(self._header, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._header, attr))

    def convert(self, *args, **kwargs):
        pass


class AmiraMeshSegmentation(Segmentation):
    '''Class representing an AmiraMesh segmentation
    
    .. code:: python
    
        from sfftk.formats.am import AmiraMeshSegmentation
        am_seg = AmiraMeshSegmentation('file.am')
        
    '''
    def __init__(self, fn, *args, **kwargs):
        self._fn = fn
        self._header, self._volume = amreader.get_data(self._fn, *args, **kwargs)

    @property
    def header(self):
        '''The AmiraMesh header obtained using the ``ahds`` package
        
        The header is wrapped with a generic AmiraMeshHeader class 
        '''
        return AmiraMeshHeader(self._header)

    @property
    def segments(self):
        '''Segments in this segmentation'''
        segments = list()
        if hasattr(self.header.parameters, 'Materials') or hasattr(self.header.parameters, 'materials'):
            for segment_id in self.header.parameters.Materials.ids:
                segments.append(AmiraMeshSegment(self._fn, self.header, segment_id))
        else:
            indices_set = set(self._volume.flatten().tolist())
            segment_indices = indices_set.difference(set([0]))
            for segment_id in segment_indices:
                segments.append(AmiraMeshSegment(self._fn, self.header, segment_id))
        return segments
        '''
        segments = list()
        for stream in self._segmentation.itervalues():
            for segment_id, segment in stream.iteritems():
                segments.append(AmiraMeshSegment(self.header, segment_id, segment))
        return segments
        '''

    def convert(self, args, *_args, **_kwargs):
        '''Convert to :py:class:`sfftk.schema.SFFSegmentation` object'''
        segmentation = schema.SFFSegmentation()

        # volume mask
        # make file
        hdf5_fn = "".join(self._fn.split('.')[:-1]) + '.hdf'
        # write hdf5 contents file
        import h5py

        with h5py.File(hdf5_fn, 'w') as f:
            print_date("Writing volume data to /mask in {}...".format(hdf5_fn))
            _ = f.create_dataset("mask", data=self._volume)

        if 'name' in _kwargs:
            segmentation.name = _kwargs['name']
        else:
            segmentation.name = "AmiraMesh Segmentation"
#         segmentation.version = segmentation.version # strange but this is how it works!
        segmentation.software = schema.SFFSoftware(
            name="Amira",
            version=_kwargs['softwareVersion'] if 'softwareVersion' in _kwargs else "{}".format(self.header.designation.version),
            processingDetails=_kwargs['processingDetails'] if 'processingDetails' in _kwargs else "None",
            )
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
                )
            )
        segmentation.filePath = os.path.dirname(os.path.abspath(self._fn))
        segmentation.primaryDescriptor = "threeDVolume"

        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
            segments.add_segment(segment)

        # finally pack everyting together
        segmentation.segments = segments

        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']
        return segmentation

