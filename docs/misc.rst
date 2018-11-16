====================================
Miscellaneous Operations Using sfftk
====================================

.. contents::

Viewing ``sfftk`` Version
=========================

To view the current version of ``sfftk`` run:

.. code:: bash

    sff --V
    sff --version

Viewing File Metadata
=====================

.. code:: bash

    sff view <file>

The full list of options is:

.. code:: bash

    sff view
    usage: sff view [-h] [-p CONFIG_PATH] [-b] [-V] [-C] [-v] from_file

    View a summary of an SFF file

    positional arguments:
      from_file             any SFF file

    optional arguments:
      -h, --help            show this help message and exit
      -p CONFIG_PATH, --config-path CONFIG_PATH
                            path to configs file
      -b, --shipped-configs
                            use shipped configs only if config path and user
                            configs fail [default: False]
      -V, --version         show SFF format version
      -C, --show-chunks     show sequence of chunks in IMOD file; only works with
                            IMOD model files (.mod) [default: False]
      -v, --verbose         verbose output

Show IMOD Chunks
----------------

The IMOD file format documentation describes that the files are partitioned into chunks,
each commencing with four byte identifier. To view the chunks in an IMOD file run:

.. code:: bash

    sff view -C file.mod
    sff view --show-chunks file.mod

This can be helpful in checking an IMOD file for meshes (``MESH`` chunks). For example, the file below
has a single mesh.

.. code:: bash

    sff view --show-chunks sfftk/test_data/segmentations/test_data.mod
    **************************************************
    IMOD Segmentation version V1.2
    Segmentation name: IMOD-NewModel
    Format: IMOD
    Primary descriptor: contours
    Auxiliary descriptors: meshes
    Pixel size: 1.90680003166
    Pixel units: nm
    xmax, ymax, zmax: (512, 512, 150)
    No. of segments: 1
    **************************************************
    IMOD 2
    OBJT 1
    MESH 1
    IMAT 1
    VIEW 2
    MINX 1
    IEOF

Prepping Segmentation Files
===========================

Some files require preparatory steps in order to efficiently convert them into EMDB-SFF.
At present, preparatory steps are required for CCP4 maps. These filetypes typically store
segmentations as masks whereby the value of the voxels determine whether or not they are
part of or outside the segment. For example, if voxels are stored as floats, all non-zero
voxels are in the segment. Alternatively, a set of integer values may denoted various
segments. By default, these schemes use four bytes per voxel meaning that they files tend
to be at least *four times* as large as they ought to be. The ``sff prep binmap`` utility
converts the standard CCP4 files according to a set of available options into a more
compact file, whose data will then be efficiently embedded into the EMDB-SFF file.

.. code:: bash

    sff prep
    usage: sff prep [-h] Preparation steps: ...

    Prepare a segmentation for conversion to EMDB-SFF

    optional arguments:
      -h, --help          show this help message and exit

    Segmentation preparation utility:
      The following commands provide a number of pre-processing steps for
      various segmentation file formats. Most only apply to one file type. See
      the help for each command by typing 'sff prep <command>'

      Preparation steps:
        binmap            bin a CCP4 map
        transform         transform an STL mesh


Binning Map Files
--------------------------

The ``binmap`` utility has the following options:

.. code:: bash

    sff prep binmap
    usage: sff prep binmap [-h] [-p CONFIG_PATH] [-b] [-m MASK_VALUE] [-o OUTPUT]
                       [--overwrite] [-c CONTOUR_LEVEL] [--negate]
                       [-B {1,2,4,8,16}] [--infix INFIX] [-v]
                       from_file

    Bin the CCP4 file to reduce file size

    positional arguments:
      from_file             the name of the segmentation file

    optional arguments:
      -h, --help            show this help message and exit
      -p CONFIG_PATH, --config-path CONFIG_PATH
                            path to configs file
      -b, --shipped-configs
                            use shipped configs only if config path and user
                            configs fail [default: False]
      -m MASK_VALUE, --mask-value MASK_VALUE
                            value to set to; all other voxels set to zero
                            [default: 1]
      -o OUTPUT, --output OUTPUT
                            output file name [default: <infile>_binned.<ext>]
      --overwrite           overwrite output file [default: False]
      -c CONTOUR_LEVEL, --contour-level CONTOUR_LEVEL
                            value (exclusive) about which to threshold [default:
                            0.0]
      --negate              use values below the contour level [default: False]
      -B {1,2,4,8,16}, --bytes-per-voxel {1,2,4,8,16}
                            number of bytes per voxel [default: 1]
      --infix INFIX         infix to be added to filenames e.g. file.map ->
                            file_<infix>.map [default: 'prep']
      -v, --verbose         verbose output


Default Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``binmap`` utility can be used with default values:

.. code:: bash

    sff prep binmap --verbose file.mrc

By default, the ``binmap`` utility works with files with a ``.mrc``, ``.map`` or ``.rec`` extension.

With verbose output this produces the following:

.. code:: bash

    Fri Oct 12 11:27:38 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
    Fri Oct 12 11:27:38 2018	Output will be written to file_prep.mrc
    Fri Oct 12 11:27:38 2018	Reading in data from file.mrc...
    Fri Oct 12 11:27:38 2018	Voxels will be of type <type 'numpy.int8'>
    Fri Oct 12 11:27:38 2018	Binarising to 1 about contour-level of 0
    Fri Oct 12 11:27:38 2018	Creating output file...
    Fri Oct 12 11:27:38 2018	Writing header data...
    Fri Oct 12 11:27:38 2018	Binarising complete!

which is a fraction of the original file:

.. code:: bash

    -rw-------@ 1 pkorir  staff   381K 12 Oct 11:27 file.mrc
    -rw-r--r--  1 pkorir  staff    96K 12 Oct 11:27 file_prep.mrc

Specify The Number Of Bytes Per Voxel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most important argument is the number of bytes per voxel to be used in the output file specified using
``-B/--bytes-per-voxel`` followed by an integer. By default, this is set to ``1`` (one) but can be
anything from the set ``1``, ``2``, ``4``, ``8`` or ``16``.

.. code:: bash

    sff prep binmap file.mrc -B 2 -v --infix double
    Fri Oct 12 11:49:55 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
    Fri Oct 12 11:49:55 2018	Output will be written to file_double.mrc
    Fri Oct 12 11:49:55 2018	Reading in data from file.mrc...
    Fri Oct 12 11:49:55 2018	Voxels will be of type <type 'numpy.int16'>
    Fri Oct 12 11:49:55 2018	Binarising to 1 about contour-level of 0
    Fri Oct 12 11:49:55 2018	Creating output file...
    Fri Oct 12 11:49:55 2018	Writing header data...
    Fri Oct 12 11:49:55 2018	Binarising complete!

which will result in file that is roughly twice as big as would be produced by default:

.. code:: bash

    -rw-------@ 1 pkorir  staff   381K 12 Oct 11:27 file.mrc
    -rw-r--r--  1 pkorir  staff   191K 12 Oct 11:49 file_double.mrc
    -rw-r--r--  1 pkorir  staff    96K 12 Oct 11:27 file_prep.m

Specify The Contour Level
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The contour level about which binarising should be carried is specified using the ``-c/--contour-level``
argument. The default contour level is ``0.0`` (zero). Note that this is an exlusive value i.e. all voxels
with values equal to the contour level will be *excluded*.

.. code:: bash

    sff prep binmap -c 0.5 -v file.mrc
    sff prep binmap --contour-level 0.5 -v file.mrc

Specifying A Mask Value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The voxel value that designates the segment may be set by setting the ``-m/--mask-value`` argument.
The default value is ``1`` (one).

.. code:: bash

    sff prep binmap -m 2 -v file.mrc
    sff prep binmap --mask-value -v file.mrc

Negate The Mask File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, all values greater than (*not greater than or equal to*) the contour level will be treated
as being *in* the segment. All other voxels will be *outside* the segment. This can be reversed using
the ``--negate`` argument.

.. code:: bash

    sff prep binmap --negate -c 0.5 -v file.mrc

Specify The Output File Infix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To prevent accidentally overwriting the original file, the default output file has a ``_prep`` infix i.e.
the file ``file.mrc`` is converted to ``file_prep.mrc``. This infix can be changed using the ``--infix``
argument.

.. code:: bash

    sff prep binmap file.mrc --infix binned
    Fri Oct 12 11:47:29 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
    Fri Oct 12 11:47:29 2018	Output will be written to file_binned.mrc
    Fri Oct 12 11:47:29 2018	Reading in data from file.mrc...
    Fri Oct 12 11:47:29 2018	Voxels will be of type <type 'numpy.int8'>
    Fri Oct 12 11:47:29 2018	Binarising to 1 about contour-level of 0
    Fri Oct 12 11:47:29 2018	Creating output file...
    Fri Oct 12 11:47:29 2018	Writing header data...
    Fri Oct 12 11:47:29 2018	Binarising complete!


Specifying The Output File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output file can be specified using the ``-o/--output`` argument. Be default, the name of the output
file is determined from the name of the source file *plus* the infix ("prep"). Note that the infix will
not be used when an output file is specified.

.. code:: bash

    sff prep binmap file.mrc -o my_output.mrc
    Fri Oct 12 12:06:41 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
    Fri Oct 12 12:06:41 2018	Output will be written to my_output.mrc
    Fri Oct 12 12:06:41 2018	Reading in data from file.mrc...
    Fri Oct 12 12:06:41 2018	Voxels will be of type <type 'numpy.int8'>
    Fri Oct 12 12:06:41 2018	Binarising to 1 about contour-level of 0
    Fri Oct 12 12:06:41 2018	Creating output file...
    Fri Oct 12 12:06:41 2018	Writing header data...
    Fri Oct 12 12:06:41 2018	Binarising complete!

Overwrite The Original File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to replace the original file (not recommended) you may do so using the ``--overwrite`` argument.
Be default, trying to overwrite the original file will fail.

.. code:: bash

    sff prep binmap file.mrc -o file.mrc
    Fri Oct 12 11:43:16 2018	Binarising preparation failed
    Fri Oct 12 11:43:16 2018	Attempting to overwrite without explicit --overwrite argument


Transforming STL Meshes
----------------------------

It is often necessary to transform meshes contained in STL files so as to get better
alignment with images. To do this we need a 4X4 matrix with the parameters.

``sfftk`` uses two kinds of parameters for this:

- **rotation** parameters, which are the top-left 3X3 sub-matrix;

- **translation** parameters, which are the top-right 3X1 sub-matrix;

Rotation parameters are specified by providing both the physical and
image dimensions of the bounding box. This is then used to determine
the voxel dimensions. The physical dimensions of the bounding box are
specified using the ``-L/--lengths`` argument while the image
dimensions of the bounding box are specified using the ``-I/--indices``.
Each of these arguments take three values - one for each of *x*, *y* and
*z*.

Optionally, the ``-O/--origin`` argument specifies the location of origin
and similarly take three values for each of *x*, *y* and *z*. The default
is located at *(0.0, 0.0, 0.0)*.


.. code:: bash

    sff prep transform --lengths <x-length> <y-length> <z-length> --indices <x-size> <y-size> <z-size> file.stl

or with a translation

.. code:: bash

    sff prep transform --lengths <x-length> <y-length> <z-length> --indices <x-size> <y-size> <z-size> --origin <x> <y> <z> file.stl

Specifying The Infix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default the output is written to a file with a name composed of the original
file name with an infix. For example, if the input file name is ``file.stl``,
then the output filename will be ``file_transformed.stl``. We can change the
infix with the ``--infix`` argument.

.. code:: bash

    sff prep transform [params] --infix tx file.stl
    # will write to file_tx.stl

Specifying The Output File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, the name of the output file may be specified using the
``-o/--output`` argument.

.. code:: bash

    sff prep transform [params] --output tx_file.stl file.stl
    # will write to tx_file.stl

Setting Configurations
=======================

Some of the functionality provided by sfftk relies on persistent configurations. 
In the section we outline all you need to know to work with sfftk configurations.

Configurations are handled using the ``config`` utility with several subcommands.

.. code:: bash 

	sff config [subcommand]

For example:

.. code:: bash

	(sfftk) pkorir@pkorir-tarakimu:docs $ sff config list
	Fri Jan 19 14:03:34 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
	Fri Jan 19 14:03:34 2018	Listing all 3 configs...
	__TEMP_FILE          = ./temp-annotated.json
	__TEMP_FILE_REF      = @
	NAME                 = VALUE

Configuration Commands
----------------------

Getting a single configuration value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config get CONFIG_NAME

Listing available configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config get --all

Setting a single configuration value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config set CONFIG_NAME CONFIG_VALUE

Deleting a single configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config del CONFIG_NAME

Clearing all configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config del --all


.. _configs:

Where Configurations Are Stored
---------------------------------

sfftk ships with a config file called ``sff.conf`` which is located in the root of the package. 
In some cases this might be a read-only location e.g. if installed in an unmodified ``/usr/local/lib/python2.7/site-packages``. 
Therefore, default read-only configurations will be obtained from this file. 
However, if the user would like to write new configs they will be written to ``~/sfftk/sff.conf``. 
Additionally, a user may specify a third location using the ``-p/--config-path`` flag to either read or write a new config. 
Correspondingly, custom configs will only be used if the ``-p/--config-path`` flag is used.

For example

.. code:: bash

	sff config set NAME VAL
	
will add the line ``NAME=VAL`` to ``~/.sfftk/sff.conf`` but 

.. code:: bash

	sff config set NAME VAL --config-path /path/to/sff.conf
	
will add it to ``/path/to/sff.conf`` (provided it is writable by the current user).

The order of precedence, therefore is:

- custom configs specified with ``-p/--config-path``;

- user configs in ``~/.sfftk/sff.conf``; then

- shipped configs (fallback if none of the above are present) which are prioritised using the ``-b/--shipped-configs`` option;


Running Unit Tests
==================

.. code:: bash

    sff tests [tool]

``<tool>`` is optional and if left out all tests for all packages are run.
