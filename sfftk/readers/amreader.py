# -*- coding: utf-8 -*-
'''
sfftk.readers.amreader
======================

Ad hoc reader for AmiraMesh files
'''
import ahds

from ..core.print_tools import print_date


__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-01-21'
__updated__ = '2018-02-14'


def get_data(fn, *args, **kwargs):
    '''Reads and returns structured data given the file name
    
    :param str fn: filename
    :return header: AmiraMesh header
    :rtype header: ``ahds.header.AmiraHeader``
    :return segments_by_stream: segments organised by stream
    :rtype segments_by_stream: ``ahds.data_streams.ImageSet``
    '''
    af = ahds.AmiraFile(fn, *args, **kwargs)
    header = af.header

    '''
    :TODO: handle <hxsurface> from .am files
    '''
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

        '''
        images_by_stream = dict()
        for data_stream in af.data_streams:
            images = data_stream.to_images()
            data_stream_index = data_stream.data_pointer.data_index
            images_by_stream[data_stream_index] = images.data
        \'''
        # convert the data into images
        images_by_stream = dict()
        for stream in data_streams:
            stream_id = stream.data_pointer.data_index
            images_by_stream[stream_id] = stream.to_images()
        
        # convert the images into segments
        segments_by_stream = dict()
        for stream_id, image_set in images_by_stream.iteritems():
            segments_by_stream[stream_id] = image_set.segments
            
        return header, segments_by_stream
        '''
