#Changes by release

## [0.8.2] (2023-01-20) - Bugfix for reading MRC files

## [0.8.1] (2023-01-19) - Stable merging of masks

* new `mergemask` option `--skip-assessment` to go straight to merging and skip checking binary-ness
* reinstated `--allow-overlap` flag; overlapping masks blocked by default; failure on the first detected overlap
* fixed a bug which excluded some data from merged mrc headers
* updated documentation to outline best practices when merging masks (only use merging for relatively small volumes
  otherwise convert large binary masks into STL meshes)
* fixed bug when deleting fewer than the total number of external references
* new tests to check mask merging

## [0.8.0.dev1] (2022-11-29) - Merge masks

* `sff prep mergemask` to merge multiple binary masks
* updated documentation to reflect new feature

## [0.7.4.post1] (2022-10-19) - v0.7.4.post1: Refinement of `sff notes search -R [emdb|empiar]` to display meaningful results

## [0.7.4] (2022-10-17) - Tentative fix for search EMDB and EMPIAR search

* not all search features remain e.g. `--start` is ignored, search results count unavailable

## [0.7.3] (2022-10-17) - Trivial bugfix and documentation update for transforms

* viewing transforms
* inserting transforms from `.map` files
* modifying transforms using the `notes` utility
* fix typo in parser

## [0.7.2] (2022-10-10) - Bugfixes for CI/CD and docbuild

* fixes for Github workflow
* removal of mock packages which prevented documentation build
* requirements.txt for building documentation
* remove all appearances of `from __future__ import <foo>`
* remove most uses of python2-3 adaption functions
* inclusion of missing image file to run test
* now including explicit rtd configs (`.readthedocs.yml`)
* added numpy as explicit dependency
* removed source dependency for ahds

## [0.7.1] (2022-10-07) - Bugfix for annotation

* temporary file should exclude geometry: FIXED

## [0.7.0] (2022-10-04) - Support for working with transforms

* `sff view --transform file.map` now outputs the image-to-physical space transform; `sff view file.map` will still
  output
* user may choose how to display the transform
  using `sff view --transform [--print-array (default) | --print-csv | --print-ssv] file.map`
* `sff convert` now takes an option `--image` that takes an `.map/.mrc/.rec` file and extracts the transform to set as
  transform `0` ; excluding `--image <file.map>` produces a warning and possibly wrong transform `0`
* `sff notes [add|edit|del] [-x/--transform-id <int>] [-X/--transform <12-floats>] file.sff` to add/modify/delete
  transforms
* `sff notes show -H file.sff` now displays the table of transforms
* all formats now honour `--image <file.map>` to set the correct transform
* `sfftk.readers.mapreader.compute_transform('file.map')` computes transform; when computing the transform from MAP
  file, only reads the header
* all associated tests
* correct spelling for ångström
* minor cleanup and improvements
* bugfixes for cases not caught by tests e.g. merge annotation does not interact with transform_list - must be done
  manually
* for map file we will not write skew and translation matrices; assume rectilinear lattices
* bugfix: `sff notes add` was always adding extra software
* bugfix: display of transforms when empty
* tests for edit and del of notes: OK
* incomplete updates to documentation
* including image used for testing transforms

## [0.6.1.dev0] - 2022-09-06

* improvements for reading SuRVoS files with additional attributes

## [0.6.0.dev2] - 2022-09-02

Cleanup

* removed all u"..." strings and other Python2 related code
* run flake8 checks; considerable reformatting

## [0.6.0.dev1] - 2022-09-02

Bugfixes

* removed .travis.yml since we don't use them anymore
* added ilastik.IlastikHeader class, which was implied but absent >:(
* fixed github workflow by removing py27 and py35 and quote py3.10

## [0.6.0.dev0] - 2022-09-01

* dropped support for Python2.7; requires Python3.6+
* fixed https://github.com/emdb-empiar/sfftk/issues/22
* now convert takes keywords; updated documentation to show keywords required

## [0.5.5.dev1] - 2020-11-10

* trivial

## [0.5.5.dev0] - 2020-05-27

Completed (rudimentary) support for ilastik segmentations

* convert ilastik `.h5` simple segmentation to EMDB-SFF
* disambiguate `.h5` with menu or `--subtype-index <int>` option
* unit tests for new reader/format

## [0.5.4.dev0] - 2020-05-20

Bugfixes: correct handling of conversion with exclusion of geometry for JSON

* added unit tests for the above
* deleted test data files not required
* trivial fix to dox for modreader.py
* added type casting for segreader.py and survosreader.py from numpy types to Python types

## [0.5.3.dev0] - 2020-05-15

Bugfixes: annotation issues

* tests to handle adding external references when the current list has some with id collisions; fix implemented
  in `sfftk-rw` v0.6.5.dev0
* fixed saving of annotations; fix implemented in `sfftk-rw` v0.6.6.dev0
* updated test data for the above tests
* Travis-CI configs: was failing with numpy; had fixed by locking numpy to 1.15.4; fix ->
  replaced `python setup.py develop` with `pip install -e .`

## [0.5.2.dev3] - 2020-04-14

Updates to dependencies for Py27

* pyparsing<3.0, kiwisolver<1.2.0 (Py27 deprecation)
* fix for failing `sfftk.unittests.test_core.TestCoreParserTests.test_multi_tool`
* simplified tool test in `sfftk.core.parser`

## [0.5.2.dev1] - 2020-04-01

* extended tests_parser from `sfftk-rw`

## [0.5.2.dev0] - 2020-03-25

* Bugfixes for faulty IMOD conversion
* triangle indices for IMOD meshes were double: fixed by dividing index values by 2
* extended tests to catch this for all mesh-types
* added package URLs to `setup.py`; changed main URL to `github.io` one

## [0.5.1.dev0] - 2020-03-23

* Bugfixes for faulty conversions
* fixed several formats that omitted important fields (`am`, `map`, `seg`, `surf`)
* strengthened tests for formats
* handle conversions for multifiles (stl, map)
* sort coverage report by Cover(age)

## [0.5.0.dev0] - 2020-03-20

- Documentation cleanup (complete)

## [0.4.0.dev0] - 2019-09-09

Python3 support

- now depends on ``ahds v0.2.0.dev0`` which is Python3 compatible

## [0.3.1.dev5] - 2018-08-01

Documentation

* shorted README.rst to render on pypi
* replaced todo with note in toolkit.rst

## [0.3.1.dev4] - 2018-08-01

Multi-file support for STL files

* docs rebuild
* map, stl: segment file basenames (not full path)
* new multi-file tests for STL and MAP

Bugfixes

* read JSON SFF file for 3D volume correctly

## [0.3.1.dev3] - 2018-07-23

## [0.3.1.dev0] - 2018-07-18

* ``sff prep <command>`` to prepare your segmentation
* ``sff prep binmap`` to bin a CCP4 map file

## [0.3.0.dev1] - 2018-07-18

* Only works with EMDB-SFF v0.7 files. The main feature of EMDB-SFF v0.7 is that 3D volumes are embedded into the
  EMDB-SFF file. Previously 3D volumes were only referred to.
* Other EMDB-SFF changes:
    * Deprecated filePath attribute
    * Transforms can only be of type transformation matrix (deprecated canonical euler angles and view vector rotattion
      transforms)
    * Segments now have both a name and description
* Added this change log
* EMDB-SFF test data is now split by version
* Update of unit tests
* Utility function ``parallelise()`` for parallel computations (mainly used for decoding 3D volume data)
* Utility function ``rgba_to_hex()``

## [0.2.1.dev5] - 2018-04-27

* Added documentation on extending for external resources
* Replaced ``print`` calls with ``print()`` (prep. for Python 3)
* Deprecated contours as a segmentation representation

