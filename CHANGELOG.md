#Changes by release

## [0.3.1.dev0] - 2018-07-18

- ``sff prep <command>`` to prepare your segmentation
    - ``sff prep binmap`` to bin a CCP4 map file
- 


## [0.3.0.dev1] - 2018-07-18

- Only works with EMDB-SFF v0.7 files. The main feature of EMDB-SFF v0.7 is that 3D volumes are embedded into the EMDB-SFF file. Previously 3D volumes were only referred to.
- Other EMDB-SFF changes:
    - Deprecated filePath attribute
    - Transforms can only be of type transformation matrix (deprecated canonical euler angles and view vector rotattion transforms)
    - Segments now have both a name and description
- Added this change log 
- EMDB-SFF test data is now split by version
- Update of unit tests
- Utility function ``parallelise()`` for parallel computations (mainly used for decoding 3D volume data)
- Utility function ``rgba_to_hex()``

## [0.2.1.dev5] - 2018-04-27

- Added documentation on extending for external resources
- Replaced ``print`` calls with ``print()`` (prep. for Python 3)
- Deprecated contours as a segmentation representation

