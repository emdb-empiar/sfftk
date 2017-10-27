========================
EMDB-SFF Toolkit (sfftk)
========================

.. contents::

Introduction
============

sfftk is a set of utilities that facilitate creation, conversion and modification of `Electron Microscopy Data Bank - Segmentation File Format (EMDB-SFF) files <https://github.com/emdb-empiar/sfftk/tree/master/sfftk/test_data/sff>`_. EMDB-SFF is an open, community-driven file format to handle annotated segmentations and subtomogram averages that facilitates segmentation file interchange. It is predominantly written in Python with some functionality implemented as C-extensions for performance. It provides both a command-line suite of commands and a Python API.

Audience
--------

sfftk is primarily targeted but not restricted to biological electron microscopists and developers of image segmentation software.

Versions
--------

sfftk is currently in development and is available as a development release v0.1.1.dev0. Expected date of release is end of September 2017.

License
-------

sfftk is released under an Apache License, Version 2.0 and is copyright of EMBL-European Bioinformatics Institute (EMBL-EBI) 2017.

Data Model
----------

sfftk is built to handle EMDB-SFF files. The corresponding schema (v0.6.0a4) may be obtained at `http://wwwdev.ebi.ac.uk/pdbe/emdb/emdb_static/doc/segmentation_da_docs/segmentation_da.html <http://wwwdev.ebi.ac.uk/pdbe/emdb/emdb_static/doc/segmentation_da_docs/segmentation_da.html>`__. Changes to the schema are welcome for discussion at the Segmentation Working Group at `https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg <https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg>`__.

Supported Formats
-----------------

The following file formats are currently supported (in alphabetical order of extensions):

-  Amira Mesh (.am)

-  CCP4 Masks (.map)

-  IMOD (.mod)

-  Segger (.seg)

-  Stereolithography (.stl)

-  Amira HyperSurface (.surf)

Contact
-------

Any questions or comments should be addressed to `ardan@ebi.ac.uk <mailto:ardan@ebi.ac.uk>`__ or `pkorir@ebi.ac.uk <mailto:pkorir@ebi.ac.uk>`__.

Publications
------------

The following articles should be cited whenever sfftk is used in a publication:

-  [TBA]

The EMDB-SFF data model is the result of various community consultations which are published in the following articles:

-  `Patwardhan, Ardan, Robert Brandt, Sarah J. Butcher, Lucy Collinson, David Gault, Kay Grünewald, Corey Hecksel et al. Building bridges between cellular and molecular structural biology. eLife 6 (2017). <http://europepmc.org/abstract/MED/28682240>`__

-  `Patwardhan, Ardan, Alun Ashton, Robert Brandt, Sarah Butcher, Raffaella Carzaniga, Wah Chiu, Lucy Collinson et al. A 3D cellular context for the macromolecular world. Nature structural & molecular biology 21, no. 10 (2014): 841-845. <http://europepmc.org/abstract/MED/25289590>`__

-  `Patwardhan, Ardan, José-Maria Carazo, Bridget Carragher, Richard Henderson, J. Bernard Heymann, Emma Hill, Grant J. Jensen et al. Data management challenges in three-dimensional EM. Nature structural & molecular biology 19, no. 12 (2012): 1203-1207. <http://europepmc.org/abstract/MED/23211764>`__

Getting Started
===============

Obtaining and Installing sfftk
------------------------------

Dependencies
~~~~~~~~~~~~

We highly recommend installing sfftk in an anaconda environment because this makes it easy to obtain some of the dependencies. You can find out more about installing anaconda at `https://www.anaconda.com/download/ <https://www.anaconda.com/download/>`__.

The following dependencies are required and will be automatically installed when `using PyPI <#pypi>`__:

-  ahds (v.0.1.6 or greater)

-  lxml

-  h5py

-  requests

-  scikit-image

-  bitarray

-  numpy

-  scipy

PyPI
~~~~

sfftk is available on PyPI meaning that all that one needs to do is run:

.. code:: bash

    pip install sfftk

Source
~~~~~~

The sfftk source is available from CCP-EM SVN repository `https://ccpforge.cse.rl.ac.uk/gf/project/ccpem/scmsvn/?action=browse&path=%2Fsrc%2Fccpem_progs%2Femdb_sfftk%2F <https://ccpforge.cse.rl.ac.uk/gf/project/ccpem/scmsvn/?action=browse&path=%2Fsrc%2Fccpem_progs%2Femdb_sfftk%2F>`__.

Features
========

The main function of sfftk is to handle conversion to and from application-specific segmentation file formats and annotation of EMDB-SFF files.

Conversion
----------

The primary functionality in sfftk is conversion of application-specific segmentation file formats to the open EMDB-SFF. For a full description of how to perform conversion, please see the :doc:`guide to format conversion <converting>`__.

Annotation
----------

sfftk provides a simple set of tools to allow viewing, searching and modifying annotations (notes) associated with the segmentation and individual segments. Annotations added should be either from a published ontology or be an accession from a published database. See the :doc:`guide to annotating segmentations <annotating>`__for a full treatment.

Miscellaneous
-------------

sfftk may also be used for several miscellaneous operations such as:

-  Viewing metadata

-  Setting configurations

-  Running unit tests

More information on this can be found in the :doc:`guide to miscellaneous operations <misc>`__.

Developing with sfftk
---------------------

sfftk has be developed to be modular with functionality decoupled between sub-packages. The main classes involved are found in the sfftk.schema package. Checkout the `full API <http://sfftk.readthedocs.io/en/latest/sfftk.html>`__. See the :doc:`guide to developing with sfftk <developing>`__ for a complete description.

Extending sfftk
---------------

sfftk has built with extensibility in mind. It is anticipated that most extension will take the form of supporting additional file formats. Please read the :doc:`guide to extending sfftk <extending>`__ to learn how to do this.
