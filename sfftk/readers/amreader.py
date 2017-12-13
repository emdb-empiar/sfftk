# -*- coding: utf-8 -*-
"""
sfftk.readers.amreader
======================

Ad hoc reader for AmiraMesh files
"""


import argparse
import sys

import ahds.data_stream
import ahds.header


def get_data(fn, *args, **kwargs):
    """Reads and returns structured data given the file name
    
    :param str fn: filename
    :return header: AmiraMesh header
    :rtype header: ``ahds.header.AmiraHeader``
    :return segments_by_stream: segments organised by stream
    :rtype segments_by_stream: ``ahds.data_streams.ImageSet``
    """
#     header = ahds.header.AmiraHeader.from_file(fn, *args, **kwargs)
#     data_streams =  ahds.data_stream.DataStreams(fn, *args, **kwargs)
    af = ahds.AmiraFile(fn, *args, **kwargs)
    header = af.header
    
    """
    :TODO: handle <hxsurface> from .am files
    """
    if header.designation.extra_format == "<hxsurface>":
        return header, None
    else:
        # read now
        af.read()
        data_streams = af.data_streams
        images_by_stream = dict()
        for data_stream in af.data_streams:
            images = data_stream.to_images()
            data_stream_index = data_stream.data_pointer.data_index
            images_by_stream[data_stream_index] = images.data
#         """
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
#         """

