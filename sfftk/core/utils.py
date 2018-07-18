# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os
import sys

from .print_tools import print_date


def get_path(D, path):
    """Get a path from a dictionary

    :param dict D: a dictionary
    :param list path: an iterable of hashables
    :return item: an item at the path from the dictionary
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


def parse_and_split(cmd):
    from .parser import parse_args
    from shlex import split
    return parse_args(split(cmd))


def printable_substring(the_str):
    """Returns the printable subset of the_str

    :param str the_str: a putative string
    :return str the_pr_str: the portion of the_str from index 0 that is printable
    """
    import string
    i = 0
    the_pr_str = ''
    while i < len(the_str):
        if the_str[i] in string.printable:
            the_pr_str += the_str[i]
            i += 1
        else:
            return the_pr_str
    return the_pr_str


def parallelise(iterable, target=None, args=(), number_of_processes=None):
    """Parallelise computation of `target` over items in `iterable`

    :param iterable: (usually) a list of items
    :param target: the function to compute
    :param args: arguments to target
    :return: the result of computing iterable in parallel
    """
    if target is None:
        return iterable

    from multiprocessing import Process, Queue, cpu_count

    def worker(input, output):
        for func, args in iter(input.get, 'STOP'):
            result = func(*args)
            output.put(result)

    if number_of_processes is not None:
        try:
            assert number_of_processes > 0
        except AssertionError as a:
            print_date("Invalid number of processes: {}".format(number_of_processes))
            print(str(a))
            return sys.exit(os.EX_DATAERR)
        NUMBER_OF_PROCESSES = number_of_processes
    else:
        NUMBER_OF_PROCESSES = cpu_count()

    # input and output queues
    input = Queue()
    output = Queue()

    # load input queue
    for item in iterable:
        my_args = tuple([item] + list(args))
        input.put((target, my_args))

    # start processes
    for _ in xrange(NUMBER_OF_PROCESSES):
        Process(target=worker, args=(input, output)).start()

    # read output
    iterable2 = list()
    for _ in xrange(len(iterable)):
        iterable2.append(output.get())

    # kill processes
    for _ in xrange(NUMBER_OF_PROCESSES):
        input.put('STOP')

    return iterable2


def rgba_to_hex(rgba, channels=3):
    """Convert RGB(A) iterable to a hex string (e.g. #aabbcc(dd)

    :param rgba: an iterable (list, tuple) with normalised ([0-1]) colour channel values
    :param channels: the number of channels (3 or 4); default 3
    :return: a hex string
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
