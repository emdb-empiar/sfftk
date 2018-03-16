#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.find

Search for terms and display ontologies
"""
from __future__ import division

import os
import sys
import textwrap

from . import RESOURCE_LIST

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"
__updated__ = '2018-02-14'


# todo: expand OLS options to below

# type
# Restrict a search to an entity type, one of {class,property,individual,ontology}
#
# slim
# Restrict a search to an particular set of slims by name
#
# fieldList
# Specifcy the fields to return, the defaults are {iri,label,short_form,short_form,ontology_name,ontology_prefix,description,type}
#
# queryFields
# Specifcy the fields to query, the defaults are {label, synonym, description, short_form, short_form, annotations, logical_description, iri}
#
# groupField
# Set to true to group results by unique id (IRI)
#
# local
# Set to true to only return terms that are in a defining ontology e.g. Only return matches to gene ontology terms in the gene ontology, and exclude ontologies where those terms are also referenced
#
# childrenOf
# You can restrict a search to children of a given term. Supply a list of IRI for the terms that you want to search under
#
# allChildrenOf
# You can restrict a search to all children of a given term. Supply a list of IRI for the terms that you want to search under (subclassOf/is-a plus any hierarchical/transitive properties like 'part of' or 'develops from')


# todo: Retrieve an ontology GET /api/ontologies/{ontology_id}

class SearchResource(object):
    """A resource against which to look for accessions or terms"""

    def __init__(self, args, configs):
        self._args = args
        self._configs = configs
        self._results = None
        try:
            self._resource = RESOURCE_LIST[args.resource]
        except KeyError:
            raise ValueError("unknown resource '{resource}".format(
                resource=args.resource,
            ))
            sys.exit(os.EX_DATAERR)

    @property
    def search_args(self):
        return self._args

    @property
    def configs(self):
        return self._configs

    @property
    def name(self):
        return self._resource['name']

    @property
    def root_url(self):
        return self._resource['root_url']

    @property
    def format(self):
        return self._resource['format']

    @property
    def results(self):
        return self._results

    def get_url(self):
        """Determine the url to search against"""
        url = None
        # ols
        if self.name == 'OLS':
            if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
                url = self.root_url + "ontologies?size=1000"
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
        # emdb
        elif self.name == 'EMDB':
            url = self.root_url + "?q={}&start={}&rows={}".format(
                self.search_args.search_term,
                self.search_args.start,
                self.search_args.rows,
            )
        # uniprot
        elif self.name == "UniProt":
            url = self.root_url + "?query={search_term}&format=tab&offset={start}&limit={rows}&columns=id,entry_name,protein_names,organism".format(
                search_term=self.search_args.search_term,
                start=self.search_args.start,
                rows=self.search_args.rows,
            )
        # pdb
        elif self.name == "PDB":
            url = self.root_url + "?q={search_term}&wt=json&fl=pdb_id,title,organism_scientific_name&start={start}&rows={rows}".format(
                search_term=self.search_args.search_term,
                start=self.search_args.start,
                rows=self.search_args.rows,
            )
        return url

    def search(self, *args, **kwargs):
        """Perform a search against this resource"""
        url = self.get_url()
        if url is not None:
            import requests
            # make the search
            R = requests.get(url)
            if R.status_code == 200:
                self._results = R.text
                # return SearchResults(self._results, self.search_args, self._configs, *args, **kwargs)
                return SearchResults(self)
            else:
                raise ValueError(R.text)
                sys.exit(os.EX_DATAERR)
        else:
            raise ValueError('url is None')
            sys.exit(os.EX_DATAERR)


class SearchQuery(object):
    """Class that handles queries"""

    def __init__(self, args, configs):
        self._resource = SearchResource(args, configs)
        self._search_args = args
        self.configs = configs
        self._results = None

    @property
    def search_args(self):
        return self._search_args

    @property
    def results(self):
        """JSON of response from HTTP API"""
        return self._results

    def search(self, *args, **kwargs):
        return self._resource.search(*args, **kwargs)
    # def search(self, *args, **kwargs):
    #     """Do the search
    #
    #     :return result: search results
    #     :rtype result: ``SearchResults``
    #     """
    #     import requests
    #     if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
    #         url = self.root_url + "ontologies?size=1000"
    #         R = requests.get(url)
    #         if R.status_code == 200:
    #             self._results = R.text
    #             return SearchResults(self.results, self.search_args, self.configs, *args, **kwargs)
    #         else:
    #             raise ValueError(R.text)
    #     else:
    #         url = self.root_url + "search?q={}&start={}&rows={}".format(
    #             self.search_args.search_term,
    #             self.search_args.start - 1,
    #             self.search_args.rows,
    #         )
    #         if self.search_args.ontology:
    #             url += "&ontology={}".format(self.search_args.ontology)
    #         if self.search_args.exact:
    #             url += "&exact=on"
    #         if self.search_args.obsoletes:
    #             url += "&obsoletes=on"
    #         R = requests.get(url)
    #         if R.status_code == 200:
    #             self._results = R.text
    #             return SearchResults(self.results, self.search_args, self.configs, *args, **kwargs)
    #         else:
    #             raise ValueError(R.text)


class SearchResults(object):
    """SearchResults class"""
    # try and get
    #     try:
    #         rows, cols = map(int, os.popen('stty size').read().split())
    #         TTY_WIDTH = cols
    #     except:
    TTY_WIDTH = 180  # unreasonable default
    INDEX_WIDTH = 6
    LABEL_WIDTH = 20
    SHORT_FORM_WIDTH = 20
    ONTOLOGY_NAME_WIDTH = 15
    DESCRIPTION_WIDTH = 80
    TYPE_WIDTH = 18

    def __init__(self, resource):
        self._resource = resource
        self._raw_results = resource.results
        self._structured_results = self._structure_results()

    def _structure_results(self):
        """Structure the raw result according to the format received"""
        if self._resource.format == 'json':
            import json
            structured_results = json.loads(self._raw_results, 'utf-8')
            return structured_results
        elif self._resource.format == 'tab':
            # split rows; split columns; dump first and last rows
            _structured_results = map(lambda r: r.split('\t'), self._raw_results.split('\n'))[1:-1]
            # make a list of dicts with the given ids
            structured_results = map(lambda r: dict(zip(['id', 'name', 'proteins', 'organism'], r)), _structured_results)
            return structured_results
        else:
            raise ValueError("unsupported format: {}".format(self._resource.format))
            return sys.exit(os.EX_DATAERR)

    @property
    def search_args(self):
        return self._resource.search_args

    @property
    def results(self):
        return self._structured_results

    def __str__(self):
        # open colour
        string = "\033[0;33m\r"
        string += self.tabulate(self.results)
        # close colour
        string += "\033[0;0m\r"
        # return encoded
        return string.encode('utf-8')

    def tabulate(self, results):
        table = ""
        if self._resource.name == 'OLS':
            if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
                if self.search_args.list_ontologies:
                    for ontology in results['_embedded']['ontologies']:
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
                        table += "\n".join(ont)
                        table += "\n" + "-" * self.TTY_WIDTH
                elif self.search_args.short_list_ontologies:
                    table += "List of ontologies\n"
                    table += "-" * self.TTY_WIDTH
                    for ontology in results['_embedded']['ontologies']:
                        c = ontology['config']
                        ont = [
                            unicode(c['namespace']).ljust(10),
                            "-",
                            unicode(c['description'][:200]) if c['description'] else '' + "...",
                        ]
                        table += "\t".join(ont) + "\n"
            else:
                table += "=" * self.TTY_WIDTH + "\n"
                table += "Search term: {}\n\n".format(self.search_args.search_term)
                header = [
                    "index".ljust(self.INDEX_WIDTH),
                    "label".ljust(self.LABEL_WIDTH),
                    "short_form".ljust(self.SHORT_FORM_WIDTH),
                    "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                    "description/IRI".ljust(self.DESCRIPTION_WIDTH),
                    "type".ljust(self.TYPE_WIDTH),
                ]
                table += "\t".join(header) + "\n"
                table += "=" * self.TTY_WIDTH + "\n"

                start = self.search_args.start

                for e in results['response']['docs']:
                    if e.has_key('description'):
                        wrapped_description = textwrap.wrap(e['description'][0] + " /{}".format(e['iri']),
                                                            self.DESCRIPTION_WIDTH)
                        if len(wrapped_description) == 1:
                            row = [
                                str(start).ljust(self.INDEX_WIDTH),
                                e['label'].ljust(self.LABEL_WIDTH),
                                e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                                    self.SHORT_FORM_WIDTH),
                                e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                                wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                                e['type'].ljust(self.TYPE_WIDTH),
                            ]
                            table += "\t".join(row) + "\n"
                        else:
                            row = [
                                str(start).ljust(self.INDEX_WIDTH),
                                e['label'].ljust(self.LABEL_WIDTH),
                                e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                                    self.SHORT_FORM_WIDTH),
                                e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                                wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                                e['type'].ljust(self.TYPE_WIDTH),
                            ]
                            table += "\t".join(row) + "\n"
                            for i in xrange(1, len(wrapped_description)):
                                row = [
                                    ''.ljust(self.INDEX_WIDTH),
                                    ''.ljust(self.LABEL_WIDTH),
                                    ''.ljust(self.SHORT_FORM_WIDTH),
                                    ''.ljust(self.ONTOLOGY_NAME_WIDTH),
                                    wrapped_description[i].ljust(self.DESCRIPTION_WIDTH),
                                    ''.ljust(self.TYPE_WIDTH),
                                ]
                                table += "\t".join(row) + "\n"
                    else:
                        row = [
                            str(start).ljust(self.INDEX_WIDTH),
                            e['label'].ljust(self.LABEL_WIDTH),
                            e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                                self.SHORT_FORM_WIDTH),
                            e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                            "{}".format(e['iri']).ljust(self.DESCRIPTION_WIDTH),
                            e['type'].ljust(self.TYPE_WIDTH),
                        ]
                        table += "\t".join(row) + "\n"

                    table += "-" * self.TTY_WIDTH + "\n"
                    start += 1

                if results['response']['numFound']:
                    table += "Showing: {} to {} of {} results found".format(
                        self.search_args.start,
                        min(results['response']['numFound'], self.search_args.start + self.search_args.rows - 1),
                        results['response']['numFound']
                    )
                else:
                    table += "No results found."
        elif self._resource.name == 'EMDB':
            table += "=" * self.TTY_WIDTH + "\n"
            table += "Search term: {}\n\n".format(self.search_args.search_term)
            header = [
                "index".ljust(self.INDEX_WIDTH),
                "label".ljust(self.LABEL_WIDTH),
                "short_form".ljust(self.SHORT_FORM_WIDTH),
                "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                "description/IRI".ljust(self.DESCRIPTION_WIDTH),
                "type".ljust(self.TYPE_WIDTH),
            ]
            table += "\t".join(header) + "\n"
            table += "=" * self.TTY_WIDTH + "\n"
            table += 'emdb'
            print self.results
        elif self._resource.name == "UniProt":
            table += "=" * self.TTY_WIDTH + "\n"
            table += "Search term: {}\n\n".format(self.search_args.search_term)
            header = [
                "index".ljust(self.INDEX_WIDTH),
                "label".ljust(self.LABEL_WIDTH),
                "short_form".ljust(self.SHORT_FORM_WIDTH),
                "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                "description/IRI".ljust(self.DESCRIPTION_WIDTH),
                "type".ljust(self.TYPE_WIDTH),
            ]
            table += "\t".join(header) + "\n"
            table += "=" * self.TTY_WIDTH + "\n"
            table += 'uniprot'
            print self.results
        elif self._resource.name == "PDB":
            table += "=" * self.TTY_WIDTH + "\n"
            table += "Search term: {}\n\n".format(self.search_args.search_term)
            header = [
                "index".ljust(self.INDEX_WIDTH),
                "label".ljust(self.LABEL_WIDTH),
                "short_form".ljust(self.SHORT_FORM_WIDTH),
                "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                "description/IRI".ljust(self.DESCRIPTION_WIDTH),
                "type".ljust(self.TYPE_WIDTH),
            ]
            table += "\t".join(header) + "\n"
            table += "=" * self.TTY_WIDTH + "\n"
            table += 'pdb'
            print self.results
        return table

    #     def __len__(self):
    #         return self._result_list
    def __repr__(self):
        pass

    #         return "SearchResult object containing {} result(s)".format(len(self))
    def __len__(self):
        return self._structured_result['response']['numFound']
