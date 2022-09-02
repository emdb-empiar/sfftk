#Changes by release

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
* tests to handle adding external references when the current list has some with id collisions; fix implemented in `sfftk-rw` v0.6.5.dev0
* fixed saving of annotations; fix implemented in `sfftk-rw` v0.6.6.dev0
* updated test data for the above tests
* Travis-CI configs: was failing with numpy; had fixed by locking numpy to 1.15.4; fix -> replaced `python setup.py develop` with `pip install -e .`

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

* Only works with EMDB-SFF v0.7 files. The main feature of EMDB-SFF v0.7 is that 3D volumes are embedded into the EMDB-SFF file. Previously 3D volumes were only referred to.
* Other EMDB-SFF changes:
    * Deprecated filePath attribute
    * Transforms can only be of type transformation matrix (deprecated canonical euler angles and view vector rotattion transforms)
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

