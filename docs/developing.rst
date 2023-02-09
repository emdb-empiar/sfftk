==========================
Developing with ``sfftk``
==========================

.. contents::

Introduction
============

``sfftk`` has been designed to be relatively straightforward to integrate into other Python applications because it has been designed in such a way that the various components are independent of one another. The main components of the package are:

* the **schema** API (:py:mod:`sfftk.schema`) which handles how data fields are represented independent of the file formats to be used (XML, HDF5 and JSON). This package provides an adapter to the underlying `GenerateDS <https://www.davekuhlman.org/generateDS.html>`_ API which *extends* and *simplifies* EMDB-SFF fields.

.. deprecated:: v0.5

    ``sfftk`` uses the schema API provided by the minimal :py:mod:`sfftkrw` package. Installing ``sfftk`` automatically installs ``sfftk-rw``.

* the **core** API (:py:mod:`sfftk.core`) provides a set of useful utilities mainly for the command-line toolkit (``sff`` command) that handle command line arguments (making sure that they have the right values), read persistent configs from disk, do any prep work on segmentation files as well as several print and miscellaneous utilities.

* the **readers** API (:py:mod:`sfftk.readers`) implements *ad hoc* segmentation file format readers. They are *ad hoc* because they are not expected to conform to a rigid API. For example, the :py:mod:`sfftk.readers.segreader` module has a single class (:py:class:`sfftk.readers.segreader.SeggerSegmentation`) which represents a Segger segmentation, which is completely different from the :py:mod:`sfftk.readers.modreader` module which has over 20 classes representing the various components of an IMOD segmentation. The only requirement of a segmentation reader module in this package is that it has to implement a ``get_data(fn, *args, **kwargs)`` function which returns the *ad hoc* segmentation object(s).

* the **format** API (:py:mod:`sfftk.formats`) provides adapters that correspond to individual readers. It is the responsibility of the modules in this package to *adapt* the *ad hoc* segmentation representation to an EMDB-SFF representation. This is where the call to ``get_data(fn, *args, **kwargs)`` will be invoked. For example, the :py:mod:`sfftk.formats.mod` module has a :py:class:`sfftk.formats.mod.IMODSegmentation` class which invokes the :py:func:`sfftk.readers.modreader.get_data()` function to supply the *ad hoc* :py:class:`sfftk.readers.modreader.IMOD` object that contains the IMOD segmentation. Presently, this API only provides the ability to read application-specific segmentation files. We hope to eventually add the ability to write out application-specific segmentation files.

* finally, the **notes** API (:py:mod:`sfftk.notes`) supplies three modules for *finding* (:py:mod:`sfftk.notes.find`), *modifying* (:py:mod:`sfftk.notes.modify`) and *viewing* (:py:mod:`sfftk.notes.view`) annotations.


Annotating EMDB-SFF Objects
===========================

Use the :py:mod:`sfftk.notes.modify` module to perform annotations

Note Objects
------------
There are two types of note objects: :py:class:`sfftk.notes.modify.GlobalSimpleNote` for annotating a segmentation and :py:class:`sfftk.notes.modify.SimpleNote` for annotating a segment.

.. code:: python

    >>> from sfftk.notes.modify import SimpleNote, GlobalSimpleNote, ExternalReference
    >>> global_note = GlobalSimpleNote()
    >>> global_note.name = "Segmentation of Mitochondria in Organism"
    >>> global_note.details = "Lorem ipsum dolor sit amet consetetur..."
    >>> global_note.software_name = "Paraview"
    >>> global_note.software_version = "5.2"
    >>> global_note.software_processing_details = "We used the contour filter to extract the isosurface at a contour level of 3.8"
    >>> note = SimpleNote()
    >>> note.name = 'some name'
    >>> note.description = 'some description'
    >>> note.number_of_instances = 5
    >>> # these are random data hence no real label and description will be found
    >>> Es = [
            ExternalReference(resource='ontology1', url='url1', accession='obo_id1'),
    ...     ExternalReference(resource='ontology2', url='url2', accession='obo_id2'),
    ... ]
    Tue Mar 12 13:21:48 2019	Could not find label and description for external reference ontology1:obo_id1
    Tue Mar 12 13:21:48 2019	Could not find label and description for external reference ontology2:obo_id2
    >>> note.external_references = Es
    >>> note
    <sfftk.notes.modify.SimpleNote object at 0x10c9c0550>
    >>> note.name
    'some name'
    >>> note.description
    'some description'
    >>> note.external_references
    [<sfftk.notes.modify.ExternalReference object at 0x10c960dd0>, <sfftk.notes.modify.ExternalReference object at 0x10bfc66d0>]
    >>> note.external_references[0]
    <sfftk.notes.modify.ExternalReference object at 0x10c960dd0>
    >>> note.external_references[0].resource
    'ontology1'
    >>> note.external_references[0].url
    'url1'
    >>> note.external_references[0].accession
    'obo_id1'
    >>>


Adding Notes
------------
Adding notes to the segmentation:

.. code:: python

    >>> from sfftkrw import SFFSegmentation
    >>>
    >>> segmentation = SFFSegmentation()
    >>>
    >>> segmentation = global_note.add_to_segmentation(segmentation)

.. code:: python

    >>> from sfftkrw import SFFSegment
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

First make an note containing the edits. For ``external_references`` specify the ``ID`` to be edited with the ``external_reference_id``.

.. code:: python

    >>> edit_note = SimpleNote(
    ...     name='some name',
	...     description='new description',
	...     number_of_instances=14,
	...     external_reference_id=0, # the external reference ID to change
	...     external_references=[
	...      ExternalReference(resource='x', url='y', accession='z')
	...      ],
	...     )
    >>>

Then call the edit method

.. code:: python

    >>> segment = edit_note.edit_in_segment(segment)

The same applies to ``GlobalSimpleNote`` objects only that we can also specify the ``software_id``, ``transform_id`` and ``external_reference_id``:

.. code:: python

    >>> from sfftk.notes.modify import GlobalSimpleNote
    >>> edit_segmentation_note = GlobalSimpleNote(
            name="A new segmentation name",
            details="Many more changes to the details than you can allow",
            software_id=0, # this is the software we will modify
            software_name="New software",
            software_version="v2023.27",
            software_processing_details="A new description of how this software was used",
            transform_id=0,
            transform=[13.0, 0, 0, 0, 0, 13.0, 0, 0, 0, 0, 13.0, 0],
    )
    >>> segmentation = edit_segmentation_note.edit_in_segmentation(segmentation)
    >>>> # you can modify the external references separately or jointly with other fields
    >>> edit_segmentation_extrefs = GlobalSimpleNote(
            external_reference_id=0,
            external_references=[('res0', 'url0', 'acc0'), ('res1', 'url1', 'acc1')]
    )
    >>> segmentation = edit_segmentation_extrefs.edit_in_segmentation(segmentation)

Deleting Notes
--------------

In a similar manner to :ref:`editing_notes`, create a note object indicating which attributes (``name``, ``description``, ``number_of_instances`` etc.) and/or IDs should be deleted in the target note.

.. code:: python

    >>> del_note = SimpleNote(
    ...     name=True,
	...     description=True,
	...     number_of_instances=True,
	...     external_reference_id=2,
	...     )
    >>>

Then call the notes ``delete`` method.

.. code:: python

    >>> segment = del_note.delete_from_segment(segment)

Similarly, for ``GlobalSimpleNote``:

.. code:: python

    >>> from sfftk.notes.modify import GlobalSimpleNote
    >>> del_global_note = GlobalSimpleNote(
            name=True, # delete the name
            details=True,
            software_id=[0], # use a list to indicate all to be deleted
            transform_id=[1,2], # delete multiple (if they exist)
            external_reference_id=[3,4,5] # again, multiple
    )
    >>> segmentation = del_global_note.del_from_segmentation(segmentation)

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

Remember, the segmentation is only an EMDB-SFF object and is not of a particular file format. The file format is chosen by the extension when using the :py:meth:`sfftkrw.schema.base.SFFType.export` method.
