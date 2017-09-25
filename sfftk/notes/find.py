#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
"""
sfftk.notes.find

Copyright 2017 EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. 

See the License for the specific language governing permissions 
and limitations under the License.
"""

__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2017-04-07"

import os

"""
:TODO: expand OLS options to below

ontology

Restrict a search to a set of ontologies e.g. ontology=uberon,ma

type

Restrict a search to an entity type, one of {class,property,individual,ontology}

slim

Restrict a search to an particular set of slims by name

fieldList

Specifcy the fields to return, the defaults are {iri,label,short_form,obo_id,ontology_name,ontology_prefix,description,type}

queryFields

Specifcy the fields to query, the defaults are {label, synonym, description, short_form, obo_id, annotations, logical_description, iri}

exact

Set to true for exact matches

groupField

Set to true to group results by unique id (IRI)

obsoletes

Set to true to include obsoleted terms in the results

local

Set to true to only return terms that are in a defining ontology e.g. Only return matches to gene ontology terms in the gene ontology, and exclude ontologies where those terms are also referenced

childrenOf

You can restrict a search to children of a given term. Supply a list of IRI for the terms that you want to search under

allChildrenOf

You can restrict a search to all children of a given term. Supply a list of IRI for the terms that you want to search under (subclassOf/is-a plus any hierarchical/transitive properties like 'part of' or 'develops from')

rows

How many results per page

start

The results page number
"""

"""
:TODO: Retrieve an ontology
GET /api/ontologies/{ontology_id}
"""

class SearchQuery(object):
    """SearchQuery class"""
    root_url = "http://www.ebi.ac.uk/ols/api/"
    def __init__(self, args):
        self._search_args = args
        self._results = None
    @property
    def search_args(self):
        return self._search_args
    @property
    def results(self):
        """JSON of response from HTTP API"""
        return self._results
    def search(self, *args, **kwargs):
        """Do the search
        
        :return result: search results
        :rtype result: ``SearchResults``
        """
        import requests
        if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
            url = self.root_url + "ontologies?size=1000"
            R = requests.get(url)
            self._results = R.text
            return SearchResults(self.results, self.search_args, *args, **kwargs)
        else:
            url = self.root_url + "search?q={}&start={}&rows={}".format(
                self.search_args.search_term,
                self.search_args.start - 1,
                self.search_args.rows,
                )
            if self.search_args.ontology:
                url += "&ontology={}".format(self.search_args.ontology)
            if self.search_args.exact:
                url += "&exact=on"
            if self.search_args.obsoletes:
                url += "&obsoletes=on"
            R = requests.get(url)
            self._results = R.text
            return SearchResults(self.results, self.search_args, *args, **kwargs)
            

class SearchResults(object):
    """SearchResults class"""
    # try and get 
#     try:
#         rows, cols = map(int, os.popen('stty size').read().split())
#         TTY_WIDTH = cols
#     except:
    TTY_WIDTH = 180 # unreasonable default
    INDEX_WIDTH = 6
    LABEL_WIDTH = 20
    OBO_ID_WIDTH = 20
    ONTOLOGY_NAME_WIDTH = 15
    DESCRIPTION_WIDTH = 80
    TYPE_WIDTH = 18
    def __init__(self, json_result, search_args, *args, **kwargs):
        self._json_result = json_result
        self._search_args = search_args
        import json
        self._str_result = json.loads(self._json_result, 'utf-8')
    @property
    def search_args(self):
        return self._search_args
    @property
    def result(self):
        return self._str_result
    def __str__(self):
        import textwrap
        string = ""
        if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
            if self.search_args.list_ontologies:
                for ontology in self.result['_embedded']['ontologies']:
                    c = ontology['config']
                    ont = [
                        "Namespace: ".ljust(30) + unicode(c['namespace']),
                        "Pref. prefix: ".ljust(30) + unicode(c['preferredPrefix']),
                        "Title: ".ljust(30) + unicode(c['title']),
                        "Description: ".ljust(30) + unicode(c['description']),
                        "Homepage: ".ljust(30) + unicode(c['homepage']),
                        "ID: ".ljust(30) + unicode(c['id']),
                        "Version :".ljust(30) + unicode(c['version']),
                        ]
                    string += "\n".join(ont)
                    string += "\n" + "-" * self.TTY_WIDTH
            elif self.search_args.short_list_ontologies:
                string +=  "List of ontologies\n"
                string += "-" * self.TTY_WIDTH
                for ontology in self.result['_embedded']['ontologies']:
                    c = ontology['config']
                    ont = [
                        unicode(c['namespace']).ljust(10),
                        "-",
                        unicode(c['description'][:200]) if c['description'] else '' + "...",
                        ]
                    string += "\t".join(ont) + "\n"
        else:
            string += "=" * self.TTY_WIDTH + "\n"
            string += "Search term: {}\n\n".format(self.search_args.search_term)
            header = [
                "index".ljust(self.INDEX_WIDTH),
                "label".ljust(self.LABEL_WIDTH),
                "obo_id".ljust(self.OBO_ID_WIDTH),
                "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                "description".ljust(self.DESCRIPTION_WIDTH),
                "type".ljust(self.TYPE_WIDTH),
                ]
            string += "\t".join(header) + "\n"
            string += "=" * self.TTY_WIDTH + "\n"
            
            start = self.search_args.start
            
            for e in self.result['response']['docs']:
                if e.has_key('description'):        
                    wrapped_description = textwrap.wrap(e['description'][0], self.DESCRIPTION_WIDTH)
                    if len(wrapped_description) == 1:
                        row = [
                            str(start).ljust(self.INDEX_WIDTH),
                            e['label'].ljust(self.LABEL_WIDTH),
                            e['obo_id'].ljust(self.OBO_ID_WIDTH) if e.has_key('obo_id') else '-'.ljust(self.OBO_ID_WIDTH),
                            e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                            wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                            e['type'].ljust(self.TYPE_WIDTH),
                            ]
                        string += "\t".join(row) + "\n"
                    else:
                        row = [
                            str(start).ljust(self.INDEX_WIDTH),
                            e['label'].ljust(self.LABEL_WIDTH),
                            e['obo_id'].ljust(self.OBO_ID_WIDTH) if e.has_key('obo_id') else '-'.ljust(self.OBO_ID_WIDTH),
                            e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                            wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                            e['type'].ljust(self.TYPE_WIDTH),
                            ]
                        string += "\t".join(row) + "\n"
                        for i in xrange(1, len(wrapped_description)):
                            row = [
                                ''.ljust(self.INDEX_WIDTH),
                                ''.ljust(self.LABEL_WIDTH),
                                ''.ljust(self.OBO_ID_WIDTH),
                                ''.ljust(self.ONTOLOGY_NAME_WIDTH),
                                wrapped_description[i].ljust(self.DESCRIPTION_WIDTH),
                                ''.ljust(self.TYPE_WIDTH),
                                ]
                            string += "\t".join(row) + "\n"
                else:
                    row = [
                        str(start).ljust(self.INDEX_WIDTH),
                        e['label'].ljust(self.LABEL_WIDTH),
                        e['obo_id'].ljust(self.OBO_ID_WIDTH) if e.has_key('obo_id') else '-'.ljust(self.OBO_ID_WIDTH),
                        e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                        ''.ljust(self.DESCRIPTION_WIDTH),
                        e['type'].ljust(self.TYPE_WIDTH),
                        ]
                    string += "\t".join(row) + "\n"
                    
                string += "-" * self.TTY_WIDTH + "\n"
                start += 1    
            
            if self.result['response']['numFound']:
                string += "Showing: {} to {} of {} results found".format(
                    self.search_args.start, 
                    min(self.result['response']['numFound'], self.search_args.start + self.search_args.rows - 1), 
                    self.result['response']['numFound']
                    )
            else:
                string += "No results found."
        # return encoded
        return string.encode('utf-8')
#     def __len__(self):
#         return self._result_list
    def __repr__(self):
        pass
#         return "SearchResult object containing {} result(s)".format(len(self))
    def __len__(self):
        return self._str_result['response']['numFound']