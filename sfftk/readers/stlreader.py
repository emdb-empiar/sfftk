#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
"""
stlreader.py
========================

Read 3D System StereoLithography (StL) files. 

Depends on the `numpy-stl` package
Reads both ASCII and binary files

Version history:
0.0.1, 2016-08-09, First working version
"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__    = '2016-08-09'


import sys
import re
from ..core.print_tools import get_printable_ascii_string 


def get_data(fn):
    """Get data from an StL file
    
    :param str fn: filename
    :return: a `generator` of meshes; each mesh is a `tuple` of a name, a `dict` of vertices indexed by `vertex_id` and a `dict` of polygons referring to vertices by `vertex_id`
    :rtype: tuple
    """
    from stl import mesh
    
#     stl_meshes = [mesh.Mesh.from_file(fn)]
    meshes = list()
    stl_meshes = mesh.Mesh.from_multi_file(fn)
    for stl_mesh in stl_meshes:
        vertex_ids = dict()
        polygons = dict()
        vertex_id = 0
        polygon_id = 0
        for facet in stl_mesh.vectors:
            v0, v1, v2 = facet
            if tuple(v0) not in vertex_ids:
                vertex_ids[tuple(v0)] = vertex_id
                vertex_id += 1
            if tuple(v1) not in vertex_ids:
                vertex_ids[tuple(v1)] = vertex_id
                vertex_id += 1
            if tuple(v2) not in vertex_ids:
                vertex_ids[tuple(v2)] = vertex_id
                vertex_id += 1
                
            polygons[polygon_id] = vertex_ids[tuple(v0)], vertex_ids[tuple(v1)], vertex_ids[tuple(v2)]
            polygon_id += 1
        
        # we now need to reverse the vertex_ids dict
        """
        :TODO: transform vertices to image space!!! 
        
        the transformation matrices are at http://www.tribe43.net/blog/article-33/        
        """
        vertices = dict(zip(vertex_ids.values(), vertex_ids.keys()))
        
        # name
        name = get_printable_ascii_string(stl_mesh.name) if get_printable_ascii_string(stl_mesh.name) != "" else None
        
        meshes.append((name, vertices, polygons))
    return meshes

