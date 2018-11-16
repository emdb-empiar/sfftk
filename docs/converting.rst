============================
Converting Files To EMDB-SFF
============================

.. contents::

Introduction
============

Converting files to use the EMDB-SFF data model is one of the core functions 
of ``sfftk``. This guide describes in detail how to accomplish conversions.

Synopsis
--------

Running

.. code:: bash

    sff convert
    sff convert -h
    sff convert --help

displays all conversion options.

.. code:: bash

    sff convert
    usage: sff convert [-h] [-p CONFIG_PATH] [-b] [-t] [-d DETAILS]
                       [-R PRIMARY_DESCRIPTOR] [-v] [-m] [-o OUTPUT | -f FORMAT]
                       [from_file [from_file ...]]

    Perform conversions to EMDB-SFF

    positional arguments:
      from_file             file to convert from

    optional arguments:
      -h, --help            show this help message and exit
      -p CONFIG_PATH, --config-path CONFIG_PATH
                            path to configs file
      -b, --shipped-configs
                            use shipped configs only if config path and user
                            configs fail [default: False]
      -t, --top-level-only  convert only the top-level segments [default: False]
      -d DETAILS, --details DETAILS
                            populates <details>...</details> in the XML file
                            [default: '']
      -R PRIMARY_DESCRIPTOR, --primary-descriptor PRIMARY_DESCRIPTOR
                            populates the
                            <primaryDescriptor>...</primaryDescriptor> to this
                            value [valid values: threeDVolume, meshList,
                            shapePrimitiveList]
      -v, --verbose         verbose output
      -m, --multi-file      enables convert to treat multiple files as individual
                            segments of a single segmentation; only works for the
                            following filetypes: stl, map, mrc, rec [default:
                            False]
      -o OUTPUT, --output OUTPUT
                            file to convert to; the extension (.sff, .hff, .json)
                            determines the output format [default: None]
      -f FORMAT, --format FORMAT
                            output file format; valid options are: sff (XML), hff
                            (HDF5), json (JSON) [default: sff]

Quick Start
-----------

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
    sff convert file.seg -o file.json # only metadata; no geometrical data

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

    sff convert -v file.hff
    sff convert --verbose file.hff

Truncate Segments (Segger Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert -t file.seg
    sff convert --top-level-only file.seg

Set Details
~~~~~~~~~~~

.. code:: bash

    sff convert -d "Lorem ipsum dolor..." file.seg
    sff convert --details "Lorem ipsum dolor..." file.seg file.seg

Change Primary Descriptor
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff convert -R contourList file.surf # AmiraHxSurface file
    sff convert --primary-descriptor contourList file.surf # AmiraHxSurface file


Input Formats
=============

``sfftk`` can convert several segmentation file formats (see 
:ref:`supported_formats`) into EMDB-SFF files.

Output Formats
==============

EMDB-SFF files can be output as XML (``.sff``), HDF5 (``.hff``) or JSON 
(``.json``).

-  XML EMDB-SFF files are typically relatively large compared to HDF5 and 
    JSON equivalents. The compression applied in HDF5 files makes them ideal
    for large datasets.

-  JSON EMDB-SFF files do not contain geometric descriptors and are primarily 
    used as temporary files during annotation.

-  Interconversion of the three formats is lossless (with the exception of 
    geometrical data when converting to JSON - all geometrical data is excluded).

There are two ways to perform conversion:

-  Specifying the output path with ``-o/--output`` flag

-  Specifying the output format with ``-f/--format`` flag

Specifying the output path with ``-o/--output`` flag
----------------------------------------------------

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

Specifying the output format with ``-f/--format`` flag
-------------------------------------------------------

The -f/--format options ensures that the output file will be in the same 
directory as the original segmentation file. The -f flag takes one of three 
values:

-  'sff' for XML files

-  'hff' for HDF5 files

-  'json' for JSON files.

Any other value raises an error.

.. code:: bash

    sff convert file.seg -f hff
    sff convert file.seg --format hff

The default format (if none is specified) is ‘sff’ (XML).

.. code:: bash

    sff convert file.seg

results in file.sff as output.

EMDB-SFF Format Interconversion
-------------------------------

It is also possible to perform interconversions between XML, HDF5 and JSON 
EMDB-SFF files.

.. code:: bash

    sff convert file.sff --output /path/to/output/file.hff

or using --format

.. code:: bash

    sff convert file.hff --format json

Even null conversions are possible:

.. code:: bash

    sff convert file.sff --format sff

As stated previously, conversion to JSON drops all geometrical descriptions. 
Similarly, conversions from JSON to EMDB-SFF will not reinstate the geometric 
description information.

Verbose Operation
=================

As with many Linux shell programs the ``-v/--verbose`` option prints status 
information on the terminal.

.. code:: bash

    sff convert --verbose file.hff
    Tue Sep 12 15:29:18 2017 Seting output file to file.sff
    Tue Sep 12 15:29:18 2017 Converting from EMDB-SFF (HDF5) file file.hff
    Tue Sep 12 15:30:03 2017 Created SFFSegmentation object
    Tue Sep 12 15:30:03 2017 Exporting to file.sff
    Tue Sep 12 15:30:07 2017 Done

Truncating Segments (Segger Only)
=================================

Segger segmentations include hundreds to thousands of sub-segmentations due to 
how the algorithm it uses (watershed algorithm) to segment the volume. 
The segmentations thus form a tree with the root having an ID of zero. 
Mostly, we are only interested in the children of the root which are in 
themselves roots of another tree. Specifying this option only transfers the 
children of the global root into the EMDB-SFF file.

Consider the following tree of segments:

.. image:: converting-01.png

The segmentation contains different levels commencing from the root down, with 
children segments *contained within* parent segments. Specifying 
``-t/--top-level-only`` treats only children of the *root* as segments and 
excludes all others. Therefore, running

.. code:: bash

    sff convert --top-level-only file.seg

on the above will produce an EMDB-SFF file with only three segments. Excluding 
this option means that the resulting EMDB-SFF file will be relatively large.

Specify Details
===============

The EMDB-SFF data model provides for an optional ``<details/>`` tag for 
auxilliary information. The contents of this option will be put into 
``<details/>.``

.. code:: bash

    sff convert --details "Lorem ipsum dolor..." file.seg

.. todo::

    Allow a user to pass a **file** whose contents will be inserted into ``<details/>``.


Changing The Primary Descriptor
===============================

The EMDB-SFF data model provides for three possible geometrical descriptors: 
`meshes (meshList), shape primitives (shapePrimitiveList)` and 
`3D volumes (threeDVolume)`.
 
In some cases, such as with IMOD segmentations, more than one geometrical 
descriptor may have been specified for the same segmentations.
 
The mandatory ``<primaryDescriptor/>`` field specifies the main geometrical
descriptor to be used when performing conversions and other processing tasks. 
Only valid values are allowed; otherwise a ``ValueError`` is raised.

The table below shows valid primary descriptors by file type.

+-------------------+-------------------------------------------------------+
|**File format**    | **Valid primary descriptors**                         |
+===================+=======================================================+
|AmiraMesh          | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
|AmiraHxSurface     | meshList                                              |
+-------------------+-------------------------------------------------------+
|CCP4 masks         | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
|IMOD               | meshList (default), shapePrimitiveList                |
+-------------------+-------------------------------------------------------+
|Segger             | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
|STL                | meshList                                              |
+-------------------+-------------------------------------------------------+

.. note::

    IMOD files must have a mesh generated using ``imodmesh`` command.

Note that the primary descriptor should only be changed to a value of a 
geometrical descriptor that is *actually* present in the EMDB-SFF file.

For IMOD files, ``sfftk`` tries to infer which primary descriptor to use. 
Also, if the primary descriptor is changed, it tries to ensure that a change
corresponds to the actual file contents.



Specifying Configurations To Use
=================================

``sfftk`` makes use of persistent configurations which affect how certain operations
are performed. There are three types of configurations detailed in the dedicated 
documentation on configs (see :ref:`configs`) in decreasing order of priority:

- custom configs defined in a ``path/to/sff.conf`` file;

- user configs stored in ``~/.sfftk/sff.conf``;

- shipped configs which will sit with the installed ``sfftk`` package.

Custom configs are invoked using the ``-p/--config-path`` option:

.. code:: bash

    sff convert -p path/to/configs file.seg
    sff convert --config-path path/to/configs file.seg

User configs are default and require no special flags.

Shipped configs use the ``-b/--shipped-configs`` flag with no arguments:

.. code:: bash

    sff convert -b file.am
    sff convert --shipped-configs file.am


Working with Multifile Segmentations
====================================

Some of the segmentation file formats supported are designed to hold one segment per file.
Therefore, representating a complete segmentation will require multiple files.

Currently the following file formats are multifile by design:

* **CCP4 and related files** - these files store segments as a 3D volume with segment region marked by
  specific voxel values (e.g. ``1`` for *in* segment voxels and ``0`` for the background. Specific file
  formats have ``.mrc``, ``.map`` and ``.rec``.

* **Stereolithography files** - while it is possible to concatenate several STL files into one,
  STL files do not contain metadata such as segment colour. Therefore, it is best to handle them as
  multifiles. STL files have a ``.stl`` extension.

Multifiles utilise the ``-m/--multi-file`` argument followed by all the files each of which should
specify a single segment.

.. code:: bash

    sff convert -m file1.map file2.map file3.map

The above command will use default options and write an EMDB-SFF file to ``file1.sff``. Alternatively,
the user should specify the output file

.. code:: bash

    sff convert -m file1.map file2.map file3.map --output file.sff


