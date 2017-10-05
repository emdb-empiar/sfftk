=====================
Developing with sfftk
=====================

Introduction
============

sfftk has been designed to be relatively straightforward to integrate into other Python applications having several decoupled packages with decoupled modules. At the heart of the package is an extensible schema API that handles all aspects of representation and export for the various file formats transparently. Developers can thus read and write EMDB-SFF files by only knowing about the top-level classes. Additionally, developers can also handle I/O for supported application-specific segmentation files and conversion to EMDB-SFF easily.

Reading EMDB-SFF Files
======================

All aspects of the structure of an EMDB-SFF file are handled by sfftk.schema package which defines the SFFSegmentation class to handle reading, creation and writing of EMDB-SFF files.

.. code:: python

    from sfftk.schema import SFFSegmentation
    from sfftk.unittests import TEST_DATA_PATH
    import os
    
    # XML file
    seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'emd_1014.sff')
    seg = SFFSegmentation(seg_fn)
    
    # HDF5 file
    seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'emd_1014.hff')
    seg = SFFSegmentation(seg_fn)
    
    # JSON file
    seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'emd_1014.json')
    seg = SFFSegmentation(seg_fn)

Viewing Segmentation Metadata
-----------------------------

.. code:: python

    # name
    print seg.name
    # schema version
    print seg.version
    # software details
    print seg.software
    # segmentation file path
    print seg.filePath
    # primary descriptor
    print seg.primaryDescriptor
    # transforms
    print seg.transforms
    print len(seg.transforms)
    print seg.transforms[0]
    # bounding box
    print seg.boundingBox
    # details
    print seg.details

Viewing Segments
----------------

.. code:: python

    print seg.segments

Getting The List of Segment IDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # segment IDs
    print seg.segments.get_ids()

Getting A Segment By ID
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    segment = seg.segments.get_by_id(<segment_id>)
    print segment

Viewing Segment Metadata
------------------------

ID and Parent ID
~~~~~~~~~~~~~~~~

.. code:: python

    print segment.id
    print segment.parentID

Biological Annotation
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    print segment.biologicalAnnotation
    print segment.biologicalAnnotation.description
    print segment.biologicalAnnotation.numberOfInstances
    print segment.biologicalAnnotation.externalReferences
    print segment.biologicalAnnotation.externalReferences[0] # first reference

Complexes and Macromolecules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    print segment.complexesAndMacromolecules
    print segment.complexesAndMacromolecules.complexes
    print segment.complexesAndMacromolecules.macromolecules

Creating EMDB-SFF Objects
=========================

Users can create EMDB-SFF objects from scratch then export them to a file format of your choice.

.. code:: python

    from sfftk import schema
    # an empty EMDB-SFF segmentation
    seg = schema.SFFSegmentation()

Setting Segmentation Metadata
-----------------------------

.. code:: python
	
	# view the schema version
	print seg.version
	
	# segmentation name
	seg.name = 'A New Segmentation'
	
	# segmentation software used
	seg.software = schema.SFFSoftware(
		name='Some Software',
		version='v0.1.3.dev3',
		processingDetails='Lorem ipsum dolor...'
		)
		
	# filePath
	seg.filePath = ‘/path/to/original/file'
	
	# bounding box
	seg.boundingBox = schema.SFFBoundingBox(
		xmin=<xmin>,
		xmax=<xmax>,
		ymin=<ymin>,
		ymax=<ymax>,
		zmin=<zmin>,
		zmax=<zmax>
		)
		
	# the list of transforms
	seg.transforms = schema.SFFTransformationMatrix()
	
	# an identity matrix with no transformation
	transform = schema.SFFTransformationMatrix(
		rows=3,
		cols=4,
		data='1 0 0 0 0 1 0 0 0 0 1 0'
		)
		
	# add it to the list of transforms
	seg.transforms.add_transform(transform)

Setting Segments
~~~~~~~~~~~~~~~~

Setting Segment Metadata
^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    segment = schema.SFFSegment()

Biological Annotation
'''''''''''''''''''''

.. code:: python

    # define the biological annotation object
    bioAnn = schema.SFFBiologicalAnnotation()
    bioAnn.description = “Some description"
    bioAnn.numberOfInstances = 7

    # define the external references
    extRefs = schema.SFFExternalReferences()
    extRefs.add_externalReference(
	    schema.SFFExternalReference(
		    type="ontology1",
		    value="obo_id1"
		    )
	    )
    extRefs.add_externalReference(
	    schema.SFFExternalReference(
		    type="ontology2",
		    value="obo_id2"
		    )
	    )

    # add the external references to the biological annotation
    bioAnn.externalReferences = extRefs

    # add the biological annotation to the segment
    segment.biologicalAnnotation = bioAnn

Complexes and Macromolecules
''''''''''''''''''''''''''''

.. code:: python

    compMacr = schema.SFFComplexesAndMacromolecules()
    
    # complexes
    comp = schema.SFFComplexes()
    comp.add_complex(“comp1")
    comp.add_complex(“comp2")

    # macromolecules
    macr = schema.SFFMacromolecules()
    macr.add_macromolecule(“macr1")
    macr.add_macromolecule(“macr2")

    # add the complexes and macromolecules
    compMacr.complexes = comp
    compMacr.macromolecules = macr

    # add them to the segment
    segment.complexesAndMacromolecules = compMacr

Colour
''''''

Colours can either be described by name or by normalised RGBA values (each channel has a value in the interval (0,1)).

.. code:: python

	# colour by name; see: https://en.wikipedia.org/wiki/Web_colors
	segment.colour = schema.SFFColour()
	LightSeaGreen: (32, 178, 170)
	segment.colour.name = “LightSeaGreen"
	
	# colour as RGBA
	rgba = schema.SFFRGBA(
	    red=0.1,
	    green=0.2,
	    blue=0.8,
	    alpha=0.5
	    )
	
	segment.colour = schema.SFFColour()
	segment.colour.rgba = rgba

Setting Contour Segments
^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from random import random, randint
    
    contours = schema.SFFContourList()
    i = 0
    while i < 10:
	    contour = schema.SFFContour()
	    j = 0
	    J = randint(10, 20)
	    while j < J:
		    contour.add_point(
			    schema.SFFContourPoint(
				    x=random()*10,
				    y=random()*10,
				    z=random()*10,
				    )
			    )
		    j += 1
		    contours.add_contour(contour)
	    i += 1

    # add the contours to the segment
    segment.contours = contours

Setting Mesh Segments
^^^^^^^^^^^^^^^^^^^^^

.. code:: python

	from random import random, randint
	
	# the list of meshes
	meshes = schema.SFFMeshList()
	
	# a mesh
	mesh = schema.SFFMesh()
	
	# a list of vertices
	vertices = schema.SFFVertexList()
	no_vertices = randint(stop=100)
	
	# add vertices from the list of vertices
	for i in xrange(no_vertices):
		vertex = schema.SFFVertex()
		vertex.point = tuple(
		map(float, (randint(1, 1000), randint(1, 1000), randint(1, 1000))))
		vertices.add_vertex(vertex)
	
	# a list of polygons
	polygons = schema.SFFPolygonList()
	no_polygons = randint(stop=100)
	
	# add polygons to the list of polygons
	for i in xrange(no_polygons):
	    polygon = schema.SFFPolygon()
	    polygon.add_vertex(random.choice(range(randint())))
	    polygon.add_vertex(random.choice(range(randint())))
	    polygon.add_vertex(random.choice(range(randint())))
	    polygons.add_polygon(polygon)
	
	# set the vertices and polygons on the mesh
	mesh.vertices = vertices
	mesh.polygons = polygons
	
	# add the mesh to the list of meshes
	meshes.add_mesh(mesh)
	
	# add the mesh to the segment
	segment.meshes = meshes

Setting Shape Segments
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from random import random, randint

    # a list of shape
    shapes = schema.SFFShapePrimitiveList()

    # a cone
    # first we define the transform that locates it in place

    transform = schema.SFFTransformationMatrix(
	    rows=3,
	    cols=4,
	    data='1 0 0 0 0 1 0 0 0 0 1 0'
	    )
    # second we define its dimension
    shapes.add_shape(
	    schema.SFFCone(
		    height=random()*100,
		    bottomRadius=random()*100,
		    transformId=transform.id,
		    )
	    )

    # add the transform to the list of transforms
    seg.transforms.add_transform(transform)

    # a cuboid
    transform = schema.SFFTransformationMatrix(
	    rows=3,
	    cols=4,
	    data='2 0 0 0 5 3 0 0 27 0 0 1 9'
	    )
    shapes.add_shape(
	    schema.SFFCuboid(
		    x=random()*100,
		    y=random()*100,
		    z=random()*100,
		    transformId=transform.id,
		    )
	    )

    # add the transform to the list of transforms
    seg.transforms.add_transform(transform)

    # a cylinder
    transform = schema.SFFTransformationMatrix(
	    rows=3,
	    cols=4,
	    data='2 0 0 0 15 3 0 0 17 0 0 1 16'
	    )
    shapes.add_shape(
	    schema.SFFCylinder(
		    height=random()*100,
		    diameter=random()*100,
		    transformId=transform.id,
		    )
	    )

    # add the transform to the list of transforms
    seg.transforms.add_transform(transform)
    # an ellipsoid
    transform = schema.SFFTransformationMatrix(
	    rows=3,
	    cols=4,
	    data='1 0 0 0 15 1 0 0 17 0 0 1 16'
	    )
    shapes.add_shape(
	    schema.SFFEllipsoid(
		    x=random()*100,
		    y=random()*100,
		    z=random()*100,
		    transformId=transform.id,
		    )
	    )

    # add the transform to the list of transforms
    seg.transforms.add_transform(transform)

Setting Volume Segments
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    segment.volume = schema.SFFThreeDVolume(
	    file="file", # works with seg.filePath to get the actual file
	    objectPath=<segment_id>,
	    contourLevel=77.0,
	    transformId=0,
	    format="MRC" # alternatives: Segger, EMAN2, CCP4
	    )

Adding A Segment To The Segmentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # create the list of segments
    seg.segments = schema.SFFSegmentList()
    # add the segment
    seg.segments.add_segment(segment)

Exporting EMDB-SFF Objects
==========================

Exporting an EMDB-SFF object infers the output format from the file extension.

.. code:: python

    # XML
    seg.export(‘file.sff')

    # HDF5
    seg.export(‘file.hff')

    # JSON
    seg.export(‘file.json')

Navigating Your Way Through A Segmentation
==========================================

Iterating
---------

Segments
~~~~~~~~

.. code:: python

    for segment in seg.segments:
    	# do something with segment
	
Contours
~~~~~~~~

.. code:: python

    for contour in segment.contours:
	    for point in contour.points:
	    	x, y, z = point.x, point.y, point.z

Meshes
~~~~~~

.. code:: python

    for mesh in segment.meshes:
	    for vertex in mesh.vertices:
		    vertex.vID
		    vertex.designation # ‘vertex' or ‘normal'
		    x, y, z = vertex.x, vertex.y, vertex.z
	
	    for polygon in mesh.polygons:
		    polygon.PID
		    polygon.vertex_ids

External References
~~~~~~~~~~~~~~~~~~~

.. code:: python

    for extRef in segment.biologicalAnnotation.externalReferences:
	    extRef.type
	    extRef.otherType
	    extRef.value

Directly Accessing A Segment
============================

.. code:: python

    # view the list of segment IDs
    seg.segment.get_ids()
    # get a segment by ID
    segment = seg.segment.get_by_id(<segment_id>)

Annotating EMDB-SFF Objects
===========================

Use the sfftk.notes.modify module to perform annotations

Note Objects
------------

.. code:: python

    from sfftk.notes.modify import SimpleNote, ExternalReference
    
    N = SimpleNote()
    N.description = ‘some description'
    N.numberOfInstances = 5
    Es = [
	    ExternalReference(type='ontology1', otherType=None, value='obo_id1'),
	    ExternalReference(type='ontology2', otherType=None, value='obo_id2'),
	    ]
    N.externalReferences = Es
    N.complexes = [‘comp1', ‘comp2']
    N.macromolecules = [‘macr1', ‘macr2']
    from sfftk.schema import SFFSegment
    segment = SFFSegment()

Adding Notes
------------

.. code:: python

    # add the notes
    segment = N.add_to_segment(segment)

Editing Notes
-------------

First make an note containing the edits

.. code:: python

    E = SimpleNote(
	    description='new description',
	    numberOfInstances=14,
	    externalReferenceId=0, # the external reference ID to change
	    externalReferences=[
		    ExternalReference(type='x', otherType='y', value='z')
		    ],
	    complexId=3,
	    complexes=[‘comp1', ‘comp2'],
	    macromoleculeId=0,
	    macromolecules=[‘macr1', ‘macr2'],
	    )

Then call the edit method

.. code:: python

    segment = N.edit_in_segment(segment)

Deleting Notes
--------------

Similary, create a note indicating which attribute (description, numberOfInstances) and/or IDs to be deleted.

.. code:: python

    D = SimpleNote(	
	    description=True,
	    numberOfInstances=True,
	    externalReferenceId=2,
	    complexId=3,
	    macromoleculeId=0
	    )

Now call the delete method.

.. code:: python

    segment = D.delete_from_segment(segment)

Reading Application-Specific Segmentation Files 
================================================

Application-specific file format readers and converters are defined in the sfftk.formats package with each module defined by the file extension. For example, AmiraMesh files have an ‘am' extension hence we would read them using the sfftk.formats.am module which defines an AmiraMeshSegmentation class.

AmiraMesh (.am)
---------------

.. code:: python

    from sfftk.formats.am import AmiraMeshSegmentation
    am_seg = AmiraMeshSegmentation(‘file.am')

CCP4 (.map)
-----------

.. code:: python

    from sfftk.formats.map import MAPSegmentation
    map_seg = MAPSegmentation(‘file.map')

IMOD (.mod)
-----------

.. code:: python

    from sfftk.formats.mod import IMODSegmentation
    mod_seg = IMODSegmentation(‘file.mod')

Segger (.seg)
-------------

.. code:: python

    from sfftk.formats.seg import SeggerSegmentation
    seg_seg = SeggerSegmentation(‘file.seg')

STL (.stl)
----------

.. code:: python

    from sfftk.formats.stl import STLSegmentation
    stl_seg = STLSegmentation(‘file.stl')

Amira HyperSurface (.surf)
--------------------------

.. code:: python

    from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
    surf_seg = AmiraHyperSurfaceSegmentation(‘file.surf')

Converting Application-Specific Segmentations to EMDB-SFF
---------------------------------------------------------

.. code:: python

    sff_seg = as_seg.convert()

Note that the segmentation is now only an EMDB-SFF object but is not of a particular file format. The file format is chosen by the extension when `*using the export method* <#exporting-emdb-sff-objects>`__.
