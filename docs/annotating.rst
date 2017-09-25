=================================
Annotating EMDB-SFF Segmentations
=================================

Introduction
============

Annotation of EMDB-SFF segmentations is the second core function of
sfftk. Here we outline how to use the terminal to annotate and EMDB-SFF
file.

Annotation is performed using the notes utility that is accessed with
the notes subcommand.

$ sff notes

Operations: find, view, modify
------------------------------

There are three main operations that a user can perform using the notes
subcommand.

-  Finding notes from an ontology principally the Ontology Lookup
       Service (OLS) hosted at EMBL-EBI;

-  Viewing notes present in an EMDB-SFF file;

-  Modifying notes in an EMDB-SFF file.

States: FIND, VIEW, MODIFY
--------------------------

Correspondingly, using the notes subcommand puts the user in one of
three states: the FIND state, the VIEW state and the MODIFY state. These
will be indicated by the colour of the text on the screen.

-  White indicates the VIEW STATE i.e. that no modifications have been
       done on any EMDB-SFF file

-  Yellow indicates the FIND STATE i.e. search results, and

-  Green indicates the MODIFY STATE i.e. that a file is currently being
       edited. Note, viewing the contents of an EMDB-SFF file in the
       MODIFY STATE will also appear in green even if it a view action.

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

The search sub-subcommand displays results from searching EMBL-EBI’s
OLS. As described in `*States* <#states-find-view-modify>`__, the
terminal text is coloured yellow.

$ sff notes search

$ sff notes search -h

$ sff notes search --help

display available options.

Specifying Search Terms
-----------------------

For single worded searches enter the term with or without quotes.
Multi-word terms must be quoted to prevent splitting them.

# single word term

$ sff notes search mitochondria

$ sff notes search ‘mitochondria’

$ sff notes search “mitochondria”

# multi-word term

$ sff notes search ‘fragment mitochondria’

The search results are displayed as a table with the following columns:

-  *index*

-  *label* of the result term

-  *obo\_id*\  [1]_ of the result term

-  *ontology\_name*

-  *description* is free text describing the term

-  *type* can have one of the following values: *class, property,
       individual, ontology*

Specifying The Ontology To Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes search -O <ontology\_name> “<term>”

$ sff notes search --ontology <ontology\_name> “<term>”

See `*Listing Available Ontologies* <#listing-available-ontologies>`__
on how to get an ontology to search.

Performing Exact Searches
~~~~~~~~~~~~~~~~~~~~~~~~~

Exact searches only return results matching the search term *exactly.*

$ sff notes search -x “<term>”

$ sff notes search --exact “<term>”

Including Obsolete Terms
~~~~~~~~~~~~~~~~~~~~~~~~

Some terms are retired and are excluded by default. They can be included
using the -o/--obsoletes flag.

$ sff notes search -o “<term>”

$ sff notes search --obsoletes “<term>”

Listing Available Ontologies
----------------------------

$ sff notes search -L “term”

$ sff notes search --list-ontologies “term”

By default this provides a multi-line result for each ontology
consisting of the *namespace* (also called *ID space), preferred prefix,
title, description, homepage, the ontology ID,* and *version* of the
ontology.

Short Listing Of Ontologies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, a simple table result can be displayed using the
-l/--short-list-ontologies flag which displays only two columns:
*namespace* and *description.*

$ sff notes search -l “term”

$ sff notes search --short-list-ontologies “term”

Traversing Searching Results
----------------------------

By default, sff notes search only shows the first page of results. Quite
often, there will be more than one page of results. This will be evident
from the last line of the results:

Showing: 1 to 10 of 139 results found

Specifying The Start Result
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can specify the result index at which results should be
displayed using the -s/--start flag.

$ sff notes search -s 1 “<term>”

$ sff notes search --start 1 “<term>”

Specifying The Number Of Rows To Display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

More results can be display using the -r/--rows flag.

$ sff notes search -r 11 “<term>”

$ sff notes search --row 11 “<term>”

Entering invalid values for -s/--start and -r/--rows raise ValueError
exceptions.

Viewing Notes
=============

sfftk includes utilities to view annotations (notes) included in
EMDB-SFF files. There are two main functionalities:

-  Listing all notes present using the sff notes list sub-subcommand,
       and

-  Showing notes in a single segmentation using the sff notes show
       sub-command.

As describe in `*States* <#states-find-view-modify>`__, the teminal text
colour when viewing is white.

Listing All Notes
-----------------

Notes are listed using the following command:

$ sff notes list file.sff

$ sff notes list file.hff

$ sff notes list file.json

The output is structured as follows:

Status information

==================

EMDB-SFF metadata

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

Segment metatdata

Here is an example:

Wed Sep 13 10:18:40 2017 Reading directly from ArcherElf.json

==============================================================================================================

EMDB-SFF v.0.6.0a4

--------------------------------------------------------------------------------------------------------------

Segmentation name:

STL Segmentation

Segmentation software:

Software: Unknown

Version: Unknown

Processing details:

-

--------------------------------------------------------------------------------------------------------------

Primary descriptor:

meshList

--------------------------------------------------------------------------------------------------------------

Segmentation details:

-\*- NOT DEFINED -\*-

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id parId description #inst #exRf #cplx #macr colour

--------------------------------------------------------------------------------------------------------------

1 0 stlexp object01 1 0 0 0 (0.973, 0.649, 0.219, 1.0)

where the first line provides some status information about the current
listing. Status messages will become much more important when we look at
`**modifying notes in EMDB-SFF files** <#_c0sybxydflf7>`__. Status
messages begin with a timestamp. Following status messages is the
EMDB-SFF header information which specifies the schema version
(0.6.0a4), the name of the segmentation (‘STL Segmentation’), software
information including processing details, the primary descriptor
(*meshList* in this case) and additional details on this segmentation. A
row asterisks then divides the metadata from the segment data where one
row per segment provides the *segment\_id, parentID, description, number
of instances, number of external references, number of complexes, number
of macromolecules,* and *RGBA colour* of the segment. When modifying
notes these values change.

Long Format

To view the list of notes by segment in long format (much more detail)
use the -l/--long-format flag.

$ sff notes list -l file.sff

$ sff notes list --long-format file.sff

having the same

Status information

==================

EMDB-SFF metadata

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

Segment metatdata

structure except now that the Segment metadata section has much more
detail.

Wed Sep 13 10:35:25 2017 Reading directly from ArcherElf.json

==============================================================================================================

EMDB-SFF v.0.6.0a4

--------------------------------------------------------------------------------------------------------------

Segmentation name:

STL Segmentation

Segmentation software:

Software: Unknown

Version: Unknown

Processing details:

-

--------------------------------------------------------------------------------------------------------------

Primary descriptor:

meshList

--------------------------------------------------------------------------------------------------------------

Segmentation details:

-\*- NOT DEFINED -\*-

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id parId description #inst #exRf #cplx #macr colour

--------------------------------------------------------------------------------------------------------------

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

ID: 1

PARENT ID: 0

Segment Type: None

--------------------------------------------------------------------------------------------------------------

Description:

stlexp object01

Number of instances:

1

--------------------------------------------------------------------------------------------------------------

External References:

# ontology type term

------------------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------------------------

Complexes:

-\*- NOT DEFINED -\*-

Macromolecules:

-\*- NOT DEFINED -\*-

--------------------------------------------------------------------------------------------------------------

Colour:

(0.9730647136101622, 0.6492013817107163, 0.21907374882651331, 1.0)

Sorting Notes By Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notes are sorted by the index (first column) by default. However, the
user can sort notes by description (third column) using the
-D/--sort-by-description flag.

$ sff notes list -D file.json

$ sff ntoes list --sort-by-description file.json

Wed Sep 13 10:41:12 2017 Reading directly from emd\_1832.json

==============================================================================================================

EMDB-SFF v.0.6.0a4

--------------------------------------------------------------------------------------------------------------

Segmentation name:

Segger

Segmentation software:

Software: segger

Version: 2

Processing details:

None

--------------------------------------------------------------------------------------------------------------

Primary descriptor:

threeDVolume

--------------------------------------------------------------------------------------------------------------

Segmentation details:

-\*- NOT DEFINED -\*-

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id parId description #inst #exRf #cplx #macr colour

--------------------------------------------------------------------------------------------------------------

85 0 GINS + Cdc45 1 0 0 0 (0.522, 0.89, 0.848, 1.0)

93 0 DNA replication licensing factor MCM4 1 0 0 0 (0.504, 0.644, 0.786,
1.0)

97 0 DNA replication licensing factor MCM2 1 0 0 0 (0.67, 0.861, 0.948,
1.0)

101 0 DNA replication licensing factor MCM7 1 0 0 0 (0.862, 0.965,
0.698, 1.0)

103 0 DNA replication licensing factor MCM6 1 0 0 0 (0.707, 0.627,
0.604, 1.0)

104 0 DNA replication licensing factor MCM3... 1 0 0 0 (0.788, 0.925,
0.951, 1.0)

becomes

Wed Sep 13 10:42:54 2017 Reading directly from emd\_1832.json

==============================================================================================================

EMDB-SFF v.0.6.0a4

--------------------------------------------------------------------------------------------------------------

Segmentation name:

Segger

Segmentation software:

Software: segger

Version: 2

Processing details:

None

--------------------------------------------------------------------------------------------------------------

Primary descriptor:

threeDVolume

--------------------------------------------------------------------------------------------------------------

Segmentation details:

-\*- NOT DEFINED -\*-

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id parId description #inst #exRf #cplx #macr colour

--------------------------------------------------------------------------------------------------------------

97 0 DNA replication licensing factor MCM2 1 0 0 0 (0.67, 0.861, 0.948,
1.0)

104 0 DNA replication licensing factor MCM3... 1 0 0 0 (0.788, 0.925,
0.951, 1.0)

93 0 DNA replication licensing factor MCM4 1 0 0 0 (0.504, 0.644, 0.786,
1.0)

103 0 DNA replication licensing factor MCM6 1 0 0 0 (0.707, 0.627,
0.604, 1.0)

101 0 DNA replication licensing factor MCM7 1 0 0 0 (0.862, 0.965,
0.698, 1.0)

85 0 GINS + Cdc45 1 0 0 0 (0.522, 0.89, 0.848, 1.0)

Note that descriptions longer than 40 characters are truncated and
terminated with an ellipsis (...) but the full description is visible in
long format.

Reverse Sorting
~~~~~~~~~~~~~~~

Alternative, sorting can be reversed using the -r/--reverse flag. This
applies to both sorting by index or by description.

Reverse sorting by index:

$ sff notes list -r file.json

$ sff notes list --reverse file.json

Reverse sorting by description

$ sff notes list -r -D file.json

$ sff notes list --reverse --sort-by-description file.json

Listing Notes In A Single Segment
---------------------------------

Listing notes from EMDB-SFF files with many segments would clutter the
screen. The user can oscillate between listing all segments to find
segment IDs of interest then display one or more segment of interest
using the sff notes show sub-subcommand. Therefore, this takes an extra
parameter -i/--segment-id which takes either one ID or a sequence of IDs
separated only by commas (,).

Show one segment:

$ sff notes show -i <int> file.json

$ sff notes show --segment-id <int> file.json

For more than one:

$ sff notes show -i <int>,<int>,<int> file.json

$ sff notes show --segment-id <int>,<int>,<int> file.json

Note that there are NO SPACES between the sequence of segment IDs. As
with listing notes, the user can show notes in long format using the
-l/--long-format flag.

$ sff notes show -i <int> -l file.json

$ sff notes --segment-id <int> --long-format file.json

Modifying Notes
===============

Modifying notes is slightly more complicated that the read-only
activities of finding and viewing described above. It involves making
changes to the annotation sections (*biologicalAnnotation: description,
numberOfInstances, externalReferences* and *complexesAndMacromolecules:
complexes* and *macromolecules*) of the segments of interest.

Temporary File
--------------

In order to avoid destroying the EMDB-SFF file to be modified, sfftk
makes a temporary copy to be used throughout the modification process.
Once the user is satisfied with the annotation the temporary file should
be saved. Alternatively, the user can discard all changes by trashing
the annotation then starting again.

A Note About EMDB-SFF Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any EMDB-SFF format (XML, HDF5, JSON) may be used for the temporary
file. However, JSON is preferred because of the absence of geometrical
data. XML (particularly) and HDF5 can have voluminous geometrical data
which can make the process of modifying an EMDB-SFF very slow. The
default format used is JSON.

Temporary File Shorthand
------------------------

Once the user has entered the MODIFY state (by either running sff notes
add or sff notes edit or or sff notes del) the user can refer to the
temporary file using a shorthand specified in the configs. The default
shorthand is the ‘at’ symbol (@).

$ sff notes add -i 1 -D ‘some description’ file.sff # add a description
(assuming none exists)

# user is now in MODIFY state

$ sff notes edit -i 1 -D ‘another description’ @

This is useful if the file has a long name or is at a distant path.

$ sff notes add -i 1 -D ‘some description’
tomo\_5\_diff\_change\_3.3\_pi\_77\_27\_paul\_publishes.json

$ sff notes edit -i 1 -D ‘another description’ @

or

$ sff notes add -i 1 -D ‘some description’
~/experiments/files/tomograms/zebra\_fish\_20170312/masks\_repeat\_19\_3.3\_relion\_2.0.json

$ sff notes edit -i 1 -D ‘some description’ @

Modify Sequence
---------------

The following diagram illustrates the sequence of steps to be carried
out with the names of the sub-subcommand next to arrows showing the
modification that occurs.

There are four types of annotations that can be made:

-  the segment description

-  the number of instances of the segment

-  external references using public accessions

   -  global external references apply to the segmentation as a whole
          such as specimen type, scientific name

   -  external references for a single segment apply only to a single
          segment

-  complexes and macromolecules

Adding Notes
------------

Notes are added using the sff notes add sub-subcommand.

$ sff notes add -i <segment\_id> [options] file.json

Adding A Description
~~~~~~~~~~~~~~~~~~~~

Use the -D/--description flag to add a description. Multi-word
descriptions will need to be quoted.

$ sff notes add -D ‘a very good description’ file.sff

$ sff notes add --description ‘a very good description’ file.sff

Adding The Number of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes add -i <segment\_id> -n <int> file.json

$ sff notes add -i <segment\_id> --number-of-instances <int> file.json

Adding An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

External references consist of two parts:

-  the name of the ontology, and

-  the obo\_id or accession

Both of these may be obtained either from the OLS website of using the
output of `*sff notes search ‘<term>’* <#finding-notes>`__.

For example, suppose we obtain the following result in a search:

|search\_results.png|

and are interested in adding the second result as an external reference
to a segment. We note down the ontology name (go) and the obo\_id
(GO:0005739) then use the following command:

$ sff notes add -i <segment\_id> -E <ontology> <obo\_id> file.json

$ sff notes add -i <segment\_id> --external-ref <ontology> <obo\_id>
file.json

Adding A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes add -i <segment\_id> -C <comp1>,<comp2>,...,<compN>
file.json

$ sff notes add -i <segment\_id> --complexes <comp1>,<comp2>,...,<compN>
file.json

Adding A Macromolecule (Internal Use>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes add -i <segment\_id> -M <macr1>,<macr2>,...,<macrN>
file.json

$ sff notes add -i <segment\_id> --macromolecules
<macr1>,<macr2>,...,<macrN> file.json

Editing Notes
-------------

If a segment in an EMDB-SFF file already contains notes then we can only
edit the notes using the sff notes edit sub-subcommand. Because some
edit options will need to refer to specific entries (e.g. the third
external reference) extra arguments are required to specify which entry
is being edited.

Editing A Description
~~~~~~~~~~~~~~~~~~~~~

$ sff notes edit -i <segment\_id> -D ‘<description>’ file.json

$ sff notes edit -i <segment\_id> -D ‘<description>’ @ # if editing a
just-added description

Editing The Number of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes edit -i <segment\_id> -n <int> file.json

$ sff notes edit -i <segment\_id> -n <int> @ # if editing a just-added
value

Editing An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes edit -i <segment\_id> -e <extref\_id> -E <ontology>
<obo\_id> file.json

$ sff notes edit -i <segment\_id> --external-ref-id <extref\_id> -E
<ontology> <obo\_id> file.json

# if editing a just-added description

$ sff notes edit -i <segment\_id> -e <extref\_id> -E <ontology>
<obo\_id> @

Editing A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes edit -i <segment\_id> -c <comp\_id> -C
<comp1>,<comp2>,...,<compN> file.json

$ sff notes edit -i <segment\_id> --complex-id <comp\_id> -C
<comp1>,<comp2>,...,<compN> file.json

If only one complex is specified then the complex at complex\_id will be
replaced. However, if more than one is specified then complex\_id will
be replaced and the new complexes will bump down all present complexes.

Editing A Macromolecule (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes edit -i <segment\_id> -m <macr\_id> -M
<macr1>,<macr2>,...,<macrN> file.json

$ sff notes edit -i <segment\_id> --macromolecule-id <macr\_id> -M
<macr1>,<macr2>,...,<macrN> file.json

Deleting Notes
--------------

Notes may be deleted using the sff notes del sub-subcommand. Because
deleting is a destructive process the user only needs to specify which
notes is being deleted.

Deleting A Description
~~~~~~~~~~~~~~~~~~~~~~

$ sff notes del -i <segment\_id> -D file.json

Deleting The Number Of Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes del -i <segment\_id> -n file.json

Deleting An External Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes del -i <segment\_id> -e <extref\_id> file.json

Deleting A Complex (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes del -i <segment\_id> -c <comp\_id> file.json

Deleting A Macromolecule (Internal Use)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$ sff notes del -i <segment\_id> -m <macr\_id> file.json

Saving Notes
------------

It is important to periodically save notes. Running sff notes save
save\_to\_file.json merges all notes from the temporary file into the
destination file.

$ sff notes save save\_to\_file.json

$ sff notes save save\_to\_file.sff

$ sff notes save save\_to\_file.hff

Note that the file specified must exist and correspond to the annotated
EMDB-SFF file.

Trashing Notes
--------------

Only one EMDB-SFF file per directory may have its notes modified at a
time. This is because only one temporary file is created and an attempt
to modify another file will raise a warning.

Wed Sep 13 12:55:42 2017 Temporary file shorthand to use: @

Wed Sep 13 12:55:42 2017 Found temp file ./temp-annotated.json. Either
run 'save' or 'trash' to discard changes before working on another file.

The user can trash using the sff notes trash @ to reset the current
directory to a VIEW state.

$ sff notes trash @

Wed Sep 13 12:56:18 2017 Discarding all changes made in temp file
./temp-annotated.json... Done

Merging Notes
-------------

Notes can be manually merged from two EMDB-SFF files. Obviously both
files must refer to the exact same segmentation i.e. the number and IDs
of segments must be identical. The user must specify an output file with
the extension determining the output format.

$ sff notes merge file1.sff file2.json -o merged\_file.hff

Configuration Settings
======================

There are two main parameters that control the annotation process:

-  \_\_TEMP\_FILE sets the path and name of the file to be used as a
       temporary store of annotations while in the MODIFY STATE. The
       temporary file holds all modifications until they are saved. All
       actions done in the MODIFY STATE occur on this file so that any
       crashes will leave the original file unchanged. Depending on the
       format used it can significantly speed up viewing and
       modification of notes. By default it is a JSON file.

-  \_\_TEMP\_FILE\_REF serves as a shorthand reference to the
       segmentation file. It can only be used in the MODIFY STATE. The
       default value is ‘@’. The use can use it to refer to the
       segmentation file instead of typing the full file path and name.

.. [1]
   A unique identifier for a term under the Open Biology Ontologies
   consortium’s OBO Foundry (see
   `*http://www.obofoundry.org/id-policy.html* <http://www.obofoundry.org/id-policy.html>`__
   to learn more about obo\_id). For example, in the Gene Ontology (GO)
   the term *positive regulation of release of cytochrome c from
   mitochondria* has the OBO ID *GO:0090200.*

.. |search\_results.png| image:: media/image2.png
   :width: 6.26772in
   :height: 1.09722in
