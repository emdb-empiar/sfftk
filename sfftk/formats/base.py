#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
"""
sfftk.formats.base

Generic application-specific segmentation file format (GAS-SFF)

Keep it as simple as possible. Assignment to attributes is done directly. Uses 
basic data structures (lists, dicts, tuples). Defines global attributes and methods.

We define a single segmentation container consisting of two top-level containers:
- a header container that holds all top-level non-segment data
- a list of segment containers

Each segment container has two main parts:
- an annotation container that lists all non-geometric descriptions i.e. textual, logical descriptions
- the actual geometric container that can either be meshes, contours, a volume or shapes

Copyright 2017 EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. 

See the License for the specific language governing permissions 
and limitations under the License.
"""

__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2017-03-28"


class SegmentationType(object):
    def convert(self, *args, **kwargs):
        """Method to implement conversion to EMDB-SFF using the intermediary API.
        
        :param str name: optional name of the segmentation used in <name/>
        :param str softwareVersion: optional software version for Amira use in <software><version/></software>
        :param str processingDetails: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/> 
        
        Implementations of this method within converters can do only two things:
        
        - use objects in the schema API
        - call objects locally extended from the formats API
        """
        raise NotImplementedError
    def __repr__(self):
        return str(self.__class__)
    def __str__(self):
        return str(self.__class__)

  
class SegmentFormat(SegmentationType):
    format = None
    def __init__(self, *args, **kwargs):
        super(SegmentFormat, self).__init__(*args, **kwargs)
 
 
class Mesh(SegmentFormat):
    """``meshList`` segmentation"""
    format = 'mesh'
    def __init__(self, *args, **kwargs):
        super(Mesh, self).__init__(*args, **kwargs)
 
 
class Contours(SegmentFormat):
    """``contourList`` segmentation"""
    format = 'contours'        
    def __init__(self, *args, **kwargs):
        super(Contours, self).__init__(*args, **kwargs)
 
 
class Shapes(SegmentFormat):
    """``shapePrimitiveList`` segmentation"""
    format = 'shapes'
    def __init__(self, *args, **kwargs):
        super(Shapes, self).__init__(*args, **kwargs)
         

class Volume(SegmentFormat):
    """``threeDVolume`` segmentation"""
    format = 'volume'
    def __init__(self, *args, **kwargs):
        super(Volume, self).__init__(*args, **kwargs)


class Segment(SegmentationType):
    """Single segment"""
    annotation = None
    meshes = None
    contours = None
    volume = None
    shapes = None
    
    def __repr__(self):
        formats = list()
        if self.meshes: formats.append(self.meshes.format)
        if self.contours: formats.append(self.contours.format)
        if self.volume: formats.append(self.volume.format)
        if self.shapes: formats.append(self.shapes.format)
        return "Segment of format(s): {}".format(', '.join(formats))


class Annotation(SegmentationType):
    """Biological annotation"""
    pass


class Header(SegmentationType):
    """Header from segmentation file"""        
    pass
        

class Segmentation(SegmentationType):
    """Segmentation class"""
    header = None
    segments = list()
