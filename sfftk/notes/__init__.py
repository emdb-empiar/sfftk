RESOURCE_LIST = dict()
FORMATS = ['json', 'tsv']
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
RESOURCE_LIST['go'] = {
    'name': 'GO',
    'root_url': 'https://www.ebi.ac.uk/ols/api/',
    'format': 'json',
    'result_path': ['response', 'docs'],
    'result_count': ['response', 'numFound'],
}
RESOURCE_LIST['emdb'] = {
    'name': 'EMDB',
    'root_url': 'https://www.ebi.ac.uk/emdb/api/search/',
    'format': 'json',
    'result_path': None,
    'result_count': None,
}
RESOURCE_LIST['uniprot'] = {
    'name': 'UniProt',
    'root_url': 'https://rest.uniprot.org/uniprotkb/search',
    'format': 'tsv',
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
RESOURCE_LIST['europepmc'] = {
    'name': 'Europe PMC',
    'root_url': 'https://www.ebi.ac.uk/europepmc/webservices/rest/',
    'format': 'json',
    'result_path': ['resultList', 'result'],
    'result_count': ['hitCount'],
}
RESOURCE_LIST['empiar'] = {
    'name': 'EMPIAR',
    'root_url': 'https://www.ebi.ac.uk/emdb/api/empiar/search/',
    'format': 'json',
    'result_path': None,
    'result_count': None,
}
RESOURCE_LIST_NAMES = [RESOURCE_LIST[k]['name'] for k in RESOURCE_LIST.keys()]
# enforce integrity
for resource in RESOURCE_LIST:
    name = RESOURCE_LIST[resource]['name']
    root_url = RESOURCE_LIST[resource]['root_url']
    format_ = RESOURCE_LIST[resource]['format']
    result_path = RESOURCE_LIST[resource]['result_path']
    result_count = RESOURCE_LIST[resource]['result_count']
    assert isinstance(name, str)
    assert isinstance(root_url, str)
    assert format_ in FORMATS
    assert result_path is None or map(hash, result_path)
    assert result_path is None or len(result_path) > 0
    assert result_count is None or map(hash, result_count)
    assert result_count is None or len(result_count) > 0
