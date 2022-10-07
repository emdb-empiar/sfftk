============================
EMDB-SFF Toolkit (``sfftk``)
============================

.. contents::


Introduction
============

``sfftk`` is a set of utilities that facilitate creation, conversion and
modification of `Electron Microscopy Data Bank - Segmentation File Format
(EMDB-SFF) files <https://github.com/emdb-empiar/sfftk/tree/master/sfftk/test_data/sff>`_.
EMDB-SFF is an open, community-driven file format to handle annotated
segmentations and subtomogram averages that facilitates segmentation file
interchange. It is written in Python and provides both a command-line
suite of commands and a Python API.

Audience
--------

``sfftk`` is primarily targeted but not restricted to biological electron
microscopists and developers of image segmentation software.


License
-------

``sfftk`` is free and open source software released under the terms of the Apache License, Version 2.0. Source code is
copyright EMBL-European Bioinformatics Institute (EMBL-EBI) 2017.

Data Model
----------

``sfftk`` is built to handle EMDB-SFF files. The corresponding schema
(``v0.8.0.dev1``) may be found at `https://emdb-empiar.github.io/EMDB-SFF <https://emdb-empiar.github.io/EMDB-SFF>`_.
Changes to the schema are welcome for discussion at the *Segmentation Working Group*
at `https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg
<https://listserver.ebi.ac.uk/mailman/listinfo/segtrans-wg>`_.

.. _supported_formats:

Supported Formats
-----------------

The following file formats are currently supported (in alphabetical order of
extensions):

-  Amira Mesh (.am)

-  SuRVoS (.h5; experimental support)

-  CCP4 Masks (.map)

-  IMOD (.mod)

-  Segger (.seg)

-  Stereolithography (.stl)

-  Amira HyperSurface (.surf)

Contact
-------

Any questions or comments should be addressed to ``pkorir at ebi dot ac dot uk``.

Publications
------------

.. Please cite the  whenever ``sfftk`` is used in a publication:

.. .. note::

..    Article to be added

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

As with any Python software, we recommend installing it in a virtual environment (of your choice). The only dependency
that may be needed is ``numpy`` which can be installed with

.. code:: bash

	 pip install numpy

PyPI
~~~~

``sfftk`` is available on PyPI meaning that all that one needs to do is run:

.. code:: bash

	 pip install sfftk

Source
~~~~~~

The ``sfftk`` source is available from Github `https://github.com/emdb-empiar/sfftk <https://github.com/emdb-empiar/sfftk>`_.

Features
========

``sfftk`` has two principal functions:

- `convert` application-specific segmentation file format (AS-SFF) files to EMDB-SFF;

- `annotate` EMDB-SFF files against known ontologies.

Conversion
----------

Segmentation files may be converted to EMDB-SFF files using the ``convert``
command.

.. code:: bash

	 sff convert file.am -o file.sff

For a full description of how to perform conversion, please see the
`guide to format conversion <https://sfftk.readthedocs.io/en/latest/converting.html>`_.

Annotation
----------

Annotation is performed using the ``notes`` utility on EMDB-SFF files.

.. code:: bash

	 sff notes show -H file.sff

``sfftk`` provides a simple set of tools to allow `viewing, searching and
modifying annotations` associated with the segmentation and individual
segments. The added annotations should be either from a public ontology or be
an accession from a public database.

See the `guide to annotating segmentations <https://sfftk.readthedocs.io/en/latest/annotating.html>`_ for a full
treatment.

Miscellaneous
-------------

``sfftk`` may also be used for several miscellaneous operations such as:

-  `Viewing segmentation metadata <https://sfftk.readthedocs.io/en/latest/misc.html#viewing-file-metadata>`_

-  `Prepping segmentations <https://sfftk.readthedocs.io/en/latest/misc.html#prepping-segmentation-files>`_ before conversion to EMDB-SFF

-  `Setting configurations <https://sfftk.readthedocs.io/en/latest/misc.html#setting-configurations>`_ that affect how ``sfftk`` works

-  `Running unit tests <https://sfftk.readthedocs.io/en/latest/misc.html#running-unit-tests>`_  with the ``tests`` command

More information on this can be found in the `guide to miscellaneous operations <https://sfftk.readthedocs.io/en/latest/misc.html>`_.

Developing with ``sfftk``
-------------------------

``sfftk`` is developed as a set of decoupled packages providing the various
functionality. The main classes involved are found in the `sfftkrw <https://sfftk-rw.readthedocs.io/en/latest/>`_ package.
There is also a `guide to developing with sfftk <https://sfftk.readthedocs.io/en/latest/developing.html>`_ which
provides useful instructions.

Extending ``sfftk``
-------------------

``sfftk`` has built with extensibility in mind. It is anticipated that most
extension will take the form of supporting additional file formats. Please
read the `guide to extending sfftk <https://sfftk.readthedocs.io/en/latest/extending.html>`_ to learn how to do
this.
