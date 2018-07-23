# -*- coding: utf-8 -*-
# mod.py
"""
sfftk.formats.mod
=================

User-facing reader classes for IMOD files

"""
from __future__ import division, print_function

import inspect
from UserList import UserList

import os.path
from numpy import matrix

from .base import Segmentation, Header, Segment, Annotation, Mesh, Contours, Shapes
from .. import schema
from ..readers import modreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-09-28"


class IMODVertex(object):
    """IMOD vertex class"""

    def __init__(self, vertex, designation='surface'):
        assert designation in ['surface', 'normal']
        self._designation = designation
        self._point = vertex

    @property
    def designation(self):
        """Is this a surface surface or normal vertex?"""
        return self._designation

    @property
    def point(self):
        """The vertex"""
        return self._point


class IMODMesh(Mesh):
    """Mesh class"""

    def __init__(self, imod_mesh):
        self._mesh = imod_mesh
        # dictionary of indices to vertices
        self._vertex_dict = dict(zip(range(len(self._mesh.vert)), self._mesh.vert))
        self._vertices, self._polygons = self._configure()

    @property
    def vertices(self):
        """The vertices constituting this mesh"""
        return self._vertices

    @property
    def polygons(self):
        """The polygons constituting this mesh"""
        return self._polygons

    def _split_indices(self):
        # convert list of vertices to a csv string
        index_string = ",".join(map(str, self._mesh.list))  # string
        # split at ',-22,'
        split_index_string = index_string.split(',-22,')  # list of strings
        # split at ','
        list_of_lists_of_index_strings = map(lambda x: x.split(','), split_index_string)
        # convert to int
        list_of_lists_of_indices = map(lambda x: map(int, x), list_of_lists_of_index_strings)
        # get rid of last list (contains list [-1])
        indices = list_of_lists_of_indices[:-1]
        #  one-line version
        #         split_indices = map(
        #             lambda x: map(int, x.split(',')),
        #             ",".join(map(str, objt.meshes[0].list)).split(',-22,')
        #             )[:-1]
        return indices

    def _configure(self):
        # get the vertix indices split
        split_indices = self._split_indices()
        # for each set of split indices
        polygon_id = 0
        polygons = dict()
        vertices = dict()
        for _indices in split_indices:  # _indices is a list of lists
            index_id, indices = _indices[0], _indices[1:]
            if index_id == -25:
                surface_indices = [tuple(indices[i:i + 3]) for i in xrange(0, len(indices), 3)]
                normal_indices = [tuple(map(lambda i: i + 1, s)) for s in surface_indices]
            elif index_id == -23:
                triangles = [tuple(indices[i:i + 6]) for i in xrange(0, len(indices), 6)]
                normal_indices = map(lambda v: tuple(v[::2]), triangles)
                surface_indices = map(lambda v: tuple(v[1::2]), triangles)
            elif index_id == -21:
                surface_indices = [tuple(indices[i:i + 3]) for i in xrange(0, len(indices), 3)]
                normal_indices = list()
            elif index_id == -24:
                raise NotImplementedError
            elif index_id == -20:
                raise NotImplementedError
            # collate vertices and polygons
            # if we have not normals we only have surface
            for i in xrange(len(surface_indices)):  # surface_indices[i] is a tuple
                if normal_indices:
                    zipped_indices = zip(surface_indices[i], normal_indices[i])
                else:
                    zipped_indices = surface_indices[i]
                # vertices
                for I in zipped_indices:
                    if normal_indices:
                        s, n = I
                    else:
                        s = I
                    # surface
                    if s not in vertices:
                        # self._vertex_dict[s] is a tuple
                        vertices[s] = IMODVertex(self._vertex_dict[s], designation='surface')
                    # normal
                    if normal_indices:
                        if n not in vertices:
                            vertices[n] = IMODVertex(self._vertex_dict[n], designation='normal')
                # polygons
                polygons[polygon_id] = zipped_indices
                polygon_id += 1
        return vertices, polygons


class IMODMeshes(UserList):
    """Container class for IMOD meshes"""

    def __init__(self, header, imod_meshes):
        self._header = header
        self._meshes = imod_meshes

    def __iter__(self):
        return iter(map(IMODMesh, self._meshes.itervalues()))

    def __getitem__(self, index):
        return IMODMesh(self._meshes.values()[index])

    def __len__(self):
        return len(self._meshes)

    def convert(self, *args, **kwargs):
        """Convert to :py:class:`sfftk.schema.SFFMeshList` object"""
        meshes = schema.SFFMeshList()
        schema.SFFMesh.reset_id()
        for m in self:
            mesh = schema.SFFMesh()
            # vertices
            vertices = schema.SFFVertexList()
            for vID, v in m.vertices.iteritems():
                x, y, z = v.point
                vertex = schema.SFFVertex(
                    vID=vID,
                    x=x,
                    y=y,
                    z=z,
                    designation=v.designation
                )
                vertices.add_vertex(vertex)
            # polygons
            polygons = schema.SFFPolygonList()
            schema.SFFPolygon.reset_id()
            for p in m.polygons.itervalues():
                polygon = schema.SFFPolygon()
                for I in p:
                    if len(I) == 2:  # if there are normals
                        s, n = I
                        polygon.add_vertex(s)
                        polygon.add_vertex(n)
                    else:
                        s = I
                        polygon.add_vertex(s)
                polygons.add_polygon(polygon)
            # set vertices and polygons on mesh
            mesh.vertices = vertices
            mesh.polygons = polygons
            meshes.add_mesh(mesh)
        return meshes


class IMODContours(Contours):
    """Contours class

    .. warning::

        .. deprecated:: 0.6.0a4
            IMOD contour segments should be converted to meshes using

        .. code:: bash

            ~$ imodmesh [options] file.mod
    """

    def __init__(self, header, conts):
        self._header = header
        self._conts = conts

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFContourList` object"""
        contours = schema.SFFContourList()
        schema.SFFContour.reset_id()
        for cont in self._conts.itervalues():
            contour = schema.SFFContour()
            for x, y, z in cont.pt:
                contour.add_point(
                    schema.SFFContourPoint(x=x, y=y, z=z)
                )
            contours.add_contour(contour)
        return contours

    def __len__(self):
        return len(self._conts)


"""
:TODO: *args, **kwargs???
"""


class IMODShape(object):
    """Base class for IMOD shapes"""
    x = 0
    y = 0
    z = 0

    @property
    def transform(self):
        """The transform associated with the shape

        Is used to place (transform) the shape in the volume
        """
        return matrix('[1 0 0 {}; 0 1 0 {}; 0 0 1 {}'.format(self.x, self.y, self.z))

    def convert(self, *args, **kwargs):
        """Convert this shape into an EMDB-SFF shape object"""
        pass


class IMODEllipsoid(IMODShape):
    """Class definition fo an ellipsoid shape primitive"""

    def __init__(self, radius, x, y, z):
        self._radius = radius
        self.x = x
        self.y = y
        self.z = z

    @property
    def radius(self):
        """Ellipsoid radius"""
        return self._radius

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFEllipsoid` object"""
        # shape
        ellipsoid = schema.SFFEllipsoid()
        ellipsoid.x = self.radius
        ellipsoid.y = self.radius
        ellipsoid.z = self.radius
        # transform
        transform = schema.SFFTransformationMatrix()
        transform.cols = 4
        transform.rows = 3
        transform.data = " ".join(map(str, self.transform.flatten().tolist()[0]))
        ellipsoid.transformId = transform.id
        return ellipsoid, transform


class IMODCylinder(IMODShape):
    """Cylinder class"""

    def __init__(self, diameter, height, x, y, z):
        self._diameter = diameter
        self._height = height
        self.x = x
        self.y = y
        self.z = z

    @property
    def diameter(self):
        """The diameter"""
        return self._diameter

    @property
    def height(self):
        """The height"""
        return self._height

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFCylinder` object"""
        # shape
        cylinder = schema.SFFCylinder()
        cylinder.diameter = self.diameter
        cylinder.height = self.height
        # transform
        transform = schema.SFFTransformationMatrix()
        transform.cols = 4
        transform.rows = 3
        transform.data = " ".join(map(str, self.transform.flatten().tolist()[0]))
        cylinder.transformId = transform.id
        return cylinder, transform


class IMODShapes(Shapes):
    """Container class for shapes"""

    def __init__(self, header, objt):
        self._header = header
        self._objt = objt
        self._shapes = self._configure()

    def __getitem__(self, index):
        return self._shapes[index]

    def __iter__(self):
        return iter(self._shapes)

    def _configure(self):
        shapes = list()
        if self._objt.pdrawsize > 0:
            radius = self._objt.pdrawsize
            for contour in self._objt.conts.itervalues():
                for x, y, z in contour.pt:
                    shapes.append(IMODEllipsoid(radius, x, y, z))
        elif modreader.OBJT_SYMBOLS[self._objt.symbol] == 'circle':
            diameter = 2 * self._objt.symsize
            height = 0
            for contour in self._objt.conts.itervalues():
                for x, y, z in contour.pt:
                    shapes.append(IMODCylinder(diameter, height, x, y, z))
        return shapes

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFShapePrimitiveList` object"""
        shapes = schema.SFFShapePrimitiveList()
        schema.SFFShape.reset_id()
        transforms = list()
        for s in self:
            shape, transform = s.convert()
            shapes.add_shape(shape)
            transforms.append(transform)
        return shapes, transforms


class IMODAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, header, objt):
        self._header, self._objt = header, objt

        for attr in dir(self._objt):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._objt, attr)):
                continue
            setattr(self, attr, getattr(self._objt, attr))

    @property
    def description(self):
        """Segment description"""
        return self.name

    @property
    def colour(self):
        """Segment colour"""
        return self.red, self.green, self.blue

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFBiologicalAnnotation` object"""
        # annotation
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.description
        annotation.numberOfInstances = 1
        # colour
        colour = schema.SFFRGBA(
            red=self.red,
            green=self.green,
            blue=self.blue,
        )
        return annotation, colour

    """
    :TODO: add methods to modify the content
    """


class IMODHeader(Header):
    """Class definition for the header in an IMOD segmentation file"""

    def __init__(self, segmentation):
        self._segmentation = segmentation

        for attr in dir(self._segmentation):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._segmentation, attr)):
                continue
            setattr(self, attr, getattr(self._segmentation, attr))

    def convert(self, *args, **kwargs):
        """Convert to an EMDB-SFF segmentation header object

        Currently not implemented
        """
        pass


class IMODSegment(Segment):
    """Segment class"""

    def __init__(self, header, objt):
        self._header = header
        self._objt = objt
        for attr in dir(objt):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(objt, attr)):
                continue
            setattr(self, 'mod_' + attr, getattr(objt, attr))

    @property
    def annotation(self):
        """The annotation for this segment"""
        return IMODAnnotation(self._header, self._objt)

    @property
    def contours(self):
        """The contours in this segment"""
        if self._objt.pdrawsize > 0:
            return None
        else:
            if self._objt.symbol == 1:
                return IMODContours(self._header, self._objt.conts)
            else:
                return None

    @property
    def meshes(self):
        """The meshes in this segment"""
        return IMODMeshes(self._header, self._objt.meshes)

    @property
    def shapes(self):
        """The shapes in this segment"""
        if self._objt.pdrawsize > 0:
            return IMODShapes(self._header, self._objt)
        elif self._objt.symbol != 1:
            return IMODShapes(self._header, self._objt)
        else:
            return None

    def convert(self):
        """Convert to :py:class:`sfftk.schema.SFFSegment` object"""
        segment = schema.SFFSegment()
        transforms = list()
        # text
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        # geometry
        # ignore contours
        #         if self.contours:
        #             segment.contours = self.contours.convert()
        if self.shapes:
            segment.shapes, transforms = self.shapes.convert()
        segment.meshes = self.meshes.convert()
        return segment, transforms


class IMODSegmentation(Segmentation):
    """Class representing an IMOD segmentation
    
    .. code:: python
    
        from sfftk.formats.mod import IMODSegmentation
        mod_seg = IMODSegmentation('file.mod')
        
    """

    def __init__(self, fn, *args, **kwargs):
        """Initialise the IMODReader
        
        :param str fn: name of Segger file
        """
        self._fn = fn
        self._segmentation = modreader.get_data(self._fn)
        self._header = IMODHeader(self._segmentation)
        self._segments = list()
        for objt in self._segmentation.objts.itervalues():
            segment = IMODSegment(self._header, objt)
            self._segments.append(segment)

    @property
    def has_mesh_or_shapes(self):
        """Check whether the segmentation has meshes or shapes
        
        If it only has contours this property is False
        Do not convert segmentations that only have contours
        """
        status = True
        for segment in self.segments:
            if segment.meshes or segment.shapes:
                pass
            else:
                status = False
                break
        return status

    @property
    def header(self):
        """Header in segmentation"""
        return self._header

    @property
    def segments(self):
        """Segments in segmentation"""
        return self._segments

    def convert(self, args, *_args, **_kwargs):
        """Method to convert an IMOD file to a :py:class:`sfftk.schema.SFFSegmentation` object"""
        segmentation = schema.SFFSegmentation()
        segmentation.name = self.header.name
        # software
        segmentation.software = schema.SFFSoftware(
            name="IMOD",
            version=self.header.version,
            processingDetails='None'
        )
        segmentation.filePath = os.path.abspath(self._fn)
        # transforms
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='{} 0.0 0.0 {} 0.0 {} 0.0 {} 0.0 0.0 {} {}'.format(
                    self.header.minx.cscale[0],
                    self.header.minx.ctrans[0],
                    self.header.minx.cscale[1],
                    self.header.minx.ctrans[1],
                    self.header.minx.cscale[2],
                    self.header.minx.ctrans[2],
                )
            ),
        )
        segmentation.boundingBox = schema.SFFBoundingBox(
            xmax=self.header.xmax,
            ymax=self.header.ymax,
            zmax=self.header.zmax
        )
        segments = schema.SFFSegmentList()
        transforms = list()
        schema.SFFSegment.reset_id()
        no_contours = 0
        no_meshes = 0
        for s in self.segments:
            segment, _transforms = s.convert()
            if s.contours is not None:
                if len(s.contours) > 0:
                    no_contours += 1
            elif s.meshes is not None:
                if len(s.meshes) > 0:
                    no_meshes += 1
            #             if len(s.contours) > 0:
            #                 no_contours += 1
            #             elif len(s.meshes) > 0:
            #                 no_meshes += 1
            transforms += _transforms
            segments.add_segment(segment)
        # if we have additional transforms from shapes
        if transforms:
            _ = [segmentation.transforms.add_transform(T) for T in transforms]
        # finally pack everything together
        segmentation.segments = segments
        # now is the right time to set the primary descriptor attribute
        # if there are at least as many segments as descriptors then set that
        segmentation.primaryDescriptor = "meshList"
        """
        if len(segmentation.segments) <= no_contours:
            segmentation.primaryDescriptor = "contourList"
        elif len(segmentation.segments) <= no_meshes:
            segmentation.primaryDescriptor = "meshList"
        else:
            segmentation.primaryDescriptor = "shapePrimitiveList"
        # custom set primary_descriptor
        if args.primary_descriptor is not None:
            if args.verbose:
                print_date("Setting primaryDescriptor to {}".format(args.primary_descriptor))
            if args.primary_descriptor == 'contourList':
                if len(segmentation.segments) <= no_contours:
                    segmentation.primaryDescriptor = "contourList"
            elif args.primary_descriptor == 'meshList':
                if len(segmentation.segments) <= no_meshes:
                    segmentation.primaryDescriptor = "meshList"
            elif args.primary_descriptor == "shapePrimitiveList":
                if not len(segmentation.segments) <= no_contours or not len(segmentation.segments) <= no_meshes:
                    segmentation.primaryDescriptor = "shapePrimitiveList"
            else:
                print_date("Invalid primary descriptor for IMOD file {}".format(args.primary_descriptor))
                print_date("Retaining detected primary descriptor")
#         if args.verbose:
#             print_date("Set primaryDescriptor to {}".format(segmentation.primaryDescriptor))
        """

        # details
        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']

        return segmentation
