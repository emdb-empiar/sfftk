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
