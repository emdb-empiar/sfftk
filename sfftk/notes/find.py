#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.find

Search for terms and display ontologies
"""
from __future__ import division, print_function

import os
import sys
import textwrap

from . import RESOURCE_LIST
from ..core import utils

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
        self._response = None
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
    def result_path(self):
        return self._resource['result_path']

    @property
    def result_count(self):
        return self._resource['result_count']

    @property
    def response(self):
        return self._response

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
                self._response = R.text
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

    # @property
    # def results(self):
    #     """JSON of response from HTTP API"""
    #     return self._results

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


class TableField(object):
    def __init__(self, name, key=None, width=20, justify='left', is_index=False, is_iterable=False):
        # todo: assert justify
        # todo: assert width
        self._name = name
        if key is None:
            self._key = name
        else:
            self._key = key
        self._width = width
        self._justify = justify
        self._is_index = is_index
        self._is_iterable = is_iterable

    def justify(self, text):
        if self._justify == 'left':
            return text.ljust(self._width)
        elif self._justify == 'right':
            return text.ljust(self._width)
        elif self._justify == 'center':
            return text.center(self._width)

    def __unicode__(self):
        # todo: other justifications
        return self.justify(self._name)

    @property
    def is_index(self):
        return self._is_index

    def render(self, row_data, index):
        if self.is_index:
            text = unicode(index)
        else:
            try:
                if self._is_iterable:
                    text = row_data[self._key][0]
                else:
                    text = row_data[self._key]
            except KeyError:
                text = u'-'
        wrapped_text = textwrap.wrap(text, self._width)
        if not wrapped_text:  # empty list for empty string
            return [self.justify(u'')]
        else:
            return map(self.justify, wrapped_text)


class Table(object):
    """Table superclass"""
    column_separator = u"\t"
    row_separator = u"\n"


class TableRow(Table):
    """A single row in the table

    Wrapping is automatically handled
    """

    def __init__(self, row_data, fields, index, *args, **kwargs):
        super(TableRow, self).__init__(*args, **kwargs)
        self._row_data = row_data
        self._fields = fields
        self._index = index
        self._rendered = self._render()

    def _render(self):
        rendered = list()
        for field in self._fields:
            rendered.append(field.render(self._row_data, self._index))
        return rendered

    def __unicode__(self):
        string = u''
        # get the max number of lines in this row
        no_lines = 0
        for f in self._rendered:
            no_lines = max(len(f), no_lines)
        # build the stack of lines for this row
        for i in xrange(no_lines):
            row = list()
            for j, F in enumerate(self._fields):
                try:
                    field = self._rendered[j][i]
                except IndexError:
                    field = F.justify(u'')
                row.append(field)
            string += self.column_separator.join(row) + self.row_separator
        return string


class ResultsTable(Table):
    """Class that formats search results as a table"""

    def __init__(self, search_results, fields, width=180, *args, **kwargs):
        """Initialise a ResultsTable object by specifying results and fields

        :param search_results: a SearchResults object
        :type search_results: SearchResults
        :param list fields: a list of TableField objects
        :param int width: a non-negative integer
        """
        super(ResultsTable, self).__init__(*args, **kwargs)
        self._search_results = search_results
        self._fields = fields
        self._width = width
        # todo: ensure width is less than the sum of fields
        # todo: there can only be one index field (result number)

    @property
    def header(self):
        header = u"=" * self._width + self.row_separator
        header += u"Search term: {}{}{}".format(
            self._search_results.search_args.search_term,
            self.row_separator,
            self.row_separator,
        )
        header += self.column_separator.join(map(unicode, self._fields)) + self.row_separator
        header += u"=" * self._width + self.row_separator
        return header

    @property
    def body(self):
        body = u''
        index = self._search_results.search_args.start  # index
        for row_data in self._search_results.results:
            body += unicode(TableRow(row_data, self._fields, index)) + self.row_separator
            body += u"-" * self._width + self.row_separator
            index += 1  # increment index
        return body

    @property
    def footer(self):
        if len(self._search_results):
            footer = u'Showing: {} to {} of {} results found'.format(
                self._search_results.search_args.start,
                min(len(self._search_results),
                    self._search_results.search_args.start + self._search_results.search_args.rows - 1),
                len(self._search_results),
            )
        else:
            footer = u"Showing {} results per page".format(
                self._search_results.search_args.rows,
            )
        return footer

    def __unicode__(self):
        string = u''
        string += self.header
        string += self.body
        string += self.footer
        return string


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
        self._raw_response = resource.response
        self._structured_response = self._structure_response()

    @property
    def structured_response(self):
        return self._structured_response

    def _structure_response(self):
        """Structure the raw result according to the format received"""
        if self._resource.format == 'json':
            import json
            structured_results = json.loads(self._raw_response, 'utf-8')
            return structured_results
        elif self._resource.format == 'tab':
            # split rows; split columns; dump first and last rows
            _structured_results = map(lambda r: r.split('\t'), self._raw_response.split('\n'))[1:-1]
            # make a list of dicts with the given ids
            structured_results = map(lambda r: dict(zip(['id', 'name', 'proteins', 'organism'], r)),
                                     _structured_results)
            return structured_results
        else:
            raise ValueError("unsupported format: {}".format(self._resource.format))
            sys.exit(os.EX_DATAERR)

    @property
    def search_args(self):
        return self._resource.search_args

    @property
    def results(self):
        if self._resource.result_path is not None:
            return utils.get_path(self._structured_response, self._resource.result_path)
        else:
            return self._structured_response

    def __str__(self):
        # open colour
        string = u"\033[0;33m\r"
        string += unicode(self.tabulate())
        # close colour
        string += u"\033[0;0m\r"
        # return encoded
        return string.encode('utf-8')

    def tabulate(self):
        """Tabulate the search results"""
        table = ""
        if self._resource.name == 'OLS':
            # only list ontologies as short or long lists
            if self.search_args.list_ontologies or self.search_args.short_list_ontologies:
                if self.search_args.list_ontologies:
                    table = u""
                    table += u"\n" + "-" * self.TTY_WIDTH + u"\n"
                    for ontology in utils.get_path(self.structured_response, ['_embedded', 'ontologies']):
                        c = ontology['config']
                        ont = [
                            u"Namespace: ".ljust(30) + unicode(c['namespace']),
                            u"Pref. prefix: ".ljust(30) + unicode(c['preferredPrefix']),
                            u"Title: ".ljust(30) + unicode(c['title']),
                            u"Description: ".ljust(30) + unicode(c['description']),
                            u"Homepage: ".ljust(30) + unicode(c['homepage']),
                            u"ID: ".ljust(30) + unicode(c['id']),
                            u"Version :".ljust(30) + unicode(c['version']),
                        ]
                        table += u"\n".join(ont)
                        table += u"\n" + "-" * self.TTY_WIDTH
                elif self.search_args.short_list_ontologies:
                    table += u"List of ontologies\n"
                    table += u"\n" + "-" * self.TTY_WIDTH + u"\n"
                    for ontology in utils.get_path(self.structured_response, ['_embedded', 'ontologies']):
                        c = ontology['config']
                        ont = [
                            unicode(c['namespace']).ljust(10),
                            u"-",
                            unicode(c['description'][:200]) if c['description'] else u'' + u"...",
                        ]
                        table += u"\t".join(ont) + u"\n"
            # list search results
            else:
                fields = [
                    TableField('index', key='index', width=6, is_index=True),
                    TableField('label', key='label', width=20),
                    TableField('short_form', key='short_form', width=20),
                    TableField('ontology_name', key='ontology_name', width=15),
                    TableField('description', key='description', width=50, is_iterable=True),
                    TableField('type', key='type', width=18),
                ]
                table = ResultsTable(self, fields=fields)
                # table += "=" * self.TTY_WIDTH + "\n"
                # table += "Search term: {}\n\n".format(self.search_args.search_term)
                # header = [
                #     "index".ljust(self.INDEX_WIDTH),
                #     "label".ljust(self.LABEL_WIDTH),
                #     "short_form".ljust(self.SHORT_FORM_WIDTH),
                #     "ontology_name".ljust(self.ONTOLOGY_NAME_WIDTH),
                #     "description/IRI".ljust(self.DESCRIPTION_WIDTH),
                #     "type".ljust(self.TYPE_WIDTH),
                # ]
                # table += "\t".join(header) + "\n"
                # table += "=" * self.TTY_WIDTH + "\n"
                #
                # start = self.search_args.start
                #
                # for e in self.results:
                #     if e.has_key('description'):
                #         wrapped_description = textwrap.wrap(e['description'][0] + " /{}".format(e['iri']),
                #                                             self.DESCRIPTION_WIDTH)
                #         if len(wrapped_description) == 1:
                #             row = [
                #                 str(start).ljust(self.INDEX_WIDTH),
                #                 e['label'].ljust(self.LABEL_WIDTH),
                #                 e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                #                     self.SHORT_FORM_WIDTH),
                #                 e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                #                 wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                #                 e['type'].ljust(self.TYPE_WIDTH),
                #             ]
                #             table += "\t".join(row) + "\n"
                #         else:
                #             row = [
                #                 str(start).ljust(self.INDEX_WIDTH),
                #                 e['label'].ljust(self.LABEL_WIDTH),
                #                 e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                #                     self.SHORT_FORM_WIDTH),
                #                 e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                #                 wrapped_description[0].ljust(self.DESCRIPTION_WIDTH),
                #                 e['type'].ljust(self.TYPE_WIDTH),
                #             ]
                #             table += "\t".join(row) + "\n"
                #             for i in xrange(1, len(wrapped_description)):
                #                 row = [
                #                     ''.ljust(self.INDEX_WIDTH),
                #                     ''.ljust(self.LABEL_WIDTH),
                #                     ''.ljust(self.SHORT_FORM_WIDTH),
                #                     ''.ljust(self.ONTOLOGY_NAME_WIDTH),
                #                     wrapped_description[i].ljust(self.DESCRIPTION_WIDTH),
                #                     ''.ljust(self.TYPE_WIDTH),
                #                 ]
                #                 table += "\t".join(row) + "\n"
                #     else:
                #         row = [
                #             str(start).ljust(self.INDEX_WIDTH),
                #             e['label'].ljust(self.LABEL_WIDTH),
                #             e['short_form'].ljust(self.SHORT_FORM_WIDTH) if e.has_key('short_form') else '-'.ljust(
                #                 self.SHORT_FORM_WIDTH),
                #             e['ontology_name'].ljust(self.ONTOLOGY_NAME_WIDTH),
                #             "{}".format(e['iri']).ljust(self.DESCRIPTION_WIDTH),
                #             e['type'].ljust(self.TYPE_WIDTH),
                #         ]
                #         table += "\t".join(row) + "\n"
                #
                #     table += "-" * self.TTY_WIDTH + "\n"
                #     start += 1
                #
                # if len(self):
                #     table += "Showing: {} to {} of {} results found".format(
                #         self.search_args.start,
                #         min(len(self), self.search_args.start + self.search_args.rows - 1),
                #         len(self),
                #     )
                # else:
                #     table += "No results found."
        elif self._resource.name == 'EMDB':
            fields = [
                TableField('index', key='index', width=6, is_index=True),
                TableField('title', key='Title', width=80),
                TableField('entry_id', key='EntryID', width=30),
            ]
            table = ResultsTable(self, fields=fields)
        elif self._resource.name == "UniProt":
            fields = [
                TableField('index', width=6, is_index=True),
                TableField('id', key='id', width=10),
                TableField('name', key='name', width=30),
                TableField('proteins', key='proteins', width=50),
                TableField('organism', key='organism', width=40),
            ]
            table = ResultsTable(self, fields=fields)
        elif self._resource.name == "PDB":
            fields = [
                TableField('index', width=6, is_index=True),
                TableField('description', key='organism_scientific_name', width=20, is_iterable=True),
                TableField('pdb_id', key='pdb_id', width=6),
                TableField('title', key='title', width=20),
            ]
            table = ResultsTable(self, fields=fields)
        return table

    #     def __len__(self):
    #         return self._result_list
    def __repr__(self):
        pass

    #         return "SearchResult object containing {} result(s)".format(len(self))
    def __len__(self):
        if self._resource.result_count is not None:
            return utils.get_path(self._structured_response, self._resource.result_count)
        else:
            return 0
