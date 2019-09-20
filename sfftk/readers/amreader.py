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
    # af = ahds.AmiraFile(fn, *args, **kwargs)
    # header = af.header
    af = AmiraFile(fn, load_streams=True, *args, **kwargs)
    if af.header.extra_format == "<hxsurface>":
        return af.header, None
    else:
        if af.header.data_stream_count == 1:
            return af.header, getattr(af.data_streams, af.data_streams.attrs()[0], None)
        else:
            print_date(
                "Multiple lattices defined. Is this file formatted properly? Trying to work with the first one...")
            return af.header, getattr(af.data_streams, af.data_streams.attrs()[0], None)

    # TODO: handle <hxsurface> from .am files
    """
    if header.designation.extra_format == "<hxsurface>":
        return header, None
    else:
        # read now
        af.read()
        data_streams = af.data_streams

        if len(data_streams) == 1:
            # get the index for the first (and only) data pointer
            index = header.data_pointers.data_pointer_1.data_index
            volume = data_streams[index].to_volume()
            return header, volume
        else:
            # get the first one and warn the user
            print_date("Multiple lattices defined. Is this file formatted properly? Trying to work with the first one...")
            index = header.data_pointers.data_pointer_1.data_index
            volume = data_streams[index].to_volume()
            return header, volume
    """
