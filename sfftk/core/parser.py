# -*- coding: utf-8 -*-
# parser.py
"""
``sfftk.core.parser``
===========================

A large number of functions in ``sfftk`` consume only two arguments: ``args``, which is the direct output of Python's :py:class:`argparse.ArgumentParser` and a ``configs`` dictionary, which consists of all persistent configs. This module extends the parser object :py:class:`sfftkrw.core.parser.Parser` as well as includes a :py:func:`sfftk.core.parser.parse_args` function which does sanity checking of all command line arguments.
"""
from __future__ import print_function

import argparse
import os
import re
import sys
from copy import deepcopy

from sfftkrw.core import _dict_iter_keys, _decode, _input, _str
# extend the sfftkrw Parser object
from sfftkrw.core.parser import Parser, subparsers, convert_parser, view_parser, add_args
from sfftkrw.core.print_tools import print_date

from ..notes import RESOURCE_LIST

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-06-10'
__updated__ = '2018-02-14'

verbosity_range = range(4)
multi_file_formats = ['stl', 'map', 'mrc', 'rec']
prepable_file_formats = ['mrc', 'map', 'rec']
rescalable_file_formats = ['stl']

Parser.description = u"The EMDB-SFF Toolkit (sfftk)"
# Parser = argparse.ArgumentParser(
#     prog='sff', description="The EMDB-SFF Toolkit (sfftk)")
# Parser.add_argument(
#     '-V', '--version',
#     action='store_true',
#     default=False,
#     help='show the sfftk version string and the supported EMDB-SFF version string',
# )

# subparsers = Parser.add_subparsers(
#     title='Tools',
#     dest='subcommand',
#     description='The EMDB-SFF Toolkit (sfftk) provides the following tools:',
#     metavar="EMDB-SFF tools"
# )

# =========================================================================
# common arguments
# =========================================================================
sff_file = {
    'args': ['sff_file'],
    'kwargs': {
        'help': 'path (rel/abs) to an EMDB-SFF file',
    }
}
description = {
    'args': ['-d', '--description'],
    'kwargs': {
        'help': 'the description'
    }
}
details = {
    'args': ['-D', '--details'],
    'kwargs': {
        'help': "populates <details>...</details> in the XML file"
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
correspond to the resource, url and accession. The following is a list 
of valid external references: {}. You can also specify multiple external 
reference arguments e.g. sff notes add -i <int> -E r11 r12 r13 -E r21 r22 r23 
file.json""".format(', '.join(_dict_iter_keys(RESOURCE_LIST))),
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
number_of_instances = {
    'args': ['-I', '--number-of-instances'],
    'kwargs': {
        'type': int,
        'help': 'the number of instances',
    }
}
segment_id = {
    'args': ['-i', '--segment-id'],
    'kwargs': {
        'help': 'refer to a segment by its ID'
    }
}
name = {
    'args': ['-N', '--name'],
    'kwargs': {
        'help': "the segmentation name"
    }
}
output = {
    'args': ['-o', '--output'],
    'kwargs': {
        'default': None,
        'help': "file to convert to; the extension (.sff, .hff, .json) determines the output format [default: None]"
    }
}
software_proc_details = {
    'args': ['-P', '--software-processing-details'],
    'kwargs': {
        'help': "details of how the segmentation was processed"
    }
}
config_path = {
    'args': ['-p', '--config-path'],
    'kwargs': {
        'help': "path to configs file"
    }
}
primary_descriptor = {
    'args': ['-R', '--primary-descriptor'],
    'kwargs': {
        'help': "populates the <primaryDescriptor>...</primaryDescriptor> to this value [valid values:  three_d_volume, mesh_list, shape_primitive_list]"
    }
}
software_name = {
    'args': ['-S', '--software-name'],
    'kwargs': {
        'help': "the name of the software used to create the segmentation"
    }
}
software_id = {
    'args': ['-s', '--software-id'],
    'kwargs': {
        'type': int,
        'help': "the software to edit",
    }
}
segment_name = {
    'args': ['-n', '--segment-name'],
    'kwargs': {
        'help': "the name of the segment"
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
    'args': ['-T', '--software-version'],
    'kwargs': {
        'help': "the version of software used to create the segmentation"
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
# prep subparser
# =========================================================================
prep_parser = subparsers.add_parser(
    'prep',
    description="Prepare a segmentation for conversion to EMDB-SFF",
    help="prepares a segmentation"
)
prep_subparsers = prep_parser.add_subparsers(
    title='Segmentation preparation utility',
    dest='prep_subcommand',
    description="The following commands provide a number of pre-processing steps for various segmentation file formats. "
                "Most only apply to one file type. See the help for each command by typing 'sff prep <command>'",
    metavar='Preparation steps:'
)
# =========================================================================
# prep: binmap
# =========================================================================
binmap_prep_parser = prep_subparsers.add_parser(
    'binmap',
    description='Bin the CCP4 file to reduce file size',
    help='bin a CCP4 map',
)
binmap_prep_parser.add_argument(
    'from_file', help='the name of the segmentation file'
)
add_args(binmap_prep_parser, config_path)
add_args(binmap_prep_parser, shipped_configs)
binmap_prep_parser.add_argument(
    '-m', '--mask-value',
    default=1, type=int,
    help='value to set to; all other voxels set to zero [default: 1]'
)
binmap_prep_parser.add_argument(
    '-o', '--output',
    default=None,
    help='output file name [default: <infile>_binned.<ext>]'
)
binmap_prep_parser.add_argument(
    '--overwrite',
    default=False,
    action='store_true',
    help='overwrite output file [default: False]'
)
binmap_prep_parser.add_argument(
    '-c', '--contour-level',
    default=0,
    type=float,
    help='value (exclusive) about which to threshold [default: 0.0]'
)
binmap_prep_parser.add_argument(
    '--negate',
    default=False,
    action='store_true',
    help='use values below the contour level [default: False]'
)
binmap_prep_parser.add_argument(
    '-B', '--bytes-per-voxel',
    default=1,
    type=int,
    choices=[1, 2, 4, 8, 16],
    help='number of bytes per voxel [default: 1]'
)
binmap_prep_parser.add_argument(
    '--infix',
    default='prep',
    help="infix to be added to filenames e.g. file.map -> file_<infix>.map [default: 'prep']",
)
add_args(binmap_prep_parser, verbose)

# =========================================================================
# prep: transform
# =========================================================================
transform_prep_parser = prep_subparsers.add_parser(
    'transform',
    description='Transform the STL mesh vertices by the given values',
    help='transform an STL mesh',
)
# todo: add a new option for the voxel coordinates e.g. --voxel-size <v_x> <v_y> <v_z> which is mutually exclusive with --lengths and --indices
transform_prep_parser.add_argument(
    'from_file', help="the name of the segmentation file"
)
add_args(transform_prep_parser, config_path)
add_args(transform_prep_parser, shipped_configs)
transform_prep_parser.add_argument(
    '-L', '--lengths',
    nargs=3, type=float,
    required=True,
    help="the X, Y and Z physical lengths (in angstrom) of the space; three (3) space-separated values [required]"
)
transform_prep_parser.add_argument(
    '-I', '--indices',
    nargs=3, type=int,
    required=True,
    help="the I, J, and K image dimensions of the space, corresponding to X, Y and Z, respectively; three (3) "
         "space-separated integers [required]"
)
transform_prep_parser.add_argument(
    '-O', '--origin',
    nargs=3, type=float,
    default=[0.0, 0.0, 0.0],
    help="the origin position (in angstrom); literally, the distance between the first voxel (lowest indices) and the "
         "physical origin; three (3) space-separated values [default: 0.0 0.0 0.0]"
)
transform_prep_parser.add_argument(
    '-o', '--output',
    default=None,
    help='output file name [default: <infile>_transformed.<ext>]'
)
transform_prep_parser.add_argument(
    '--infix',
    default='transformed',
    help="infix to be added to filenames e.g. file.stl -> file_<infix>.stl [default: 'transformed']",
)
add_args(transform_prep_parser, verbose)

# =========================================================================
# convert subparser
# =========================================================================
# extend the sfftk-rw convert parser
convert_parser.description = "Perform conversions to EMDB-SFF"
convert_parser.help = "converts to EMDB-SFF"
add_args(convert_parser, config_path)
add_args(convert_parser, shipped_configs)
convert_parser.add_argument(
    '-a', '--all-levels',
    default=False,
    action='store_true',
    help="for segments structured hierarchically (e.g. Segger from UCSF Chimera and Chimera X) "
         "convert all segment leves in the hierarchy [default: False]"
)
convert_parser.add_argument(
    '-m', '--multi-file',
    action='store_true',
    default=False,
    help="enables convert to treat multiple files as individual segments of a single segmentation; only works for the "
         "following filetypes: {} [default: False]".format(
        ', '.join(multi_file_formats),
    )
)

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
# config: get
# =============================================================================
get_config_parser = config_subparsers.add_parser(
    'get',
    description='Get the value of a single configuration parameter',
    help='get single sfftk config'
)
get_config_parser.add_argument(
    'name',
    nargs="?",
    default=None,
    help="the name of the argument to retrieve",
)
add_args(get_config_parser, config_path)
add_args(get_config_parser, shipped_configs)
get_config_parser.add_argument(
    '-a', '--all',
    action='store_true',
    default=False,
    help='get all configs'
)
add_args(get_config_parser, verbose)

# =============================================================================
# config: set
# =============================================================================
set_config_parser = config_subparsers.add_parser(
    'set',
    description='Set the value of a single configuration parameter',
    help='set single sfftk config'
)
set_config_parser.add_argument(
    'name', help="the name of the argument to set",
)
set_config_parser.add_argument(
    'value', help="the value of the argument to set",
)
add_args(set_config_parser, config_path)
add_args(set_config_parser, shipped_configs)
add_args(set_config_parser, verbose)
set_config_parser.add_argument(
    '-f', '--force',
    action='store_true',
    default=False,
    help='force overwriting of an existing config; do not ask to confirm [default: False]'
)

# =============================================================================
# config: del
# =============================================================================
del_config_parser = config_subparsers.add_parser(
    'del',
    description='Delete the named configuration parameter',
    help='delete single sfftk config'
)
del_config_parser.add_argument(
    'name',
    nargs='?',
    default=None,
    help="the name of the argument to be deleted"
)
add_args(del_config_parser, config_path)
add_args(del_config_parser, shipped_configs)
del_config_parser.add_argument(
    '-a', '--all',
    action='store_true',
    default=False,
    help='delete all configs (asks the user to confirm before deleting) [default: False]'
)
del_config_parser.add_argument(
    '-f', '--force',
    action='store_true',
    default=False,
    help='force deletion; do not ask to confirm deletion [default: False]'
)
add_args(del_config_parser, verbose)

# =========================================================================
# view subparser
# =========================================================================
# extend the sfftk-rw view parser
# handle configs
add_args(view_parser, config_path)
add_args(view_parser, shipped_configs)
view_parser.add_argument('-C', '--show-chunks', action='store_true',
                         help="show sequence of chunks in IMOD file; only works with IMOD model files (.mod) [default: False]")

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
search_notes_parser.add_argument(
    'search_term',
    nargs='?',
    default='',
    help="the term to search; add quotes if spaces are included")
add_args(search_notes_parser, config_path)
add_args(search_notes_parser, shipped_configs)
l = list(_dict_iter_keys(RESOURCE_LIST))
search_notes_parser.add_argument(
    '-R', '--resource', default=l[0], choices=l,
    help='the resource to search for terms or accessions; other valid options are {resources} [default: {default}]'.format(
        resources=l,
        default=l[0],
    )
)
search_notes_parser.add_argument(
    '--start', type=int, default=1, help="start index [default: 1]"
)
search_notes_parser.add_argument(
    '--rows', type=int, default=10, help="number of rows [default: 10]"
)
ols_parser = search_notes_parser.add_argument_group(
    title='EBI Ontology Lookup Service (OLS)',
    description='The Ontology Lookup Service (OLS) is a repository for biomedical ontologies that aims to provide a '
                'single point of access to the latest ontology versions. You can use the following options to modify '
                'your search against OLS by ensuring that the -R/--resource flag is set to \'ols\' (default).'
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
list_notes_parser.add_argument('-D', '--sort-by-name', default=False,
                               action='store_true', help="sort listings by segment name [default: False (sorts by ID)]")
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
add_args(add_global_notes_parser, details)
# segment notes
add_segment_notes_parser = add_notes_parser.add_argument_group(
    title="add segment notes",
    description="add attributes to a single segment in an EMDB-SFF file"
)
add_args(add_segment_notes_parser, segment_id)
add_args(add_segment_notes_parser, segment_name)
add_args(add_segment_notes_parser, description)
add_args(add_segment_notes_parser, number_of_instances)

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
add_args(edit_notes_parser, verbose)
del external_ref['kwargs']['action']
#  global notes
edit_global_notes_parser = edit_notes_parser.add_argument_group(
    title="edit global notes",
    description="edit global attributes to an EMDB-SFF file"
)
add_args(edit_global_notes_parser, name)
add_args(edit_global_notes_parser, software_id)
add_args(edit_global_notes_parser, software_name)
add_args(edit_global_notes_parser, software_version)
add_args(edit_global_notes_parser, software_proc_details)
add_args(edit_global_notes_parser, details)
# segment notes
edit_segment_notes_parser = edit_notes_parser.add_argument_group(
    title="edit segment notes",
    description="edit attributes to a single segment in an EMDB-SFF file"
)
add_args(edit_segment_notes_parser, segment_id)
add_args(edit_segment_notes_parser, segment_name)
add_args(edit_segment_notes_parser, description)
add_args(edit_segment_notes_parser, number_of_instances)

# =========================================================================
# notes: del
# =========================================================================
# todo: sff notes del -e 1,3,4,5,6 file.json
del_notes_parser = notes_subparsers.add_parser(
    'del',
    description="Delete an existing annotation to an EMDB-SFF file",
    help="delete existing annotations",
)
add_args(del_notes_parser, sff_file)
add_args(del_notes_parser, config_path)
add_args(del_notes_parser, shipped_configs)
add_args(del_notes_parser, verbose)
# for deleting notes we handle external refs as a comma'd string e.g. 1,2,3,4 therefore not an 'int'
del external_ref_id['kwargs']['type']
add_args(del_notes_parser, external_ref_id)
# put it back
external_ref_id['kwargs']['type'] = int
# global notes
del_global_notes_parser = del_notes_parser.add_argument_group(
    title="delete global notes",
    description="delete global attributes to an EMDB-SFF file"
)
# name['kwargs'] = {
#     'action': 'store_true',
#     'default': False,
#     'help': 'delete the name [default: False]',
# }
# add_args(del_global_notes_parser, name)
# we need a way to identify which software entity in the list is to be acted up
# remove type so that we can store a list of comma-sep'd ints
del software_id['kwargs']['type']
_software_id_help = software_id['kwargs']['help']
software_id['kwargs']['help'] = 'the software(s) to delete; delete depends on whether -S, -T and -P are specified ' \
                                '(see below); if none are specified then the whole software is deleted from the list'
# add it to the parser
add_args(del_global_notes_parser, software_id)
# return things to the way you found them
software_id['kwargs']['type'] = int
software_id['kwargs']['help'] = _software_id_help
software_name['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software name for the specified software id(s) [default: False]'
}
add_args(del_global_notes_parser, software_name)
software_version['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software version for the specified software id(s) [default: False]'
}
add_args(del_global_notes_parser, software_version)
software_proc_details['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the software processing details for the specified software id(s) [default: False]'
}
add_args(del_global_notes_parser, software_proc_details)
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
segment_name['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the segment name [default: False]'
}
add_args(del_segment_notes_parser, segment_name)
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
add_args(clear_notes_parser, verbose)
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
    help="write all changes made since the last 'save' action"
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
# print(tool_list)
tool_list = ['all', 'core', 'formats', 'notes', 'readers', 'schema', 'main']

# tests
test_help = "one or none of the following: {}".format(", ".join(tool_list))
tests_parser = subparsers.add_parser(
    'tests', description="Run unit tests", help="run unit tests")
tests_parser.add_argument('tool', nargs='+', help=test_help)
add_args(tests_parser, config_path)
add_args(tests_parser, shipped_configs)
tests_parser.add_argument('-v', '--verbosity', default=1, type=int,
                          help="set verbosity; valid values: %s [default: 0]" % ", ".join(map(str, verbosity_range)))


def check_multi_file_formats(file_names):
    """Check file names for file formats

    When working with multifile segmentations, this function checks that all files are consistent

    :param list file_names: a list of file names
    :return: a tuple consisting of whether or not the set of file formats if valid, the set of file formats observed
        and the set of invalid file formats
    :rtype: tuple[bool, set, set]
    """
    is_valid_format = True
    file_formats = set()
    invalid_formats = set()
    for fn in file_names:
        ff = fn.split('.')[-1].lower()
        if ff in multi_file_formats:
            file_formats.add(ff)
        else:
            invalid_formats.add(ff)
            is_valid_format = False
    if len(file_formats) == 1:
        file_format = file_formats.pop()
    else:
        file_format = None
        invalid_formats.union(file_formats)
    return is_valid_format, file_format, invalid_formats


# parser function
def parse_args(_args, use_shlex=False):
    """
    Parse and check command-line arguments and also return configs.

    This function does all the heavy lifting in ensuring that commandline
    arguments are properly formatted and checked for sanity. It also 
    extracts configs from the config files.

    In this way command handlers (defined in :py:mod:`sfftk.sff` e.g. :py:meth:`sfftk.sff.handle_convert`) assume correct argument values and can concentrate on functionality making the code more readable.

    :param list _args: list of arguments (``use_shlex=False``); string of arguments (``use_shlex=True``)
    :type _args: list or str
    :param bool use_shlex: treat ``_args`` as a string instead for parsing using ``shlex`` lib
    :return: parsed arguments
    :rtype: tuple[:py:class:`argparse.Namespace`, :py:class:`sfftk.core.configs.Configs`]
    """
    if use_shlex:  # if we treat _args as a command string for shlex to process
        try:
            assert isinstance(_args, str)
        except AssertionError:
            return os.EX_USAGE, None
        import shlex
        _args = shlex.split(_args)

    # if we have no subcommands then show the available tools
    if len(_args) == 0:
        Parser.print_help()
        return os.EX_OK, None
    # if we only have a subcommand then show that subcommand's help
    elif len(_args) == 1:
        # print(_args[0])
        # print(Parser._actions[2].choices)
        # if _args[0] == 'tests':
        #     pass
        if _args[0] == '-V' or _args[0] == '--version':
            from .. import SFFTK_VERSION
            print_date("sfftk version: {}".format(SFFTK_VERSION))
            return os.EX_OK, None
        # anytime a new argument is added to the base parser subparsers are bumped down in index
        elif _args[0] in _dict_iter_keys(Parser._actions[2].choices):
            exec('{}_parser.print_help()'.format(_args[0]))
            return os.EX_OK, None
    # if we have 'notes' as the subcommand and a sub-subcommand show the
    # options for that sub-subcommand
    elif len(_args) == 2:
        if _args[0] == 'notes':
            if _args[1] in _dict_iter_keys(Parser._actions[2].choices['notes']._actions[1].choices):
                exec('{}_notes_parser.print_help()'.format(_args[1]))
                return os.EX_OK, None
        elif _args[0] == 'prep':
            if _args[1] in _dict_iter_keys(Parser._actions[2].choices['prep']._actions[1].choices):
                exec('{}_prep_parser.print_help()'.format(_args[1]))
                return os.EX_OK, None
        elif _args[0] == 'config':
            if _args[1] in _dict_iter_keys(Parser._actions[2].choices['config']._actions[1].choices):
                exec('{}_config_parser.print_help()'.format(_args[1]))
                return os.EX_OK, None
    # parse arguments
    args = Parser.parse_args(_args)
    from .configs import get_config_file_path
    # get the file to use for configs given args
    config_file_path = get_config_file_path(args)
    if config_file_path is None:
        print_date("Invalid destination for configs. Omit --shipped-configs to write to user configs.")
        return os.EX_USAGE, None
    from .configs import load_configs
    # now get configs to use
    configs = load_configs(config_file_path)

    # check values
    # config
    if args.subcommand == 'config':
        if args.verbose:
            print_date("Reading configs from {}...".format(config_file_path))
        # handle config-specific argument modifications here
        if args.config_subcommand == 'del':
            if args.name not in configs and not args.all:
                print_date("Missing config with name '{}'. Aborting...".format(args.name))
                return None, configs
            # if force pass
            if not args.force:
                default_choice = 'n'
                # get user choice
                user_choice = _input("Are you sure you want to delete config '{}' [y/N]? ".format(
                    args.name)).lower()
                if user_choice == '':
                    choice = default_choice
                elif user_choice == 'n' or user_choice == 'N':
                    choice = 'n'
                elif user_choice == 'y' or user_choice == 'Y':
                    choice = 'y'
                else:
                    print_date("Invalid choice: '{}'")
                    return os.EX_USAGE, configs
                # act on user choice
                if choice == 'n':
                    print_date("You have opted to cancel deletion of '{}'".format(args.name))
                    return os.EX_USAGE, configs
                elif choice == 'y':
                    pass
        elif args.config_subcommand == 'set':
            if args.name in configs:
                # if force pass
                if not args.force:
                    default_choice = 'n'
                    # get user choice
                    user_choice = _input("Are you sure you want to overwrite config '{}={}' [y/N]? ".format(
                        args.name, configs[args.name])).lower()
                    if user_choice == '':
                        choice = default_choice
                    elif user_choice == 'n' or user_choice == 'N':
                        choice = 'n'
                    elif user_choice == 'y' or user_choice == 'Y':
                        choice = 'y'
                    else:
                        print_date("Invalid choice: '{}'")
                        return os.EX_USAGE, configs
                    # act on user choice
                    if choice == 'n':
                        print_date("You have opted to cancel overwriting of '{}'".format(args.name))
                        return None, configs
                    elif choice == 'y':
                        pass
    # prep
    elif args.subcommand == 'prep':
        # binmap
        if args.prep_subcommand == 'binmap':
            ext = args.from_file.split('.')[-1]
            if ext.lower() not in prepable_file_formats:
                print_date("File format {} not available for prepping".format(ext.lower()))
                return os.EX_USAGE, configs
            if args.output is None:
                if args.infix != '':
                    args.output = '.'.join(args.from_file.split('.')[:-1]) + '_' + args.infix + '.' + ext
                else:
                    print_date("Cannot overwrite input file")
                    return os.EX_USAGE, configs
                if args.verbose:
                    print_date("Output will be written to {}".format(args.output))
        elif args.prep_subcommand == 'transform':
            ext = args.from_file.split('.')[-1]
            if ext.lower() not in rescalable_file_formats:
                print_date("File format {} not available for transforming".format(ext.lower()))
                return os.EX_USAGE, configs
            if args.output is None:
                if args.infix != '':
                    args.output = '.'.join(args.from_file.split('.')[:-1]) + '_' + args.infix + '.' + ext
                else:
                    print_date("Cannot overwrite input file")
                    return os.EX_USAGE, configs
                if args.verbose:
                    print_date("Output will be written to {}".format(args.output))

    # view
    elif args.subcommand == 'view':
        if args.show_chunks:
            if not re.match(r".*\.mod$", args.from_file, re.IGNORECASE):
                print_date("Invalid file type to view chunks. Only works with IMOD files")
                return os.EX_USAGE, configs
    # convert
    elif args.subcommand == 'convert':
        # convert details to unicode
        if args.details is not None:
            args.details = _decode(args.details, 'utf-8')
        # single vs. multi-file
        # single vs. multiple file names provided
        if len(args.from_file) == 1:
            args.from_file = args.from_file[0]
            try:
                assert os.path.exists(args.from_file)
            except AssertionError:
                print_date("File {} was not found".format(args.from_file))
                return os.EX_USAGE, configs
        else:
            if args.multi_file:
                is_valid_format, file_format, invalid_formats = check_multi_file_formats(args.from_file)
                if is_valid_format:
                    file_missing = False
                    for fn in args.from_file:
                        try:
                            assert os.path.exists(fn)
                        except AssertionError:
                            print_date("File {} was not found".format(fn))
                            file_missing = True
                    if file_missing:
                        return os.EX_USAGE, configs
                else:
                    print_date("Invalid format(s) for multi-file segmentation: {}; should be only one of: {}".format(
                        ', '.join(invalid_formats),
                        ', '.join(multi_file_formats),
                    ))
                    return os.EX_USAGE, configs
            else:
                print_date("Please use -m/--multi-file argument for multi-file segmentations")
                return os.EX_USAGE, configs
        # set the output file
        if args.output is None:
            if args.multi_file:
                from_file = args.from_file[0]
            else:
                from_file = args.from_file
            dirname = os.path.dirname(from_file)
            if args.format:
                try:
                    assert args.format in list(map(lambda x: x[0], FORMAT_LIST))
                except AssertionError:
                    print_date("Invalid output format: {}; valid values are: {}".format(
                        args.format, ", ".join(map(lambda x: x[0], FORMAT_LIST))))
                    return os.EX_USAGE, configs
                fn = ".".join(os.path.basename(from_file).split(
                    '.')[:-1]) + '.{}'.format(args.format)
                args.__setattr__('output', os.path.join(dirname, fn))
            # convert file.sff to file.hff
            elif re.match(r'.*\.sff$', from_file):
                fn = ".".join(
                    os.path.basename(from_file).split('.')[:-1]) + '.hff'
                args.__setattr__('output', os.path.join(dirname, fn))
            # convert file.hff to file.sff
            elif re.match(r'.*\.hff$', from_file):
                fn = ".".join(
                    os.path.basename(from_file).split('.')[:-1]) + '.sff'
                args.__setattr__('output', os.path.join(dirname, fn))
            else:
                fn = ".".join(
                    os.path.basename(from_file).split('.')[:-1]) + '.sff'
                args.__setattr__('output', os.path.join(dirname, fn))
            if args.verbose:
                print_date("Setting output file to {}".format(args.output))
        else:
            print_date("Writing output to {}".format(args.output))

        # ensure valid primary_descriptor
        if args.primary_descriptor:
            try:
                assert args.primary_descriptor in [
                    'three_d_volume', 'mesh_list', 'shape_primitive_list']
            except:
                if args.verbose:
                    print_date(
                        "Invalid value for primary descriptor: {}".format(args.primary_descriptor))
                return os.EX_USAGE, configs
            if args.verbose:
                print_date(
                    "Trying to set primary descriptor to {}".format(args.primary_descriptor))
        # using -a/--all-levels
        if args.all_levels:
            if args.verbose:
                print_date("Writing out all levels of segment hierarchy")

    # tests
    elif args.subcommand == 'tests':
        # check if we have a temp-annotated file and complain then die if one exists
        if os.path.exists(configs['__TEMP_FILE']):
            print_date("Unable to run tests with {} in current path ({})".format(configs['__TEMP_FILE'],
                                                                                 os.path.abspath(__file__)))
            print_date("Run 'sff notes save <file.sff>' or 'sff notes trash @' before proceeding.")
            return os.EX_USAGE, configs
        # normalise tool list
        # if 'all' is specified together with others then it should simply be 'all'
        if 'all' in args.tool:
            args.tool = ['all']
        # if isinstance(args.tool, list):
        for tool in args.tool:
            try:
                assert tool in tool_list
            except AssertionError:
                print_date(
                    "Unknown tool: {}; Available tools for test: {}".format(tool, ", ".join(tool_list))
                )
                return os.EX_USAGE, configs
        if args.verbosity:
            try:
                assert args.verbosity in range(4)
            except:
                print_date(
                    "Verbosity should be in {}-{}: {} given".format(
                        verbosity_range[0],
                        verbosity_range[-1],
                        args.verbosity
                    )
                )
                return os.EX_USAGE, configs
    # notes
    elif args.subcommand == 'notes':
        # convenience: the user can use '@' to refer to an EMDB-SFF file whch is the previous
        # file that was edited ('add', 'edit', 'del', 'copy', 'clear')
        temp_file = configs['__TEMP_FILE']
        temp_file_ref = configs['__TEMP_FILE_REF']
        if args.notes_subcommand in ['list', 'show', 'add', 'edit', 'del', 'save', 'trash', 'copy', 'clear']:
            # find, view
            if args.notes_subcommand in ['list', 'show', 'search']:
                if args.sff_file == temp_file_ref:
                    if os.path.exists(temp_file):
                        args.sff_file = temp_file
                        if args.verbose:
                            print_date(
                                "Working on temp file {}".format(temp_file), stream=sys.stdout)
                    else:
                        print_date("Temporary file {} does not exist. \
Try invoking an edit ('add', 'edit', 'del') action on a valid EMDB-SFF file.".format(temp_file), stream=sys.stdout)
                        return os.EX_USAGE, configs
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
                    return os.EX_USAGE, configs

        if args.notes_subcommand == "search":
            # ensure start is valid
            if args.start < 1:
                print_date("Invalid start value: {}; should be greater than 1".format(args.start))
                return os.EX_USAGE, configs
            # ensure rows is valid
            if args.rows < 1:
                print_date("Invalid rows value: {}; should be greater than 1".format(args.rows))
                return os.EX_USAGE, configs
            if args.resource != 'ols' and (
                    args.ontology is not None or args.exact or args.list_ontologies or \
                    args.short_list_ontologies or args.obsoletes):
                print_date("Invalid usage: -O, -x, -o, -L, -l can only be used with -R ols")
                return os.EX_USAGE, None
        elif args.notes_subcommand == "show":
            if args.segment_id is not None:
                args.segment_id = list(map(int, args.segment_id.split(',')))

        elif args.notes_subcommand == "add":
            # if we want to add to a segment
            if args.segment_id is not None:
                args.segment_id = list(map(int, args.segment_id.split(',')))

                # ensure we have at least one item to add
                try:
                    assert (args.segment_name is not None) or (args.description is not None) or \
                           (args.number_of_instances is not None) or \
                           (args.external_ref is not None)
                except AssertionError:
                    print_date("Nothing specified to add. Use one or more of the following options:\n\t"
                               "-n <segment_name> \n\t-D <description> \n\t-E <extrefType> <extrefOtherType> <extrefValue> \n\t"
                               "-I <int>")

                    return os.EX_USAGE, configs

            # unicode conversion
            if args.name is not None:
                args.name = _decode(args.name, 'utf-8')
            if args.details is not None:
                args.details = _decode(args.details, 'utf-8')
            if args.software_name is not None:
                args.software_name = _decode(args.software_name, 'utf-8')
            if args.software_version is not None:
                args.software_version = _decode(args.software_version, 'utf-8')
            if args.software_processing_details is not None:
                args.software_processing_details = _decode(args.software_processing_details, 'utf-8')
            if args.external_ref is not None:
                external_ref = list()
                for t, o, v in args.external_ref:
                    external_ref.append([_decode(t, 'utf-8'), _decode(o, 'utf-8'), _decode(v, 'utf-8')])
                args.external_ref = external_ref
            if args.segment_name is not None:
                args.segment_name = _decode(args.segment_name, 'utf-8')
            if args.description is not None:
                args.description = _decode(args.description, 'utf-8')

        elif args.notes_subcommand == "edit":
            # external references can be added globally (header) or to a
            # segment
            if args.external_ref:
                try:
                    assert args.external_ref_id is not None
                except AssertionError:
                    print_date("Will not be able to edit an external reference without \
specifying an external reference ID. Run 'list' or 'show' to see available \
external reference IDs for segment {}".format(args.segment_id), stream=sys.stdout)
                    return os.EX_USAGE, configs

                # consistency of format
                # todo: check this; doesn't seem right
                if len(args.external_ref) == 0 and isinstance(args.external_ref[0], _str):
                    args.external_ref = [args.external_ref]

            # software
            if args.software_name or args.software_version or args.software_processing_details:
                try:
                    assert args.software_id is not None
                except AssertionError:
                    print_date("Will not be able to edit a software intance without specifying an software ID. "
                               "Run 'show' to see the available software IDs.")
                    return os.EX_USAGE, configs

            if args.segment_id is not None:
                args.segment_id = list(map(int, args.segment_id.split(',')))

            # unicode
            if args.name is not None:
                args.name = _decode(args.name, 'utf-8')
            if args.details is not None:
                args.details = _decode(args.details, 'utf-8')
            if args.software_name is not None:
                args.software_name = _decode(args.software_name, 'utf-8')
            if args.software_version is not None:
                args.software_version = _decode(args.software_version, 'utf-8')
            if args.software_processing_details is not None:
                args.software_processing_details = _decode(args.software_processing_details, 'utf-8')
            if args.external_ref is not None:
                external_ref = list()
                for t, o, v in args.external_ref:
                    external_ref.append([_decode(t, 'utf-8'), _decode(o, 'utf-8'), _decode(v, 'utf-8')])
                args.external_ref = external_ref
            if args.segment_name is not None:
                args.segment_name = _decode(args.segment_name, 'utf-8')
            if args.description is not None:
                args.description = _decode(args.description, 'utf-8')

        elif args.notes_subcommand == "del":
            if args.segment_id is not None:
                try:
                    assert args.segment_id is not None
                except AssertionError:
                    print_date(
                        "Please specify a segment ID", stream=sys.stdout)
                    return os.EX_USAGE, configs

                args.segment_id = list(map(int, args.segment_id.split(',')))

                # ensure we have at least one item to del
                try:
                    assert args.segment_name or args.description or args.number_of_instances or \
                           (args.external_ref_id is not None)
                except AssertionError:
                    print_date("Incorrect usage; please use -h for help")
                    return os.EX_USAGE, configs
            # convert from string to list of ints
            if args.external_ref_id is not None:
                ext_ref_ids = list(map(int, args.external_ref_id.split(',')))
                args.external_ref_id = ext_ref_ids
            # convert from string to list of ints for software
            if args.software_id is not None:
                software_ids = list(map(int, args.software_id.split(',')))
                args.software_id = software_ids

                # if missing -S, -T, and -P then set them since we have -s set
                if not args.software_name and not args.software_version and not args.software_processing_details:
                    args.software_name = True
                    args.software_version = True
                    args.software_processing_details = True


        elif args.notes_subcommand == "copy":
            # convert from and to to lists of ints
            if args.segment_id is not None:
                from_segment = list(map(int, args.segment_id.split(',')))
                if isinstance(from_segment, int):
                    args.segment_id = [from_segment]
                else:
                    args.segment_id = from_segment
            if args.to_segment is not None:
                to_segment = list(map(int, args.to_segment.split(',')))
                if isinstance(to_segment, int):
                    args.to_segment = [to_segment]
                else:
                    args.to_segment = to_segment

            if args.segment_id is not None and args.to_segment is not None:
                from_set = set(args.segment_id)
                to_set = set(args.to_segment)
                common = from_set.intersection(to_set)
                if len(common) > 0:
                    print_date(
                        "the following segment IDs appear in both --segment-id and --to-segment: {}".format(
                            " ".join(map(str, common))
                        ))
                    return os.EX_USAGE, configs

        elif args.notes_subcommand == "clear":
            # where to clear notes from
            if args.segment_id is not None:
                from_segment = list(map(int, args.segment_id.split(',')))
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
