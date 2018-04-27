# -*- coding: utf-8 -*-
"""
sfftk.readers.surfreader
=========================

Ad hoc reader for Amira HyperSurface files
"""
from __future__ import division, print_function

import random
import sys

import ahds.data_stream
import ahds.header


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-06"
__updated__ = '2018-02-14'


class HxSurfSegment(object):
    """Generic HxSurface segment class
    
    The `ahds <http://ahds.readthedocs.io/en/latest/>`_ package provides a better abstraction of this filetype
    """
    def __init__(self, material, vertices, triangles):
        self._material = material
        # id
        self._segment_id = self._material.Id
        # name
        if self._material.name:
            self._name = self._material.name
        else:
            self._name = None
        # colour
        if self._material.Color:
            self._colour = self._material.Color
        else:
            r, g, b = random.random(), random.random(), random.random()
            self._colour = r, g, b
            print("Warning: random colour ({:.4f}, {:.4f}, {:.4f}) for segment {}".format(r, g, b, self._segment_id),
                  file=sys.stderr)
        # vertices and triangles
        self._vertices = vertices
        self._triangles = triangles
    @property
    def id(self):
        """The segment ID"""
        return self._segment_id
    @property
    def name(self):
        """The name of the segment"""
        return self._name
    @property
    def colour(self):
        """The colour of the segment"""
        return self._colour
    @property
    def vertices(self):
        """The set of vertices in this segment"""
        return self._vertices
    @property
    def triangles(self):
        """The set of triangles in this segment"""
        return self._triangles


def vertices_for_patches(vertices, patches):
    """Compiles the set of vertices for the list of patches only read from an Amira HyperSurface file
    
    :param vertices: a sequence of vertices (see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package)
    :type vertices: ``ahds.data_stream.VerticesDataStream``
    :param list patches: a list of patches each of class ``ahds.data_stream.PatchesDataStream`` ((see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package) 
    :return dict patches_vertices: the vertices only referenced from this patch 
    """
    # first we make a dictionary of vertices
    # keys are indices (1-based)
    vertices_list = vertices.decoded_data
    vertices_dict = dict(zip(range(1, len(vertices_list) + 1), vertices_list))
    # then we repack the vertices and patches into vertices and triangles (collate triangles from all patches)
    patches_vertices = dict()
    patch_triangles = list()
    for patch in patches:
        triangles = patch['Triangles'].decoded_data
        patch_triangles += triangles
        for v1, v2, v3 in triangles:
            if v1 not in patches_vertices:
                patches_vertices[v1] = vertices_dict[v1]
            if v2 not in patches_vertices:
                patches_vertices[v2] = vertices_dict[v2]
            if v3 not in patches_vertices:
                patches_vertices[v3] = vertices_dict[v3]
    return patches_vertices, patch_triangles


def get_data(fn, *args, **kwargs):
    """Get segmentation data from the Amira HxSurface file
    
    :param str fn: file name
    :return header: AmiraHxSurface header
    :rtype header: ``ahds.header.AmiraHeader`` (see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package)
    :return dict segments: segments each of class :py:class:`sfftk.readers.surfreader.HxSurfSegment`
    """
    header = ahds.header.AmiraHeader.from_file(fn, *args, **kwargs)
    data_streams = ahds.data_stream.DataStreams(fn, *args, **kwargs)
    segments = dict()
    for patch_name in data_streams['Patches']:
        patch_material = getattr(header.parameters.Materials, patch_name)
        patch_vertices, patch_triangles = vertices_for_patches(data_streams['Vertices'], data_streams['Patches'][patch_name])
        # we use the material ID as the key because it is a unique reference to the patch
        segments[patch_material.Id] = (patch_vertices, patch_triangles)
        segments[patch_material.Id] = HxSurfSegment(patch_material, patch_vertices, patch_triangles)
    return header, segments
