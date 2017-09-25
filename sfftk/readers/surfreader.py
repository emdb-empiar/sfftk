# -*- coding: utf-8 -*-
# surfreader.py
"""
sfftk.readers.surfreader



Copyright 2017 EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. 

See the License for the specific language governing permissions 
and limitations under the License.
"""

from __future__ import division

import sys
import random
import ahds.header
import ahds.data_stream


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-06"


class HxSurfSegment(object):
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
            print >> sys.stderr, "Warning: random colour ({:.4f}, {:.4f}, {:.4f}) for segment {}".format(r, g, b, self._segment_id)
        # vertices and triangles
        self._vertices = vertices
        self._triangles = triangles
    @property
    def id(self):
        return self._segment_id
    @property
    def name(self):
        return self._name
    @property
    def colour(self):
        return self._colour
    @property
    def vertices(self):
        return self._vertices
    @property
    def triangles(self):
        return self._triangles


def vertices_for_patches(vertices, patches):
    """Compiles the set of vertices for the list of patches only read from an Amira HyperSurface file
    
    :param vertices: a sequence of vertices
    :type vertices: ``ahds.data_stream.VerticesDataStream``
    :param list patches: a list of patches each of class ``ahds.data_stream.PatchesDataStream`` 
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
