#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.find

Search for terms and display ontologies
"""
from __future__ import division, print_function

import math
import os
import sys
import textwrap

from backports.shutil_get_terminal_size import get_terminal_size

from . import RESOURCE_LIST
from ..core import utils
from ..core.print_tools import print_date

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


JUSTIFY = ['left', 'right', 'center']


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
    def __init__(self, name, key=None, text=None, width=20, pc=None, justify='left', format=None, is_index=False,
                 is_iterable=False, position_in_iterable=0):
        """A single field (column) in a table

        :param str name: the name of the field that will appear in header; can be any object that implements __str__
        :param str key: the key to use to extract the value for the field; if this is not defined then the value of
        name is used instead
        :param str text: a substitute for key; fixed text to appear in this field for all rows
        :param int width: a positive integer for the width of this field
        :param float pc: percentage width of the terminal occupied by this field
        :param str justify: 'left' (default), 'right' or 'center'; how to align text in the field
        :param str format: a format string with one pair of empty braces to construct a string for each row
        :param bool is_index: if true then this field will be an index (numeric value) for the row
        :param bool is_iterable: if true then the value obtained using key will be from a list and position_in_iterable
        index will be retrieved from the iterable
        :param int position_in_iterable: if is_iterable is true then the value for this field will be retrieved from the
         specified index in the iterable value
        """
        # check mutex nature of key and text
        try:
            assert key is None or text is None
        except AssertionError:
            raise ValueError('key and text are mutually exclusive; only define one or none of them')
            sys.exit(os.EX_DATAERR)
        # check valid type for width
        try:
            assert isinstance(width, int) or isinstance(width, long)
        except AssertionError:
            raise ValueError('field width must be int or long')
            sys.exit(os.EX_DATAERR)
        # check valid value for width
        try:
            assert width > 0
        except AssertionError:
            raise ValueError('field width must be greater than 0')
            sys.exit(os.EX_DATAERR)
        # ensure pc is valid type
        try:
            assert isinstance(pc, int) or isinstance(pc, long) or isinstance(pc, float) or pc is None
        except AssertionError:
            raise ValueError('invalid type for pc (percentage): {}'.format(type(pc)))
            sys.exit(os.EX_DATAERR)
        # ensure pc is a valid value
        try:
            assert 0 < pc < 100 or pc is None
        except AssertionError:
            raise ValueError('invalid value for pc (percentage): {}'.format(pc))
            sys.exit(os.EX_DATAERR)
        # check valid values for justify
        try:
            assert justify in JUSTIFY
        except AssertionError:
            raise ValueError("invalid value for kwarg justify: {}; should be {}".format(
                justify,
                ', '.join(JUSTIFY),
            ))
        # check valid value for format
        try:
            assert format is None or format.find("{}") >= 0
        except AssertionError:
            raise ValueError(
                "invalid value for format: {}; it should be either None or have one and only one pair of braces".format(
                    format,
                ))
        # check valid type for position_in_iterable
        try:
            assert isinstance(position_in_iterable, int) or isinstance(position_in_iterable, long)
        except AssertionError:
            raise ValueError('field position_in_iterable must be int or long')
            sys.exit(os.EX_DATAERR)
        # check valid value for position_in_iterable
        try:
            assert position_in_iterable >= 0
        except AssertionError:
            raise ValueError('field position_in_iterable must be greater or equal than 0')
            sys.exit(os.EX_DATAERR)
        self._name = str(name)
        if key is None and text is None:
            self._key = name
        else:
            self._key = key
        self._text = text
        self._width = width
        self._pc = pc
        self._format = format
        self._justify = justify
        self._is_index = is_index
        self._is_iterable = is_iterable
        self._position_in_iterable = position_in_iterable

    def justify(self, text):
        if self._justify == 'left':
            return text.ljust(self._width)
        elif self._justify == 'right':
            return text.rjust(self._width)
        elif self._justify == 'center':
            return text.center(self._width)

    def __unicode__(self):
        # todo: other justifications
        return self.justify(self._name)

    @property
    def is_index(self):
        return self._is_index

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        try:
            assert isinstance(width, int) or isinstance(width, long)
        except AssertionError:
            raise ValueError('width must be an int or long')
            sys.exit(os.EX_DATAERR)
        self._width = width

    @property
    def pc(self):
        return self._pc

    def render(self, row_data, index):
        if self.is_index:
            text = unicode(index)
        elif self._key is not None:
            try:
                if self._is_iterable:
                    text = row_data[self._key][self._position_in_iterable]
                else:
                    text = row_data[self._key]
            except KeyError:
                text = u'-'
        elif self._text is not None:
            text = self._text
        # format
        if self._format is not None:
            wrapped_text = textwrap.wrap(self._format.format(text), self._width)
        else:
            wrapped_text = textwrap.wrap(text, self._width)
        if not wrapped_text:  # empty list for empty string
            return [self.justify(u'')]
        else:
            return map(self.justify, wrapped_text)


class Table(object):
    """Table superclass"""
    column_separator = u" | "
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
            # don't add an extra row separator to the last line
            if i == no_lines - 1:
                string += self.column_separator.join(row)
            else:
                string += self.column_separator.join(row) + self.row_separator
        return string


class ResultsTable(Table):
    """Class that formats search results as a table"""

    def __init__(self, search_results, fields, width='auto', *args, **kwargs):
        """Initialise a ResultsTable object by specifying results and fields

        :param search_results: a SearchResults object
        :type search_results: SearchResults
        :param list fields: a list of TableField objects
        :param int width: a non-negative integer
        """
        # check the type of search_results
        try:
            assert isinstance(search_results, SearchResults)
        except AssertionError:
            raise ValueError('search_results must be a SearchResults object')
            sys.exit(os.EX_DATAERR)
        # ensure that we have at least one field
        try:
            assert fields  # nice! an empty list asserts to False
        except AssertionError:
            raise ValueError('fields kwarg should not be empty')
            sys.exit(os.EX_DATAERR)
        # ensure that the fields kwarg is populated with TableField objects
        try:
            assert all(map(lambda f: isinstance(f, TableField), fields))
        except AssertionError:
            raise ValueError('non-TableField object in iterable fields')
            sys.exit(os.EX_DATAERR)
        # check valid type for width
        try:
            assert isinstance(width, int) or isinstance(width, long) or width == 'auto'
        except AssertionError:
            raise ValueError("field width must be instance of int or long or the string 'auto'")
            sys.exit(os.EX_DATAERR)
        # check valid value for width
        try:
            assert width > 0 or width == 'auto'
        except AssertionError:
            raise ValueError("field width must be greater than 0 or the string 'auto'")
            sys.exit(os.EX_DATAERR)
        # only one index field per table
        try:
            assert len(filter(lambda f: f.is_index, fields)) <= 1
        except AssertionError:
            raise ValueError(
                'there is more than one field with is_index=True set; only one index field per table supported')
            sys.exit(os.EX_DATAERR)
        super(ResultsTable, self).__init__(*args, **kwargs)
        self._search_results = search_results
        if width == 'auto':
            terminal_size = get_terminal_size((200, 80))  # fallback values
            self._width = terminal_size.columns
        else:
            self._width = width
        self._fields = self._evaluate_widths(fields)
        # ensure width is less than the sum of fields
        total_width = sum([f.width for f in fields])
        try:
            assert total_width < self._width
        except AssertionError:
            print_date(
                'total field widths greater than table width; distortion will occur: table width={}; total field width={}'.format(
                    self._width,
                    total_width,
                ))

    def _evaluate_widths(self, fields):
        """Convert percentage widths into fixed widths

        :param list fields: list of TableField objects
        :return list _fields: list of TableField objects
        """
        _fields = list()
        # we calculate the field's width by taking into account the column separator
        inter_column_distance = len(fields) * len(self.column_separator)
        # subtract the inter-column distance from the screen width
        reduced_width = self._width - inter_column_distance
        for field in fields:
            if field.pc is not None:
                # the field's width is now...
                field.width = int(math.floor(reduced_width * field.pc / 100))
            _fields.append(field)
        return _fields

    @property
    def header(self):
        header = u"=" * self._width + self.row_separator
        header += u"Search term: {}{}{}".format(
            self._search_results.search_args.search_term,
            self.row_separator,
            self.row_separator,
        )
        # _fields = list()
        # for f in self._fields:
        #     _f_unicode = unicode(f)
        #     if len(_f_unicode) > f.width:
        #         f_unicode = _f_unicode[:f.width]
        #     else:
        #         f_unicode = _f_unicode
        #     _fields.append(f_unicode)
        # header += self.column_separator.join(_fields) + self.row_separator
        header += self.column_separator.join(map(lambda f: unicode(f)[:f.width], self._fields)) + self.row_separator
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
                    TableField('index', key='index', pc=5, is_index=True, justify='right'),
                    TableField('label', key='label', pc=10),
                    TableField('short_form', key='short_form', pc=10, justify='center'),
                    TableField('resource', key='ontology_name', pc=5, justify='center'),
                    TableField('description', key='description', pc=40, is_iterable=True),
                    TableField('iri', key='iri', pc=30),
                ]
                table = ResultsTable(self, fields=fields)
        elif self._resource.name == 'EMDB':
            fields = [
                TableField('index', key='index', pc=5, is_index=True, justify='right'),
                TableField('label', text=self._resource.search_args.search_term, pc=10),
                TableField('short_form', key='EntryID', pc=10, format='EMD-{}'),
                TableField('resource', text='EMDB', pc=5),
                TableField('description', key='Title', pc=40),
                TableField('iri', key='EntryID', format='https://www.ebi.ac.uk/pdbe/emdb/EMD-{}', pc=30),
            ]
            table = ResultsTable(self, fields=fields)
        elif self._resource.name == "UniProt":
            fields = [
                TableField('index', pc=5, is_index=True, justify='right'),
                TableField('label', key='name', pc=10),
                TableField('short_form', key='id', pc=10),
                TableField('resource', text='UniProt', pc=5),
                TableField('description', key='proteins', pc=40),
                # TableField('organism', key='organism', width=40),
                TableField('iri', key='id', format='https://www.uniprot.org/uniprot/{}', pc=30),
            ]
            table = ResultsTable(self, fields=fields)
        elif self._resource.name == "PDB":
            fields = [
                TableField('index', pc=5, is_index=True, justify='right'),
                TableField('label', text=self._resource.search_args.search_term, pc=10),
                TableField('short_form', key='pdb_id', pc=10),
                TableField('resource', text='PDB', pc=5),
                # TableField('title', key='organism_scientific_name', pc=20, is_iterable=True),
                TableField('description', key='title', pc=40),
                TableField('iri', key='pdb_id', format='https://www.ebi.ac.uk/pdbe/entry/pdb/{}', pc=30),
            ]
            table = ResultsTable(self, fields=fields)
        return table

    def __repr__(self):
        pass

    def __len__(self):
        if self._resource.result_count is not None:
            return utils.get_path(self._structured_response, self._resource.result_count)
        else:
            return 0
