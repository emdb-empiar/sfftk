# -*- coding: utf-8 -*-
# parser.py
"""Parses command-line options"""

import argparse
import os
import sys
from copy import deepcopy

from .print_tools import print_date
from ..notes import RESOURCE_LIST

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-06-10'
__updated__ = '2018-02-14'

verbosity_range = range(4)


def add_args(parser, the_arg):
    """Convenience function to add ``the_arg`` to the ``parser``.

    This relies on the argument being structured as a dictionary with the keys 
    ``args`` for positional arguments and ``kwargs`` for the keyword
    arguments. The value of doing this is that arguments that are reused
    in several parsers can be referred to by a variable instead of being 
    redefined. 

    Usage::

    >>> my_arg = {'arg': ['-x'], 'kwargs': {'help': 'help'}}
    >>> this_parser = argparse.ArgumentParser()
    >>> add_args(this_parser, my_arg)

    :param parser: a parser
    :type parser: ``argparse.Parser``
    :param dict the_arg: the argument specified as a dict with keys 'args' and 'kwargs'
    :return parser: a parser
    :rtype parser: ``argparse.Parser``
    """
    return parser.add_argument(*the_arg['args'], **the_arg['kwargs'])


Parser = argparse.ArgumentParser(
    prog='sff', description="The EMDB-SFF Toolkit (sfftk)")

subparsers = Parser.add_subparsers(
    title='Tools',
    dest='subcommand',
    description='The EMDB-SFF Toolkit (sfftk) provides the following tools:',
    metavar="EMDB-SFF tools"
)

# =========================================================================
# common arguments
# =========================================================================
sff_file = {
    'args': ['sff_file'],
    'kwargs': {
        'help': 'path (rel/abs) to an EMDB-SFF file',
    }
}
complexes = {
    'args': ['-C', '--complexes'],
    'kwargs': {
        'help': "PDBe accession for complexes separated by commas without spaces \
between e.g. 'comp1,comp2,...,compN'",
    }
}
complex_id = {
    'args': ['-c', '--complex-id'],
    'kwargs': {
        'type': int,
        'help': "the complex ID as shown with the 'list' command",
    }
}
description = {
    'args': ['-D', '--description'],
    'kwargs': {
        'help': 'the description'
    }
}
details = {
    'args': ['-d', '--details'],
    'kwargs': {
        'default': "",
        'help': "populates <details>...</details> in the XML file [default: '']"
    }
}
external_ref_id = {
    'args': ['-e', '--external-ref-id'],
    'kwargs': {
        'type': int,
        'help': "the external reference ID as shown with the 'list' command",
    }
}
external_ref = {
    'args': ['-E', '--external-ref'],
    'kwargs': {
        'nargs': 3,
        'help': """An external reference consists of three components: the 
name of the external reference, a URL to the particular external reference 
and the accession. If you use the sff notes search utility these will 
correspond to the ontology_name, IRI and short_form. The following is a list 
of valid external references: {}. You can also specify multiple external 
reference arguments e.g. sff notes add -i <int> -E r11 r12 r13 -E r21 r22 r23 
file.json""".format(', '.join(RESOURCE_LIST.keys())),
    }
}
file_path = {
    'args': ['-F', '--file-path'],
    'kwargs': {
        'default': None,
        'help': "file path [default: '.']"
    }
}
FORMAT_LIST = [
    ('sff', 'XML'),
    ('hff', 'HDF5'),
    ('json', 'JSON'),
]
format_ = {
    'args': ['-f', '--format'],
    'kwargs': {
        'default': 'sff',
        'help': "output file format; valid options are: {} [default: sff]".format(
            ", ".join(map(lambda x: "{} ({})".format(x[0], x[1]), FORMAT_LIST))
        ),
    }
}
header = {
    'args': ['-H', '--header'],
    'kwargs': {
        'default': False,
        'action': 'store_true',
        'help': 'show EMDB-SFF header (global) attributes [default: False]'
    }
}
segment_id = {
    'args': ['-i', '--segment-id'],
    'kwargs': {
        'help': 'refer to a segment by its ID'
    }
}
macromolecules = {
    'args': ['-M', '--macromolecules'],
    'kwargs': {
        'help': "PDBe accession for macromolecules separated by commas without \
spaces between e.g. 'macr1,macr2,...,macrN'",
    }
}
macromolecule_id = {
    'args': ['-m', '--macromolecule-id'],
    'kwargs': {
        'type': int,
        'help': "the macromolecule ID as shown with the 'list' command",
    }
}
name = {
    'args': ['-N', '--name'],
    'kwargs': {
        'default': None,
        'help': "the segmentation name [default: '']"
    }
}
number_of_instances = {
    'args': ['-n', '--number-of-instances'],
    'kwargs': {
        'type': int,
        'help': 'the number of instances',
    }
}
output = {
    'args': ['-o', '--output'],
    'kwargs': {
        'default': None,
        'help': "file to convert to; the extension (.sff, .hff, .json) determines the output format [default: None]"
    }
}
primary_descriptor = {
    'args': ['-R', '--primary-descriptor'],
    'kwargs': {
        'help': "populates the <primaryDescriptor>...</primaryDescriptor> to this value [valid values:  threeDVolume, contourList, meshList, shapePrimitiveList]"
    }
}
software_proc_details = {
    'args': ['-P', '--software-processing-details'],
    'kwargs': {
        'default': None,
        'help': "details of how the segmentation was processed [default: None]"
    }
}
config_path = {
    'args': ['-p', '--config-path'],
    'kwargs': {
        'help': "path to configs file"
    }
}
software_name = {
    'args': ['-S', '--software-name'],
    'kwargs': {
        'default': None,
        'help': "the name of the software used to create the segmentation [default: None]"
    }
}
shipped_configs = {
    'args': ['-b', '--shipped-configs'],
    'kwargs': {
        'default': False,
        'action': 'store_true',
        'help': 'use shipped configs only if config path and user configs fail [default: False]'
    }
}
software_version = {
    'args': ['-V', '--software-version'],
    'kwargs': {
        'default': None,
        'help': "the version of software used to create the segmentation [default: None]"
    }
}
verbose = {
    'args': ['-v', '--verbose'],
    'kwargs': {
        'action': 'store_true',
        'default': False,
        'help': "verbose output"
    },
}

# =========================================================================
# convert subparser
# =========================================================================
convert_parser = subparsers.add_parser(
    'convert', description="Perform conversions to EMDB-SFF", help="converts from/to EMDB-SFF")
convert_parser.add_argument('from_file', help="file to convert from")
add_args(convert_parser, config_path)
add_args(convert_parser, shipped_configs)
convert_parser.add_argument('-t', '--top-level-only', default=False,
                            action='store_true', help="convert only the top-level segments [default: False]")
# convert_parser.add_argument('-M', '--contours-to-mesh', default=False, action='store_true', help="convert an 'contourList' EMDB-SFF to a 'meshList' EMDB-SFF")
convert_parser.add_argument(*details['args'], **details['kwargs'])
convert_parser.add_argument(
    *primary_descriptor['args'], **primary_descriptor['kwargs'])
convert_parser.add_argument(*verbose['args'], **verbose['kwargs'])
convert_parser.add_argument('-s', '--sub-tomogram-average', nargs=2,
                            help="convert a subtomogram average into an EMDB-SFF file; two arguments are required: the table file and volume file (in that order)")
group = convert_parser.add_mutually_exclusive_group()
group.add_argument(*output['args'], **output['kwargs'])
group.add_argument(*format_['args'], **format_['kwargs'])

# =========================================================================
# config subparser
# =========================================================================
config_parser = subparsers.add_parser(
    'config',
    description="Configuration utility",
    help="manage sfftk configs"
)

config_subparsers = config_parser.add_subparsers(
    title='sfftk configurations',
    dest='config_subcommand',
    description='Persistent configurations utility',
    metavar='Commands:'
)

# =============================================================================
# config: list
# =============================================================================
list_configs_parser = config_subparsers.add_parser(
    'list',
    description='List sfftk configuration parameters',
    help='list sfftk configs'
)
add_args(list_configs_parser, config_path)
add_args(list_configs_parser, shipped_configs)

# =============================================================================
# config: get
# =============================================================================
get_configs_parser = config_subparsers.add_parser(
    'get',
    description='Get the value of a single configuration parameter',
    help='get single sfftk config'
)
get_configs_parser.add_argument(
    'name', help="the name of the argument to retrieve"
)
add_args(get_configs_parser, config_path)
add_args(get_configs_parser, shipped_configs)

# =============================================================================
# config: set
# =============================================================================
set_configs_parser = config_subparsers.add_parser(
    'set',
    description='Set the value of a single configuration parameter',
    help='set single sfftk config'
)
set_configs_parser.add_argument(
    'name', help="the name of the argument to set",
)
set_configs_parser.add_argument(
    'value', help="the value of the argument to set",
)
add_args(set_configs_parser, config_path)
add_args(set_configs_parser, shipped_configs)

# =============================================================================
# config: del
# =============================================================================
del_configs_parser = config_subparsers.add_parser(
    'del',
    description='Delete the named configuration parameter',
    help='delete single sfftk config'
)
del_configs_parser.add_argument(
    'name', help="the name of the argument to be deleted"
)
add_args(del_configs_parser, config_path)
add_args(del_configs_parser, shipped_configs)

# =============================================================================
# config: clear
# =============================================================================
clear_configs_parser = config_subparsers.add_parser(
    'clear',
    description='Clear all configuration parameters',
    help='clear all sfftk configs'
)
add_args(clear_configs_parser, config_path)
add_args(clear_configs_parser, shipped_configs)

# =========================================================================
# view subparser
# =========================================================================
view_parser = subparsers.add_parser(
    'view', description="View a summary of an SFF file", help="view file summary")
view_parser.add_argument('from_file', help="any SFF file")
add_args(view_parser, config_path)
add_args(view_parser, shipped_configs)
view_parser.add_argument(
    '-V', '--version', action='store_true', help="show SFF format version")
view_parser.add_argument('-C', '--show-chunks', action='store_true',
                         help="show sequence of chunks in IMOD file; only works with IMOD model files (.mod) [default: False]")
view_parser.add_argument(*verbose['args'], **verbose['kwargs'])

# =============================================================================
# notes parser
# =============================================================================
notes_parser = subparsers.add_parser(
    'notes',
    description="The EMDB-SFF Annotation Toolkit",
    help="annotate an EMDB-SFF file",
)

notes_subparsers = notes_parser.add_subparsers(
    title='Annotation tools',
    dest='notes_subcommand',
    description='The EMDB-SFF Annotation Toolkit provides the following tools:',
    metavar="EMDB-SFF annotation tools",
)

# =========================================================================
# notes: search
# =========================================================================
search_notes_parser = notes_subparsers.add_parser(
    'search',
    description="Search ontologies for annotation by text labels",
    help="search for terms by labels",
)
# todo: how to make search_term optional for -l/-L?
search_notes_parser.add_argument(
    'search_term', help="the term to search; add quotes if spaces are included")
add_args(search_notes_parser, config_path)
add_args(search_notes_parser, shipped_configs)
search_notes_parser.add_argument(
    '-R', '--resource', default=RESOURCE_LIST.keys()[0], choices=RESOURCE_LIST.keys(),
    help='the resource to search for terms or accessions; other valid options are {resources} [default: {default}]'.format(
        resources=RESOURCE_LIST.keys(),
        default=RESOURCE_LIST.keys()[0],
    )
)
search_notes_parser.add_argument(
    '-s', '--start', type=int, default=1, help="start index [default: 1]"
)
search_notes_parser.add_argument(
    '-r', '--rows', type=int, default=10, help="number of rows [default: 10]"
)
ols_parser = search_notes_parser.add_argument_group(
    title='EBI Ontology Lookup Service (OLS)',
    description='The Ontology Lookup Service (OLS) is a repository for biomedical ontologies that aims to provide a '
                'single point of access to the latest ontology versions. Searching against OLS can use the following '
                'options:'
)
ols_parser.add_argument(
    '-O', '--ontology', default=None, help="the ontology to search [default: None]")
ols_parser.add_argument(
    '-x', '--exact', default=False, action='store_true', help="exact matches? [default: False]")
ols_parser.add_argument(
    '-o', '--obsoletes', default=False, action='store_true', help="include obsoletes? [default: False]")
ols_parser.add_argument(
    '-L', '--list-ontologies', default=False,
    action='store_true', help="list available ontologies [default: False]"
)
ols_parser.add_argument(
    '-l', '--short-list-ontologies', default=False,
    action='store_true', help="short list of available ontologies [default: False]"
)

# todo: add resource-specific argument groups
# emdb_parser = search_notes_parser.add_argument_group(
#     title='The Electron Microscopy Data Bank (EMDB)',
#     description='The Electron Microscopy Data Bank (EMDB) is a public repository for electron microscopy density maps '
#                 'of macromolecular complexes and subcellular structures. Searching against EMDB can use the following '
#                 'options:'
# )
# uniprot_parser = search_notes_parser.add_argument_group(
#     title='The Universal Protein Resource (UniProt)',
#     description='The Universal Protein Resource (UniProt) is a comprehensive resource for protein sequence and '
#                 'annotation data. Searching against UniProt can use the following options:'
# )
# pdb_parser = search_notes_parser.add_argument_group(
#     title='The Protein Data Bank archive (PDB)',
#     description='Since 1971, the Protein Data Bank archive (PDB) has served as the single repository of information '
#                 'about the 3D structures of proteins, nucleic acids, and complex assemblies. Searching against EMDB '
#                 'can use the following options:'
# )

# =========================================================================
# notes: suggest
# =========================================================================
# todo: suggest terms from a description
# TBA

# =========================================================================
# notes: list
# =========================================================================
list_notes_parser = notes_subparsers.add_parser(
    'list',
    description="List all available annotations present in an EMDB-SFF file",
    help="list available annotations",
)
add_args(list_notes_parser, sff_file)
add_args(list_notes_parser, header)
add_args(list_notes_parser, config_path)
add_args(list_notes_parser, shipped_configs)
long_format = {
    'args': ['-l', '--long-format'],
    'kwargs': {
        'default': False,
        'action': 'store_true',
        'help': "only show segment ID and description (if present) [default: False]"
    }
}
add_args(list_notes_parser, long_format)
list_notes_parser.add_argument('-D', '--sort-by-description', default=False,
                               action='store_true', help="sort listings by description [default: False (sorts by ID)]")
list_notes_parser.add_argument(
    '-r', '--reverse', default=False, action='store_true', help="reverse the sort order [default: False]")
list_notes_parser.add_argument('-I', '--list-ids', default=False, action='store_true',
                               help="only list the IDs for segments one per line [default: False]")
add_args(list_notes_parser, verbose)

# =========================================================================
# notes: show
# =========================================================================
show_notes_parser = notes_subparsers.add_parser(
    'show',
    description="Show a specific annotations by ID present in an EMDB-SFF file",
    help="show an annotation by ID",
)
add_args(show_notes_parser, sff_file)
add_args(show_notes_parser, config_path)
add_args(show_notes_parser, shipped_configs)
add_args(show_notes_parser, header)
add_args(show_notes_parser, long_format)
add_args(show_notes_parser, verbose)
show_segment_id = deepcopy(segment_id)
# todo: use nargs='+' instead of csv
show_segment_id['kwargs'][
    'help'] += "; pass more than one ID as a comma-separated list with no spaces e.g. 'id1,id2,...,idN'"
show_notes_parser.add_argument(
    *show_segment_id['args'], **show_segment_id['kwargs'])

# =========================================================================
# notes:add
# =========================================================================
add_notes_parser = notes_subparsers.add_parser(
    'add',
    description="Add a new annotation to an EMDB-SFF file",
    help="add new annotations",
)
# all notes refer to some sff file
add_args(add_notes_parser, sff_file)
add_args(add_notes_parser, config_path)
add_args(add_notes_parser, shipped_configs)
# external references apply to both
external_ref['kwargs']['action'] = 'append'
add_args(add_notes_parser, external_ref)
add_args(add_notes_parser, verbose)
del external_ref['kwargs']['action']
# global notes
add_global_notes_parser = add_notes_parser.add_argument_group(
    title="add global notes",
    description="add global attributes to an EMDB-SFF file"
)
add_args(add_global_notes_parser, name)
add_args(add_global_notes_parser, software_name)
add_args(add_global_notes_parser, software_version)
add_args(add_global_notes_parser, software_proc_details)
add_args(add_global_notes_parser, file_path)
add_args(add_global_notes_parser, details)
# segment notes
add_segment_notes_parser = add_notes_parser.add_argument_group(
    title="add segment notes",
    description="add attributes to a single segment in an EMDB-SFF file"
)
add_args(add_segment_notes_parser, segment_id)
add_args(add_segment_notes_parser, description)
add_args(add_segment_notes_parser, number_of_instances)
add_args(add_segment_notes_parser, complexes)
add_args(add_segment_notes_parser, macromolecules)

# =========================================================================
# notes: edit
# =========================================================================
edit_notes_parser = notes_subparsers.add_parser(
    'edit',
    description="Edit an existing annotation to an EMDB-SFF file",
    help="edit existing annotations",
)
add_args(edit_notes_parser, sff_file)
add_args(edit_notes_parser, config_path)
add_args(edit_notes_parser, shipped_configs)
add_args(edit_notes_parser, external_ref_id)
external_ref['kwargs']['action'] = 'append'
add_args(edit_notes_parser, external_ref)
del external_ref['kwargs']['action']
#  global notes
edit_global_notes_parser = edit_notes_parser.add_argument_group(
    title="edit global notes",
    description="edit global attributes to an EMDB-SFF file"
)
add_args(edit_global_notes_parser, name)
add_args(edit_global_notes_parser, software_name)
add_args(edit_global_notes_parser, software_version)
add_args(edit_global_notes_parser, software_proc_details)
add_args(edit_global_notes_parser, file_path)
add_args(edit_global_notes_parser, details)
# segment notes
edit_segment_notes_parser = edit_notes_parser.add_argument_group(
    title="edit segment notes",
    description="edit attributes to a single segment in an EMDB-SFF file"
)
add_args(edit_segment_notes_parser, segment_id)
add_args(edit_segment_notes_parser, description)
add_args(edit_segment_notes_parser, number_of_instances)
add_args(edit_segment_notes_parser, complex_id)
add_args(edit_segment_notes_parser, complexes)
add_args(edit_segment_notes_parser, macromolecule_id)
add_args(edit_segment_notes_parser, macromolecules)

# =========================================================================
# notes: del
# =========================================================================
del_notes_parser = notes_subparsers.add_parser(
    'del',
    description="Delete an existing annotation to an EMDB-SFF file",
    help="delete existing annotations",
)
add_args(del_notes_parser, sff_file)
add_args(del_notes_parser, config_path)
add_args(del_notes_parser, shipped_configs)
add_args(del_notes_parser, external_ref_id)
# global notes
del_global_notes_parser = del_notes_parser.add_argument_group(
    title="delete global notes",
    description="delete global attributes to an EMDB-SFF file"
)
name['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the name [default: False]',
}
add_args(del_global_notes_parser, name)
software_name['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software name [default: False]'
}
add_args(del_global_notes_parser, software_name)
software_version['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software version [default: False]'
}
add_args(del_global_notes_parser, software_version)
software_proc_details['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software processing details [default: False]'
}
add_args(del_global_notes_parser, software_proc_details)
file_path['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the file path [default: False]'
}
add_args(del_global_notes_parser, file_path)
details['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the details [default: False]'
}
add_args(del_global_notes_parser, details)
# segment notes
del_segment_notes_parser = del_notes_parser.add_argument_group(
    title="delete segment notes",
    description="delete attributes to a single segment in an EMDB-SFF file"
)
add_args(del_segment_notes_parser, segment_id)
description['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the description [default: False]',
}
add_args(del_segment_notes_parser, description)
del number_of_instances['kwargs']['type']
number_of_instances['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the number of instances [default: False]',
}
add_args(del_segment_notes_parser, number_of_instances)
add_args(del_segment_notes_parser, complex_id)
add_args(del_segment_notes_parser, macromolecule_id)

# =============================================================================
# notes: copy
# =============================================================================
copy_notes_parser = notes_subparsers.add_parser(
    'copy',
    description="Copy notes from one/multiple segment to one/multiple/all other segments within the same EMDB-SFF file",
    help="copy notes across segments within the same EMDB-SFF file"
)
add_args(copy_notes_parser, sff_file)
add_args(copy_notes_parser, config_path)
add_args(copy_notes_parser, shipped_configs)
# todo: merge with segment_id above
copy_notes_parser.add_argument(
    '-i', '--segment-id',
    help="segment ID or a comma-separated sequence of segment IDs of source segment(s); run 'sff notes list <file>' for a list of "
         "segment IDs",
)
copy_global_notes_parse = copy_notes_parser.add_mutually_exclusive_group()
copy_global_notes_parse.add_argument(
    '--from-global',
    action='store_true',
    default=False,
    help="copy notes from global (metadata) to --to-segment segments"
)
copy_global_notes_parse.add_argument(
    '--to-global',
    action='store_true',
    default=False,
    help="copy notes from --segment-id segment to global (metadata)"
)
to_segment_or_all_copy_notes_parser = copy_notes_parser.add_mutually_exclusive_group()
to_segment_or_all_copy_notes_parser.add_argument(
    '-t', '--to-segment',
    help="segment ID or a comma-separated sequence of segment IDs of destination segment(s); run 'sff notes list <file>' for a list of "
         "segment IDs",
)
to_segment_or_all_copy_notes_parser.add_argument(
    '--to-all',
    action='store_true',
    default=False,
    help="copy notes from --segment-id segment to all (other) segments"
)

# =============================================================================
# notes: clear
# =============================================================================
clear_notes_parser = notes_subparsers.add_parser(
    'clear',
    description="Clear all notes for one or more segments in an EMDB-SFF file",
    help="clear notes in an EMDB-SFF file"
)
add_args(clear_notes_parser, config_path)
add_args(clear_notes_parser, shipped_configs)
add_args(clear_notes_parser, sff_file)
clear_notes_parser.add_argument(
    '--all',
    action='store_true',
    default=False,
    help="clear all notes; USE WITH CARE!"
)
clear_notes_parser.add_argument(
    '--from-global',
    action='store_true',
    default=False,
    help="clear notes from global (metadata)"
)
from_segment_or_all_clear_notes_parser = clear_notes_parser.add_mutually_exclusive_group()
from_segment_or_all_clear_notes_parser.add_argument(
    '-i', '--segment-id',
    help="segment ID or a comma-separated sequence of segment IDs of source segment(s); run 'sff notes list <file>' for a list of "
         "segment IDs",
)
from_segment_or_all_clear_notes_parser.add_argument(
    '--from-all-segments',
    action='store_true',
    default=False,
    help="clear notes from all segments"
)


# =============================================================================
# notes: merge
# =============================================================================
merge_notes_parser = notes_subparsers.add_parser(
    'merge',
    description="Merge notes from two EMDB-SFF files",
    help="merge notes from two EMDB-SFF files"
)
add_args(merge_notes_parser, config_path)
add_args(merge_notes_parser, shipped_configs)
merge_notes_parser.add_argument('--source', help="EMDB-SFF file from which to obtain notes", required=True)
merge_notes_parser.add_argument('other',
                                help="EMDB-SFF file whose content will be merged with notes from the file specified with --source")
output['kwargs'][
    'help'] = "file to convert to; the extension (.sff, .hff, .json) determines the output format; if not specified then NOTES IN OTHER ONLY will be overwritten [default: None]"
merge_notes_parser.add_argument(*output['args'], **output['kwargs'])
merge_notes_parser.add_argument(*verbose['args'], **verbose['kwargs'])

# =========================================================================
# notes: save
# =========================================================================
save_notes_parser = notes_subparsers.add_parser(
    'save',
    description="Save all changes made to the actual file",
    help="write all changes made until the last 'save' action"
)
save_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
add_args(save_notes_parser, config_path)
add_args(save_notes_parser, shipped_configs)

# =========================================================================
# notes: trash
# =========================================================================
trash_notes_parser = notes_subparsers.add_parser(
    'trash',
    description="Discard all notes by deleting the temporary file",
    help="discard all changes made since the last the edit action (add, edit, del)",
)
trash_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
add_args(trash_notes_parser, config_path)
add_args(trash_notes_parser, shipped_configs)

# get the full list of tools from the Parser object
# tool_list = Parser._actions[1].choices.keys()
# print tool_list
tool_list = ['core', 'formats', 'notes', 'readers', 'schema', 'main']

# tests
test_help = "one or none of the following: {}".format(", ".join(tool_list))
tests_parser = subparsers.add_parser(
    'tests', description="Run unit tests", help="run unit tests")
tests_parser.add_argument('tool', nargs='*', default='all', help=test_help)
add_args(tests_parser, config_path)
add_args(tests_parser, shipped_configs)
tests_parser.add_argument('-v', '--verbosity', default=1, type=int,
                          help="set verbosity; valid values: %s [default: 0]" % ", ".join(map(str, verbosity_range)))


# test_parser = subparsers.add_parser('test', description="Run unit tests", help="run unit tests")
# test_parser.add_argument('tool', nargs='*', default='all', help=test_help)
# add_args(test_parser, config_path)
# test_parser.add_argument('-v', '--verbosity', default=1, type=int, help="set verbosity; valid values: %s [default: 0]" % ", ".join(map(str, verbosity_range)))

# parser function


def parse_args(_args):
    """
    Parse and check command-line arguments and also return configs.

    This function does all the heavy lifting in ensuring that commandline
    arguments are properly formatted and checked for sanity. It also 
    extracts configs from the config files.

    In this way command handlers (defined in ``sfftk/sff.py`` e.g. ``handle_convert(...)``)
    assume correct argument values and can concentrate on functionality.

    :param list _args: list of arguments
    :return: parsed arguments
    :rtype: ``argparse.Namespace``
    :return: config dict-like object
    :rtype: ``sfftk.core.configs.Config``
    """
    # if we have no subcommands then show the available tools
    if len(_args) == 0:
        Parser.print_help()
        sys.exit(0)
    # if we only have a subcommand then show that subcommand's help
    elif len(_args) == 1:
        if _args[0] == 'tests':
            pass
        elif _args[0] in Parser._actions[1].choices.keys():
            exec ('{}_parser.print_help()'.format(_args[0]))
            sys.exit(0)
    # if we have 'notes' as the subcommand and a sub-subcommand show the
    # options for that sub-subcommand
    elif len(_args) == 2:
        if _args[0] == 'notes':
            if _args[1] in Parser._actions[1].choices['notes']._actions[1].choices.keys():
                exec ('{}_notes_parser.print_help()'.format(_args[1]))
                sys.exit(0)
    # parse arguments
    args = Parser.parse_args(_args)
    from .configs import load_configs
    configs = load_configs(args)

    # check values
    # config
    if args.subcommand == 'config':
        # handle config-specific argument modifications here
        pass
    # convert
    elif args.subcommand == 'convert':
        try:
            assert os.path.exists(args.from_file)
        except AssertionError:
            print_date("File {} was not found".format(args.from_file))
            sys.exit(1)
        # set the output file
        if args.output is None:
            try:
                assert args.format in map(lambda x: x[0], FORMAT_LIST)
            except AssertionError:
                print_date("Invalid output format: {}; valid values are: {}".format(
                    args.format, ", ".join(map(lambda x: x[0], FORMAT_LIST))))
                return None, configs
            import re
            dirname = os.path.dirname(args.from_file)
            if args.format:
                fn = ".".join(os.path.basename(args.from_file).split(
                    '.')[:-1]) + '.{}'.format(args.format)
                args.__setattr__('output', os.path.join(dirname, fn))
            else:
                # convert file.sff to file.hff
                if re.match(r'.*\.sff$', args.from_file):
                    fn = ".".join(
                        os.path.basename(args.from_file).split('.')[:-1]) + '.hff'
                    args.__setattr__('output', os.path.join(dirname, fn))
                # convert file.hff to file.sff
                elif re.match(r'.*\.hff$', args.from_file):
                    fn = ".".join(
                        os.path.basename(args.from_file).split('.')[:-1]) + '.sff'
                    args.__setattr__('output', os.path.join(dirname, fn))
            if args.verbose:
                print_date("Setting output file to {}".format(args.output))

        # ensure valid primary_descriptor
        if args.primary_descriptor:
            try:
                assert args.primary_descriptor in [
                    'threeDVolume', 'contourList', 'meshList', 'shapePrimitive']
            except:
                if args.verbose:
                    print_date(
                        "Found invalid primary descriptor: {}".format(args.primary_descriptor))
                raise ValueError(
                    'Invalid value for primaryDescriptor: %s' % args.primary_descriptor)
            if args.verbose:
                print_date(
                    "Trying to setting primary descriptor to {}".format(args.primary_descriptor))

    # tests
    elif args.subcommand == 'tests':
        if isinstance(args.tool, list):
            for tool in args.tool:
                try:
                    assert tool in tool_list
                except AssertionError:
                    print >> sys.stderr, "Unknown tool: {}".format(tool)
                    print >> sys.stderr, "Available tools for test: {}".format(
                        ", ".join(tool_list))
        if args.verbosity:
            try:
                assert args.verbosity in range(4)
            except:
                raise ValueError("Verbosity should be in %s-%s: %s given" %
                                 (verbosity_range[0], verbosity_range[-1], args.verbosity))
    # notes
    elif args.subcommand == 'notes':
        # convenience: the user can use '@' to refer to an EMDB-SFF file whch is the previous
        # file that was edited ('add', 'edit', 'del')
        temp_file = configs['__TEMP_FILE']
        temp_file_ref = configs['__TEMP_FILE_REF']
        if args.notes_subcommand in ['list', 'show', 'add', 'edit', 'del', 'save', 'trash']:
            # find, view
            if args.notes_subcommand in ['list', 'show', 'search']:
                if args.sff_file == temp_file_ref:
                    if os.path.exists(temp_file):
                        args.sff_file = temp_file
                        if args.verbose:
                            print_date(
                                "\033[0;92m", incl_date=False, newline=False)
                            print_date(
                                "Working on temp file {}".format(temp_file), stream=sys.stdout)
                    else:
                        print_date("Temporary file {} does not exist. \
Try invoking an edit ('add', 'edit', 'del') action on a valid EMDB-SFF file.".format(temp_file), stream=sys.stdout)
                        return None, configs
                else:
                    if args.verbose:
                        print_date(
                            "Reading directly from {}".format(args.sff_file), stream=sys.stdout)
            # modify
            elif args.notes_subcommand in ['save']:
                try:
                    assert os.path.exists(args.sff_file)
                except AssertionError:
                    print_date(
                        "Save-to file {} not found.".format(args.sff_file))
                    return None, configs

        if args.notes_subcommand == "search":
            # ensure start is valid
            if args.start < 1:
                raise ValueError(
                    "Invalid start value: {}; should be greater than 1".format(args.start))

            # ensure rows is valid
            if args.rows < 1:
                raise ValueError(
                    "Invalid rows value: {}; should be greater than 1".format(args.rows))

        elif args.notes_subcommand == "show":
            if args.segment_id is not None:
                args.segment_id = map(int, args.segment_id.split(','))

        elif args.notes_subcommand == "add":
            # external ref consistency
            if args.external_ref:
                # todo: check this; doesn't seem right
                if len(args.external_ref) == 2 and isinstance(args.external_ref[0], str):
                    args.external_ref = [args.external_ref]

            if args.segment_id is not None:
                args.segment_id = map(int, args.segment_id.split(','))

                # ensure we have at least one item to add
                try:
                    assert (args.description is not None) or (args.number_of_instances is not None) or \
                           (args.external_ref is not None) or (args.complexes is not None) or \
                           (args.macromolecules is not None)
                except AssertionError:
                    print_date(
                        "Nothing specified to add. Use one or more of the following options:\n\t-D <description> \n\t-E <extrefType> <extrefValue> \n\t-C cmplx1,cmplx2,...,cmplxN \n\t-M macr1,macr2,...,macrN \n\t-n <int>")
                    return None, configs

                # replace the string in args.complexes with a list
                if args.complexes:
                    args.complexes = args.complexes.split(',')

                # ditto
                if args.macromolecules:
                    args.macromolecules = args.macromolecules.split(',')

        elif args.notes_subcommand == "edit":
            # external references can be added globally (header) or to a
            # segment
            if args.external_ref:
                try:
                    assert args.external_ref_id is not None
                except AssertionError:
                    print_date("Will not be able to edit an external reference without \
specifying an external reference ID. Run 'list' or 'show' to see available \
external reference IDs for {}".format(args.segment_id), stream=sys.stdout)
                    return None, configs

                # consistency of format
                # todo: check this; doesn't seem right
                if len(args.external_ref) == 0 and isinstance(args.external_ref[0], str):
                    args.external_ref = [args.external_ref]

            if args.segment_id is not None:
                args.segment_id = map(int, args.segment_id.split(','))

                # replace the string in args.complexes with a list
                if args.complexes:
                    args.complexes = args.complexes.split(',')

                # ditto
                if args.macromolecules:
                    args.macromolecules = args.macromolecules.split(',')

                if args.complexes:
                    try:
                        assert args.complex_id is not None
                    except AssertionError:
                        print_date("Will not be able to edit a complex without specifying \
    a complex ID. Run 'list' or 'show' to see available complex \
    IDs for {}".format(args.segment_id), stream=sys.stdout)
                        return None, configs

                if args.macromolecules:
                    try:
                        assert args.macromolecule_id is not None
                    except AssertionError:
                        print_date("Will not be able to edit a macromolecule without specifying\
    a macromolecule ID. Run 'list' or 'show' to see available \
    macromolecule IDs for {}".format(args.segment_id), stream=sys.stdout)
                        return None, configs

        elif args.notes_subcommand == "del":
            if args.segment_id is not None:
                try:
                    assert args.segment_id is not None
                except AssertionError:
                    print_date(
                        "Please specify a segment ID", stream=sys.stdout)
                    return None, configs

                args.segment_id = map(int, args.segment_id.split(','))

                # ensure we have at least one item to add
                assert args.description or args.number_of_instances or \
                       (args.external_ref_id is not None) or (args.complex_id is not None) or \
                       (args.macromolecule_id is not None)

        elif args.notes_subcommand == "copy":
            # convert from and to to lists of ints
            if args.segment_id is not None:
                from_segment = map(int, args.segment_id.split(','))
                if isinstance(from_segment, int):
                    args.segment_id = [from_segment]
                else:
                    args.segment_id = from_segment
            if args.to_segment is not None:
                to_segment = map(int, args.to_segment.split(','))
                if isinstance(to_segment, int):
                    args.to_segment = [to_segment]
                else:
                    args.to_segment = to_segment

            # enforced automatically by package
            # if args.to_segment is not None and args.all:
            #     raise ValueError("--to-segment and --all are mutually exclusive")
            #     sys.exit(os.EX_DATAERR)

            if args.segment_id is not None and args.to_segment is not None:
                from_set = set(args.segment_id)
                to_set = set(args.to_segment)
                common = from_set.intersection(to_set)
                if len(common) > 0:
                    raise ValueError(
                        "the following segment IDs appear in both --segment-id and --to-segment: {}".format(
                            " ".join(map(str, common))
                        ))
                    sys.exit(os.EX_DATAERR)

        elif args.notes_subcommand == "clear":
            # where to clear notes from
            if args.segment_id is not None:
                from_segment = map(int, args.segment_id.split(','))
                if isinstance(from_segment, int):
                    args.segment_id = [from_segment]
                else:
                    args.segment_id = from_segment
            elif args.all:
                args.from_global = True
                args.from_all_segments = True

        elif args.notes_subcommand == "merge":
            if args.output is None:
                args.output = args.other

    return args, configs
