# -*- coding: utf-8 -*-
# notes
# EXTERNAL_REFERENCES = ['pdb', 'uniprot', 'emdb']
import collections

RESOURCE_LIST = collections.OrderedDict()
"""
Enter a set of resources to search
Each resource must have the following keys:

- name: <string>
- root_url: <url>
- format: json|tab|xml
"""
RESOURCE_LIST['ols'] = {
    'name': 'OLS',
    'root_url': 'https://www.ebi.ac.uk/ols/api/',
    'format': 'json',
}
RESOURCE_LIST['emdb'] = {
    'name': 'EMDB',
    'root_url': 'https://www.ebi.ac.uk/pdbe/emdb/search/',
    'format': 'json',
}
RESOURCE_LIST['uniprot'] = {
    'name': 'UniProt',
    'root_url': 'https://www.uniprot.org/uniprot/',
    'format': 'tab',
}
RESOURCE_LIST['pdb'] = {
    'name': 'PDB',
    'root_url': 'https://www.ebi.ac.uk/pdbe/search/pdb/select',
    'format': 'json',
}
