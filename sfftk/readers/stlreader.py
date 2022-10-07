"""
``sfftk.readers.stlreader``
===========================

Ad hoc reader for Stereolithography (STL) files

- Depends on the `numpy-stl` package

- Reads both ASCII and binary files
"""
import os

from sfftkrw.core import _dict

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-08-09'
__updated__ = '2018-02-14'


def get_data(fn):
    """Get data from an StL file

    :param str fn: filename
    :return: a `generator` of meshes; each mesh is a `tuple` of a name, a `dict` of vertices indexed by `vertex_id`
        and a `dict` of polygons referring to vertices by `vertex_id`
    :rtype: tuple
    """
    from stl import mesh

    #     stl_meshes = [mesh.Mesh.from_file(fn)]
    meshes = list()
    stl_meshes = mesh.Mesh.from_multi_file(fn)
    mesh_id = 0
    for stl_mesh in stl_meshes:
        vertex_ids = _dict()
        polygons = _dict()
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
        vertices = _dict(zip(vertex_ids.values(), vertex_ids.keys()))

        name = "{}#{}".format(os.path.basename(fn), mesh_id)
        meshes.append((name, vertices, polygons))
    return meshes
