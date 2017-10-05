# -*- coding: utf-8 -*-
# amreader.py
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
    header = ahds.header.AmiraHeader.from_file(fn, *args, **kwargs)
    data_streams =  ahds.data_stream.DataStreams(fn, *args, **kwargs)
    
    """
    :TODO: handle <hxsurface> from .am files
    """
    if header.designation.extra_format == "<hxsurface>":
        return header, None
    else:
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

