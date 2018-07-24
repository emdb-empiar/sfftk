# -*- coding: utf-8 -*-
from __future__ import division, print_function

import sys
import os
import mrcfile
import numpy

from .print_tools import print_date

def bin_map(args, configs):
    """Bin the CCP4 map

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return int exit_status: exit status
    """
    if args.verbose:
        print_date('Reading in data from {}...'.format(args.from_file))
    with mrcfile.mmap(args.from_file) as mrc:
        if args.bytes_per_voxel == 1:
            out_type = numpy.int8
        elif args.bytes_per_voxel == 2:
            out_type = numpy.int16
        elif args.bytes_per_voxel == 4:
            out_type = numpy.int32
        elif args.bytes_per_voxel == 8:
            out_type = numpy.int64
        elif args.bytes_per_voxel == 16:
            out_type = numpy.int128
        if args.verbose:
            print_date('Voxels will be of type {}'.format(out_type))
            print_date('Binarising to {} about contour-level of {}'.format(args.mask_value, args.contour_level))
            if args.negate:
                print_date('Negating...')
                data = ((mrc.data < args.contour_level) * args.mask_value).astype(out_type)  # only need a byte per voxel
            else:
                data = ((mrc.data > args.contour_level) * args.mask_value).astype(out_type)  # only need a byte per voxel
        if args.verbose:
            print_date('Creating output file...')
        mrc2 = mrcfile.new(args.output, data, overwrite=args.overwrite)
        if args.verbose:
            print_date('Writing header data...')
        mrc2.header.cella = mrc.header.cella
        mrc2.flush()
        mrc2.close()
        if args.verbose:
            print_date('Binarising complete!')
    return os.EX_OK