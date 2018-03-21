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
