# -*- coding: utf-8 -*-
# surf.py
"""
User-facing reader classes
"""
from __future__ import division

__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2016-11-11"


import os.path
import inspect
from base import Segmentation, Header, Segment, Annotation, Mesh
from .. import schema
from ..readers import stlreader


class STLMesh(Mesh):
    def __init__(self, vertices, polygons):
        self._vertices = vertices
        self._polygons = polygons
    @property
    def vertices(self):
        return self._vertices
    @property
    def polygons(self):
        return self._polygons
    def convert(self):
        schema.SFFMesh.reset_id()
        mesh = schema.SFFMesh()
        # polygon
        polygons = schema.SFFPolygonList()
        schema.SFFPolygon.reset_id()
        for P in self.polygons.itervalues():
            polygon = schema.SFFPolygon()
             
            v1, v2, v3 = P
            polygon.add_vertex(v1)
            polygon.add_vertex(v2)
            polygon.add_vertex(v3)
             
            polygons.add_polygon(polygon)
        # vertices
        vertices = schema.SFFVertexList()
        for vertex_id, v in self.vertices.iteritems():
            x, y, z = v
            vertex = schema.SFFVertex(vID=vertex_id, x=x, y=y, z=z)
            vertices.add_vertex(vertex)
        # final tying
        mesh.vertices = vertices
        mesh.polygons = polygons
        return mesh


class STLAnnotation(Annotation):
    def __init__(self, name):
        self.name = name
        import random
        self.colour = tuple([random.random() for _ in xrange(3)])
    def convert(self):
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.name
        annotation.numberOfInstances = 1
        
        red, green, blue = self.colour
        colour = schema.SFFColour()
        colour.rgba=schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
            )
        return annotation, colour 


class STLSegment(Segment):
    def __init__(self, name, vertices, polygons):
        self._name = name
        self._vertices = vertices
        self._polygons = polygons
    @property
    def name(self):
        return self._name
    @property
    def annotation(self):
        return STLAnnotation(self.name)
    @property
    def meshes(self):
        return [STLMesh(self._vertices, self._polygons)]
    def convert(self):
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for mesh in self.meshes:
            meshes.add_mesh(mesh.convert())
        segment.meshes = meshes
        return segment


class STLHeader(Header):
    def __init__(self, segmentation):
        self._segmentation = segmentation
        
        for attr in dir(self._segmentation):
            if attr[:1] == "_":
                continue
            elif inspect.ismethod(getattr(self._segmentation, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._segmentation, attr))


class STLSegmentation(Segmentation):
    def __init__(self, fn):
        self._fn = fn
        self._segmentation = stlreader.get_data(self._fn)
        self._segments = [STLSegment(name, vertices, polygons) for name, vertices, polygons in self._segmentation]
    @property
    def header(self):
        return STLHeader(self._segmentation)
    @property
    def segments(self):
        return self._segments
    def convert(self, *args, **kwargs):
        segmentation = schema.SFFSegmentation()
        
        segmentation.name = "STL Segmentation"
        segmentation.software = schema.SFFSoftware(
            name="Unknown",
            version="Unknown",
            )
        segmentation.transforms = schema.SFFTransformList()
        segmentation.filePath = os.path.abspath(self._fn)
        segmentation.primaryDescriptor = "meshList"
        
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segments.add_segment(s.convert())

        segmentation.segments = segments
        # details
        if 'details' in kwargs:
            segmentation.details = kwargs['details']
        return segmentation
        