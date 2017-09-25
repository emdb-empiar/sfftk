# -*- coding: utf-8 -*-
"""
configs.py
===========

SFFTK configs
"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__    = '2016-08-23'


import os.path
from collections import OrderedDict
import sfftk

def get_configs(fn=os.path.join(sfftk.__path__[0], 'sff.conf')):
    """Get SFFTK configs
    
    :param str fn: filename (default: ``./sff.conf``)
    :return dict configs: dictionary of configs
    """ 
    configs = OrderedDict()
    
    try:
        assert os.path.exists(fn)
    except AssertionError:
        raise IOError("File '%s' does not exist." % fn)
    
    with open(fn, 'r') as f:
        for row in f:
            if row[0] == '#': # comments
                continue
            if row.strip() == '': # blank lines
                continue
            name, value = row.strip().split('=')
            configs[name] = value
    
    return configs


# def set_configs(var, val, fn='./sff.conf'):
#     """Set the variable 'var' to the value held in 'val'
#     
#     :param str var: variable name
#     :param str val: value to set
#     :param str fn: path to the conf file
#     :return int status: 0 on success; otherwise, fail
#     """
#     configs = get_configs(fn=fn)
    