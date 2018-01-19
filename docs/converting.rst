============================
Converting Files To EMDB-SFF
============================

.. contents::

Introduction
============

Converting files to use the EMDB-SFF data model is one of the core functions of sfftk. This guide describes in detail how to accomplish conversions.

Quick Start
-----------

Getting Help
~~~~~~~~~~~~

.. code:: bash

    sff convert
    sff convert --help

Output to XML (Default)
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert file.seg

Specify Output File
~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert file.seg -o file.sff
    sff convert file.seg --output /path/to/output/file.sff
    sff convert file.seg -o file.hff

Specify Output Format
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert file.seg -f hff
    sff convert file.seg --format hff

EMDB-SFF Format Interconversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert file.sff --output /path/to/output/file.hff
    sff convert file.hff --format json
    sff convert file.sff --format sff

Verbose Operation
~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert --verbose file.hff

Truncate Segments (Segger Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert --top-level-only file.seg

Set Details
~~~~~~~~~~~

.. code:: bash

    sff convert --details “Lorem ipsum dolor…” file.seg

Change Primary Descriptor
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert --primary-descriptor contourList file.surf # AmiraHxSurface file

Contours To Mesh (Experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert -M file.sff
    sff convert --contour-to-mesh file.sff --output file_mesh.sff

Input Formats
=============

sfftk can convert `several segmentation file formats <https://docs.google.com/document/d/1ljX7mlo5Vj4dTSf7jSzbwRoqPfab2r5tjFijqEi3hGM/edit#heading=h.6rhhnuaqaszp>`__ into EMDB-SFF files.

Output Formats
==============

EMDB-SFF files can be output as XML (.sff), HDF5 (.hff) or JSON (.json).

-  XML EMDB-SFF files are typically relatively large compared to HDF5 and JSON equivalents. The compression applied in HDF5 files makes them ideal for large datasets.

-  JSON EMDB-SFF files do not contain geometric descriptors and are primarily used as temporary files during annotation.

-  Interconversion of the three formats is lossless (with the exception of geometrical data when converting to JSON - all geometrical data is excluded).

There are two ways to perform conversion:

-  Specifying the output path with -o/--output flag

-  Specifying the output format with -f/--format flag

Specifying the output path with -o/--output flag
------------------------------------------------

Conversion is performed as follows:

.. code:: bash

    sff convert file.seg -o file.sff
    sff convert file.seg --output /path/to/output/file.sff

The output file extension determines the output format i.e.

.. code:: bash

    sff convert file.seg -o file.hff

will result in an HDF5 file while

.. code:: bash

    sff convert file.seg --output file.json

will be a JSON file.

Specifying the output format with -f/--format flag
--------------------------------------------------

The -f/--format options ensures that the output file will be in the same directory as the original segmentation file. The -f flag takes one of three values:

-  ‘sff’ for XML files

-  ‘hff’ for HDF5 files

-  ‘json’ for JSON files.

Any other value raises an error.

.. code:: bash

    sff convert file.seg -f hff
    sff convert file.seg --format hff

The default format (if none is specified) is ‘sff’ (XML).

.. code:: bash

    sff convert file.seg

results in file.sff as output.

Running sff convert with no options or with -h/--help displays help.

.. code:: bash

    sff convert
    INSERT OUTPUT

EMDB-SFF Format Interconversion
-------------------------------

It is also possible to perform interconversions from XML, HDF5 and JSON EMDB-SFF files.

.. code:: bash

    sff convert file.sff --output /path/to/output/file.hff

or using --format

.. code:: bash

    sff convert file.hff --format json

Even null conversions are possible:

.. code:: bash

    sff convert file.sff --format sff

As stated previously, conversion to JSON drops all geometrical descriptions. Similarly, conversions from JSON to EMDB-SFF will not reinstate the geometric description information.

Verbose Operation
=================

As with many Linux shell programs the -v/--verbose option prints status information on the terminal.

.. code:: bash

    sff convert --verbose file.hff
    Tue Sep 12 15:29:18 2017 Seting output file to file.sff
    Tue Sep 12 15:29:18 2017 Converting from EMDB-SFF (HDF5) file file.hff
    Tue Sep 12 15:30:03 2017 Created SFFSegmentation object
    Tue Sep 12 15:30:03 2017 Exporting to file.sff
    Tue Sep 12 15:30:07 2017 Done

Truncating Segments (Segger Only)
=================================

Segger segmentations include hundreds to thousands of sub-segmentations due to how the algorithm it uses (watershed algorithm) identifies segmentations. The segmentations thus form a tree with the root having a value of zero. Mostly, we are only interested in the children of the root which are in themselves roots of another tree. This option only transfers the children of the global root into the EMDB-SFF file.

Consider the following tree of segments:

.. image:: converting-01.png

The segmentation contains different levels commencing from the root down, with children segments *contained within* parent segments. Specifying -t/--top-level-only treats only children of the *root* as segments and excludes all others. Therefore, running

.. code:: bash

    sff convert --top-level-only file.seg

on the above will produce an EMDB-SFF file with only three segments. Excluding this option means that the resulting EMDB-SFF file will be relatively large.

Specify Details
===============

The EMDB-SFF data model provides for an optional <details/> tag for auxilliary information. The contents of this option will be put into <details/>.

.. code:: bash

    sff convert --details “Lorem ipsum dolor…” file.seg

TODO: ALLOW A USER TO PASS A FILE WHOSE CONTENTS WILL BE INSERTED INTO <details/>.

Changing The Primary Descriptor
===============================

The EMDB-SFF data model provides for four possible geometrical descriptors: `meshes (meshList), shape primitives (shapePrimitiveList)` and `3D volumes (threeDVolume)`. 
In some cases, e.g., IMOD segmentations, more than one geometrical descriptor may have been specified for the same segmentations. 
The mandatory `<primaryDescriptor/>` field specifies the main geometrical descriptor to be used when performing conversions and other processing tasks. 
Only valid values are allowed; otherwise a ValueError is raised.

.. code:: bash

    sff convert --primary-descriptor contourList file.surf # AmiraHxSurface file

The table below shows valid primary descriptors by file type.
	
+-------------------+-------------------------------------------------------+
|**File format**    | **Valid primary descriptors**                         |
+===================+=======================================================+
|AmiraMesh          | contourList                                           |
+-------------------+-------------------------------------------------------+
|AmiraHxSurface     | meshList                                              |
+-------------------+-------------------------------------------------------+
|CCP4 masks         | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
|IMOD               | contourList (default), meshList, shapePrimitiveList   |
+-------------------+-------------------------------------------------------+
|Segger             | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
|STL                | meshList                                              |
+-------------------+-------------------------------------------------------+

Note that the primary descriptor should only be changed to a value of a geometrical descriptor that is *actually* present in the EMDB-SFF file.

For IMOD files, sfftk tries to intelligently determine which primary descriptor to use. Also, it also tries to ensure that a change corresponds to the actual file contents.

