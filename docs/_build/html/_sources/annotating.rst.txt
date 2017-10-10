=================================
Annotating EMDB-SFF Segmentations
=================================

Introduction
============

Annotation of EMDB-SFF segmentations is the second core function of sfftk. Here we outline how to perform annotations of EMDB-SFF segmentations via the command-line.

Annotation is performed using the notes utility that is accessed with the notes subcommand.

.. code:: bash

    sff notes

Operations: find, view, modify
------------------------------

There are three main operations that a user can perform using the notes subcommand.

-  Finding notes from an ontology principally the Ontology Lookup Service (OLS) hosted at EMBL-EBI;

-  Viewing notes present in an EMDB-SFF file;

-  Modifying notes in an EMDB-SFF file.

States: FIND, VIEW, MODIFY
--------------------------

Correspondingly, using the notes subcommand puts the user in one of three states: the FIND state, the VIEW state and the MODIFY state. These will be indicated by the colour of the text on the screen.

-  White indicates the VIEW STATE i.e. that no modifications have been done on any EMDB-SFF file

-  Yellow indicates the FIND STATE i.e. search results, and

-  Green indicates the MODIFY STATE i.e. that a file is currently being edited. Note, viewing the contents of an EMDB-SFF file in the MODIFY STATE will also appear in green even if it a view action.

The full listing of sub-subcommands organised by operation are:

-  Finding

   -  search

-  Viewing

   -  list

   -  show

-  Modifying

   -  add

   -  edit

   -  del

   -  merge

   -  save

   -  trash

We will look at each of these in turn.

Quick Start
-----------

Finding Notes
=============

The search sub-subcommand displays results from searching EMBL-EBI’s OLS. As described in `*States* <#states-find-view-modify>`__, the terminal text is coloured yellow.

.. code:: bash

    sff notes search
    sff notes search -h
    sff notes search --help

display available options.

Specifying Search Terms
-----------------------

For single worded searches enter the term with or without quotes. Multi-word terms must be quoted to prevent splitting them.

.. code:: bash

    # single word term
    sff notes search mitochondria
    sff notes search ‘mitochondria’
    sff notes search “mitochondria”
    # multi-word term
    sff notes search ‘fragment mitochondria’

The search results are displayed as a table with the following columns:

-  *index*

-  *label* of the result term

-  *obo_id*  [1]_ of the result term

-  *ontology_name*

-  *description* is free text describing the term

-  *type* can have one of the following values: *class, property, individual, ontology*

Specifying The Ontology To Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes search -O <ontology_name> “<term>”
    sff notes search --ontology <ontology_name> “<term>”

See `*Listing Available Ontologies* <#listing-available-ontologies>`__ on how to get an ontology to search.

Performing Exact Searches
~~~~~~~~~~~~~~~~~~~~~~~~~

Exact searches only return results matching the search term *exactly.*

.. code:: bash

    sff notes search -x “<term>”
    sff notes search --exact “<term>”

Including Obsolete Terms
~~~~~~~~~~~~~~~~~~~~~~~~

Some terms are retired and are excluded by default. They can be included using the -o/--obsoletes flag.

.. code:: bash

    sff notes search -o “<term>”
    sff notes search --obsoletes “<term>”

Listing Available Ontologies
----------------------------

.. code:: bash

    sff notes search -L “term”
    sff notes search --list-ontologies “term”

By default this provides a multi-line result for each ontology consisting of the *namespace* (also called *ID space), preferred prefix, title, description, homepage, the ontology ID,* and *version* of the ontology.

Short Listing Of Ontologies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, a simple table result can be displayed using the -l/--short-list-ontologies flag which displays only two columns: *namespace* and *description.*

.. code:: bash

    sff notes search -l “term”
    sff notes search --short-list-ontologies “term”

Traversing Searching Results
----------------------------

By default, sff notes search only shows the first page of results. Quite often, there will be more than one page of results. This will be evident from the last line of the results:

Showing: 1 to 10 of 139 results found

Specifying The Start Result
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can specify the result index at which results should be displayed using the -s/--start flag.

.. code:: bash

    sff notes search -s 1 “<term>”
    sff notes search --start 1 “<term>”

Specifying The Number Of Rows To Display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

More results can be display using the -r/--rows flag.

.. code:: bash

    sff notes search -r 11 “<term>”
    sff notes search --row 11 “<term>”

Entering invalid values for -s/--start and -r/--rows raise ValueError exceptions.

Viewing Notes
=============

sfftk includes utilities to view annotations (notes) included in EMDB-SFF files. There are two main functionalities:

-  Listing all notes present using the sff notes list sub-subcommand, and

-  Showing notes in a single segmentation using the sff notes show sub-command.

As describe in `*States* <#states-find-view-modify>`__, the teminal text colour when viewing is white.

Listing All Notes
-----------------

Notes are listed using the following command:

.. code:: bash

    sff notes list file.sff
    sff notes list file.hff
    sff notes list file.json

The output is structured as follows:

.. code::

    Status information
    ==================
    EMDB-SFF metadata
    ******************
    Segment metatdata

Here is an example:

.. code::

    INSERT OUTPUT HERE

where the first line provides some status information about the current listing. Status messages will become much more important when we look at `**modifying notes in EMDB-SFF files** <#_c0sybxydflf7>`__. Status messages begin with a timestamp. Following status messages is the EMDB-SFF header information which specifies the schema version (0.6.0a4), the name of the segmentation (‘STL Segmentation’), software information including processing details, the primary descriptor (*meshList* in this case) and additional details on this segmentation. A row asterisks then divides the metadata from the segment data where one row per segment provides the *segment_id, parentID, description, number of instances, number of external references, number of complexes, number of macromolecules,* and *RGBA colour* of the segment. When modifying notes these values change.

Long Format
~~~~~~~~~~~

To view the list of notes by segment in long format (much more detail) use the -l/--long-format flag.

.. code:: bash

    sff notes list -l file.sff
    sff notes list --long-format file.sff

having the same

.. code::

    Status information
    ==================
    EMDB-SFF metadata
    ******************
    Segment metatdata

structure except now that the Segment metadata section has much more detail.

.. code::

    INSERT OUTPUT HERE

Sorting Notes By Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notes are sorted by the index (first column) by default. However, the user can sort notes by description (third column) using the -D/--sort-by-description flag.

.. code:: bash

    sff notes list -D file.json
    sff notes list --sort-by-description file.json

.. code::

    INSERT OUTPUT HERE

becomes

.. code::

    INSERT OUTPUT HERE

Note that descriptions longer than 40 characters are truncated and terminated with an ellipsis (...) but the full description is visible in long format.

Reverse Sorting
~~~~~~~~~~~~~~~

Alternative, sorting can be reversed using the -r/--reverse flag. This applies to both sorting by index or by description.

Reverse sorting by index:

.. code:: bash

    sff notes list -r file.json
    sff notes list --reverse file.json

Reverse sorting by description

.. code:: bash

    sff notes list -r -D file.json
    sff notes list --reverse --sort-by-description file.json

Listing Notes In A Single Segment
---------------------------------

Listing notes from EMDB-SFF files with many segments could clutter the screen. The user can switch between listing all segments to finding segment IDs of interest then displaying one or more segments of interest using the sff notes show sub-subcommand. Therefore, this takes an extra parameter -i/--segment-id which takes either one ID or a sequence of IDs separated only by commas (,).

Show one segment:

.. code:: bash

    sff notes show -i <int> file.json
    sff notes show --segment-id <int> file.json

For more than one:

.. code:: bash

    sff notes show -i <int>,<int>,<int> file.json
    sff notes show --segment-id <int>,<int>,<int> file.json

Note that there are NO SPACES between the sequence of segment IDs. As with listing notes, the user can show notes in long format using the -l/--long-format flag.

.. code:: bash

    sff notes show -i <int> -l file.json
    sff notes --segment-id <int> --long-format file.json

Modifying Notes
===============

Modifying notes is slightly more complicated than the read-only activities of finding and viewing described above. It involves making changes to the annotation sections (*biologicalAnnotation: description, numberOfInstances, externalReferences* and *complexesAndMacromolecules: complexes* and *macromolecules*) of the segments of interest.

Temporary File
--------------

In order to avoid destroying the EMDB-SFF file to be modified, sfftk makes a temporary copy to be used throughout the modification process. Once the user is satisfied with the annotation the temporary file should be saved. Alternatively, the user can discard all changes by trashing the annotation then starting again.

A Note About EMDB-SFF Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any EMDB-SFF format (XML, HDF5, JSON) may be used for the temporary file. However, JSON is preferred because of the absence of geometrical data. XML (particularly) and HDF5 can have voluminous geometrical data which can make the process of modifying an EMDB-SFF very slow. The default format used is JSON.

Temporary File Shorthand
------------------------

Once the user has entered the MODIFY state (by either running sff notes add or sff notes edit or or sff notes del) the user can refer to the temporary file using a shorthand specified in the configs. The default shorthand is the ‘at’ symbol (@).

.. code:: bash

    # add a description (assuming none exists)
    sff notes add -i 1 -D ‘some description’ file.sff
    # user is now in MODIFY state
    sff notes edit -i 1 -D ‘another description’ @

This is useful if the file has a long name or is at a distant path.

.. code:: bash

    sff notes add -i 1 -D ‘some description’ tomo_5_diff_change_3.3_pi_77_27_paul_publishes.json

    sff notes edit -i 1 -D ‘another description’ @

or

.. code:: bash

    sff notes add -i 1 -D ‘some description’ ~/experiments/files/tomograms/zebra_fish_20170312/masks_repeat_19_3.3_relion_2.0.json
    sff notes edit -i 1 -D ‘some description’ @

Modify Sequence
---------------

The following diagram illustrates the sequence of steps to be carried out with the names of the sub-subcommand next to arrows showing the modification that occurs.

.. image:: annotating-01.png

There are four types of annotations that can be made:

-  the segment description

-  the number of instances of the segment

-  external references using public accessions

   -  global external references apply to the segmentation as a whole such as specimen type, scientific name

   -  external references for a single segment apply only to a single segment

-  complexes and macromolecules

Adding Notes
------------

Notes are added using the sff notes add sub-subcommand.

.. code:: bash

    sff notes add -i <segment_id> [options] file.json

Adding A Description
~~~~~~~~~~~~~~~~~~~~

Use the -D/--description flag to add a description. Multi-word descriptions will need to be quoted.

.. code:: bash

    sff notes add -D ‘a very good description’ file.sff
    sff notes add --description ‘a very good description’ file.sff

Adding The Number of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes add -i <segment_id> -n <int> file.json
    sff notes add -i <segment_id> --number-of-instances <int> file.json

Adding An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

External references consist of two parts:

-  the name of the ontology, and

-  the obo_id or accession

Both of these may be obtained either from the OLS website of using the output of `*sff notes search ‘<term>’* <#finding-notes>`__.

For example, suppose we obtain the following result in a search:

INSERT NEW IMAGE

and are interested in adding the second result as an external reference to a segment. We note down the ontology name (go) and the obo_id (GO:0005739) then use the following command:

.. code:: bash

    sff notes add -i <segment_id> -E <ontology> <obo_id> file.json
    sff notes add -i <segment_id> --external-ref <ontology> <obo_id> file.json

Adding A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes add -i <segment_id> -C <comp1>,<comp2>,...,<compN> file.json
    sff notes add -i <segment_id> --complexes <comp1>,<comp2>,...,<compN> file.json

Adding A Macromolecule (Internal Use>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes add -i <segment_id> -M <macr1>,<macr2>,...,<macrN> file.json
    sff notes add -i <segment_id> --macromolecules <macr1>,<macr2>,...,<macrN> file.json

Editing Notes
-------------

If a segment in an EMDB-SFF file already contains notes then we can only edit the notes using the sff notes edit sub-subcommand. Because some edit options will need to refer to specific entries (e.g. the third external reference) extra arguments are required to specify which entry is being edited.

Editing A Description
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes edit -i <segment_id> -D ‘<description>’ file.json
    sff notes edit -i <segment_id> -D ‘<description>’ @ # if editing a just-added description

Editing The Number of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes edit -i <segment_id> -n <int> file.json
    sff notes edit -i <segment_id> -n <int> @ # if editing a just-added value

Editing An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes edit -i <segment_id> -e <extref_id> -E <ontology> <obo_id> file.json
    sff notes edit -i <segment_id> --external-ref-id <extref_id> -E <ontology> <obo_id> file.json
    # if editing a just-added description
    sff notes edit -i <segment_id> -e <extref_id> -E <ontology> <obo_id> @

Editing A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes edit -i <segment_id> -c <comp_id> -C <comp1>,<comp2>,...,<compN> file.json
    sff notes edit -i <segment_id> --complex-id <comp_id> -C <comp1>,<comp2>,...,<compN> file.json

If only one complex is specified then the complex at complex_id will be replaced. However, if more than one is specified then complex_id will be replaced and the new complexes will bump down all present complexes.

Editing A Macromolecule (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes edit -i <segment_id> -m <macr_id> -M <macr1>,<macr2>,...,<macrN> file.json
    sff notes edit -i <segment_id> --macromolecule-id <macr_id> -M <macr1>,<macr2>,...,<macrN> file.json

Deleting Notes
--------------

Notes may be deleted using the sff notes del sub-subcommand. Because deleting is a destructive process the user only needs to specify which notes is being deleted.

Deleting A Description
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes del -i <segment_id> -D file.json

Deleting The Number Of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes del -i <segment_id> -n file.json

Deleting An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes del -i <segment_id> -e <extref_id> file.json

Deleting A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes del -i <segment_id> -c <comp_id> file.json

Deleting A Macromolecule (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    sff notes del -i <segment_id> -m <macr_id> file.json

Saving Notes
------------

It is important to periodically save notes. Running sff notes save save_to_file.json merges all notes from the temporary file into the destination file.

.. code:: bash

    sff notes save save_to_file.json
    sff notes save save_to_file.sff
    sff notes save save_to_file.hff

Note that the file specified must exist and correspond to the annotated EMDB-SFF file.

Trashing Notes
--------------

Only one EMDB-SFF file per directory may have its notes modified at a time. This is because only one temporary file is created and an attempt to modify another file will raise a warning.

.. code:: bash

    Wed Sep 13 12:55:42 2017 Temporary file shorthand to use: @
    Wed Sep 13 12:55:42 2017 Found temp file ./temp-annotated.json. Either run 'save' or 'trash' to discard changes before working on another file.

The user can trash using the sff notes trash @ to reset the current directory to a VIEW state.

.. code:: bash

    sff notes trash @
    Wed Sep 13 12:56:18 2017 Discarding all changes made in temp file ./temp-annotated.json... Done

Merging Notes
-------------

Notes can be manually merged from two EMDB-SFF files. Obviously both files must refer to the exact same segmentation i.e. the number and IDs of segments must be identical. The user must specify an output file with the extension determining the output format.

.. code:: bash

    sff notes merge file1.sff file2.json -o merged_file.hff

Configuration Settings
======================

There are two main parameters that control the annotation process:

-  __TEMP_FILE sets the path and name of the file to be used as a temporary store of annotations while in the MODIFY STATE. The temporary file holds all modifications until they are saved. All actions done in the MODIFY STATE occur on this file so that any crashes will leave the original file unchanged. Depending on the format used it can significantly speed up viewing and modification of notes. By default it is a JSON file.

-  __TEMP_FILE_REF serves as a shorthand reference to the segmentation file. It can only be used in the MODIFY STATE. The default value is ‘@’. The use can use it to refer to the segmentation file instead of typing the full file path and name.

.. [1]
   A unique identifier for a term under the Open Biology Ontologies consortium’s OBO Foundry (see `*http://www.obofoundry.org/id-policy.html* <http://www.obofoundry.org/id-policy.html>`__ to learn more about obo_id). For example, in the Gene Ontology (GO) the term *positive regulation of release of cytochrome c from mitochondria* has the OBO ID *GO:0090200.*
