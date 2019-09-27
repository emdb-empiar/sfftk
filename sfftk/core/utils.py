# -*- coding: utf-8 -*-
# utils.py
"""
utils.py
========

A collection of helpful utilities
"""
from __future__ import print_function, division


def get_path(D, path):
    """Get a path from a dictionary

    :param dict D: a dictionary
    :param list path: an iterable of hashables
    :return: the item at the path from the dictionary
    """
    assert isinstance(D, dict)
    try:
        assert map(hash, path)
    except TypeError:
        raise TypeError('path should be an iterable of hashables')

    item = D
    for p in path:
        item = item[p]
    return item


def rgba_to_hex(rgba, channels=3):
    """Convert RGB(A) iterable to a hex string (e.g. #aabbcc(dd)

    :param rgba: an iterable with normalised (values in the closed interval ``[0-1]``) colour channel values
    :type rgba: list or tuple
    :param int channels: the number of channels (3 or 4); default 3
    :return: a hex string
    :rtype: str
    """
    try:
        assert channels in [3, 4]  # you can only return 3 or 4 channels
    except AssertionError:
        raise ValueError("keyword 'channels' can only be 3 or 4")
    min_channel_value = 0.0
    max_channel_value = 1.0
    if len(rgba) == 4:
        r, g, b, a = rgba
    elif len(rgba) == 3:
        r, g, b = rgba
        a = 1
    if r < min_channel_value or r > max_channel_value or \
            g < min_channel_value or g > max_channel_value or \
            b < min_channel_value or b > max_channel_value or \
            a < min_channel_value or a > max_channel_value:
        raise ValueError(
            'values of rgba should be [{}-{}] (inclusive)'.format(
                min_channel_value,
                max_channel_value
            )
        )
    import math

    def dd_hex(val):
        _, hex_val = hex(int(math.floor(val * 255))).split('x')
        if len(hex_val) == 1:
            hex_val = '0' + hex_val
        return hex_val

    if channels == 3:
        hex_colour = '#' + dd_hex(r) + dd_hex(g) + dd_hex(b)
    elif channels == 4:
        hex_colour = '#' + dd_hex(r) + dd_hex(g) + dd_hex(b) + dd_hex(a)
    return hex_colour
