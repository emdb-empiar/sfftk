# -*- coding: utf-8 -*-
# schema package
'''
sfftk.schema
============

Adapter for emdb_sff.py
'''

import re
import sys
import time
import unittest
from warnings import warn

import h5py

import emdb_sff as sff
import numpy as np

from ..core.print_tools import print_date


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-09-14"
__updated__ = '2018-02-23'


# ensure that we can read/write encoded data
sff.ExternalEncoding = "utf-8"

# unused = 0
# containers = [
#     sff.contourListType, sff.meshListType,
#     sff.shapePrimitiveListType, sff.segmentListType,
#     sff.vertexListType, sff.polygonListType,
#     sff.transformListType
#     ]

class SFFTypeError(Exception):
    '''SFF type error'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("not object of {}".format(self.value))


class SFFType(object):
    '''SFF base class
     
    Base class from which all SFF objects inherit. It reads the subclass declaration and configures attributes using the structure specified here.
     
    Subclasses define attributes using properties which bind to classes objects of type specified by ``gds_type``. 
     
    :param str gds_type: A class defined in the generateDS API
    :param str ref: A name by which to refer to the subclass
    :param str repr_str: A formatable string (using braces) used by the Python __str__ protocol i.e. when the object is printed. The format locations are filled with values in the ``repr_args`` argument otherwise they will be retained in the string representation as braces.
    :param tuple repr_args: A tuple of attributes of the subclass to use as values that will fill the ``repr_string`` attribute. One can specify ``len()`` to get the length of the subclass.
    :param tuple iter_attr: A two-tuple of the name and type of an attribute that will be iterable on the subclass. Only one attribute can be iterable.
    '''
    gds_type = None
    ref = ""
    repr_string = ""
    repr_args = ()
    iter_attr = ()
    iter_dict = dict()

    def __init__(self, var=None, *args, **kwargs):
        '''Base initialiser
        
        The top-level class has three forms
        #1 - SFFSegmentation() # empty segmentation object
        #2 - SFFSegmentation(emdb_sff.segmentation, *args, **kwargs) # build a segmentation object from an emdb_sff.segmentation object
        
        All other classes have two forms (e.g. SFFSoftware):
        #1 - SFFSoftware() # empty software object
        #2 - SFFSoftware(emdb_sff.softwareType) # build a software object from an emdb_sff.softwareType object
        #3 - SFFSoftware(name="name", version="version", processingDetails="details") # use gds_type kwargs
        
        '''
        if self.gds_type:
            if var:
                if isinstance(var, self.gds_type):  # 2 - gds_type to SFFType
                    self._local = var
                else:
                    raise ValueError('{} is not of type {}'.format(var, self.gds_type))
            else:
                self._local = self.gds_type(*args, **kwargs)  # 1 and #3 - SFFType from (*a, **kw)
                # ensure that the version is copied without requiring user intervention
                if isinstance(self._local, sff.segmentation):
                    self.version = self._local.schemaVersion
        else:
            raise TypeError("attribute 'gds_type' cannot be 'None'")
        # load dict
        self._load_dict()

    def __repr__(self):
        return self.ref

    def __str__(self):
        if self.repr_string:
            if self.repr_args:
                assert isinstance(self.repr_args, tuple)
                if len(self.repr_args) == self.repr_string.count('{}'):
                    repr_args = list()
                    for arg in self.repr_args:
                        if arg == 'len()':
                            repr_args.append(len(self))
                        else:
                            repr_args.append(getattr(self, arg, None))
                    return self.repr_string.format(*repr_args)
                else:
                    raise ValueError("Unmatched number of '{}' and args in repr_args")
            else:
                return self.repr_string
        else:
            return str(type(self))

    def __iter__(self):
        if self.iter_attr:
            iter_name, iter_type = self.iter_attr
            if iter_name and iter_type:
                return iter(map(iter_type, getattr(self._local, iter_name)))
            elif iter_name:
                return iter(getattr(self._local, iter_name))
            elif iter_type:
                return iter(map(iter_type, self._local))
        else:
            raise TypeError("{} object is not iterable".format(self.__class__))

    def __len__(self):
        if self.iter_attr:
            iter_name, _ = self.iter_attr
            return len(getattr(self._local, iter_name))
        else:
            raise TypeError("object of type {} has no len()".format(self.__class__))

    def __getitem__(self, index):
        if self.iter_attr:
            iter_name, iter_type = self.iter_attr
            return iter_type(getattr(self._local, iter_name)[index])

    def __delitem__(self, index):
        if self.iter_attr:
            iter_name, _ = self.iter_attr
            # get the name of the iterable in _local (a list) then delete index pos from it
            del getattr(self._local, iter_name)[index]

    def _load_dict(self):
        self.iter_dict = dict()  #  initialise
        if self.iter_attr:
            for item in self:
                if isinstance(item, SFFType):
                    if isinstance(item, SFFContourPoint):
                        pass  # contours points do not have ids (no reason why they can't though)
                    else:
                        self.iter_dict[item.id] = item
                elif isinstance(item, int):
                    self.iter_dict[item] = item
                elif isinstance(item, str):
                    self.iter_dict[item] = item
                else:
                    raise ValueError("Unknown class {}".format(type(item)))

    def get_ids(self):
        if self.iter_attr:
            return self.iter_dict.keys()

    def get_by_id(self, item_id):
        if self.iter_attr:
            if item_id in self.iter_dict:
                return self.iter_dict[item_id]
            else:
                raise ValueError("ID {} not found".format(item_id))

    @classmethod
    def reset_id(cls):
        '''Reset the ID for a subclass'''
        if issubclass(cls, SFFTransform):
            cls.transform_id = -1
        elif issubclass(cls, SFFContour):
            cls.contour_id = -1
        elif issubclass(cls, SFFMesh):
            cls.mesh_id = -1
        elif issubclass(cls, SFFPolygon):
            cls.polygon_id = -1
        elif issubclass(cls, SFFSegment):
            cls.segment_id = 0
        elif issubclass(cls, SFFShape):
            cls.shape_id = -1
        elif issubclass(cls, SFFVertex):
            cls.vertex_id = -1

    def export(self, fn, *_args, **_kwargs):
        '''Export to a file on disc

        :param str fn: filename to export to
        :param str ext: extension to signify which file format to export as [default: 'sff']
        '''
        fn_ext = fn.split('.')[-1]
        valid_extensions = ['sff', 'hff', 'json']
        try:
            assert fn_ext in valid_extensions
        except AssertionError:
            print_date("Invalid filename: extension should be one of {}: {}".format(
                ", ".join(valid_extensions),
                fn,
                ))
            sys.exit(1)
        if fn_ext == 'sff':
            with open(fn, 'w') as f:
                # write version and encoding
                version = _kwargs.get('version') if 'version' in _kwargs else "1.0"
                encoding = _kwargs.get('encoding') if 'encoding' in _kwargs else "UTF-8"
                f.write('<?xml version="{}" encoding="{}"?>\n'.format(version, encoding))
                # always export from the root
                self._local.export(f, 0, *_args, **_kwargs)
        elif fn_ext == 'hff':
            with h5py.File(fn, 'w') as f:
                self.as_hff(f, *_args, **_kwargs)
        elif fn_ext == 'json':
            with open(fn, 'w') as f:
                self.as_json(f, *_args, **_kwargs)


class SFFAttribute(object):
    '''Descriptor for SFFType subclass attributes'''
    def __init__(self, name, sff_type=None, get_from=None, set_to=None, del_from=None):
        '''Initialiser for an attribute
        
        This class acts as an intermediary between ``SFFType`` and ``emdb_sff`` objects. Each ``SFFType``
        defines a ``_local`` attribute (defined from the ``gds_type`` class attribute, which points to 
        the ``emdb_sff`` object.
        
        Occassionally, the name of the ``emdb_sff`` attribute is different from the ``SFFType`` attribute.
        In this cases, a ``get_from`` argument controls where in the ``emdb_sff`` object the data should
        be obtained from and the ``set_to`` argument controls which attribute in ``emdb_sff`` it should 
        be set to. If both arguments are ``None`` (default) then get from the argument referred to by
        ``name``.
        
        :param str name: the name the attribute is referred to on the containing object
        :param sff_type: class of attribute (default: None - standard Python types like int, str, float)
        :type sff_type: ``SFFType``
        :param str get_from: which ``emdb_sff`` attribute to get the data from
        :param str set_to: which ``emdb_sff`` attribute to set the data to
        '''
        self._name = name
        self._sff_type = sff_type
        self._get_from = get_from
        self._set_to = set_to
        self._del_from = del_from

    def __get__(self, obj, _):  # replaced objtype with _
        if self._sff_type:
            if self._get_from:
                return self._sff_type(getattr(obj._local, self._get_from, None))
            else:
                return self._sff_type(getattr(obj._local, self._name, None))
        else:
            if self._get_from:
                return getattr(obj._local, self._get_from, None)
            else:
                return getattr(obj._local, self._name, None)

    def __set__(self, obj, value):
        if self._sff_type:
            if isinstance(value, self._sff_type):
                if self._set_to:
                    setattr(obj._local, self._set_to, value._local)
                else:
                    setattr(obj._local, self._name, value._local)
            else:
                raise SFFTypeError(self._sff_type)
        else:
            if self._set_to:
                setattr(obj._local, self._set_to, value)
            else:
                setattr(obj._local, self._name, value)

    def __delete__(self, obj):
        if self._del_from:
            delattr(obj._local, self._del_from)
        else:
            delattr(obj._local, self._name)


class SFFRGBA(SFFType):
    '''RGBA colour'''
    gds_type = sff.rgbaType
    ref = "RGBA colour"
    repr_string = "({}, {}, {}, {})"
    repr_args = ('red', 'green', 'blue', 'alpha')

    # attributes
    red = SFFAttribute('red')
    green = SFFAttribute('green')
    blue = SFFAttribute('blue')
    alpha = SFFAttribute('alpha')

    @property
    def value(self):
        return self.red, self.green, self.blue, self.alpha

    @value.setter
    def value(self, c):
        if len(c) == 3:
            self.red, self.green, self.blue = c
        elif len(c) == 4:
            self.red, self.green, self.blue, self.alpha = c

    def __repr__(self):
        return str(self.value)

    def __nonzero__(self):
        if self.red is None or self.green is None or self.blue is None or self.alpha is None:
            return False
        else:
            return True


class SFFColour(SFFType):
    '''Segment colour'''
    gds_type = sff.colourType
    ref = "Colour"
    repr_string = "Segment colour: {}"
    repr_args = ('rgba',)

    # attributes
    name = SFFAttribute('name')
    rgba = SFFAttribute('rgba', sff_type=SFFRGBA)

    def __nonzero__(self):
        if self.name or self.rgba:
            return True
        else:
            return False

    def as_hff(self, parent_group, name="colour"):
        '''Return the data of this object as an HDF5 group in the given parent group'''

        assert isinstance(parent_group, h5py.Group)

        group = parent_group.create_group(name)

        if self.name:
            group['name'] = self.name
        elif self.rgba:
            group['rgba'] = self.rgba.value

        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''

        assert isinstance(hff_data, h5py.Group)

        obj = cls()
        if "name" in hff_data:
            obj.name = hff_data['name'].value
        elif "rgba" in hff_data:
            r = SFFRGBA()
            r.value = hff_data['rgba'].value
            obj.rgba = r

        return obj


class SFFComplexes(SFFType):
    '''Class that encapsulates complex'''
    gds_type = sff.complexType
    ref = "Complexes"
    repr_string = "Complex list of length {}"
    repr_args = ('len()',)
    '''
    :TODO: buggy; refers to emdb_sff attribute instead of SFFType attribute (which is inconsistent)
    '''
    iter_attr = ('id', str)

    def set_complexes(self, cs):
        if isinstance(cs, list):
            self._local.set_id(cs)
        else:
            raise SFFTypeError(list)

    def add_complex(self, c):
        if isinstance(c, str):
            self._local.add_id(c)
        else:
            raise SFFTypeError(str)

    def insert_complex_at(self, index, c):
        if isinstance(c, str):
            self._local.insert_id_at(index, c)
        else:
            raise SFFTypeError(str)

    def replace_complex_at(self, index, c):
        if isinstance(c, str):
            self._local.replace_id_at(index, c)
        else:
            raise SFFTypeError(str)

    def delete_at(self, index):
        del self._local.id[index]

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''

        assert isinstance(hff_data, h5py.Dataset)

        obj = cls()
        [obj.add_complex(_) for _ in hff_data]

        return obj


class SFFMacromolecules(SFFType):
    '''Class that encapsulates macromolecule'''
    gds_type = sff.macromoleculeType
    ref = "Macromolecules"
    repr_string = "Macromolecule list of length {}"
    repr_args = ("len()",)
    iter_attr = ('id', str)
    iter_dict = dict()

    def set_macromolecules(self, ms):
        if isinstance(ms, list):
            self._local.set_id(ms)
        else:
            raise SFFTypeError(list)

    def add_macromolecule(self, m):
        if isinstance(m, str):
            self._local.add_id(m)
        else:
            raise SFFTypeError(str)

    def insert_macromolecule_at(self, index, m):
        if isinstance(m, str):
            self._local.insert_id_at(index, m)
        else:
            raise SFFTypeError(str)

    def replace_macromolecule_at(self, index, m):
        if isinstance(m, str):
            self._local.replace_id_at(index, m)
        else:
            raise SFFTypeError(str)

    def delete_at(self, index):
        del self._local.id[index]

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''

        assert isinstance(hff_data, h5py.Dataset)

        obj = cls()
        [obj.add_macromolecule(_) for _ in hff_data]

        return obj


class SFFComplexesAndMacromolecules(SFFType):
    '''Complexes and macromolecules'''
    gds_type = sff.macromoleculesAndComplexesType
    ref = "Complexes and macromolecules"
    repr_string = "Complexes: {}; Macromolecules: {}"
    repr_args = ('numComplexes', 'numMacromolecules')

    # attributes
    complexes = SFFAttribute('complex', sff_type=SFFComplexes)
    macromolecules = SFFAttribute('macromolecule', sff_type=SFFMacromolecules)

    @property
    def numComplexes(self):
        return len(self.complexes)

    @property
    def numMacromolecules(self):
        return len(self.macromolecules)

    def __nonzero__(self):
        if self.complexes or self.macromolecules:
            return True
        else:
            return False

    def as_hff(self, parent_group, name="complexesAndMacromolecules"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        if self.complexes:
            group['complexes'] = self.complexes
        if self.macromolecules:
            group['macromolecules'] = self.macromolecules
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        obj.complexes = SFFComplexes.from_hff(hff_data['complexes'])
        obj.macromolecules = SFFMacromolecules.from_hff(hff_data['macromolecules'])

        return obj


class SFFExternalReference(SFFType):
    '''Class that encapsulates an external reference'''
    gds_type = sff.externalReferenceType
    ref = "externalReference"
    repr_string = "Reference: {}; {}; {}"
    repr_args = ('type', 'otherType', 'value')

    # attributes
    id = SFFAttribute('id')
    type = SFFAttribute('type_')
    otherType = SFFAttribute('otherType')
    value = SFFAttribute('value')
    label = SFFAttribute('label')
    description = SFFAttribute('description')

    # methods
    def __init__(self, *args, **kwargs):
        # remap kwargs
        if 'type' in kwargs:
            kwargs['type_'] = kwargs['type']
            del kwargs['type']
        super(SFFExternalReference, self).__init__(*args, **kwargs)


class SFFExternalReferences(SFFType):
    '''Container for external references'''
    gds_type = sff.externalReferencesType
    ref = "externalReferences"
    repr_string = "External references list with {} reference(s)"
    repr_args = ('len()',)
    iter_attr = ('ref', SFFExternalReference)
    iter_dict = dict()

    # methods
    def add_externalReference(self, eR):
        if isinstance(eR, SFFExternalReference):
            self._local.add_ref(eR._local)
        else:
            raise SFFTypeError(SFFExternalReference)

    def insert_externalReference(self, eR, index):
        if isinstance(eR, SFFExternalReference) and isinstance(index, int):
            self._local.insert_ref_at(index, eR._local)
        else:
            if not isinstance(eR, SFFExternalReference):
                raise SFFTypeError(SFFExternalReference)
            elif not isinstance(index, int):
                raise SFFTypeError(int)

    def replace_externalReference(self, eR, index):
        if isinstance(eR, SFFExternalReference) and isinstance(index, int):
            self._local.replace_ref_at(index, eR._local)
        else:
            if not isinstance(eR, SFFExternalReference):
                raise SFFTypeError(SFFExternalReference)
            elif not isinstance(index, int):
                raise SFFTypeError(int)



class SFFBiologicalAnnotation(SFFType):
    '''Biological annotation'''
    gds_type = sff.biologicalAnnotationType
    ref = "biologicalAnnotation"
    repr_string = "Container for biological annotation with {} external references"
    repr_args = ('numExternalReferences',)

    # attributes
    description = SFFAttribute('description')
    externalReferences = SFFAttribute('externalReferences', SFFExternalReferences)
    numberOfInstances = SFFAttribute('numberOfInstances')

    # methods
    def __nonzero__(self):
        if not self.description and not self.externalReferences and not self.numberOfInstances:
            return False
        else:
            return True

    @property
    def numExternalReferences(self):
        return len(self.externalReferences)

    def as_hff(self, parent_group, name="biologicalAnnotation"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        if self:
            vl_str = h5py.special_dtype(vlen=str)
            h_ext = group.create_dataset(
                 "externalReferences",
                 (self.numExternalReferences,),
                 dtype=[
                     ('type', vl_str),
                     ('otherType', vl_str),
                     ('value', vl_str),
                     ('label', vl_str),
                     ('description', vl_str),
                     ]
                 )
            # description and nubmerOfInstances as attributes
            group['description'] = self.description if self.description else ''
            group['numberOfInstances'] = self.numberOfInstances if self.numberOfInstances > 0 else 0
            i = 0
            for extref in self.externalReferences:
                h_ext[i] = (extref.type, extref.otherType, extref.value, extref.label, extref.description)
                i += 1
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        if hff_data['description']:
            obj.description = hff_data['description'].value
        obj.numberOfInstances = int(hff_data['numberOfInstances'].value)
        if "externalReferences" in hff_data:
            obj.externalReferences = SFFExternalReferences()
            for ref in hff_data['externalReferences']:
                e = SFFExternalReference()
                e.type, e.otherType, e.value, e.label, e.description = ref
                obj.externalReferences.add_externalReference(e)
        return obj


class SFFThreeDVolume(SFFType):
    gds_type = sff.threeDVolumeType
    ref = 'threeDVolume'
    repr_string = "ThreeDVolume formatted segmentation"

    # attributes
    id = SFFAttribute('id')
    file = SFFAttribute('file')
    objectPath = SFFAttribute('objectPath')
    contourLevel = SFFAttribute('contourLevel')
    transformId = SFFAttribute('transformId')
    format = SFFAttribute('format')

    def __nonzero__(self):
        if self.file and self.format:
            return True
        else:
            return False

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Dataset)
        obj = cls()
        obj.file = str(hff_data['file'][0])
        obj.format = str(hff_data['format'][0])
        try:
            obj.contourLevel = float(hff_data['contourLevel'][0])
        except ValueError:
            obj.contourLevel = None
        try:
            obj.transformId = int(hff_data['transformId'][0])
        except ValueError:
            obj.transformId = None
        try:
            obj.objectPath = str(hff_data['objectPath'][0])
        except ValueError:
            obj.objectPath = None

        return obj


class SFFShape(SFFType):
    repr_string = "{} {}"
    repr_args = ('ref', 'id')
    shape_id = -1

    # attributes
    id = SFFAttribute('id')
    transformId = SFFAttribute('transformId')
    attribute = SFFAttribute('attribute')


class SFFCone(SFFShape):
    gds_type = sff.cone
    ref = "cone"

    # attributes
    height = SFFAttribute('height')
    bottomRadius = SFFAttribute('bottomRadius')

    def __new__(cls, *args, **kwargs):
        cls.shape_id = super(SFFCone, cls).shape_id + 1
        return super(SFFCone, cls).__new__(cls, *args, **kwargs)

    def __init__(self, s=None, *args, **kwargs):
        super(SFFCone, self).__init__(s, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFShape.shape_id = self.shape_id
        elif not s:
            self._local.id = self.shape_id
            SFFShape.shape_id = self.shape_id
        self._local.original_tagname_ = self.ref


class SFFCuboid(SFFShape):
    gds_type = sff.cuboid
    ref = "cuboid"

    # attributes
    x = SFFAttribute('x')
    y = SFFAttribute('y')
    z = SFFAttribute('z')

    def __new__(cls, *args, **kwargs):
        cls.shape_id = super(SFFCuboid, cls).shape_id + 1
        return super(SFFCuboid, cls).__new__(cls, *args, **kwargs)

    def __init__(self, s=None, *args, **kwargs):
        super(SFFCuboid, self).__init__(s, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFShape.shape_id = self.shape_id
        elif not s:
            self._local.id = self.shape_id
            SFFShape.shape_id = self.shape_id
        self._local.original_tagname_ = self.ref


class SFFCylinder(SFFShape):
    gds_type = sff.cylinder
    ref = "cylinder"

    # attributes
    height = SFFAttribute('height')
    diameter = SFFAttribute('diameter')

    def __new__(cls, *args, **kwargs):
        cls.shape_id = super(SFFCylinder, cls).shape_id + 1
        return super(SFFCylinder, cls).__new__(cls, *args, **kwargs)

    def __init__(self, s=None, *args, **kwargs):
        super(SFFCylinder, self).__init__(s, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFShape.shape_id = self.shape_id
        elif not s:
            self._local.id = self.shape_id
            SFFShape.shape_id = self.shape_id
        self._local.original_tagname_ = self.ref


class SFFEllipsoid(SFFShape):
    gds_type = sff.ellipsoid
    ref = "ellipsoid"

    # attributes
    x = SFFAttribute('x')
    y = SFFAttribute('y')
    z = SFFAttribute('z')

    def __new__(cls, *args, **kwargs):
        cls.shape_id = super(SFFEllipsoid, cls).shape_id + 1
        return super(SFFEllipsoid, cls).__new__(cls, *args, **kwargs)

    def __init__(self, s=None, *args, **kwargs):
        super(SFFEllipsoid, self).__init__(s, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFShape.shape_id = self.shape_id
        elif not s:
            self._local.id = self.shape_id
            SFFShape.shape_id = self.shape_id
        self._local.original_tagname_ = self.ref


class SFFShapePrimitiveList(SFFType):
    gds_type = sff.shapePrimitiveListType
    ref = 'shapePrimitiveList'
    repr_string = "Shape primitive list with some shapes"

    def __init__(self, s=None, *args, **kwargs):
        # reset id
        SFFShape.reset_id()
        super(SFFShapePrimitiveList, self).__init__(s, *args, **kwargs)

    def add_shape(self, s):
        if isinstance(s, SFFShape):
            self._local.shapePrimitive.append(s._local)
        else:
            raise SFFTypeError(SFFShape)

    def __len__(self):
        return len(self._local.shapePrimitive)

    def __getitem__(self, index):
        return self._shape_cast(self._local.shapePrimitive[index])

    @staticmethod
    def _shape_cast(shape):
        if isinstance(shape, sff.ellipsoid):
            return SFFEllipsoid(shape)
        elif isinstance(shape, sff.cuboid):
            return SFFCuboid(shape)
        elif isinstance(shape, sff.cylinder):
            return SFFCylinder(shape)
        elif isinstance(shape, sff.cone):
            return SFFCone(shape)
        else:
            raise TypeError("unknown shape type '{}'".format(type(shape)))

    def __iter__(self):
        return iter(map(self._shape_cast, self._local.shapePrimitive))

    def _shape_count(self, shape_type):
        return len(filter(lambda s: isinstance(s, shape_type), self._local.shapePrimitive))

    @property
    def numEllipsoids(self):
        return self._shape_count(sff.ellipsoid)

    @property
    def numCuboids(self):
        return self._shape_count(sff.cuboid)

    @property
    def numCylinders(self):
        return self._shape_count(sff.cylinder)

    @property
    def numCones(self):
        return self._shape_count(sff.cone)

#     @property
#     def numSubtomogramAverages(self):
#         return self._shape_count(sff.subtomogramAverage)

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''

        assert isinstance(hff_data, h5py.Group)

        obj = cls()
        if "ellipsoids" in hff_data:
            for ellipsoid in hff_data["ellipsoids"]:
                e = SFFEllipsoid()
                e.id = int(ellipsoid['id'])
                e.x = float(ellipsoid['x'])
                e.y = float(ellipsoid['y'])
                e.z = float(ellipsoid['z'])
                e.transformId = int(ellipsoid['transformId'])
                if not np.isnan(ellipsoid['attribute']):
                    e.attribute = float(ellipsoid['attribute'])
                obj.add_shape(e)
        if "cones" in hff_data:
            for cone in hff_data["cones"]:
                c = SFFCone()
                c.id = int(cone['id'])
                c.bottomRadius = float(cone['bottomRadius'])
                c.height = float(cone['height'])
                c.transformId = int(cone['transformId'])
                if not np.isnan(cone['attribute']):
                    c.attribute = float(cone['attribute'])
                obj.add_shape(c)
        if "cuboids" in hff_data:
            for cuboid in hff_data["cuboids"]:
                c = SFFCuboid()
                c.id = int(cuboid['id'])
                c.x = float(cuboid['x'])
                c.y = float(cuboid['y'])
                c.z = float(cuboid['z'])
                c.transformId = int(cuboid['transformId'])
                if not np.isnan(cuboid['attribute']):
                    c.attribute = float(cuboid['attribute'])
                obj.add_shape(c)
        if "cylinders" in hff_data:
            for cylinder in hff_data["cylinders"]:
                c = SFFCylinder()
                c.id = int(cylinder['id'])
                c.height = float(cylinder['height'])
                c.diameter = float(cylinder['diameter'])
                c.transformId = int(cylinder['transformId'])
                if not np.isnan(cylinder['attribute']):
                    c.attribute = float(cylinder['attribute'])
                obj.add_shape(c)

        return obj


class SFFContourPoint(SFFType):
    '''Point in 3-space'''
    gds_type = sff.floatVectorType
    ref = "Contour point"
    repr_string = "Contour point: ({}, {}, {})"
    repr_args = ('x', 'y', 'z')

    # attributes
    x = SFFAttribute('x')
    y = SFFAttribute('y')
    z = SFFAttribute('z')

    @property
    def value(self):
        return self.x, self.y, self.z

    @value.setter
    def value(self, p):
        if isinstance(p, tuple):
            if len(p) == 3:
                self.x, self.y, self.z = p
            else:
                raise ValueError("point must have three values")
        else:
            raise SFFTypeError(tuple)


class SFFContour(SFFType):
    '''Single contour'''
    gds_type = sff.contourType
    ref = "Contour"
    repr_string = "Contour {} composed of {} points"
    repr_args = ('id', 'len()')
    iter_attr = ('p', SFFContourPoint)
    contour_id = -1
    iter_dict = dict()

    # attributes
    id = SFFAttribute('id')

    def __new__(cls, *args, **kwargs):
        cls.contour_id += 1
        return super(SFFContour, cls).__new__(cls, *args, **kwargs)

    def __init__(self, c=None, *args, **kwargs):
        '''Initialiser for SFFContour
        
        :param bool reset_id: reset the contour ID to start from zero otherwise the ID values across contour lists will be continuous
        '''
        super(SFFContour, self).__init__(c, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
        elif not c:
            self._local.id = self.contour_id

    @property
    def points(self):
        return self.__iter__()

    @property
    def numPoints(self):
        return len(self)

    def add_point(self, p):
        if isinstance(p, SFFContourPoint):
            self._local.add_p(p._local)
        else:
            raise SFFTypeError(SFFContourPoint)

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''

        assert isinstance(hff_data, h5py.Group)

        obj = cls()
        def load_point(p, P):
            _p = SFFContourPoint()
            _p.value = tuple(map(float, p))
            P.add_point(_p)
            return P

        [load_point(_, obj) for _ in hff_data['points'].value]

        return obj


class SFFContourList(SFFType):
    '''Contour list representation'''
    gds_type = sff.contourListType
    ref = "contourList"
    repr_string = "Contour list with {} contours"
    repr_args = ("len()",)
    iter_attr = ('contour', SFFContour)
    iter_dict = dict()

    # attributes
    transformId = SFFAttribute('transformId')

    def __init__(self, *args, **kwargs):
        # reset id of contours
        SFFContour.reset_id()
        super(SFFContourList, self).__init__(*args, **kwargs)

    @property
    def transformId(self):
        return self._local.transformId

    @transformId.setter
    def transformId(self, i):
        if isinstance(i, int):
            self._local.transformId = i
        else:
            raise SFFTypeError(int)

    @property
    def contours(self):
        return self.__iter__()

    def add_contour(self, c):
        if isinstance(c, SFFContour):
            self._local.add_contour(c._local)
        else:
            raise SFFTypeError(SFFContour)

    def as_hff(self, parent_group, name="contours"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        # /sff/segments/1/contours
        group = parent_group.create_group(name)
        for contour in self.contours:
            # /sff/segments/1/contours/0 - contour 0
            h_contour = group.create_group("{}".format(contour.id))
            # structure
            # /sff/segments/1/contours/0/points
            h_points = h_contour.create_dataset(
                "points",
                (contour.numPoints,),
                dtype=[
                    ('x', 'f4'),
                    ('y', 'f4'),
                    ('z', 'f4'),
                    ],
                )
            # load data
            i = 0
            for point in contour.points:
#                 print 'i: {} | contour.numPoints: {}: unused: {}'.format(i, contour.numPoints, unused)
                h_points[i] = (point.x, point.y, point.z)
                i += 1
        if self.transformId:
            group["transformId"] = self.transformId
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        for contour_id in hff_data:
            C = SFFContour.from_hff(hff_data["{}".format(contour_id)])
            C.id = int(contour_id)
            obj.add_contour(C)
        return obj


class SFFVertex(SFFType):
    '''Single vertex'''
    gds_type = sff.vertexType
    ref = "Vertex"
    repr_string = "{} vertex {}: ({}, {}, {})"
    repr_args = ('designation', 'vID', 'x', 'y', 'z')
    vertex_id = -1

    # attributes
    vID = SFFAttribute('vID')
    designation = SFFAttribute('designation')
    x = SFFAttribute('x')
    y = SFFAttribute('y')
    z = SFFAttribute('z')

    def __new__(cls, *args, **kwargs):
        cls.vertex_id += 1
        return super(SFFVertex, cls).__new__(cls, *args, **kwargs)

    def __init__(self, v=None, *args, **kwargs):
        super(SFFVertex, self).__init__(v, *args, **kwargs)
        '''
        :TODO: vID fails to take effect; fails with IMODSegmentation
        '''
        if 'vID' in kwargs:
            self._local.vID = kwargs['vID']
        elif not v:
            self._local.vID = self.vertex_id

    @property
    def point(self):
        return self.x, self.y, self.z

    @point.setter
    def point(self, p):
        if isinstance(p, tuple):
            if len(p) == 3:
                self.x, self.y, self.z = p
            else:
                raise TypeError("point does not have three values")
        else:
            raise SFFTypeError(tuple)


class SFFPolygon(SFFType):
    '''Single polygon'''
    gds_type = sff.polygonType
    ref = "Polygon"
    repr_string = "Polygon {}"
    repr_args = ('PID',)
    iter_attr = ('v', int)
    polygon_id = -1
    iter_dict = dict()

    # attributes
    PID = SFFAttribute('PID')

    def __new__(cls, *args, **kwargs):
        cls.polygon_id += 1
        return super(SFFPolygon, cls).__new__(cls, *args, **kwargs)

    def __init__(self, p=None, *args, **kwargs):
        super(SFFPolygon, self).__init__(p, *args, **kwargs)
        if 'PID' in kwargs:
            self._local.PID = kwargs['PID']
        elif not p:
            self._local.PID = self.polygon_id

    @property
    def vertex_ids(self):
        return [v for v in self]

    def add_vertex(self, v):
        if isinstance(v, int):
            self._local.add_v(v)
        else:
            raise SFFTypeError(int)


class SFFVertexList(SFFType):
    '''List of vertices'''
    gds_type = sff.vertexListType
    ref = "List of vertices"

    def __init__(self, vL=None, *args, **kwargs):
        # reset id
        SFFVertex.reset_id()
        super(SFFVertexList, self).__init__(vL, *args, **kwargs)
        self._vertex_dict = {v.vID: v for v in map(SFFVertex, self._local.v)}

    @property
    def numVertices(self):
        return len(self)

    def __str__(self):
        return "Vertex dict with {} vertices".format(len(self))

    def __len__(self):
        return len(self._local.v)

    def __iter__(self):
        return iter(self._vertex_dict.values())

    @property
    def vertex_ids(self):
        return iter(self._vertex_dict.keys())

    def __getitem__(self, vertex_id):
        return self._vertex_dict[vertex_id]

    def add_vertex(self, v):
        if isinstance(v, SFFVertex):
            self._local.add_v(v._local)
            self._local.numVertices = self.numVertices
        else:
            raise SFFTypeError(SFFVertex)

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Dataset)
        obj = cls()
        for vertex in hff_data:
            obj.add_vertex(
                SFFVertex(
                    vID=vertex['vID'],
                    designation=vertex['designation'],
                    x=float(vertex['x']),
                    y=float(vertex['y']),
                    z=float(vertex['z'])
                    )
            )
        return obj


class SFFPolygonList(SFFType):
    '''List of polygons'''
    gds_type = sff.polygonListType
    ref = "List of polygons"
    repr_string = "Polygon list with {} polygons"
    repr_args = ('len()',)

    def __init__(self, pL=None, *args, **kwargs):
        # reset id
        SFFPolygon.reset_id()
        super(SFFPolygonList, self).__init__(pL, *args, **kwargs)
        self._polygon_dict = {P.PID: P for P in map(SFFPolygon, self._local.P)}

    @property
    def numPolygons(self):
        return len(self)

    def __len__(self):
        return len(self._local.P)

    def __iter__(self):
        return iter(self._polygon_dict.values())

    @property
    def polygon_ids(self):
        return self.__iter__()

    def __getitem__(self, polygon_id):
        return self._polygon_dict[polygon_id]

    def __str__(self):
        return "Polygon list with {} polygons".format(len(self))

    def add_polygon(self, P):
        if isinstance(P, SFFPolygon):
            self._local.add_P(P._local)
            self._local.numPolygons = self.numPolygons
        else:
            raise SFFTypeError(SFFPolygon)

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Dataset)
        obj = cls()
        for polygon in hff_data:
            P = SFFPolygon()
            P.PID = int(polygon['PID'])
            [P.add_vertex(int(_)) for _ in polygon['v']]
            obj.add_polygon(P)
        return obj


class SFFMesh(SFFType):
    '''Single mesh'''
    gds_type = sff.meshType
    ref = "Mesh"
    repr_string = "Mesh {} with {} and {}"
    repr_args = ('id', 'vertices', 'polygons')
    mesh_id = -1

    # attributes
    id = SFFAttribute('id')
    polygons = SFFAttribute('polygonList', sff_type=SFFPolygonList)
    vertices = SFFAttribute('vertexList', sff_type=SFFVertexList)
    transformId = SFFAttribute('transformId')

    def __new__(cls, *args, **kwargs):
        cls.mesh_id += 1
        return super(SFFMesh, cls).__new__(cls, *args, **kwargs)

    def __init__(self, m=None, *args, **kwargs):
        super(SFFMesh, self).__init__(m, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
        elif not m:
            self._local.id = self.mesh_id

    @property
    def numVertices(self):
        return len(self.vertices)

    @property
    def numPolygons(self):
        return len(self.polygons)

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        obj.vertices = SFFVertexList.from_hff(hff_data['vertices'])
        obj.polygons = SFFPolygonList.from_hff(hff_data['polygons'])
        return obj


class SFFMeshList(SFFType):
    '''Mesh list representation'''
    gds_type = sff.meshListType
    ref = "meshList"
    repr_string = "Mesh list with {} meshe(s)"
    repr_args = ('len()',)
    iter_attr = ('mesh', SFFMesh)
    iter_dict = dict()

    def __init__(self, *args, **kwargs):
        # reset id
        SFFMesh.reset_id()
        super(SFFMeshList, self).__init__(*args, **kwargs)

    def add_mesh(self, m):
        if isinstance(m, SFFMesh):
            self._local.add_mesh(m._local)
        else:
            raise SFFType(SFFMesh)

    def as_hff(self, parent_group, name="meshes"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        # structures
        vlen_str = h5py.special_dtype(vlen=str)
        vertex_array = h5py.special_dtype(vlen=np.dtype('u4'))  # create a variable-length for vertices
        for mesh in self:
            # /sff/segments/1/meshes/0 - mesh 0
            h_mesh = group.create_group("{}".format(mesh.id))
            # /sff/segments/1/meshes/0/vertices
            h_v = h_mesh.create_dataset(
                "vertices",
                (mesh.numVertices,),
                dtype=[
                    ('vID', 'u4'),
                    ('designation', vlen_str),
                    ('x', 'f4'),
                    ('y', 'f4'),
                    ('z', 'f4'),
                    ],
#                 compression="gzip",
                )
            # load vertex data
            i = 0
            for vertex in mesh.vertices:
                '''
                :FIXME: recurrent bug
                RuntimeError: Unable to register datatype id (Can't insert duplicate key)
                '''
                h_v[i] = (vertex.vID, vertex.designation, vertex.x, vertex.y, vertex.z)
                i += 1
#         # attempt to avoid RuntimeError
#         for mesh in self:
            # /sff/segments/1/meshes/0/polygons
            h_P = h_mesh.create_dataset(
                "polygons",
                (mesh.numPolygons,),
                dtype=[
                    ('PID', 'u4'),
                    ('v', vertex_array),
                    ],
#                 compression="gzip",
                )
            #  load polygon data
            j = 0
            for polygon in mesh.polygons:
                h_P[j] = (polygon.PID, np.array(polygon.vertex_ids))
                j += 1
            if mesh.transformId:
                h_mesh["transformId"] = mesh.transformId
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        for mesh_id in hff_data:
            M = SFFMesh.from_hff(hff_data["{}".format(mesh_id)])
            M.id = int(mesh_id)
            obj.add_mesh(M)
        return obj


class SFFSegment(SFFType):
    '''Class that encapsulates segment data'''
    gds_type = sff.segmentType
    ref = "Segment"
    repr_string = "Segment {}"
    repr_args = ('id',)
    segment_id = 0
    segment_parentID = 0

    # attributes
    id = SFFAttribute('id')
    parentID = SFFAttribute('parentID')
    biologicalAnnotation = SFFAttribute('biologicalAnnotation', sff_type=SFFBiologicalAnnotation)
    complexesAndMacromolecules = SFFAttribute('complexesAndMacromolecules', sff_type=SFFComplexesAndMacromolecules)
    colour = SFFAttribute('colour', sff_type=SFFColour)
    meshes = SFFAttribute('meshList', sff_type=SFFMeshList)
    contours = SFFAttribute('contourList', sff_type=SFFContourList)
    volume = SFFAttribute('threeDVolume', sff_type=SFFThreeDVolume)
    shapes = SFFAttribute('shapePrimitiveList', sff_type=SFFShapePrimitiveList)
    mask = SFFAttribute('mask')  # used in sfftkplus

    def __new__(cls, *args, **kwargs):
        cls.segment_id += 1
        return super(SFFType, cls).__new__(cls, *args, **kwargs)

    def __init__(self, s=None, *args, **kwargs):
        super(SFFSegment, self).__init__(s, *args, **kwargs)
        '''
        :TODO: if I want to add a new segment to a set of available segments does the id begin at the right value?
        '''
        # id
        if 'id' in kwargs:
            self._local.id = kwargs['id']
        elif not s:
            self._local.id = self.segment_id
        # parentID
        if 'parentID' in kwargs:
            self._local.parentID = kwargs['parentID']
        elif not s:
            self._local.parentID = self.segment_parentID

    def as_hff(self, parent_group, name="{}"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name.format(self.id))
        group['parentID'] = self.parentID
        # add annotation data
        if self.biologicalAnnotation:
            group = self.biologicalAnnotation.as_hff(group)
        if self.complexesAndMacromolecules:
            group = self.complexesAndMacromolecules.as_hff(group)
        if self.colour:
            group = self.colour.as_hff(group)
        # add segmentation data
        if self.meshes:
            group = self.meshes.as_hff(group)
        if self.contours:
            group = self.contours.as_hff(group)
        if self.shapes:
            # /sff/segments/1/shapes
            h_shapes = group.create_group("shapes")
            # /sff/segments/1/shapes/ellipsoids
            h_ell = h_shapes.create_dataset(
                "ellipsoids",
                (self.shapes.numEllipsoids,),
                dtype=[
                    ('id', 'u4'),
                    ('x', 'f4'),
                    ('y', 'f4'),
                    ('z', 'f4'),
                    ('transformId', 'u4'),
                    ('attribute', 'f4'),
                    ]
                )
            h_cub = h_shapes.create_dataset(
                "cuboids",
                (self.shapes.numCuboids,),
                dtype=[
                    ('id', 'u4'),
                    ('x', 'f4'),
                    ('y', 'f4'),
                    ('z', 'f4'),
                    ('transformId', 'u4'),
                    ('attribute', 'f4'),
                    ]
                )

            h_cyl = h_shapes.create_dataset(
                "cylinders",
                (self.shapes.numCylinders,),
                dtype=[
                    ('id', 'u4'),
                    ('height', 'f4'),
                    ('diameter', 'f4'),
                    ('transformId', 'u4'),
                    ('attribute', 'f4'),
                    ]
                )

            h_con = h_shapes.create_dataset(
                "cones",
                (self.shapes.numCones,),
                dtype=[
                    ('id', 'u4'),
                    ('height', 'f4'),
                    ('bottomRadius', 'f4'),
                    ('transformId', 'u4'),
                    ('attribute', 'f4'),
                    ]
                )
            i = 0  # ellipsoid
            j = 0  # cuboid
            k = 0  # cylinder
            m = 0  # cone
            # n = 0 # subtomogram average
            for shape in self.shapes:
                if shape.ref == "Ellipsoid":
                    h_ell[i] = (shape.id, shape.x, shape.y, shape.z, shape.transformId, shape.attribute if hasattr(shape, 'attribute') else None)
                    i += 1
                elif shape.ref == "Cuboid":
                    h_cub[j] = (shape.id, shape.x, shape.y, shape.z, shape.transformId, shape.attribute if hasattr(shape, 'attribute') else None)
                    j += 1
                elif shape.ref == "Cylinder":
                    h_cyl[k] = (shape.id, shape.height, shape.diameter, shape.transformId, shape.attribute if hasattr(shape, 'attribute') else None)
                    k += 1
                elif shape.ref == "Cone":
                    h_con[m] = (shape.id, shape.height, shape.bottomRadius, shape.transformId, shape.attribute if hasattr(shape, 'attribute') else None)
                    m += 1
                elif shape.ref == "Subtomogram average":
                    warn("Unimplemented portion")
        if self.volume:
            # /sff/segments/1/volume
            vl_str = h5py.special_dtype(vlen=str)
            h_vol = group.create_dataset(
                "volume",
                (1,),
                dtype=[
                    ('file', vl_str),
                    ('objectPath', vl_str),
                    ('contourLevel', 'f4'),
                    ('transformId', 'u4'),
                    ('format', vl_str),
                    ]
                )
            h_vol[0] = (
                self.volume.file,
                self.volume.objectPath if self.volume.objectPath else '',
                self.volume.contourLevel if self.volume.contourLevel else -1.0,
                self.volume.transformId if self.volume.transformId else 0,
                self.volume.format,
                )
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        obj.parentID = int(hff_data['parentID'].value)
        if "biologicalAnnotation" in hff_data:
            obj.biologicalAnnotation = SFFBiologicalAnnotation.from_hff(hff_data["biologicalAnnotation"])
        if "complexesAndMacromolecules" in hff_data:
            obj.complexesAndMacromolecules = SFFComplexesAndMacromolecules.from_hff(hff_data["complexesAndMacromolecules"])
        if "colour" in hff_data:
            obj.colour = SFFColour.from_hff(hff_data["colour"])
        if "meshes" in hff_data:
            obj.meshes = SFFMeshList.from_hff(hff_data["meshes"])
        if "contours" in hff_data:
            obj.contours = SFFContourList.from_hff(hff_data["contours"])
        if "shapes" in hff_data:
            obj.shapes = SFFShapePrimitiveList.from_hff(hff_data["shapes"])
        if "volume" in hff_data:
            obj.volume = SFFThreeDVolume.from_hff(hff_data["volume"])
        return obj


class SFFSegmentList(SFFType):
    '''Container for segments'''
    gds_type = sff.segmentListType
    ref = "segmentList"
    repr_string = "Segment container"
    iter_attr = ('segment', SFFSegment)
    iter_dict = dict()

    def __init__(self, *args, **kwargs):
        # reset id
        SFFSegment.reset_id()
        super(SFFSegmentList, self).__init__(*args, **kwargs)

    def add_segment(self, s):
        if isinstance(s, SFFSegment):
            self._local.add_segment(s._local)
        else:
            raise SFFTypeError(SFFSegment)

    def as_hff(self, parent_group, name="segments"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        for segment in self:
            group = segment.as_hff(group)
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        for segment_id in hff_data:
            S = SFFSegment.from_hff(hff_data[segment_id])
            S.id = int(segment_id)
            obj.add_segment(S)
        return obj


class SFFTransform(SFFType):
    '''Transform'''
    ref = "transform"
    transform_id = -1

    # attributes
    id = SFFAttribute('id')


class SFFTransformationMatrix(SFFTransform):
    '''Transformation matrix transform'''
    gds_type = sff.transformationMatrixType
    ref = "transformationMatrix"

    # attributes
    rows = SFFAttribute('rows')
    cols = SFFAttribute('cols')
    data = SFFAttribute('data')

    def __new__(cls, *args, **kwargs):
        cls.transform_id = super(SFFTransformationMatrix, cls).transform_id + 1
        return super(SFFTransformationMatrix, cls).__new__(cls, *args, **kwargs)

    def __init__(self, t=None, *args, **kwargs):
        super(SFFTransformationMatrix, self).__init__(t, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFTransform.transform_id = self.transform_id
        elif not t:
            self._local.id = self.transform_id
            SFFTransform.transform_id = self.transform_id
        self._local.original_tagname_ = self.ref

    @property
    def data_array(self):
        data_list = self.data.split(' ')
        data_array = np.array(data_list).reshape(self.rows, self.cols)
        return data_array

    def __str__(self):
        return '''Transformation matrix:
        \r[[{:>.4f} {:>.4f} {:>.4f} {:>.4f}]
        \r [{:>.4f} {:>.4f} {:>.4f} {:>.4f}]
        \r [{:>.4f} {:>.4f} {:>.4f} {:>.4f}]]'''.format(*map(float, self.data.split(' ')))
    '''
    :TODO: a setter for the above attribute
    '''


class SFFCanonicalEulerAngles(SFFTransform):
    '''Canonical euler angles'''
    gds_type = sff.canonicalEulerAnglesType
    ref = "canonicalEulerAngles"

    # attributes
    phi = SFFAttribute('phi')
    theta = SFFAttribute('theta')
    psi = SFFAttribute('psi')

    def __new__(cls, *args, **kwargs):
        cls.transform_id = super(SFFCanonicalEulerAngles, cls).transform_id + 1
        return super(SFFCanonicalEulerAngles, cls).__new__(cls, *args, **kwargs)

    def __init__(self, t=None, *args, **kwargs):
        super(SFFCanonicalEulerAngles, self).__init__(t, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFTransform.transform_id = self.transform_id
        elif not t:
            self._local.id = self.transform_id
            SFFTransform.transform_id = self.transform_id
        self._local.original_tagname_ = self.ref


class SFFViewVectorRotation(SFFTransform):
    '''View vector rotation'''
    gds_type = sff.viewVectorRotationType
    ref = "viewVectorRotation"

    # attributes
    x = SFFAttribute('x')
    y = SFFAttribute('y')
    z = SFFAttribute('z')
    r = SFFAttribute('r')

    def __new__(cls, *args, **kwargs):
        cls.transform_id = super(SFFViewVectorRotation, cls).transform_id + 1
        return super(SFFViewVectorRotation, cls).__new__(cls, *args, **kwargs)

    def __init__(self, t=None, *args, **kwargs):
        super(SFFViewVectorRotation, self).__init__(t, *args, **kwargs)
        if 'id' in kwargs:
            self._local.id = kwargs['id']
            SFFTransform.transform_id = self.transform_id
        elif not t:
            self._local.id = self.transform_id
            SFFTransform.transform_id = self.transform_id
        self._local.original_tagname_ = self.ref


class SFFTransformList(SFFType):
    gds_type = sff.transformListType
    ref = "Transform list"
    repr_string = "List of transforms"

    def __init__(self, *args, **kwargs):
        # a new container of transforms needs the transform ID reset
        SFFTransform.reset_id()
        super(SFFTransformList, self).__init__(*args, **kwargs)

    # attributes
    @staticmethod
    def _transform_cast(transform):
        if isinstance(transform, sff.transformationMatrixType):
            return SFFTransformationMatrix(transform)
        elif isinstance(transform, sff.canonicalEulerAnglesType):
            return SFFCanonicalEulerAngles(transform)
        elif isinstance(transform, sff.viewVectorRotationType):
            return SFFViewVectorRotation(transform)
        else:
            raise TypeError("unknown shape type '{}'".format(type(transform)))

    def _transform_count(self, transform_type):
        return len(filter(lambda s: isinstance(s, transform_type), self._local.transform))

    @property
    def transformationMatrixCount(self):
        return self._transform_count(sff.transformationMatrixType)

    @property
    def canonicalEulerAnglesCount(self):
        return self._transform_count(sff.canonicalEulerAnglesType)

    @property
    def viewVectorRotationCount(self):
        return self._transform_count(sff.viewVectorRotationType)

    def add_transform(self, T):
        self._local.add_transform(T._local)

    def __len__(self):
        return len(self._local.transform)

    def __iter__(self):
        return iter(map(self._transform_cast, self._local.transform))

    def __getitem__(self, index):
        return self._transform_cast(self._local.transform[index])

    def check_transformation_matrix_homogeneity(self):
        '''Helper method to check transformation matrix homogeneity
        
        If the transformation matrices are not homogeneous then we cannot use
        structured arrays in numpy :'(        
        '''
        transformationMatricesSimilar = True  # assume they are all similar
        first = True
        rows = None
        cols = None
        for transform in self:
            if transform.ref == "transformationMatrix":
                if first:
                    rows = transform.rows
                    cols = transform.cols
                    first = False
                    continue
                else:
                    if transform.rows != rows or transform.cols != cols:
                        transformationMatricesSimilar = False
                        break
        return transformationMatricesSimilar, rows, cols

    def as_hff(self, parent_group, name="transforms"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        # we need to check whether all transformationMatrices are of the same dimension
        # what we need to know:
        # - rows
        #  - cols
        # if they are then we just use rows and cols
        # else we should
        transformationMatricesSimilar, rows, cols = self.check_transformation_matrix_homogeneity()
        if self.transformationMatrixCount:
            if transformationMatricesSimilar:
                h_tM = group.create_dataset(
                    "transformationMatrix",
                    (self.transformationMatrixCount,),
                    dtype=[
                        ('id', 'u4'),
                        ('rows', 'u1'),
                        ('cols', 'u1'),
                        ('data', 'f4', (rows, cols)),
                        ]
                    )
            else:
                h_tM = group.create_group("transformationMatrix")
        if self.canonicalEulerAnglesCount:
            h_cEA = group.create_dataset(
                "canonicalEulerAngles",
                (self.canonicalEulerAnglesCount,),
                dtype=[
                    ('id', 'u4'),
                    ('phi', 'f4'),
                    ('theta', 'f4'),
                    ('psi', 'f4'),
                    ]
                )
        if self.viewVectorRotationCount:
            h_vVR = group.create_dataset(
                "viewVectorRotation",
                (self.viewVectorRotationCount,),
                dtype=[
                    ('id', 'u4'),
                    ('x', 'f4'),
                    ('y', 'f4'),
                    ('z', 'f4'),
                    ('r', 'f4'),
                    ]
                )
        i = 0  # h_tM index
        j = 0  # h_cEA index
        k = 0  # h_vVR index
        for transform in self:
            if transform.ref == "transformationMatrix":
                if transformationMatricesSimilar:
                    h_tM[i] = (transform.id, transform.rows, transform.cols, transform.data_array)
                    i += 1
                else:
                    tM = h_tM.create_dataset(
                        "{}".format(transform.id),
                        (1,),
                        dtype=[
                            ('id', 'u4'),
                            ('rows', 'u1'),
                            ('cols', 'u1'),
                            ('data', 'f4', (rows, cols)),
                            ]
                        )
                    tM[0] = (transform.id, transform.rows, transform.cols, transform.data_array)
                    i += 1
            elif transform.ref == "canonicalEulerAngles":
                h_cEA[j] = (transform.id, transform.phi, transform.theta, transform.psi)
                j += 1
            elif transform.ref == "viewVectorRotation":
                h_vVR[k] = (transform.id, transform.x, transform.y, transform.z, transform.r)
                k += 1
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        if "transformationMatrix" in hff_data:
            for _transform in hff_data['transformationMatrix']:
                if isinstance(hff_data['transformationMatrix'], h5py.Group):
                    transform = hff_data['transformationMatrix'][_transform][0]
                else:
                    transform = _transform
                T = SFFTransformationMatrix()
                T.id = transform['id']
                T.rows = transform['rows']
                T.cols = transform['cols']
                T.data = " ".join(map(str, transform['data'].flatten()))
                obj.add_transform(T)
        if "canonicalEulerAngles" in hff_data:
            for transform in hff_data['canonicalEulerAngles']:
                T = SFFCanonicalEulerAngles(type="canonicalEulerAngles")
                T.id = transform['id']
                T.phi = transform['phi']
                T.theta = transform['theta']
                T.psi = transform['psi']
                obj.add_transform(T)
        if "viewVectorRotations" in hff_data:
            for transform in hff_data['viewVectorRotations']:
                T = SFFViewVectorRotation(type="viewVectorRotation")
                T.id = transform['id']
                T.x = transform['x']
                T.y = transform['y']
                T.z = transform['z']
                T.r = transform['r']
                obj.add_transform(T)
        return obj


class SFFSoftware(SFFType):
    gds_type = sff.softwareType
    ref = "Software"
    repr_string = "Software object"

    # attributes
    name = SFFAttribute('name')
    version = SFFAttribute('version')
    processingDetails = SFFAttribute('processingDetails')

    def as_hff(self, parent_group, name="software"):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        group['name'] = self.name
        group['version'] = self.version
        if self.processingDetails:
            group['processingDetails'] = self.processingDetails
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Return an SFFType object given an HDF5 object'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        obj.name = hff_data['name'].value
        obj.version = hff_data['version'].value
        if 'processingDetails' in hff_data:
            obj.processingDetails = hff_data['processingDetails'].value
        return obj


class SFFBoundingBox(SFFType):
    '''Dimensions of bounding box'''
    #  config
    gds_type = sff.boundingBoxType
    ref = "Bounding box"
    repr_string = "Bounding box: ({}, {}, {}, {}, {}, {})"
    repr_args = ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax')

    # attributes
    xmin = SFFAttribute('xmin')
    xmax = SFFAttribute('xmax')
    ymin = SFFAttribute('ymin')
    ymax = SFFAttribute('ymax')
    zmin = SFFAttribute('zmin')
    zmax = SFFAttribute('zmax')

    # methods
    def as_hff(self, parent_group, name="boundingBox"):
        '''Bounding box as HDF5 group'''
        assert isinstance(parent_group, h5py.Group)
        group = parent_group.create_group(name)
        group['xmin'] = self.xmin
        group['xmax'] = self.xmax
        group['ymin'] = self.ymin
        group['ymax'] = self.ymax
        group['zmin'] = self.zmin
        group['zmax'] = self.zmax
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Bounding box from HDF5 group'''
        assert isinstance(hff_data, h5py.Group)
        obj = cls()
        obj.xmin = hff_data['xmin'].value
        obj.xmax = hff_data['xmax'].value
        obj.ymin = hff_data['ymin'].value
        obj.ymax = hff_data['ymax'].value
        obj.zmin = hff_data['zmin'].value
        obj.zmax = hff_data['zmax'].value
        return obj


class SFFGlobalExternalReferences(SFFType):
    '''Container for global external references'''
    gds_type = sff.globalExternalReferencesType
    ref = "globalExternalReference"
    repr_string = "Global external reference list with {} reference(s)"
    repr_args = ('len()',)
    iter_attr = ('ref', SFFExternalReference)
    iter_dict = dict()

    # methods
    def add_externalReference(self, eR):
        if isinstance(eR, SFFExternalReference):
            self._local.add_ref(eR._local)
        else:
            raise SFFTypeError(SFFExternalReference)

    def insert_externalReference(self, eR, index):
        if isinstance(eR, SFFExternalReference) and isinstance(index, int):
            self._local.insert_ref_at(index, eR._local)
        else:
            if not isinstance(eR, SFFExternalReference):
                raise SFFTypeError(SFFExternalReference)
            elif not isinstance(index, int):
                raise SFFTypeError(int)

    def replace_externalReference(self, eR, index):
        if isinstance(eR, SFFExternalReference) and isinstance(index, int):
            self._local.replace_ref_at(index, eR._local)
        else:
            if not isinstance(eR, SFFExternalReference):
                raise SFFTypeError(SFFExternalReference)
            elif not isinstance(index, int):
                raise SFFTypeError(int)


class SFFSegmentation(SFFType):
    '''Adapter class to make using the output of ``generateDS`` easier to use'''
    gds_type = sff.segmentation
    ref = "Segmentation"
    repr_string = ""

    # attributes
    name = SFFAttribute('name')
    version = SFFAttribute('version')
    software = SFFAttribute('software', sff_type=SFFSoftware)
    filePath = SFFAttribute('filePath')
    primaryDescriptor = SFFAttribute('primaryDescriptor')
    transforms = SFFAttribute('transformList', sff_type=SFFTransformList)
    boundingBox = SFFAttribute('boundingBox', sff_type=SFFBoundingBox)
    globalExternalReferences = SFFAttribute('globalExternalReferences', sff_type=SFFGlobalExternalReferences)
    segments = SFFAttribute('segmentList', sff_type=SFFSegmentList)
    details = SFFAttribute('details')

    # properties, methods
    def __init__(self, var=None, *args, **kwargs):
        '''Initialiser to handle opening from EMDB-SFF files (XML, HDF5, JSON)'''
        if isinstance(var, str) or isinstance(var, unicode):
            # Experimental
            if re.match(r'.*\.sff$', var, re.IGNORECASE):
                self._local = sff.parse(var, silence=True, *args, **kwargs)
            elif re.match(r'.*\.hff$', var, re.IGNORECASE):
                with h5py.File(var) as h:
                    self._local = self.__class__.from_hff(h, *args, **kwargs)._local
            elif re.match(r'.*\.json$', var, re.IGNORECASE):
                self._local = self.__class__.from_json(var, *args, **kwargs)._local
            else:
                print_date("Invalid EMDB-SFF file name: {}".format(var))
                sys.exit(1)
        else:
            super(SFFSegmentation, self).__init__(var, *args, **kwargs)

    @property
    def numGlobalExternalReferences(self):
        '''The number of global external references'''
        return len(self.globalExternalReferences)

    def as_hff(self, parent_group, name=None):
        '''Return the data of this object as an HDF5 group in the given parent group'''
        assert isinstance(parent_group, h5py.File)
        if name:
            group = parent_group.create_group(name)
        else:
            group = parent_group
        group['name'] = self.name
        group['version'] = self.version
        group['filePath'] = self.filePath
        group['primaryDescriptor'] = self.primaryDescriptor
        # if we are adding another group then don't set dict style; just return the populated group
        group = self.software.as_hff(group)
        group = self.transforms.as_hff(group)
        if self.boundingBox.xmax:
            group = self.boundingBox.as_hff(group)
        if self.globalExternalReferences:
            vl_str = h5py.special_dtype(vlen=str)
            h_gext = group.create_dataset(
                "globalExternalReferences",
                (self.numGlobalExternalReferences,),
                dtype=[
                    ('type', vl_str),
                    ('otherType', vl_str),
                    ('value', vl_str),
                    ('label', vl_str),
                    ('description', vl_str),
                    ]
                )
            i = 0
            for gExtRef in self.globalExternalReferences:
                h_gext[i] = (gExtRef.type, gExtRef.otherType, gExtRef.value, gExtRef.label, gExtRef.description)
                i += 1
        group = self.segments.as_hff(group)
        group['details'] = self.details if self.details else ''
        return parent_group

    @classmethod
    def from_hff(cls, hff_data):
        '''Create an :py:class:`sfftk.schema.SFFSegmentation` object from HDF5 formatted data
        
        :param hff_data: an HDF5 File object
        :type hff_data: ``h5py.File``
        :return sff_seg: an EMDB-SFF segmentation
        :rtype sff_seg: :py:class:`sfftk.schema.SFFSegmentation`
        '''
        assert isinstance(hff_data, h5py.File)
        obj = cls()
        try:
            obj.name = hff_data['name'].value
        except KeyError:
            print_date('Segmentation name not found. Please check that {} is a valid EMDB-SFF file'.format(
                hff_data.filename
                ))
            sys.exit(1)
        obj.version = hff_data['version'].value
        obj.software = SFFSoftware.from_hff(hff_data['software'])
        obj.transforms = SFFTransformList.from_hff(hff_data['transforms'])
        obj.filePath = hff_data['filePath'].value
        obj.primaryDescriptor = hff_data['primaryDescriptor'].value
        if 'boundingBox' in hff_data:
            obj.boundingBox = SFFBoundingBox.from_hff(hff_data['boundingBox'])
        if "globalExternalReferences" in hff_data:
            obj.globalExternalReferences = SFFGlobalExternalReferences()
            for gref in hff_data['globalExternalReferences']:
                g = SFFExternalReference()
                g.type, g.otherType, g.value, g.label, g.description = gref
                obj.globalExternalReferences.add_externalReference(g)
        obj.segments = SFFSegmentList.from_hff(hff_data['segments'])
        obj.details = hff_data['details'].value
        return obj

    def as_json(self, f, sort_keys=True, indent_width=2):
        '''Render an EMDB-SFF to JSON
        
        :param file f: open file handle
        :param bool annotation_only: only extract annotation information and do not render geometric data
        :param bool sort_keys: whether (default) or not to sort keys in the dictionaries
        :param int indent_width: indent width (default: 2)
        '''
        '''
        :TODO: also extract geometrical data
        '''
        sff_data = dict()
        # can be simplified
        sff_data['name'] = self.name
        sff_data['version'] = self.version
        sff_data['software'] = {
            'name': self.software.name,
            'version': self.software.version,
            'processingDetails': self.software.processingDetails if self.software.processingDetails is not None else None,
            }
        sff_data['primaryDescriptor'] = self.primaryDescriptor
        sff_data['filePath'] = self.filePath
        sff_data['details'] = self.details
        sff_data['transforms'] = list()
        boundingBox = {
            'xmin': self.boundingBox.xmin,
            'xmax': self.boundingBox.xmax,
            'ymin': self.boundingBox.ymin,
            'ymax': self.boundingBox.ymax,
            'zmin': self.boundingBox.zmin,
            'zmax': self.boundingBox.zmax,
            }
        sff_data['boundingBox'] = boundingBox
        globalExternalReferences = list()
        for gextref in self.globalExternalReferences:
            globalExternalReferences.append({
                'type': gextref.type,
                'otherType': gextref.otherType,
                'value': gextref.value,
                'label': gextref.label,
                'description': gextref.description
                })
        sff_data['globalExternalReferences'] = globalExternalReferences
        sff_data['segments'] = list()
        for segment in self.segments:
            seg_data = dict()
            seg_data['id'] = int(segment.id)
            seg_data['parentID'] = int(segment.parentID)
            bioAnn = dict()
            bioAnn['description'] = str(segment.biologicalAnnotation.description) if segment.biologicalAnnotation.description is not None else None
            bioAnn['numberOfInstances'] = segment.biologicalAnnotation.numberOfInstances if segment.biologicalAnnotation.numberOfInstances is not None else None

            bioAnn['externalReferences'] = list()
            if segment.biologicalAnnotation.externalReferences:
                for extref in segment.biologicalAnnotation.externalReferences:
                    bioAnn['externalReferences'].append(
                        {
                            'type': extref.type,
                            'otherType': extref.otherType,
                            'value': extref.value,
                            'label': extref.label,
                            'description': extref.description,
                        }
                    )
            seg_data['biologicalAnnotation'] = bioAnn
            if segment.complexesAndMacromolecules:
                complexes = list()
                for _complex in segment.complexesAndMacromolecules.complexes:
                    complexes.append(_complex)
                macromolecules = list()
                for macromolecule in segment.complexesAndMacromolecules.macromolecules:
                    macromolecules.append(macromolecule)
                seg_data['complexesAndMacromolecules'] = {
                    'complexes': complexes,
                    'macromolecules': macromolecules,
                    }
            if segment.colour.name:
                seg_data['colour'] = segment.colour.name
            elif segment.colour.rgba:
                seg_data['colour'] = map(float, segment.colour.rgba.value)
            if segment.contours:
                seg_data['contourList'] = len(segment.contours)
            if segment.meshes:
                seg_data['meshList'] = len(segment.meshes)
            if segment.volume:
                seg_data['threeDVolume'] = {
                    'file': segment.volume.file,  # mandatory
                    'format': segment.volume.format,  # mandatory
                    'objectPath': segment.volume.objectPath if segment.volume.objectPath is not None else None,
                    'contourLevel': segment.volume.contourLevel if segment.volume.contourLevel is not None else None,
                    'transformId': segment.volume.transformId if segment.volume.transformId is not None else None,
                    }
            if segment.shapes:
                seg_data['shapePrimitiveList'] = len(segment.shapes)
            sff_data['segments'].append(seg_data)
        sff_data['details'] = self.details
        # write to f
        with f:
            import json
            json.dump(sff_data, f, sort_keys=sort_keys, indent=indent_width)

    @classmethod
    def from_json(cls, json_file):
        '''Create an :py:class:`sfftk.schema.SFFSegmentation` object from JSON formatted data
        
        :param str json_file: name of a JSON-formatted file
        :return sff_seg: an EMDB-SFF segmentation
        :rtype sff_seg: :py:class:`sfftk.schema.SFFSegmentation`
        '''
        with open(json_file) as j:
            import json
            J = json.load(j, 'utf-8')
        sff_seg = cls()
        # header
        sff_seg.name = J['name']
        sff_seg.version = J['version']
        sff_seg.software = SFFSoftware(
            name=J['software']['name'],
            version=J['software']['version'],
            processingDetails=J['software']['processingDetails'],
            )
        sff_seg.filePath = J['filePath']
        sff_seg.primaryDescriptor = J['primaryDescriptor']
        if 'boundingBox' in J:
            sff_seg.boundingBox = SFFBoundingBox(
                xmin=J['boundingBox']['xmin'],
                xmax=J['boundingBox']['xmax'],
                ymin=J['boundingBox']['ymin'],
                ymax=J['boundingBox']['ymax'],
                zmin=J['boundingBox']['zmin'],
                zmax=J['boundingBox']['zmax'],
                )
        if 'globalExternalReferences' in J:
            sff_seg.globalExternalReferences = SFFGlobalExternalReferences()
            for gextref in J['globalExternalReferences']:
                try:
                    label = gextref['label']
                except KeyError:
                    label = None
                try:
                    description = gextref['description']
                except KeyError:
                    description = None
                sff_seg.globalExternalReferences.add_externalReference(
                    SFFExternalReference(
                        type=gextref['type'],
                        otherType=gextref['otherType'],
                        value=gextref['value'],
                        label=label,
                        description=description,
                        )
                    )
        # segments
        segments = SFFSegmentList()
        for s in J['segments']:
            r, g, b, a = s['colour']
            segment = SFFSegment()
            segment.id = s['id']
            segment.parentID = s['parentID']
            if 'biologicalAnnotation' in s:
                biologicalAnnotation = SFFBiologicalAnnotation()
                biologicalAnnotation.description = s['biologicalAnnotation']['description']
                biologicalAnnotation.numberOfInstances = s['biologicalAnnotation']['numberOfInstances']
                if 'externalReferences' in s['biologicalAnnotation']:
                    biologicalAnnotation.externalReferences = SFFExternalReferences()
                    for extRef in s['biologicalAnnotation']['externalReferences']:
                        try:
                            label = extRef['label']
                        except KeyError:
                            label = None
                        try:
                            description = extRef['description']
                        except KeyError:
                            description = None
                        externalReference = SFFExternalReference(
                            type=extRef['type'],
                            otherType=extRef['otherType'],
                            value=extRef['value'],
                            label=label,
                            description=description,
                            )
                        biologicalAnnotation.externalReferences.add_externalReference(externalReference)
                segment.biologicalAnnotation = biologicalAnnotation
            if 'complexesAndMacromolecules' in s:
                complexesAndMacromolecules = SFFComplexesAndMacromolecules()
                if 'complexes' in s['complexesAndMacromolecules']:
                    complexes = SFFComplexes()
                    complexes.set_complexes(s['complexesAndMacromolecules']['complexes'])
                    complexesAndMacromolecules.complexes = complexes
                if 'macromolecules' in s['complexesAndMacromolecules']:
                    macromolecules = SFFMacromolecules()
                    macromolecules.set_macromolecules(s['complexesAndMacromolecules']['macromolecules'])
                    complexesAndMacromolecules.macromolecules = macromolecules
                segment.complexesAndMacromolecules = complexesAndMacromolecules
            segment.colour = SFFColour()
            segment.colour.rgba = SFFRGBA(
                red=r,
                green=g,
                blue=b,
                alpha=a,
                )
            # in order for sff notes to work with JSON there should be an empty geom
            if 'contourList' in s:
                segment.contours = SFFContourList()
                for _ in xrange(s['contourList']):
                    segment.contours.add_contour(SFFContour())
            if 'meshList' in s:
                segment.meshes = SFFMeshList()
                for _ in xrange(s['meshList']):
                    segment.meshes.add_mesh(SFFMesh())
            if 'threeDVolume' in s:
                segment.volume = SFFThreeDVolume()
                tDV = s['threeDVolume']
                segment.volume.file = tDV['file']
                segment.volume.format = tDV['format']
                segment.volume.objectPath = tDV['objectPath']  if 'objectPath' in tDV else None
                segment.volume.contourLevel = tDV['contourLevel'] if 'contourLevel' in tDV else None
                segment.volume.transformId = tDV['transformId'] if 'transformId' in tDV else None
            if 'shapePrimitiveList' in s:
                segment.shapes = SFFShapePrimitiveList()
                for _ in xrange(s['shapePrimitiveList']):
                    segment.shapes.add_shape(SFFEllipsoid())
            segments.add_segment(segment)
        sff_seg.segments = segments
        # details
        sff_seg.details = J['details']
        return sff_seg

    def merge_annotation(self, other_seg):
        '''Merge the annotation from another sff_seg to this one
        
        :param other_seg: segmentation to get annotations from
        :type other_seg: :py:class:`sfftk.schema.SFFSegmentation`
        '''
        try:
            assert isinstance(other_seg, SFFSegmentation)
        except AssertionError:
            print_date("Invalid type for other_seg: {}".format(type(other_seg)))
            sys.exit(1)
        # global data
        self.name = other_seg.name
        self.filePath = other_seg.filePath
        self.software = other_seg.software
        self.globalExternalReferences = other_seg.globalExternalReferences
        self.details = other_seg.details
        # loop through segments
        for segment in self.segments:
            other_segment = other_seg.segments.get_by_id(segment.id)
            segment.biologicalAnnotation = other_segment.biologicalAnnotation
            segment.complexesAndMacromolecules = other_segment.complexesAndMacromolecules

    def copy_annotation(self, from_id, to_id):
        """Copy annotation across segments

        :param int/list from_id: segment ID to get notes from; use -1 for for global notes
        :param int/list to_id: segment ID to copy notes to; use -1 for global notes
        """
        if from_id == -1:
            _from = self.globalExternalReferences
        else:
            _from = self.segments.get_by_id(from_id).biologicalAnnotation.externalReferences
        if to_id == -1:
            to = self.globalExternalReferences
        else:
            to = self.segments.get_by_id(to_id).biologicalAnnotation.externalReferences
        # the id for global notes
        for extref in _from:
            to.add_externalReference(extref)

    def clear_annotation(self, from_id):
        """Clear all annotations from the segment with ID specified

        :param from_id: segment ID
        :return:
        """
        if from_id == -1:
            self.globalExternalReferences = SFFGlobalExternalReferences()
        else:
            segment = self.segments.get_by_id(from_id)
            segment.biologicalAnnotation.externalReferences = SFFExternalReferences()
