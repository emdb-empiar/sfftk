============================
Converting Files To EMDB-SFF
============================

Introduction
============

Converting files to use the EMDB-SFF data model is one of the core
functions of sfftk. This guide describes in detail how to accomplish
conversions.

Quick Start
-----------

Getting Help
~~~~~~~~~~~~

$ sff convert

$ sff convert --help

Output to XML (Default)
~~~~~~~~~~~~~~~~~~~~~~~

$ sff convert file.seg

Specify Output File
~~~~~~~~~~~~~~~~~~~

| $ sff convert file.seg -o file.sff
| $ sff convert file.seg --output /path/to/output/file.sff

$ sff convert file.seg -o file.hff

Specify Output Format
~~~~~~~~~~~~~~~~~~~~~

| $ sff convert file.seg -f hff
| $ sff convert file.seg --format hff

EMDB-SFF Format Interconversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff convert file.sff --output /path/to/output/file.hff

$ sff convert file.hff --format json

$ sff convert file.sff --format sff

Verbose Operation
~~~~~~~~~~~~~~~~~

$ sff convert --verbose file.hff

Truncate Segments (Segger Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff convert --top-level-only file.seg

Set Details
~~~~~~~~~~~

$ sff convert --details “Lorem ipsum dolor…” file.seg

Change Primary Descriptor
~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff convert --primary-descriptor contourList file.surf #
AmiraHxSurface file

Contours To Mesh (Experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff convert -M file.sff

$ sff convert --contour-to-mesh file.sff --output file\_mesh.sff

Input Formats
=============

sfftk can convert `*several segmentation file
formats* <https://docs.google.com/document/d/1ljX7mlo5Vj4dTSf7jSzbwRoqPfab2r5tjFijqEi3hGM/edit#heading=h.6rhhnuaqaszp>`__
into EMDB-SFF files.

Output Formats
==============

EMDB-SFF files can be output as XML (.sff), HDF5 (.hff) or JSON (.json).

-  XML EMDB-SFF files are typically relatively large compared to HDF5
       and JSON equivalents. The compression applied in HDF5 files makes
       them ideal for large datasets.

-  JSON EMDB-SFF files do not contain geometric descriptors and are
       primarily used as a temporary files during annotation.

-  Interconversion of the three formats is lossless (with the exception
       of geometrical data when converting to JSON - all geometrical
       data is excluded).

There are two ways to perform conversion:

-  Specifying the output path with -o/--output flag

-  Specifying the output format with -f/--format flag

Specifying the output path with -o/--output flag
------------------------------------------------

Conversion is performed as follows:

| $ sff convert file.seg -o file.sff
| $ sff convert file.seg --output /path/to/output/file.sff

The output file extension determines the output format i.e.

$ sff convert file.seg -o file.hff

will result in an HDF5 file while

$ sff convert file.seg --output file.json

will be a JSON file.

Specifying the output format with -f/--format flag
--------------------------------------------------

The -f/--format options ensures that the output file will be in the same
directory as the original segmentation file. The -f flag takes one of
three values:

-  ‘sff’ for XML files

-  ‘hff’ for HDF5 files

-  ‘json’ for JSON files.

Any other value raises an error.

| $ sff convert file.seg -f hff
| $ sff convert file.seg --format hff

The default format (if none is specified) is ‘sff’ (XML).

$ sff convert file.seg

results in file.sff as output.

Running sff convert with no options or with -h/--help displays help.

$ sff convert

usage: sff convert [-h] [-t] [-M] [-d DETAILS] [-P PRIMARY\_DESCRIPTOR]
[-v]

[-s SUB\_TOMOGRAM\_AVERAGE SUB\_TOMOGRAM\_AVERAGE]

[-o OUTPUT \| -f FORMAT]

from\_file

Perform conversions to EMDB-SFF

positional arguments:

from\_file file to convert from

optional arguments:

-h, --help show this help message and exit

-t, --top-level-only convert only the top-level segments [default:
False]

-M, --contours-to-mesh

convert an 'contourList' EMDB-SFF to a 'meshList'

EMDB-SFF

-d DETAILS, --details DETAILS

populates <details>...</details> in the XML file

[default: '']

-P PRIMARY\_DESCRIPTOR, --primary-descriptor PRIMARY\_DESCRIPTOR

populates the

<primaryDescriptor>...</primaryDescriptor> to this

value [valid values: threeDVolume, contourList,

meshList, shapePrimitiveList]

-v, --verbose verbose output

-s SUB\_TOMOGRAM\_AVERAGE SUB\_TOMOGRAM\_AVERAGE, --sub-tomogram-average
SUB\_TOMOGRAM\_AVERAGE SUB\_TOMOGRAM\_AVERAGE

convert a subtomogram average into an EMDB-SFF file;

two arguments are required: the table file and volume

file (in that order)

-o OUTPUT, --output OUTPUT

file to convert to; the extension (.sff, .hff, .json)

determines the output format [default: None]

-f FORMAT, --format FORMAT

output file format; valid options are: sff (XML), hff

(HDF5), json (JSON) [default: sff]

EMDB-SFF Format Interconversion
-------------------------------

It is also possible to perform interconversions from XML, HDF5 and JSON
EMDB-SFF files.

$ sff convert file.sff --output /path/to/output/file.hff

or using --format

$ sff convert file.hff --format json

Even null conversions are possible:

$ sff convert file.sff --format sff

As stated previously, conversion to JSON drop all geometrical
descriptions. Similarly, conversions from JSON EMDB-SFF

Verbose Operation
=================

As with many Linux shell programs the -v/--verbose option prints status
information on the terminal.

$ sff convert --verbose file.hff

Tue Sep 12 15:29:18 2017 Seting output file to file.sff

Tue Sep 12 15:29:18 2017 Converting from EMDB-SFF (HDF5) file file.hff

Tue Sep 12 15:30:03 2017 Created SFFSegmentation object

Tue Sep 12 15:30:03 2017 Exporting to file.sff

Tue Sep 12 15:30:07 2017 Done

Truncating Segments (Segger Only)
=================================

Segger segmentations include hundreds to thousands of sub-segmentations
due to how the algorithm it uses (watershed algorithm) identifies
segmentations. The segmentations thus form a tree with the root having a
value of zero. Mostly, we are only interested in the children of the
root which are in themselves roots of another tree. This option only
transfers the children of the global root into the EMDB-SFF file.

Consider the following tree of segments:

The segmentation contains different levels commencing from the root down
with children segments *contained within* parent segments. Specifying
-t/--top-level-only treats only children of the *root* as segments and
excludes all others. Therefore, running

$ sff convert --top-level-only file.seg

on the above will produce an EMDB-SFF file with only three segments.
Excluding this option means that the resulting EMDB-SFF file will be
relatively large.

Specify Details
===============

The EMDB-SFF data model provides for an optional <details/> tag. The
contents of this option will be put into <details/>.

$ sff convert --details “Lorem ipsum dolor…” file.seg

TODO: ALLOW A USER TO PASS A FILE WHOSE CONTENTS WILL BE INSERTED INTO
<details/>.

Changing The Primary Descriptor
===============================

The EMDB-SFF data model provides for four possible geometrical
descriptors: contours (contourList), meshes (meshList), shape primitives
(shapePrimitiveList) and 3D volumes (threeDVolume). The mandatory
<primaryDescriptor/> field specifies the main geometrical descriptor to
be used when performing conversions and other processing tasks. Only
valid values are allowed; otherwise a ValueError is raised.

$ sff convert --primary-descriptor contourList file.surf #
AmiraHxSurface file

The table below shows valid primary descriptors by file type.

+-------------------+-------------------------------------------------------+
| **File format**   | **Valid primary descriptors**                         |
+===================+=======================================================+
| AmiraMesh         | contourList                                           |
+-------------------+-------------------------------------------------------+
| AmiraHxSurface    | meshList                                              |
+-------------------+-------------------------------------------------------+
| CCP4 masks        | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
| IMOD              | contourList (default), meshList, shapePrimitiveList   |
+-------------------+-------------------------------------------------------+
| Segger            | threeDVolume                                          |
+-------------------+-------------------------------------------------------+
| STL               | meshList                                              |
+-------------------+-------------------------------------------------------+

Note that the primary descriptor should only be changed to a value of a
geometrical descriptor that is *actually* present in the EMDB-SFF file.

For IMOD files, sfftk tries to intelligently determine which primary
descriptor to use. Also, it also tries to ensure that a change
corresponds to the actual file contents.

*Experimental*: Convert Contour Segmentation to Mesh Surface
============================================================

Mesh surfaces are more efficient to work with than contours. However,
converting contours to a mesh is not straightforward. This option relies
on IMOD imodmesh command to convert an (note!) EMDB-SFF file with
contours into one with a mesh. It is experimental and may fail on some
files.

$ sff convert -M file.sff

$ sff convert --contour-to-mesh file.sff --output file\_mesh.sff

Here file.sff has a *contourList* primary descriptor. If successful, the
converted file will have meshes and primary descriptor set to
*meshList*. The output file will be XML (by default).
