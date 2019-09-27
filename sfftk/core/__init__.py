# -*- coding: utf-8 -*-
"""

Convenience utilities

"""
import sys

# redefinitions used globally
if sys.version_info[0] > 2:
    # xrange
    _xrange = range
    # iter* methods on dictionaries
    _dict_iter_keys = dict.keys
    _dict_iter_values = dict.values
    _dict_iter_items = dict.items
    # dictionaries preserve order in Python3
    if sys.version_info[1] >= 7:
        _dict = dict
    else:
        from collections import OrderedDict

        _dict = OrderedDict
    # UserList
    from collections import UserList

    _UserList = UserList
    # pseudo unicode function (does not exist in Python3)
    _bytes = bytes
    _str = str


    def _unicode(data):
        return data


    # urlencode
    from urllib.parse import urlencode

    _urlencode = urlencode
    # string base is str
    _basestring = str


    # decode is meaningless for str in Python3
    def _decode(data, encoding):
        if isinstance(data, str):
            return data
        elif isinstance(data, bytes):
            return data.decode(encoding)
        return data


    # encoding
    def _encode(data, encoding):
        if isinstance(data, str):
            return data.encode(encoding)
        elif isinstance(data, bytes):
            return data
        return data


    _input = input
else:
    import __builtin__

    # xrange
    _xrange = __builtin__.xrange

    # iter* methods on dictionaries
    _dict_iter_keys = dict.iterkeys
    _dict_iter_values = dict.itervalues
    _dict_iter_items = dict.iteritems

    # for order preservation in dicts user OrderedDict
    from collections import OrderedDict

    _dict = OrderedDict

    from UserList import UserList

    _UserList = UserList
    # unicode
    _bytes = str
    _str = __builtin__.unicode


    def _unicode(data):
        return _str(data)


    # urlencode
    from urllib import urlencode

    _urlencode = urlencode
    # string base is basestring
    _basestring = __builtin__.basestring


    # decode Python2 str object
    def _decode(data, encoding):
        if isinstance(data, str):
            return data.decode(encoding)
        elif isinstance(data, __builtin__.unicode):
            return data
        return data


    # encoding
    def _encode(data, encoding):
        if isinstance(data, str):
            return data
        elif isinstance(data, __builtin__.unicode):
            return data.encode(encoding)
        return data


    _input = __builtin__.raw_input
