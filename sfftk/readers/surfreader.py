# -*- coding: utf-8 -*-
"""
sfftk.readers.surfreader
=========================

Ad hoc reader for Amira HyperSurface files
"""
from __future__ import division, print_function

import random
import sys

# import ahds.data_stream
# import ahds.header
from ahds import AmiraFile


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-06"
__updated__ = '2018-02-14'


# class HxSurfSegment(object):
#     """Generic HxSurface segment class
#
#     The `ahds <http://ahds.readthedocs.io/en/latest/>`_ package provides a better abstraction of this filetype
#     """
#     def __init__(self, material, vertices, triangles):
#         self._material = material
#         # id
#         self._segment_id = self._material.Id
#         # name
#         if self._material.name:
#             self._name = self._material.name
#         else:
#             self._name = None
#         # colour
#         if self._material.Color:
#             self._colour = self._material.Color
#         else:
#             r, g, b = random.random(), random.random(), random.random()
#             self._colour = r, g, b
#             print("Warning: random colour ({:.4f}, {:.4f}, {:.4f}) for segment {}".format(r, g, b, self._segment_id),
#                   file=sys.stderr)
#         # vertices and triangles
#         self._vertices = vertices
#         self._triangles = triangles
#     @property
#     def id(self):
#         """The segment ID"""
#         return self._segment_id
#     @property
#     def name(self):
#         """The name of the segment"""
#         return self._name
#     @property
#     def colour(self):
#         """The colour of the segment"""
#         return self._colour
#     @property
#     def vertices(self):
#         """The set of vertices in this segment"""
#         return self._vertices
#     @property
#     def triangles(self):
#         """The set of triangles in this segment"""
#         return self._triangles
#
#
# def vertices_for_patches(vertices, patches):
#     """Compiles the set of vertices for the list of patches only read from an Amira HyperSurface file
#
#     :param vertices: a sequence of vertices (see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package)
#     :type vertices: ``ahds.data_stream.VerticesDataStream``
#     :param list patches: a list of patches each of class ``ahds.data_stream.PatchesDataStream`` ((see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package)
#     :return dict patches_vertices: the vertices only referenced from this patch
#     """
#     # first we make a dictionary of vertices
#     # keys are indices (1-based)
#     vertices_list = vertices.decoded_data
#     vertices_dict = dict(zip(range(1, len(vertices_list) + 1), vertices_list))
#     # then we repack the vertices and patches into vertices and triangles (collate triangles from all patches)
#     patches_vertices = dict()
#     patch_triangles = list()
#     for patch in patches:
#         triangles = patch['Triangles'].decoded_data
#         patch_triangles += triangles
#         for v1, v2, v3 in triangles:
#             if v1 not in patches_vertices:
#                 patches_vertices[v1] = vertices_dict[v1]
#             if v2 not in patches_vertices:
#                 patches_vertices[v2] = vertices_dict[v2]
#             if v3 not in patches_vertices:
#                 patches_vertices[v3] = vertices_dict[v3]
#     return patches_vertices, patch_triangles


class HxSurfSegment(object):
    """Generic HxSurface segment class

    The `ahds <http://ahds.readthedocs.io/en/latest/>`_ package provides a better abstraction of this filetype
    """

    def __init__(self, material, vertices, triangles, prune=True):
        """A single segment from an Amira HxSurface file

        Each such segment corresponds to an HxSurface patch. This is a convenience class to present
        key attributes (id, name, colour).

        :param material: an individual Block object with the Material block
        :param dict vertices: a dictionary of vertices indexed by vertex_ids (which appear in the triangles list)
        :param list triangles: a list of 3-lists containing vertex IDs which define each triangle
        :param bool prune: whether or not the prune the vertices for this segment/patch so that we only bear the
        vertices referenced here; default is True
        """
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
        if prune:
            self._vertices = self._prune_vertices(vertices, triangles)
        else:
            self._vertices = vertices
        self._triangles = triangles
        # print(self._triangles[:20], list(map(lambda x: (x, self._vertices[x]), list(self._vertices.keys())[:20])))

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
        """A dictionary of vertices in this segment indexed by vertex ID"""
        return self._vertices

    @property
    def triangles(self):
        """A list of triangles (lists with 3 vertex IDs) in this segment"""
        return self._triangles

    def _prune_vertices(self, vertices, triangles):
        """Reduce the vertices and triangles to only those required by this segment"""
        # flatten the list of vertex ids in triangles
        unique_vertex_ids = set([vertex for triangle in triangles for vertex in triangle])
        # get only those vertices present in this segments triangles
        unique_vertices = {vertex: vertices[vertex] for vertex in unique_vertex_ids}
        return unique_vertices


def extract_segments(af, *args, **kwargs):
    """Extract patches as segments

    :param af: an `AmiraFile` object
    :return dict segments: a dictionary of segments with keys set to Material Ids (voxel values)
    """
    # make sure it's an AmiraFile object
    try:
        assert isinstance(af, AmiraFile)
    except AssertionError:
        raise TypeError("must be a valid AmiraFile object")
    # make sure it's read otherwise read it
    if not af.meta.streams_loaded:
        print("Data streams not yet loaded. Reading...", file=sys.stderr)
        af.read()
    segments = dict()
    # first we make a dictionary of vertices
    # keys are indices (1-based)
    vertices_list = af.data_streams.Data.Vertices.data
    # a dictionary of all vertices
    vertices_dict = dict(zip(range(1, len(vertices_list) + 1), vertices_list))
    # then we repack the vertices and patches into vertices and triangles (collate triangles from all patches)
    for patch in af.data_streams.Data.Vertices.Patches:
        material = af.header.Parameters.Materials.material_dict[patch.InnerRegion]
        patch_id = material.Id
        # sanity check
        if patch_id is None:
            raise ValueError('patch ID is None')
        # now collate triangles and vertices
        triangles = patch.Triangles.data
        hxsurfsegment = HxSurfSegment(material, vertices_dict, triangles.tolist(), *args, **kwargs)
        if patch_id not in segments:
            segments[patch_id] = [hxsurfsegment]
        else:
            segments[patch_id] += [hxsurfsegment]
    return segments


def get_data(fn, *args, **kwargs):
    """Get segmentation data from the Amira HxSurface file
    
    :param str fn: file name
    :return header: AmiraHxSurface header
    :rtype header: ``ahds.header.AmiraHeader`` (see `ahds <http://ahds.readthedocs.io/en/latest/>`_ package)
    :return dict segments: segments each of class :py:class:`sfftk.readers.surfreader.HxSurfSegment`
    """
    af = AmiraFile(fn, load_streams=True, *args, **kwargs)
    segments = extract_segments(af, *args, **kwargs)
    return af.header, segments
    """
    header = ahds.header.AmiraHeader.from_file(fn, *args, **kwargs)
    data_streams = ahds.data_stream.DataStreams(fn, *args, **kwargs)
    segments = dict()
    for patch_name in data_streams['Patches']:
        patch_material = getattr(header.Parameters.Materials, patch_name)
        patch_vertices, patch_triangles = vertices_for_patches(data_streams['Vertices'], data_streams['Patches'][patch_name])
        # we use the material ID as the key because it is a unique reference to the patch
        # segments[patch_material.Id] = (patch_vertices, patch_triangles)
        segments[patch_material.Id] = HxSurfSegment(patch_material, patch_vertices, patch_triangles)
    return header, segments
    """


