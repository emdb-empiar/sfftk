==========================
Developing with ``sfftk``
==========================

.. contents::

Introduction
============

``sfftk`` has been designed to be relatively straightforward to integrate into other Python applications because it has been designed in such a way that the various components are independent of one another. The main components of the package are:

* the **schema** API (:py:mod:`sfftk.schema`) which handles how data fields are represented independent of the file formats to be used (XML, HDF5 and JSON). This package provides an adapter to the underlying `GenerateDS <https://www.davekuhlman.org/generateDS.html>`_ API which *extends* and *simplifies* EMDB-SFF fields.

* the **core** API (:py:mod:`sfftk.core`) provides a set of useful utilities mainly for the command-line toolkit (``sff`` command) that handle command line arguments (making sure that they have the right values), read persistent configs from disk, do any prep work on segmentation files as well as several print and miscellaneous utilities.

* the **readers** API (:py:mod:`sfftk.readers`) implements *ad hoc* segmentation file format readers. They are *ad hoc* because they are not expected to conform to a rigid API. For example, the :py:mod:`sfftk.readers.segreader` module has a single class (:py:class:`sfftk.readers.segreader.SeggerSegmentation`) which represents a Segger segmentation, which is completely different from the :py:mod:`sfftk.readers.modreader` module which has over 20 classes representing the various components of an IMOD segmentation. The only requirement of a segmentation reader module in this package is that it has to implement a ``get_data(fn, *args, **kwargs)`` function which returns the *ad hoc* segmentation object(s).

* the **format** API (:py:mod:`sfftk.formats`) provides adapters that correspond to individual readers. It is the responsibility of the modules in this package to *adapt* the *ad hoc* segmentation representation to an EMDB-SFF representation. This is where the call to ``get_data(fn, *args, **kwargs)`` will be invoked. For example, the :py:mod:`sfftk.formats.mod` module has a :py:class:`sfftk.formats.mod.IMODSegmentation` class which invokes the :py:func:`sfftk.readers.modreader.get_data()` function to supply the *ad hoc* :py:class:`sfftk.readers.modreader.IMOD` object that contains the IMOD segmentation. Presently, this API only provides the ability to read application-specific segmentation files. We hope to eventually add the ability to write out application-specific segmentation files.

* finally, the **notes** API (:py:mod:`sfftk.notes`) supplies three modules for *finding* (:py:mod:`sfftk.notes.find`), *modifying* (:py:mod:`sfftk.notes.modify`) and *viewing* (:py:mod:`sfftk.notes.view`) annotations.


Reading EMDB-SFF Files
======================

All aspects of the structure of an EMDB-SFF file are handled by :py:mod:`sfftk.schema` package which defines the :py:class:`sfftk.schema.SFFSegmentation` class to handle reading, creation and writing of EMDB-SFF files. Please consult the section on :ref:`output_formats` for background information.

.. code:: python

    >>> from sfftk.schema import SFFSegmentation
    >>> from sfftk.unittests import TEST_DATA_PATH
    >>> import os
    >>>
    >>> # XML file
    >>> seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
    >>> seg_fn
    '/Users/pkorir/PycharmProjects/sfftk/sfftk/test_data/sff/v0.7/emd_1014.sff'
    >>> seg = SFFSegmentation(seg_fn)
    >>>
    >>> # HDF5 file
    >>> seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.hff')
    >>> seg = SFFSegmentation(seg_fn)
    >>>
    >>> # JSON file
    >>> seg_fn = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.json')
    >>> seg = SFFSegmentation(seg_fn)

Viewing Segmentation Metadata
-----------------------------

.. code:: python

    >>> from __future__ import print_function
    >>> from sfftk.schema import SFFSegmentation
    >>> from sfftk.unittests import TEST_DATA_PATH
    >>> import os
    >>> # XML file
    >>> seg_fn = os.path.join(TEST_DATA_PATH, 'annotated_sff', 'v0.7', 'emd_6338.sff')
    >>> seg = SFFSegmentation(seg_fn)
    >>>
    >>> # name
    >>> print(seg.name)
    Segger Segmentation
    >>>
    >>> # schema version
    >>> print(seg.version)
    0.7.0.dev0
    >>>
    >>> # software details
    ... print(seg.software)
    Software object
    >>>
    >>> # primary descriptor
    >>> print(seg.primaryDescriptor)
    threeDVolume
    >>>
    >>> # transforms
    >>> print(seg.transforms)
    List of transforms
    >>> print(len(seg.transforms))
    2
    >>> print(seg.transforms[0])
    [1.0000 0.0000 0.0000 1.0000 ]
    [0.0000 1.0000 0.0000 1.0000 ]
    [0.0000 0.0000 1.0000 1.0000 ]

    >>>
    >>> # bounding box
    >>> print(seg.boundingBox)
    Bounding box: (0.0, None, 0.0, None, 0.0, None)
    >>>
    >>> # details
    >>> print(seg.details)
    DNA replication in eukaryotes is strictly regulated by several mechanisms. A central step in this replication is the assembly of the heterohexameric minichromosome maintenance (MCM2-7) helicase complex at replication origins during G1 phase as an inactive double hexamer. Here, using cryo-electron microscopy, we report a near-atomic structure of the MCM2-7 double hexamer purified from yeast G1 chromatin. Our structure shows that two single hexamers, arranged in a tilted and twisted fashion through interdigitated amino-terminal domain interactions, form a kinked central channel. Four constricted rings consisting of conserved interior β-hairpins from the two single hexamers create a narrow passageway that tightly fits duplex DNA. This narrow passageway, reinforced by the offset of the two single hexamers at the double hexamer interface, is flanked by two pairs of gate-forming subunits, MCM2 and MCM5. These unusual features of the twisted and tilted single hexamers suggest a concerted mechanism for the melting of origin DNA that requires structural deformation of the intervening DNA.
    >>>

Viewing Segments
----------------

.. code:: python

    >>> print(seg.segments)
    Segment container

Getting The List of Segment IDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> # segment IDs
    >>> print(seg.segments.get_ids())
    [9952, 9859, 9764, 9893, 9897, 9911, 9840, 9955, 9814, 9815, 9956, 9914]

Getting A Segment By ID
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> segment = seg.segments.get_by_id(9911)
    >>> print(segment)
    Segment 9911

Viewing Segment Metadata
------------------------

ID and Parent ID
~~~~~~~~~~~~~~~~

.. code:: python

    >>> print(segment.id)
    9911
    >>> # Every segment is a child of the root segment with parentID = 0
    >>> print(segment.parentID)
    0

Biological Annotation
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> print(segment.biologicalAnnotation)
    Container for biological annotation with 2 external references
    >>>
    >>> print(segment.biologicalAnnotation.description)
    DNA replication licensing factor MCM7
    >>>
    >>> print(segment.biologicalAnnotation.numberOfInstances)
    1
    >>>
    >>> print(segment.biologicalAnnotation.externalReferences)
    External references list with 2 reference(s)
    >>>
    >>> print(segment.biologicalAnnotation.externalReferences[0]) # first reference
    Reference: pr; http://purl.obolibrary.org/obo/PR_P38132; PR_P38132

Complexes and Macromolecules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> print(segment.complexesAndMacromolecules)
    Complexes: 0; Macromolecules: 0
    >>>
    >>> print(segment.complexesAndMacromolecules.complexes)
    Complex list of length 0
    >>>
    >>> print(segment.complexesAndMacromolecules.macromolecules)
    Macromolecule list of length 0

Creating EMDB-SFF Objects
=========================

Users can create EMDB-SFF objects from scratch then export them to a file format of your choice.

.. code:: python

    >>> from __future__ import print_function
    >>> from sfftk import schema
    >>> import sys
    >>> seg = schema.SFFSegmentation()
    >>>
    >>> # We can view how the file looks like so far; note the lack of an XML header <?xml ...>
    >>> seg.export(sys.stderr)
    <segmentation>
        <version>0.7.0.dev0</version>
    </segmentation>

Setting Segmentation Metadata
-----------------------------

.. code:: python
	
    >>> # segmentation name
    >>> seg.name = 'A New Segmentation'
    >>>
    >>> # segmentation software used
    >>> seg.software = schema.SFFSoftware(
    ...     name='Some Software',
    ...     version='v0.1.3.dev3',
    ...     processingDetails='Lorem ipsum dolor...'
    ...     )
    >>>
    >>> # bounding box
    >>> seg.boundingBox = schema.SFFBoundingBox(
    ...     xmin=0,
    ...     xmax=512,
    ...     ymin=0,
    ...     ymax=1024,
    ...     zmin=0,
    ...     zmax=256
    ...     )
    >>>
    >>> # an identity matrix with no transformation
    >>> transform = schema.SFFTransformationMatrix(
    ...     rows=3,
    ...     cols=4,
    ...     data='1 0 0 0 0 1 0 0 0 0 1 0'
    ...     )
    >>>
    >>> # add it to the list of transforms
    >>> seg.transforms = schema.SFFTransformList()
    >>> seg.transforms.add_transform(transform)

Setting Segments
~~~~~~~~~~~~~~~~

Setting Segment Metadata
^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> segment = schema.SFFSegment()

Biological Annotation
'''''''''''''''''''''

.. code:: python


    >>> # define the biological annotation object
    >>> bioAnn = schema.SFFBiologicalAnnotation()
    >>> bioAnn.name = "Segment name"
    >>> bioAnn.description = "Some description"
    >>> bioAnn.numberOfInstances = 1
    >>>
    >>> # define the external references
    >>> extRefs = schema.SFFExternalReferences()
    >>> extRefs.add_externalReference(
    ...     schema.SFFExternalReference(
    ...         type="ncbitaxon",
    ...         otherType="http://purl.obolibrary.org/obo/NCBITaxon_559292",
    ...         value="NCBITaxon_559292",
    ...         label="Saccharomyces cerevisiae S288C",
    ...         description="",
    ...         )
    ...     )
    >>> extRefs.add_externalReference(
    ...     schema.SFFExternalReference(
    ...         type="pdb",
    ...         otherType="http://www.ebi.ac.uk/pdbe/entry/pdb/3ja8",
    ...         value="3ja8",
    ...         label="",
    ...         description="",
    ...         )
    ...     )
    >>> # add the external references to the biological annotation
    >>> bioAnn.externalReferences = extRefs
    >>>
    >>> # add the biological annotation to the segment
    >>> segment.biologicalAnnotation = bioAnn

Complexes and Macromolecules
''''''''''''''''''''''''''''

.. code:: python

    >>> compMacr = schema.SFFComplexesAndMacromolecules()
    >>> # complexes
    >>> comp = schema.SFFComplexes()
    >>> comp.add_complex("comp1")
    >>> comp.add_complex("comp2")
    >>>
    >>> # macromolecules
    >>> macr = schema.SFFMacromolecules()
    >>> macr.add_macromolecule("macr1")
    >>> macr.add_macromolecule("macr2")
    >>>
    >>> # add the complexes and macromolecules
    >>> compMacr.complexes = comp
    >>> compMacr.macromolecules = macr
    >>>
    >>> # add them to the segment
    >>> segment.complexesAndMacromolecules = compMacr

Colour
''''''

Colours should be described using normalised RGBA values (each channel has a value in the interval [0,1]).

.. code:: python

    >>> segment.colour = schema.SFFRGBA(
    ...     red=0.1,
    ...     green=0.2,
    ...     blue=0.3,
    ...     alpha=0.7
    ... )
    >>> segment.colour
    (0.1, 0.2, 0.3, 0.7)


Setting Mesh Segments
^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> from random import random, randint, choice
    >>>
    >>> # the list of meshes
    ...
    >>> meshes = schema.SFFMeshList()
    >>>
    >>> # a mesh
    ...
    >>> mesh = schema.SFFMesh()
    >>>
    >>> # a list of vertices
    ...
    >>> vertices = schema.SFFVertexList()
    >>> no_vertices = randint(0, 100)
    >>>
    >>> # add vertices from the list of vertices
    ...
    >>> for i in range(no_vertices):
    ...     vertex = schema.SFFVertex()
    ...     vertex.point = tuple(
    ...     map(float, (randint(1, 1000), randint(1, 1000), randint(1, 1000))))
    ...     vertices.add_vertex(vertex)
    ...
    >>> # a list of polygons
    ...
    >>> polygons = schema.SFFPolygonList()
    >>> no_polygons = randint(0, 100)
    >>>
    >>> # add polygons to the list of polygons
    ...
    >>> for i in range(no_polygons):
    ...     polygon = schema.SFFPolygon()
    ...     polygon.add_vertex(choice(range(randint(1, 1000))))
    ...     polygon.add_vertex(choice(range(randint(1, 1000))))
    ...     polygon.add_vertex(choice(range(randint(1, 1000))))
    ...     polygons.add_polygon(polygon)
    ...
    >>> # set the vertices and polygons on the mesh
    ...
    >>> mesh.vertices = vertices
    >>> mesh.polygons = polygons
    >>>
    >>> # add the mesh to the list of meshes
    ...
    >>> meshes.add_mesh(mesh)
    >>>
    >>> # add the mesh to the segment
    ...
    >>> segment.meshes = meshes
    >>> segment.meshes
    meshList
    >>> len(segment.meshes)
    1
    >>>

Setting Shape Segments
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> from random import random
    >>>
    >>> # a list of shape
    >>> shapes = schema.SFFShapePrimitiveList()
    >>>
    >>> # a cone
    >>> # first we define the transform that locates it in place
    >>> transform = schema.SFFTransformationMatrix(
    ...     rows=3,
    ...     cols=4,
    ...     data='1 0 0 0 0 1 0 0 0 0 1 0'
    ... )
    >>>
    >>> # second we define its dimension
    >>> shapes.add_shape(
    ...     schema.SFFCone(
    ...         height=random()*100,
    ...         bottomRadius=random()*100,
    ...         transformId=transform.id,
    ...     )
    ... )
    >>>
    >>> # add the transform to the list of transforms
    >>> seg.transforms.add_transform(transform)
    >>>
    >>> # a cuboid
    >>> transform = schema.SFFTransformationMatrix(
    ...     rows=3,
    ...     cols=4,
    ...     data='2 0 0 0 5 3 0 0 27 0 0 1 9'
    ... )
    >>> shapes.add_shape(
    ...     schema.SFFCuboid(
    ...         x=random()*100,
    ...         y=random()*100,
    ...         z=random()*100,
    ...         transformId=transform.id,
    ...     )
    ... )
    >>>
    >>> # add the transform to the list of transforms
    >>> seg.transforms.add_transform(transform)
    >>>
    >>> # a cylinder
    >>> transform = schema.SFFTransformationMatrix(
    ...     rows=3,
    ...     cols=4,
    ...     data='2 0 0 0 15 3 0 0 17 0 0 1 16'
    ... )
    >>> shapes.add_shape(
    ...     schema.SFFCylinder(
    ...         height=random()*100,
    ...         diameter=random()*100,
    ...         transformId=transform.id,
    ...     )
    ... )
    >>>
    >>> # add the transform to the list of transforms
    >>> seg.transforms.add_transform(transform)
    >>>
    >>> # an ellipsoid
    >>> transform = schema.SFFTransformationMatrix(
    ...     rows=3,
    ...     cols=4,
    ...     data='1 0 0 0 15 1 0 0 17 0 0 1 16'
    ... )
    >>> shapes.add_shape(
    ...     schema.SFFEllipsoid(
    ...         x=random()*100,
    ...         y=random()*100,
    ...         z=random()*100,
    ...         transformId=transform.id,
    ...     )
    ... )
    >>>
    >>> # add the transform to the list of transforms
    >>> seg.transforms.add_transform(transform)

Setting Volume Segments
^^^^^^^^^^^^^^^^^^^^^^^

Working with 3D volumes consists of two steps:

* first, we need to define the volumes that contain the actual volume data as a set of :py:class:`sfftk.schema.SFFLattice` objects contained in a :py:class:`sfftk.schema.SFFLatticeList`;

* next, we reference the lattice by specifying how the segment is associated with the lattice e.g. by contour level or voxel value using a :py:class:`sfftk.schema.SFFThreeDVolume` object contained in a :py:class:`sfftk.schema.SFFSegment` object as a ``volume`` attribute i.e. if ``segment`` is a :py:class:`sfftk.schema.SFFSegment` object then ``segment.volume`` will be a :py:class:`sfftk.schema.SFFThreeDVolume` object and we say that ``segment`` contains a ``threeDVolume`` segment representation.

.. code:: python

    >>> import numpy
    >>> # lattice 1
    >>> import random

    >>> # lattice container
    >>> lattices = schema.SFFLatticeList()
    >>>
    >>> # lattice 1
    >>> binlist = numpy.array([random.randint(0, 5) for i in range(20 * 20 * 20)])
    >>> lattice = schema.SFFLattice(
    ...     mode='uint32',
    ...     endianness='little',
    ...     size=schema.SFFVolumeStructure(cols=20, rows=20, sections=20),
    ...     start=schema.SFFVolumeIndex(cols=0, rows=0, sections=0),
    ...     data=binlist,
    ... )
    >>> lattices.add_lattice(lattice)
    >>> lattices
    Container for 3D lattices
    >>> binlist
    array([2, 4, 4, ..., 3, 0, 3])
    >>> binlist.shape
    (8000,)
    >>> lattice = schema.SFFLattice(
    ...     mode='uint32',
    ...     endianness='little',
    ...     size=schema.SFFVolumeStructure(cols=20, rows=20, sections=20),
    ...     start=schema.SFFVolumeIndex(cols=0, rows=0, sections=0),
    ...     data=binlist,
    ... )
    >>> lattice
    3D lattice
    >>> lattice.mode
    'uint32'
    >>> lattice.endianness
    'little'
    >>> lattice.size
    3D volume structure: cols, rows, sections
    >>> lattice.start
    3D volume start index: cols, rows, sections
    >>> # the lattice data is base64 encoded
    >>> lattice.data
    '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'
    >>>
    >>> # lattice 2
    >>> binlist2 = numpy.array([random.random() * 100 for i in xrange(30 * 40 * 50)])
    >>> lattice2 = schema.SFFLattice(
    ...     mode='float32',
    ...     endianness='big',
    ...     size=schema.SFFVolumeStructure(cols=30, rows=40, sections=50),
    ...     start=schema.SFFVolumeIndex(cols=-50, rows=-40, sections=100),
    ...     data=binlist2,
    ... )
    >>> lattices.add_lattice(lattice2)
    >>>
    >>> lattices
    Container for 3D lattices
    >>> len(lattices)
    2
    >>>
    >>> # now we define the segments that reference the lattices above
    >>> # segments
    >>> segments = schema.SFFSegmentList()
    >>>
    >>> # segment one
    >>> segment = schema.SFFSegment()
    >>> vol1_value = 1
    >>> segment.volume = schema.SFFThreeDVolume(
    ...     latticeId=0,
    ...     value=vol1_value,
    ... )
    >>> segment.colour = schema.SFFRGBA(
    ...     red=random.random(),
    ...     green=random.random(),
    ...     blue=random.random(),
    ...     alpha=random.random()
    ... )
    >>> segments.add_segment(segment)
    >>>
    >>> # segment two
    >>> segment = schema.SFFSegment()
    >>> vol2_value = 37.1
    >>> segment.volume = schema.SFFThreeDVolume(
    ...     latticeId=1,
    ...     value=vol2_value
    ... )
    >>> segment.colour = schema.SFFRGBA(
    ...     red=random.random(),
    ...     green=random.random(),
    ...     blue=random.random(),
    ...     alpha=random.random()
    ... )
    >>>

Adding A Segment To The Segmentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once we have added the individual segment representations to the respective segments we can add the segment to the segmentation. The list of segments is contained in a :py:class:`sfftk.schema.SFFSegmentList` object.

.. code:: python

    >>> # create the list of segments
    >>> seg.segments = schema.SFFSegmentList()
    >>>
    >>> # add the segment
    >>> seg.segments.add_segment(segment)
    >>>

Exporting EMDB-SFF Objects
==========================

Finally, after completing the segmentation we can export it to disk as a file. The :py:meth:`sfftk.schema.SFFType.export()` method infers the output file type from from the file extension.

.. code:: python

    >>> # XML
    >>> seg.export('file.sff')
    >>>
    >>> # HDF5
    >>> seg.export('file.hff')
    >>>
    >>> # JSON
    >>> seg.export('file.json')
    >>>

Navigating Your Way Through A Segmentation
==========================================

Iterating
---------

Segments
~~~~~~~~

.. code:: python

    >>> for segment in seg.segments:
    >>>     # do something with segment
    ...     print(segment.id, segment.parentID)
    ...
    2 0


Meshes
~~~~~~

.. code:: python

    >>> for mesh in segment.meshes:
    ...     for vertex in mesh.vertices:
    ...         print(vertex.vID)
    ...         print(vertex.designation) # 'surface' or 'normal'
    ...         x, y, z = vertex.x, vertex.y, vertex.z
    ...
    ...     for polygon in mesh.polygons:
    ...         print(polygon.PID)
    ...         print(polygon.vertex_ids)
    ...
    >>>

External References
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> for extRef in segment.biologicalAnnotation.externalReferences:
    ...     print(extRef.type)
    ...     print(extRef.otherType)
    ...     print(extRef.value)
    ...     print(extRef.label)
    ...     print(extRef.description)
    ...
    >>>


Annotating EMDB-SFF Objects
===========================

Use the :py:mod:`sfftk.notes.modify` module to perform annotations

Note Objects
------------

.. code:: python

    >>> from sfftk.notes.modify import SimpleNote, ExternalReference
    >>>
    >>> note = SimpleNote()
    >>> note.name = 'some name'
    >>> note.description = 'some description'
    >>> note.numberOfInstances = 5
    >>> # these are random data hence no real label and description will be found
    >>> Es = [
        ExternalReference(type_='ontology1', otherType='iri1', value='obo_id1'),
    ...     ExternalReference(type_='ontology2', otherType='iri2', value='obo_id2'),
    ... ]
    Tue Mar 12 13:21:48 2019	Could not find label and description for external reference ontology1:obo_id1
    Tue Mar 12 13:21:48 2019	Could not find label and description for external reference ontology2:obo_id2
    >>> note.externalReferences = Es
    >>> note.complexes = ['comp1', 'comp2']
    >>> note.macromolecules = ['macr1', 'macr2']
    >>> note
    <sfftk.notes.modify.SimpleNote object at 0x10c9c0550>
    >>> note.name
    'some name'
    >>> note.description
    'some description'
    >>> note.externalReferences
    [<sfftk.notes.modify.ExternalReference object at 0x10c960dd0>, <sfftk.notes.modify.ExternalReference object at 0x10bfc66d0>]
    >>> note.externalReferences[0]
    <sfftk.notes.modify.ExternalReference object at 0x10c960dd0>
    >>> note.externalReferences[0].type
    'ontology1'
    >>> note.externalReferences[0].otherType
    'iri1'
    >>> note.externalReferences[0].value
    'obo_id1'
    >>> note.complexes
    ['comp1', 'comp2']
    >>> note.macromolecules
    ['macr1', 'macr2']
    >>>


Adding Notes
------------

.. code:: python

    >>> from sfftk.schema import SFFSegment
    >>>
    >>> segment = SFFSegment()
    >>>
    >>> # add the notes
    >>> segment = note.add_to_segment(segment)
    Tue Mar 12 13:24:06 2019	Could not find label and description for external reference ontology1:obo_id1
    Tue Mar 12 13:24:06 2019	Could not find label and description for external reference ontology2:obo_id2
    >>>


.. _editing_notes:

Editing Notes
-------------

First make an note containing the edits. For ``externalReference``, ``complex`` and ``macromolecules`` specify the ``ID`` to be edited with the ``externalReferenceId``, ``complexId`` and ``macromoleculeId``, respectively.

.. code:: python

    >>> edit_note = SimpleNote(
	...     description='new description',
	...     numberOfInstances=14,
	...     externalReferenceId=0, # the external reference ID to change
	...     externalReferences=[
	...      ExternalReference(type='x', otherType='y', value='z')
	...      ],
	...     complexId=3,
	...     complexes=['comp1', 'comp2'],
	...     macromoleculeId=0,
	...     macromolecules=['macr1', 'macr2'],
	...     )
    >>>

Then call the edit method

.. code:: python

    >>> segment = edit_note.edit_in_segment(segment)

Deleting Notes
--------------

In a similar manner to :ref:`editing_notes`, create a note object indicating which attributes (``description``, ``numberOfInstances`` etc.) and/or IDs should be deleted in the target note.

.. code:: python

    >>> del_note = SimpleNote(
	...     description=True,
	...     numberOfInstances=True,
	...     externalReferenceId=2,
	...     complexId=3,
	...     macromoleculeId=0
	...     )
    >>>

Then call the notes ``delete`` method.

.. code:: python

    >>> segment = del_note.delete_from_segment(segment)

Reading Application-Specific Segmentation Files 
================================================

Application-specific file format readers and converters are defined in the sfftk.formats package with each module defined by the file extension. For example, AmiraMesh files have an 'am' extension hence we would read them using the sfftk.formats.am module which defines an AmiraMeshSegmentation class.

AmiraMesh (.am)
---------------

.. code:: python

    >>> from sfftk.formats.am import AmiraMeshSegmentation
    >>> am_seg = AmiraMeshSegmentation('file.am')

CCP4 (.map)
-----------

.. code:: python

    >>> from sfftk.formats.map import MAPSegmentation
    >>> map_seg = MAPSegmentation('file.map')

IMOD (.mod)
-----------

.. code:: python

    >>> from sfftk.formats.mod import IMODSegmentation
    >>> mod_seg = IMODSegmentation('file.mod')

Segger (.seg)
-------------

.. code:: python

    >>> from sfftk.formats.seg import SeggerSegmentation
    >>> seg_seg = SeggerSegmentation('file.seg')

STL (.stl)
----------

.. code:: python

    >>> from sfftk.formats.stl import STLSegmentation
    >>> stl_seg = STLSegmentation('file.stl')

Amira HyperSurface (.surf)
--------------------------

.. code:: python

    >>> from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
    >>> surf_seg = AmiraHyperSurfaceSegmentation('file.surf')

Converting Application-Specific Segmentations to EMDB-SFF
---------------------------------------------------------

Use the ``convert`` method on a segmentation object to effect the conversion to an EMDB-SFF object.

.. code:: python

    >>> sff_seg = as_seg.convert()

Remember, the segmentation is only an EMDB-SFF object and is not of a particular file format. The file format is chosen by the extension when `using the export method <#exporting-emdb-sff-objects>`__.
