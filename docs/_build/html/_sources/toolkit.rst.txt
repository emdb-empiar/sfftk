============================
EMDB-SFF Toolkit (``sfftk``)
============================

.. image:: https://badge.fury.io/py/sfftk.svg
    :target: https://badge.fury.io/py/sfftk
    
.. image:: https://travis-ci.org/emdb-empiar/sfftk.svg?branch=master
    :target: https://travis-ci.org/emdb-empiar/sfftk

.. image:: https://coveralls.io/repos/github/emdb-empiar/sfftk/badge.svg?branch=master
	:target: https://coveralls.io/github/emdb-empiar/sfftk?branch=master
	
.. image:: https://readthedocs.org/projects/sfftk/badge/?version=latest
	:target: http://sfftk.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

.. contents::

Introduction
============

``sfftk`` is a set of utilities that facilitate creation, conversion and 
modification of `Electron Microscopy Data Bank - Segmentation File Format 
(EMDB-SFF) files <https://github.com/emdb-empiar/sfftk/tree/master/sfftk/test_data/sff>`_. 
EMDB-SFF is an open, community-driven file format to handle annotated 
segmentations and subtomogram averages that facilitates segmentation file 
interchange. It is predominantly written in Python with some functionality 
implemented as C-extensions for performance. It provides both a command-line 
suite of commands and a Python API.

Audience
--------

``sfftk`` is primarily targeted but not restricted to biological electron 
microscopists and developers of image segmentation software.


License
-------

``sfftk`` is released under an Apache License, Version 2.0 and is copyright of 
EMBL-European Bioinformatics Institute (EMBL-EBI) 2017.

Data Model
----------

``sfftk`` is built to handle EMDB-SFF files. The corresponding schema 
(``v0.6.0a4``) may be obtained at `http://wwwdev.ebi.ac.uk/pdbe/emdb/emdb_static/doc/segmentation_da_docs/segmentation_da.html 
<http://wwwdev.ebi.ac.uk/pdbe/emdb/emdb_static/doc/segmentation_da_docs/segmentation_da.html>`_. 
Changes to the schema are welcome for discussion at the *Segmentation Working Group* 
at `https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg 
<https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg>`_.

.. _supported_formats:

Supported Formats
-----------------

The following file formats are currently supported (in alphabetical order of 
extensions):

-  Amira Mesh (.am)

-  CCP4 Masks (.map)

-  IMOD (.mod)

-  Segger (.seg)

-  Stereolithography (.stl)

-  Amira HyperSurface (.surf)

Contact
-------

Any questions or comments should be addressed to 
`ardan@ebi.ac.uk <mailto:ardan@ebi.ac.uk>`_ or 
`pkorir@ebi.ac.uk <mailto:pkorir@ebi.ac.uk>`_.

Publications
------------

The following articles should be cited whenever ``sfftk`` is used in a 
publication:

.. todo::

	Article to be added

The EMDB-SFF data model is the result of various community consultations which 
are published in the following articles:

-  `Patwardhan, Ardan, Robert Brandt, Sarah J. Butcher, Lucy Collinson, David Gault, Kay Grünewald, Corey Hecksel et al. Building bridges between cellular and molecular structural biology. eLife 6 (2017). <http://europepmc.org/abstract/MED/28682240>`_

-  `Patwardhan, Ardan, Alun Ashton, Robert Brandt, Sarah Butcher, Raffaella Carzaniga, Wah Chiu, Lucy Collinson et al. A 3D cellular context for the macromolecular world. Nature structural & molecular biology 21, no. 10 (2014): 841-845. <http://europepmc.org/abstract/MED/25289590>`_

-  `Patwardhan, Ardan, José-Maria Carazo, Bridget Carragher, Richard Henderson, J. Bernard Heymann, Emma Hill, Grant J. Jensen et al. Data management challenges in three-dimensional EM. Nature structural & molecular biology 19, no. 12 (2012): 1203-1207. <http://europepmc.org/abstract/MED/23211764>`_

Getting Started
===============

Obtaining and Installing ``sfftk``
----------------------------------

Dependencies
~~~~~~~~~~~~

We highly recommend installing ``sfftk`` in an anaconda environment because 
this makes it easy to obtain some of the dependencies. You can find out more 
about installing anaconda at `https://www.anaconda.com/download/ 
<https://www.anaconda.com/download/>`_.

The following dependencies are required and will be automatically installed 
when using PyPI:

-  `ahds <http://ahds.readthedocs.io/en/latest/>`_ (v.0.1.6 or greater)

-  lxml

-  h5py

-  requests

-  scikit-image

-  bitarray

-  numpy

-  scipy

These packages should automatically be installed during installation of ``sfftk``.


PyPI
~~~~

``sfftk`` is available on PyPI meaning that all that one needs to do is run:

.. code:: bash

    pip install sfftk

Source
~~~~~~

The ``sfftk`` source is available from Github `https://github.com/emdb-empiar/sfftk 
<https://github.com/emdb-empiar/sfftk>`_ 
or from CCP-EM Gitlab repository 
`https://gitlab.com/ccpem/ccpem/tree/master/src/ccpem_progs/emdb_sfftk 
<https://gitlab.com/ccpem/ccpem/tree/master/src/ccpem_progs/emdb_sfftk>`_.

Features
========

``sfftk`` has two principal functions:

- `convert` application-specific segmentation file format (AS-SFF) files to \
	EMDB-SFF;

- `annotate` EMDB-SFF files against known ontologies.

Conversion
----------

Segmentation files may be converted to EMDB-SFF files using the ``convert`` 
command.

.. code:: bash

	sff convert file.am -o file.sff

For a full description of how to perform conversion, please see the 
:doc:`guide to format conversion <converting>`.

Annotation
----------

Annotation is performed using the ``notes`` utility on EMDB-SFF files.

.. code:: bash

	sff notes show -H file.sff

``sfftk`` provides a simple set of tools to allow `viewing, searching and 
modifying annotations` associated with the segmentation and individual 
segments. The added annotations should be either from a public ontology or be 
an accession from a public database. 

See the :doc:`guide to annotating segmentations <annotating>` for a full 
treatment.

Miscellaneous
-------------

``sfftk`` may also be used for several miscellaneous operations such as:

-  Viewing segmentation metadata

-  Setting configurations that affect how ``sfftk`` works

-  Running unit tests with the ``tests`` command

More information on this can be found in the :doc:`guide to miscellaneous 
operations <misc>`.

Developing with ``sfftk``
-------------------------

``sfftk`` is developed as a set of decoupled packages providing the various 
functionality. The main classes involved are found in the ``sfftk.schema 
package``. Please see `full API <http://sfftk.readthedocs.io/en/latest/sfftk.html>`_. 
There is also a :doc:`guide to developing with sfftk <developing>` which 
provides useful instructions.

Extending ``sfftk``
-------------------

``sfftk`` has built with extensibility in mind. It is anticipated that most 
extension will take the form of supporting additional file formats. Please 
read the :doc:`guide to extending sfftk <extending>` to learn how to do 
this.