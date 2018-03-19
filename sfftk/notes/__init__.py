# -*- coding: utf-8 -*-
# notes
from __future__ import print_function
import collections

RESOURCE_LIST = collections.OrderedDict()
FORMATS = ['json', 'tab']
"""
Enter a set of resources to search
Each resource must have the following keys:

- name: <string>
- root_url: <url>
- format: one of the format values listed above
- result_path: a non-empty iterable of string OR unicode objects
- result_count: None OR a non-emty iterable of strings or unicode
"""
RESOURCE_LIST['ols'] = {
    'name': 'OLS',
    'root_url': 'https://www.ebi.ac.uk/ols/api/',
    'format': 'json',
    'result_path': ['response', 'docs'],
    'result_count': ['response', 'numFound'],
}
RESOURCE_LIST['emdb'] = {
    'name': 'EMDB',
    'root_url': 'https://www.ebi.ac.uk/pdbe/emdb/search/',
    'format': 'json',
    'result_path': ['ResultSet', 'Result'],
    'result_count': ['ResultSet', 'totalResultsAvailable'],
}
RESOURCE_LIST['uniprot'] = {
    'name': 'UniProt',
    'root_url': 'https://www.uniprot.org/uniprot/',
    'format': 'tab',
    'result_path': None,
    'result_count': None,
}
RESOURCE_LIST['pdb'] = {
    'name': 'PDB',
    'root_url': 'https://www.ebi.ac.uk/pdbe/search/pdb/select',
    'format': 'json',
    'result_path': ['response', 'docs'],
    'result_count': ['response', 'numFound'],
}

# enforce integrity
for resource in RESOURCE_LIST:
    name = RESOURCE_LIST[resource]['name']
    root_url = RESOURCE_LIST[resource]['root_url']
    format = RESOURCE_LIST[resource]['format']
    result_path = RESOURCE_LIST[resource]['result_path']
    result_count = RESOURCE_LIST[resource]['result_count']
    assert isinstance(name, str) or isinstance(name, unicode)
    assert isinstance(root_url, str) or isinstance(root_url, unicode)  # fixme: not sufficient assertion
    assert format in FORMATS
    assert result_path is None or map(hash, result_path)
    assert result_path is None or len(result_path) > 0
    assert result_count is None or map(hash, result_count)
    assert result_count is None or len(result_count) > 0
