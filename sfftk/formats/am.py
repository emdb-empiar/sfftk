# -*- coding: utf-8 -*-
# am.py
"""
User-facing reader classes
"""
from __future__ import division

__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2016-11-10"


import os.path
import inspect
from base import Segmentation, Header, Segment, Annotation, Contours, Mesh
from .. import schema
from ..readers import amreader


"""
:TODO: handle meshes <hxsurface>
"""

class AmiraMeshMesh(Mesh):
    def __init__(self):
        self._vertices = None
        self._triangles = None
    @property
    def vertices(self):
        return self._vertices
    @property
    def triangles(self):
        return self._triangles
    def convert(self):
        mesh = schema.SFFMesh()
        vertices = schema.SFFVertexList()
        polygons = schema.SFFPolygonList()
        mesh.vertices = vertices
        mesh.polygons = polygons
        return mesh


class AmiraMeshAnnotation(Annotation):
    def __init__(self, material):
        self._material = material
    @property
    def description(self):
        try:
            return self._material.name
        except AttributeError:
            return None
    @property
    def colour(self):
        """Colour may or may not exist. Return None if it doesn't and the caller will determine what to do"""
        try:
            colour = self._material.Color
        except AttributeError:
            colour = None
        return colour
#         self.colour_to_material = colour_to_material
    def convert(self):
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.description
        annotation.numberOfInstances = 1
        if self.colour:
            red, green, blue = self.colour
        else:
            import random
            from warnings import warn
            red, green, blue = random.random(), random.random(), random.random()
            warn("Colour not defined for segment (Material) {}. Setting colour to random RGB value of {}".format(self.description, (red, green, blue)))
        
        colour = schema.SFFColour()
        colour.rgba = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
            )
        return annotation, colour


class AmiraMeshContours(Contours):
    def __init__(self, z_segment):
        self.z_segment = z_segment
    def __iter__(self):
        return iter(self.z_segment)
    def convert(self):
        contours = schema.SFFContourList()
        for z, cs in self.z_segment.iteritems(): # for each contour_set at this value of z
            for c in cs: # for each contour in the contour set (at this value of z)
                contour = schema.SFFContour()
                for x, y in c: # for each point (x,y) in the contour (at this value of z)
                    # add the point as an SFFContourPoint to the contour (as an SFFContour) 
                    contour.add_point(
                        schema.SFFContourPoint(x=x, y=y, z=z) 
                        )
                contours.add_contour(contour) # add the contour to the list of contours (as an SFFContourList)
        return contours


class AmiraMeshSegment(Segment):
    def __init__(self, header, segment_id, segment):
        """Initialisor of AmiraMeshSegment
        
        :param header: an ``AmiraMeshHeader`` object containing header metadata
        :type header: AmiraMeshHeader
        :param int segment_id: the integer identifier for this segment ('Id' in Materials)
        :param dict segment: dictionary of z value to ``amira.data_streams.ContourSets`` objects (lists of ``amira.data_streams.Contour`` objects)
        """ 
        self._header = header
        self.id = segment_id
        self._segment = segment
    @property
    def material(self):
        """Material may or may not exist. Return None if it doesn't and the caller will determine what to do"""
        try: # assume that we have materials defined
            material = self._header.parameters.Materials[self.id + 1] # Ids are 1-based but in the images are 0-based
        except AttributeError:
            material = None
        return material
    @property
    def annotation(self):
        return AmiraMeshAnnotation(self.material)
    @property
    def contours(self):
        return AmiraMeshContours(self._segment)
    @property
    def meshes(self):
        return None
    def convert(self):
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        segment.contours = self.contours.convert()
        return segment


class AmiraMeshHeader(Header):
    def __init__(self, header):
        self._header = header
    
        for attr in dir(header):
            if attr[:2] == "__":
                continue
            elif inspect.ismethod(getattr(self._header, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._header, attr))


class AmiraMeshSegmentation(Segmentation):
    def __init__(self, fn, *args, **kwargs):
        self._fn = fn   
        self._header, self._segmentation = amreader.get_data(self._fn, *args, **kwargs)
    """
    :TODO: use hidden attributes instead
    """
    @property
    def header(self):
        return AmiraMeshHeader(self._header)
    @property
    def segments(self):
        segments = list()
        for stream in self._segmentation.itervalues():
            for segment_id, segment in stream.iteritems():
                segments.append(AmiraMeshSegment(self.header, segment_id, segment))
        return segments
    def convert(self, *args, **kwargs):
        segmentation = schema.SFFSegmentation()
        
        if 'name' in kwargs:
            segmentation.name = kwargs['name']
        else:
            segmentation.name = "AmiraMesh Segmentation"
        segmentation.version = segmentation.version # strange but this is how it works!
        segmentation.software = schema.SFFSoftware(
            name="Amira",
            version=kwargs['softwareVersion'] if 'softwareVersion' in kwargs else "{}".format(self.header.designation.version),
            processingDetails=kwargs['processingDetails'] if 'processingDetails' in kwargs else "None",
            )
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
                )
            )
        segmentation.filePath = os.path.abspath(self._fn)
        segmentation.primaryDescriptor = "contourList"
        
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert() 
            segments.add_segment(segment)
        
        # finally pack everyting together
        segmentation.segments = segments
        
        if 'details' in kwargs:
            segmentation.details = kwargs['details']
        return segmentation
            
