# -*- coding: utf-8 -*-
# test_schema.py
'''
Unit tests for schema adapter
'''
import json
import os
import random
import tempfile
import unittest

import __init__ as tests

from .. import schema


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-02-20"
__updated__ = '2018-02-14'


class TestSFFSegmentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # empty segmentation object
        segmentation = schema.SFFSegmentation()
        # header
        segmentation.name = 'name'
        segmentation.software = schema.SFFSoftware(
            name="Software",
            version="1.0.9",
            processingDetails="Processing details"
            )
        segmentation.filePath = "filePath"
        segmentation.primaryDescriptor = "primaryDescriptor"
        segmentation.details = "Details"
        # transforms
        transforms = schema.SFFTransformList()
        transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data=" ".join(map(str, range(12)))
                )
            )
        transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data=" ".join(map(str, range(12)))
                )
            )
        transforms.add_transform(
            schema.SFFCanonicalEulerAngles(
                phi=10.0,
                theta=10.0,
                psi=10.0
                )
            )
        transforms.add_transform(
            schema.SFFViewVectorRotation(
                x=10.0,
                y=10.0,
                z=10.0,
                r=10.0
                )
            )
        transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data=" ".join(map(str, range(12)))
                )
            )
        # boundingBox
        cls.xmax = tests._random_integer(start=500)
        cls.ymax = tests._random_integer(start=500)
        cls.zmax = tests._random_integer(start=500)
        segmentation.boundingBox = schema.SFFBoundingBox(
            xmax=cls.xmax,
            ymax=cls.ymax,
            zmax=cls.zmax
            )
        # global external references
        segmentation.globalExternalReferences = schema.SFFGlobalExternalReferences()
        segmentation.globalExternalReferences.add_externalReference(
            schema.SFFExternalReference(
                type='one',
                otherType='two',
                value='three'
                )
            )
        segmentation.globalExternalReferences.add_externalReference(
            schema.SFFExternalReference(
                type='four',
                otherType='five',
                value='six'
                )
            )
        #  segments
        segments = schema.SFFSegmentList()
        # segment one
        segment = schema.SFFSegment()
        biolAnn = schema.SFFBiologicalAnnotation()
        biolAnn.description = "Some description"
        # external refs
        biolAnn.externalReferences = schema.SFFExternalReferences()
        biolAnn.externalReferences.add_externalReference(
            schema.SFFExternalReference(
                type="sldjflj",
                value="doieaik"
                )
            )
        biolAnn.externalReferences.add_externalReference(
            schema.SFFExternalReference(
                type="sljd;f",
                value="20ijalf"
                )
            )
        biolAnn.externalReferences.add_externalReference(
            schema.SFFExternalReference(
                type="lsdjlsd",
                otherType="lsjfd;sd",
                value="23ijlsdjf"
                )
            )
        biolAnn.numberOfInstances = 30
        segment.biologicalAnnotation = biolAnn
        # complexes and macromolecules
        # complexes
        compMac = schema.SFFComplexesAndMacromolecules()
        comp = schema.SFFComplexes()
        comp.add_complex(str(tests._random_integer(1, 1000)))
        comp.add_complex(str(tests._random_integer(1, 1000)))
        comp.add_complex(str(tests._random_integer(1, 1000)))
        comp.add_complex(str(tests._random_integer(1, 1000)))
        comp.add_complex(str(tests._random_integer(1, 1000)))
        # macromolecules
        macr = schema.SFFMacromolecules()
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        macr.add_macromolecule(str(tests._random_integer(1, 1000)))
        compMac.complexes = comp
        compMac.macromolecules = macr
        segment.complexesAndMacromolecules = compMac
        # colour
        segment.colour = schema.SFFColour()
        segment.colour.rgba = schema.SFFRGBA(
            red=1,
            green=0,
            blue=1,
            alpha=0
            )
        # volume
        segment.volume = schema.SFFThreeDVolume(
            file="/path/to/file",
            objectPath=33,
            contourLevel=77.0,
            transformId=0,
            format="MRC"
            )
        # contours
        contours = schema.SFFContourList()
        i = 0
        while i < 10:
            contour = schema.SFFContour()
            j = 0
            J = tests._random_integer(10, 20)
            while j < J:
                contour.add_point(
                    schema.SFFContourPoint(
                        x=tests._random_float() * 10,
                        y=tests._random_float() * 10,
                        z=tests._random_float() * 10,
                        )
                    )
                j += 1
            contours.add_contour(contour)
            i += 1
        segment.contours = contours
        # meshes
        meshes = schema.SFFMeshList()
        mesh = schema.SFFMesh()
        mesh2 = schema.SFFMesh()
        vertices1 = schema.SFFVertexList()
        cls.no_vertices1 = tests._random_integer(stop=100)
        for i in xrange(cls.no_vertices1):
            vertex = schema.SFFVertex()
            vertex.point = tuple(
                map(float, (
                    tests._random_integer(1, 1000),
                    tests._random_integer(1, 1000),
                    tests._random_integer(1, 1000)
                    ))
                )
            vertices1.add_vertex(vertex)
        polygons1 = schema.SFFPolygonList()
        cls.no_polygons1 = tests._random_integer(stop=100)
        for i in xrange(cls.no_polygons1):
            polygon = schema.SFFPolygon()
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygons1.add_polygon(polygon)
        mesh.vertices = vertices1
        mesh.polygons = polygons1
        vertices2 = schema.SFFVertexList()
        cls.no_vertices2 = tests._random_integer(stop=100)
        for i in xrange(cls.no_vertices2):
            vertex = schema.SFFVertex()
            vertex.point = tuple(map(float, (tests._random_integer(1, 1000), tests._random_integer(1, 1000), tests._random_integer(1, 1000))))
            vertices2.add_vertex(vertex)
        polygons2 = schema.SFFPolygonList()
        cls.no_polygons2 = tests._random_integer(stop=100)
        for i in xrange(cls.no_polygons2):
            polygon = schema.SFFPolygon()
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygons2.add_polygon(polygon)
        mesh2.vertices = vertices2
        mesh2.polygons = polygons2
        meshes.add_mesh(mesh)
        meshes.add_mesh(mesh2)
        segment.meshes = meshes
        # shapes
        shapes = schema.SFFShapePrimitiveList()
        transform = schema.SFFViewVectorRotation(
            x=10.0,
            y=10.0,
            z=10.0,
            r=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFViewVectorRotation(
            x=10.0,
            y=10.0,
            z=10.0,
            r=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCuboid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCuboid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCylinder(
                height=tests._random_float() * 100,
                diameter=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFEllipsoid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFEllipsoid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFCanonicalEulerAngles(
            phi=10.0,
            theta=10.0,
            psi=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        segment.shapes = shapes
        segments.add_segment(segment)
        # segment two
        segment = schema.SFFSegment()
        # colour
        segment.colour = schema.SFFColour()
        segment.colour.rgba = schema.SFFRGBA(
            red=0,
            green=0.5,
            blue=0.2,
            alpha=0.7,
            )
        # contours
        contours = schema.SFFContourList()
        i = 0
        while i < 20:
            contour = schema.SFFContour()
            j = 0
            J = tests._random_integer(10, 20)
            while j < J:
                contour.add_point(
                    schema.SFFContourPoint(
                        x=tests._random_float() * 10,
                        y=tests._random_float() * 10,
                        z=tests._random_float() * 100,
                        )
                    )
                j += 1
            contours.add_contour(contour)
            i += 1
        segment.contours = contours
        # mesh
        meshes = schema.SFFMeshList()
        mesh = schema.SFFMesh()
        vertices3 = schema.SFFVertexList()
        cls.no_vertices3 = tests._random_integer(stop=100)
        for i in xrange(cls.no_vertices3):
            vertex = schema.SFFVertex()
            vertex.point = tuple(
                map(float, (
                    tests._random_integer(1, 1000),
                    tests._random_integer(1, 1000),
                    tests._random_integer(1, 1000)
                    ))
                )
            vertices3.add_vertex(vertex)
        polygons3 = schema.SFFPolygonList()
        cls.no_polygons3 = tests._random_integer(stop=100)
        for i in xrange(cls.no_polygons3):
            polygon = schema.SFFPolygon()
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygon.add_vertex(random.choice(range(tests._random_integer())))
            polygons3.add_polygon(polygon)
        mesh.vertices = vertices3
        mesh.polygons = polygons3
        meshes.add_mesh(mesh)
        segment.meshes = meshes
        # shapes
        shapes = schema.SFFShapePrimitiveList()
        transform = schema.SFFViewVectorRotation(
            x=10.0,
            y=10.0,
            z=10.0,
            r=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFViewVectorRotation(
            x=10.0,
            y=10.0,
            z=10.0,
            r=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCuboid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCuboid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCylinder(
                height=tests._random_float() * 100,
                diameter=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFEllipsoid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFTransformationMatrix(
            rows=3,
            cols=4,
            data=" ".join(map(str, range(12))),
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFEllipsoid(
                x=tests._random_float() * 100,
                y=tests._random_float() * 100,
                z=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        transform = schema.SFFCanonicalEulerAngles(
            phi=10.0,
            theta=10.0,
            psi=10.0
            )
        transforms.add_transform(transform)
        shapes.add_shape(
            schema.SFFCone(
                height=tests._random_float() * 100,
                bottomRadius=tests._random_float() * 100,
                transformId=transform.id,
                )
            )
        segment.shapes = shapes
        # add segmen to segments
        segments.add_segment(segment)
        segmentation.transforms = transforms
        segmentation.segments = segments
        # segmentation one
        cls.segmentation = segmentation
        # segmentation two
        segmentation2 = schema.SFFSegmentation()
        segmentation2.segments = schema.SFFSegmentList()
        segmentation2.segments.add_segment(
            schema.SFFSegment()
            )
        cls.segmentation2 = segmentation2
        # write out an XML, HDF5, JSON version for later testing
        cls.sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'test_data.sff')
        cls.hff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'test_data.hff')
        cls.json_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'test_data.json')
        # export
        cls.segmentation.export(cls.sff_file)
        cls.segmentation.export(cls.hff_file)
        cls.segmentation.export(cls.json_file)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.sff_file)
        os.remove(cls.hff_file)
        os.remove(cls.json_file)
        # ensure they're gone
        assert not os.path.exists(cls.sff_file)
        assert not os.path.exists(cls.hff_file)
        assert not os.path.exists(cls.json_file)

    def test_create(self):
        """Create an SFFSegmentation object from scratch"""
        # assertions
        self.assertEqual(self.segmentation.name, 'name')
        self.assertEqual(self.segmentation.version, self.segmentation._local.schemaVersion)  # automatically set
        self.assertEqual(self.segmentation.software.name, "Software")
        self.assertEqual(self.segmentation.software.version, "1.0.9")
        self.assertEqual(self.segmentation.software.processingDetails, "Processing details")
        self.assertEqual(self.segmentation.filePath, "filePath")
        self.assertEqual(self.segmentation.primaryDescriptor, "primaryDescriptor")
        self.assertEqual(self.segmentation.details, "Details")
        self.assertEqual(self.segmentation.boundingBox.xmin, 0)
        self.assertEqual(self.segmentation.boundingBox.xmax, self.xmax)
        self.assertEqual(self.segmentation.boundingBox.ymin, 0)
        self.assertEqual(self.segmentation.boundingBox.ymax, self.ymax)
        self.assertEqual(self.segmentation.boundingBox.zmin, 0)
        self.assertEqual(self.segmentation.boundingBox.zmax, self.zmax)
        self.assertEqual(self.segmentation.globalExternalReferences[0].type, 'one')
        self.assertEqual(self.segmentation.globalExternalReferences[0].otherType, 'two')
        self.assertEqual(self.segmentation.globalExternalReferences[0].value, 'three')
        self.assertEqual(self.segmentation.globalExternalReferences[1].type, 'four')
        self.assertEqual(self.segmentation.globalExternalReferences[1].otherType, 'five')
        self.assertEqual(self.segmentation.globalExternalReferences[1].value, 'six')
        # test the number of transforms
        self.assertEqual(len(self.segmentation.transforms), 23)
        # test the transform IDs
        self.assertItemsEqual(map(lambda t: t.id, self.segmentation.transforms), range(23))
        # segments
        self.assertEqual(len(self.segmentation.segments), 2)
        # segment one
        segment = self.segmentation.segments[0]
        # segment: biologicalAnnotation
        self.assertEqual(segment.biologicalAnnotation.description, "Some description")
        self.assertEqual(len(segment.biologicalAnnotation.externalReferences), 3)
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].type, "sldjflj")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].value, "doieaik")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[1].type, "sljd;f")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[1].value, "20ijalf")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[2].type, "lsdjlsd")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[2].otherType, "lsjfd;sd")
        self.assertEqual(segment.biologicalAnnotation.externalReferences[2].value, "23ijlsdjf")
        self.assertEqual(segment.biologicalAnnotation.numberOfInstances, 30)
        # segment: complexesAndMacromolecules
        # complexes
        self.assertEqual(len(segment.complexesAndMacromolecules.complexes), 5)
        complexes_bool = map(lambda c: c > 0, segment.complexesAndMacromolecules.complexes)
        self.assertTrue(all(complexes_bool))
        # macromolecules
        self.assertEqual(len(segment.complexesAndMacromolecules.macromolecules), 6)
        macromolecules_bool = map(lambda c: c > 0, segment.complexesAndMacromolecules.macromolecules)
        self.assertTrue(all(macromolecules_bool))
        # colour
        self.assertEqual(segment.colour.rgba.value, (1, 0, 1, 0))
        # volume
        self.assertEqual(segment.volume.file, "/path/to/file")
        self.assertEqual(segment.volume.objectPath, 33)
        self.assertEqual(segment.volume.contourLevel, 77.0)
        self.assertEqual(segment.volume.transformId, 0)
        self.assertEqual(segment.volume.format, "MRC")
        # contours
        self.assertEqual(len(segment.contours), 10)
        # meshes
        self.assertEqual(len(segment.meshes), 2)
        mesh1, mesh2 = segment.meshes
        self.assertEqual(len(mesh1.vertices), self.no_vertices1)
        self.assertEqual(len(mesh1.polygons), self.no_polygons1)
        self.assertEqual(len(mesh2.vertices), self.no_vertices2)
        self.assertEqual(len(mesh2.polygons), self.no_polygons2)
        # shapes
        self.assertEqual(len(segment.shapes), 9)
        self.assertEqual(segment.shapes.numCones, 4)
        self.assertEqual(segment.shapes.numCylinders, 1)
        self.assertEqual(segment.shapes.numCuboids, 2)
        self.assertEqual(segment.shapes.numEllipsoids, 2)
        # tests to ensure IDs are correctly reset
        # segment two :: mainly to test that ids of mesh, contour, polygon, segment, shape, vertex reset
        segment = self.segmentation.segments[1]
        # mesh
        self.assertEqual(segment.meshes[0].id, 0)
        # contour
        self.assertEqual(segment.contours[0].id, 0)
        # polygon
        self.assertEqual(segment.meshes[0].polygons[0].PID, 0)
        # vertex
        self.assertEqual(segment.meshes[0].vertices[0].vID, 0)
        # shape
        self.assertEqual(segment.shapes[0].id, 0)
        # segment in segmentation2
        segment2 = self.segmentation2.segments[0]
        self.assertEqual(segment2.id, 1)


    def test_read_sff(self):
        """Read from XML (.sff) file"""
        sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
        segmentation = schema.SFFSegmentation(sff_file)
        transform = segmentation.transforms[1]
        # assertions
        self.assertEqual(segmentation.name, "Segger Segmentation")
        self.assertTrue(len(segmentation.version) > 0)
        self.assertEqual(segmentation.software.name, "segger")
        self.assertEqual(segmentation.software.version, "2")
        self.assertEqual(segmentation.software.processingDetails, None)
        self.assertEqual(segmentation.filePath, "/Users/pkorir/Documents/workspace/bioimaging-scripts/trunk/sfftk/sfftk/test_data/sff")
        self.assertEqual(segmentation.primaryDescriptor, "threeDVolume")
        self.assertEqual(transform.rows, 3)
        self.assertEqual(transform.cols, 4)
        self.assertEqual(transform.data, "3.3900001049 0.0 0.0 -430.529998779 0.0 3.3900001049 0.0 -430.529998779 0.0 0.0 3.3900001049 -430.529998779")

    def test_read_hff(self):
        """Read from HDF5 (.hff) file"""
        hff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.hff')
        segmentation = schema.SFFSegmentation(hff_file)
        # assertions
        self.assertEqual(segmentation.name, "Segger Segmentation")
        self.assertTrue(len(segmentation.version) > 0)
        self.assertEqual(segmentation.software.name, "segger")
        self.assertEqual(segmentation.software.version, "2")
        self.assertEqual(segmentation.software.processingDetails, None)
        self.assertEqual(segmentation.filePath, "/Users/pkorir/Documents/workspace/bioimaging-scripts/trunk/sfftk/sfftk/test_data/sff")
        self.assertEqual(segmentation.primaryDescriptor, "threeDVolume")

    def test_read_json(self):
        """Read from JSON (.json) file"""
        json_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.json')
        segmentation = schema.SFFSegmentation(json_file)
        # assertions
        self.assertEqual(segmentation.name, "Segger Segmentation")
        self.assertTrue(len(segmentation.version) > 0)
        self.assertEqual(segmentation.software.name, "segger")
        self.assertEqual(segmentation.software.version, "2")
        self.assertEqual(segmentation.software.processingDetails, None)
        self.assertEqual(segmentation.filePath, "/Users/pkorir/Documents/workspace/bioimaging-scripts/trunk/sfftk/sfftk/test_data/sff")
        self.assertEqual(segmentation.primaryDescriptor, "threeDVolume")

    def test_export_sff(self):
        """Export to an XML (.sff) file"""
        temp_file = tempfile.NamedTemporaryFile()
        self.segmentation.export(temp_file.name + '.sff')
        # assertions
        with open(temp_file.name + '.sff') as f:
            self.assertEqual(f.readline(), '<?xml version="1.0" encoding="UTF-8"?>\n')

    def test_export_hff(self):
        """Export to an HDF5 file"""
        temp_file = tempfile.NamedTemporaryFile()
        self.segmentation.export(temp_file.name + '.hff')
        # assertions
        with open(temp_file.name + '.hff') as f:
            self.assertGreaterEqual(f.readline().find('HDF'), 0)

    def test_export_json(self):
        """Export to a JSON file"""
        temp_file = tempfile.NamedTemporaryFile()
        self.segmentation.export(temp_file.name + '.json')
        # assertions
        with open(temp_file.name + '.json') as f:
            J = json.load(f)
            self.assertEqual(J['primaryDescriptor'], u"primaryDescriptor")


if __name__ == "__main__":

    unittest.main()
