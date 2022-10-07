"""
``sfftk.readers.amreader``
===========================

Ad hoc reader for AmiraMesh files
"""
from ahds import AmiraFile

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-01-21'


def get_data(fn, *args, **kwargs):
    """Reads and returns structured data given the file name

    :param str fn: filename
    :return header: Amira(R) file header
    :rtype header: :py:class:`ahds.header.AmiraHeader`
    :return labels: the segments as a 3D volume
    :rtype labels: :py:class:`ahds.data_stream.AmiraMeshDataStream`
    """
    af = AmiraFile(fn, load_streams=True, *args, **kwargs)
    if af.header.extra_format == "<hxsurface>":
        return af.header, None
    else:
        return af.header, af.data_streams.Labels  # segments are always in the 'Labels' attribute
