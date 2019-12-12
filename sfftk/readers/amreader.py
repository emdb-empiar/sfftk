# -*- coding: utf-8 -*-
'''
sfftk.readers.amreader
======================

Ad hoc reader for AmiraMesh files
'''
from __future__ import print_function

from ahds import AmiraFile

from ..core.print_tools import print_date

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-01-21'


def get_data(fn, *args, **kwargs):
    '''Reads and returns structured data given the file name
    
    :param str fn: filename
    :return header: AmiraMesh header
    :rtype header: ``ahds.header.AmiraHeader``
    :return segments_by_stream: segments organised by stream
    :rtype segments_by_stream: ``ahds.data_streams.ImageSet``
    '''
    af = AmiraFile(fn, load_streams=True, *args, **kwargs)
    if af.header.extra_format == "<hxsurface>":
        return af.header, None
    else:
        return af.header, af.data_streams.Labels # segments are always in the 'Labels' attribute
