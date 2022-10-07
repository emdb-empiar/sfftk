"""
``sfftk.formats.mod``
=====================

User-facing reader classes for IMOD files

"""
import inspect

import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _UserList, _dict_iter_values, _str

from .base import Segmentation, Header, Annotation
from ..readers import modreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-09-28"


class IMODMesh(object):
    """Mesh class"""

    def __init__(self, imod_mesh):
        self._mesh = imod_mesh
        # dictionary of indices to vertices
        # the type is the value first value
        # -25: only surface vertex ids provided; normal vertex ids implied from surface vertices
        # actual: s00, s01, s02, s11, s12, s20, s21, s22, ...
        # -23: both surface and normal vertex ids provided
        # actual: n00, s00, n01, s01, n02, s02, n10, s10, n11, s11, n12, s12, ...
        # -21: only surface vertex ids provided
        _id_type = self._mesh.list[0]
        if _id_type == -25:
            # remove negative values
            _triangles = list(filter(lambda i: i >= 0, self._mesh.list))
            surface_vertices = self._mesh.vert[::2]
            normal_vertices = self._mesh.vert[1::2]
            # divide by 2 because indices now point every second
            self._triangles = numpy.array(_triangles).reshape(len(_triangles) // 3, 3) // 2
            self._surface_vertices = numpy.array(surface_vertices)
            self._normal_vertices = numpy.array(normal_vertices)
        elif _id_type == -23:
            # we have both surface and normal indices
            mixed_indices = list(filter(lambda i: i >= 0, self._mesh.list))
            # every other second one is a surface vertex id
            _triangles = mixed_indices[1::2]
            surface_vertices = self._mesh.vert[::2]
            normal_vertices = self._mesh.vert[1::2]
            self._triangles = numpy.array(_triangles).reshape(len(_triangles) // 3, 3) // 2
            self._surface_vertices = numpy.array(surface_vertices)
            self._normal_vertices = numpy.array(normal_vertices)
        elif _id_type == -21:
            _triangles = list(filter(lambda i: i >= 0, self._mesh.list))
            self._triangles = numpy.array(_triangles).reshape(len(_triangles) // 3, 3)
            surface_vertices = self._mesh.vert[::2]
            self._surface_vertices = numpy.array(surface_vertices)
            self._normal_vertices = numpy.array([])

    def is_empty(self):
        if numpy.prod(self._surface_vertices.shape) == 0:
            return True
        return False

    @property
    def vertices(self):
        """The surface vertices defining this mesh's geometry"""
        return self._surface_vertices

    @property
    def normals(self):
        """The normal vertices defining surface smoothness for shading"""
        return self._normal_vertices

    @property
    def polygons(self):
        """The polygons constituting this mesh"""
        return self._triangles

    @property
    def triangles(self):
        """Polygons are triangles"""
        return self._triangles

    def convert(self, **kwargs):
        """Convert this to an EMDB-SFF object"""
        mesh = schema.SFFMesh(
            vertices=schema.SFFVertices.from_array(self.vertices),
            normals=schema.SFFNormals.from_array(self.normals),
            triangles=schema.SFFTriangles.from_array(self.triangles)
        )
        return mesh


class IMODMeshes(_UserList):
    """Container class for IMOD meshes"""

    def __init__(self, header, imod_meshes, args=None, *_args, **_kwargs):
        super(IMODMeshes, self).__init__(*_args, **_kwargs)
        self._header = header
        self._meshes = self._configure(imod_meshes)

    @staticmethod
    def _configure(imod_meshes, include_empty=False):
        """Exclude any meshes that have no vertices"""
        return list(_dict_iter_values(imod_meshes))
        # if include_empty:
        # return [mesh for mesh in _dict_iter_values(imod_meshes) if mesh.vsize > 0]

    def __iter__(self):
        return iter(map(IMODMesh, self._meshes))

    def __getitem__(self, index):
        return IMODMesh(self._meshes[index])

    def __len__(self):
        return len(self._meshes)

    def convert(self, **kwargs):
        """Convert the set of meshes for this segment into a container of mesh objects"""
        mesh_list = schema.SFFMeshList()
        for mesh in self:
            if mesh.is_empty():
                continue
            mesh_list.append(mesh.convert(**kwargs))
        return mesh_list


class IMODEllipsoid(object):
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

    @property
    def transform(self):
        """A (3,4) transformation matrix that locates the shape in the space from the origin"""
        return numpy.matrix('[1 0 0 {}; 0 1 0 {}; 0 0 1 {}'.format(self.x, self.y, self.z))

    def convert(self):
        """Convert to :py:class:`sfftkrw.SFFEllipsoid` object"""
        # shape
        ellipsoid = schema.SFFEllipsoid(
            x=self.radius, y=self.radius, z=self.radius
        )
        # transform
        transform = schema.SFFTransformationMatrix(
            rows=3, cols=4,
            data=" ".join(map(repr, self.transform.flatten().tolist()[0]))
        )
        ellipsoid.transform_id = transform.id
        return ellipsoid, transform


class IMODShapes(_UserList):
    """Container class for shapes"""

    def __init__(self, header, objt, *args, **kwargs):
        super(IMODShapes, self).__init__(*args, **kwargs)
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
            for contour in _dict_iter_values(self._objt.conts):
                for x, y, z in contour.pt:
                    shapes.append(IMODEllipsoid(radius, x, y, z))
        return shapes

    def convert(self):
        """Convert to :py:class:`sfftkrw.SFFShapePrimitiveList` object"""
        shapes = schema.SFFShapePrimitiveList()
        transforms = list()
        for s in self:
            shape, transform = s.convert()
            shapes.append(shape)
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
        """Convert to :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        # annotation
        annotation = schema.SFFBiologicalAnnotation()
        annotation.name = self.name.strip(' ')
        annotation.description = self.description.strip(' ')
        annotation.number_of_instances = 1
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

    def convert(self, **kwargs):
        """Convert to an EMDB-SFF segmentation header object

        Currently not implemented
        """
        pass


class IMODSegment(object):
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

    def is_empty(self):
        if self.meshes or self.shapes:
            return False
        return True

    @property
    def annotation(self):
        """The annotation for this segment"""
        return IMODAnnotation(self._header, self._objt)

    @property
    def meshes(self):
        """The meshes in this segment"""
        return IMODMeshes(self._header, self._objt.meshes)

    @property
    def shapes(self):
        """The shapes in this segment"""
        if self._objt.pdrawsize > 0:
            return IMODShapes(self._header, self._objt)
        else:
            return []

    def convert(self):
        """Convert to :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment()
        transforms = list()
        # text
        segment.biological_annotation, segment.colour = self.annotation.convert()
        # geometry
        if self.shapes:
            segment.shape_primitive_list, transforms = self.shapes.convert()
        # meshes
        if self.meshes:
            segment.mesh_list = self.meshes.convert()
        return segment, transforms


class IMODSegmentation(Segmentation):
    """Class representing an IMOD segmentation

    .. code-block:: python

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
        for objt in _dict_iter_values(self._segmentation.objts):
            segment = IMODSegment(self._header, objt)
            self._segments.append(segment)

    def __str__(self):
        return _str(self._segmentation)

    @property
    def has_mesh_or_shapes(self):
        """Check whether the segmentation has meshes or shapes

        If it only has contours this property is False
        Do not convert segmentations that only have contours
        """
        status = False
        for segment in self.segments:
            if segment.meshes or segment.shapes:
                status = True
                break
            else:
                pass
        return status

    @property
    def header(self):
        """Header in segmentation"""
        return self._header

    @property
    def segments(self):
        """Segments in segmentation"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Method to convert an IMOD file to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else self.header.name.strip(' ')
        # software
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="IMOD",
                version=software_version if software_version is not None else self.header.version,
                processing_details=processing_details
            )
        )
        # transforms
        segmentation.transform_list = schema.SFFTransformList()
        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(self._segmentation.ijk_to_xyz_transform)
            )
        segmentation.bounding_box = schema.SFFBoundingBox(
            xmax=self.header.x_length,
            ymax=self.header.y_length,
            zmax=self.header.z_length,
        )
        segments = schema.SFFSegmentList()
        transforms = list()
        no_meshes = 0
        for s in self.segments:
            if s.is_empty():
                continue
            segment, _transforms = s.convert()
            if s.meshes:  # is not None:
                # if len(s.meshes) > 0:
                no_meshes += 1
            transforms += _transforms
            segments.append(segment)
        # # if we have additional transforms from shapes
        if transforms:
            _ = [segmentation.transform_list.append(T) for T in transforms]
        # # finally pack everything together
        segmentation.segment_list = segments
        # now is the right time to set the primary descriptor attribute
        segmentation.primary_descriptor = "mesh_list"
        # details
        segmentation.details = details

        return segmentation
