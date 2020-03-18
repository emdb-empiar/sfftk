# -*- coding: utf-8 -*-
# notes
from __future__ import print_function

import sys

from sfftkrw.core import _dict

# RESOURCE_LIST = collections.OrderedDict()
RESOURCE_LIST = _dict()
FORMATS = [u'json', u'tab']
"""
Enter a set of resources to search
Each resource must have the following keys:

- name: <string>
- root_url: <url>
- format: one of the format values listed above
- result_path: a non-empty iterable of string OR unicode objects
- result_count: None OR a non-emty iterable of strings or unicode
"""
RESOURCE_LIST[u'ols'] = {
    u'name': u'OLS',
    u'root_url': u'https://www.ebi.ac.uk/ols/api/',
    u'format': u'json',
    u'result_path': [u'response', u'docs'],
    u'result_count': [u'response', u'numFound'],
}
RESOURCE_LIST[u'go'] = {
    u'name': u'GO',
    u'root_url': u'https://www.ebi.ac.uk/ols/api/',
    u'format': u'json',
    u'result_path': [u'response', u'docs'],
    u'result_count': [u'response', u'numFound'],
}
RESOURCE_LIST[u'emdb'] = {
    u'name': u'EMDB',
    u'root_url': u'https://www.ebi.ac.uk/pdbe/emdb/search/',
    u'format': u'json',
    u'result_path': [u'ResultSet', u'Result'],
    u'result_count': [u'ResultSet', u'totalResultsAvailable'],
}
RESOURCE_LIST[u'uniprot'] = {
    u'name': u'UniProt',
    u'root_url': u'https://www.uniprot.org/uniprot/',
    u'format': u'tab',
    u'result_path': None,
    u'result_count': None,
}
RESOURCE_LIST[u'pdb'] = {
    u'name': u'PDB',
    u'root_url': u'https://www.ebi.ac.uk/pdbe/search/pdb/select',
    u'format': u'json',
    u'result_path': [u'response', u'docs'],
    u'result_count': [u'response', u'numFound'],
}
RESOURCE_LIST[u'europepmc'] = {
    u'name': u'Europe PMC',
    u'root_url': u'https://www.ebi.ac.uk/europepmc/webservices/rest/',
    u'format': u'json',
    u'result_path': [u'resultList', u'result'],
    u'result_count': [u'hitCount'],
}
RESOURCE_LIST[u'empiar'] = {
    u'name': u'EMPIAR',
    u'root_url': u'https://www.ebi.ac.uk/pdbe/emdb/empiar/solr/select',
    u'format': u'json',
    u'result_path': [u'response', u'docs'],
    u'result_count': [u'response', u'numFound']
}
RESOURCE_LIST_NAMES = [RESOURCE_LIST[k][u'name'] for k in RESOURCE_LIST.keys()]
# enforce integrity
for resource in RESOURCE_LIST:
    name = RESOURCE_LIST[resource][u'name']
    root_url = RESOURCE_LIST[resource][u'root_url']
    format = RESOURCE_LIST[resource][u'format']
    result_path = RESOURCE_LIST[resource][u'result_path']
    result_count = RESOURCE_LIST[resource][u'result_count']
    assert isinstance(name, str) or isinstance(name, unicode)
    if sys.version_info[0] > 2:
        assert isinstance(root_url, str)
    else:
        assert isinstance(root_url, basestring)
    assert format in FORMATS
    assert result_path is None or map(hash, result_path)
    assert result_path is None or len(result_path) > 0
    assert result_count is None or map(hash, result_count)
    assert result_count is None or len(result_count) > 0
