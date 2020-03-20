# -*- coding: utf-8 -*-
# prep.py
"""
``sfftk.core.prep``
==========================

This module consists of preparation utilities to condition segmentation files prior to conversion.
"""
from __future__ import division, print_function

import os
import re

import mrcfile
import numpy
from sfftkrw.core import _str
from sfftkrw.core.print_tools import print_date
from stl import Mesh


def bin_map(args, configs):
    """Bin the CCP4 map

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return: exit status
    :rtype: int
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
            data = ((mrc.data < args.contour_level) * args.mask_value).astype(
                out_type)  # only need a byte per voxel
        else:
            data = ((mrc.data > args.contour_level) * args.mask_value).astype(
                out_type)  # only need a byte per voxel
        if args.verbose:
            print_date('Creating output file...')
        try:
            mrc2 = mrcfile.new(args.output, data, overwrite=args.overwrite)
        except ValueError:
            print_date("Binarising preparation failed")
            print_date("Attempting to overwrite without explicit --overwrite argument")
            return os.EX_DATAERR
        if args.verbose:
            print_date('Writing header data...')
        mrc2.header.cella = mrc.header.cella
        mrc2.flush()
        mrc2.close()
        if args.verbose:
            print_date('Binarising complete!')
    return os.EX_OK


def transform(args, configs):
    """Rescale the STL mesh using the params in the arguments namespace

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return: exit status
    :rtype: int
    """
    # we now constitute the transformation matrix
    transform = construct_transformation_matrix(args)
    # let the reader understand...
    if args.verbose:
        print_date("Transformation matrix: ")
        print_date(_str(transform), incl_date=False)
    if re.match(r'.*\.stl$', args.from_file, re.IGNORECASE):
        # mesh operations
        in_mesh = Mesh.from_file(args.from_file)
        out_mesh = transform_stl_mesh(in_mesh, transform)
        if out_mesh is None:
            return os.EX_DATAERR
        if args.verbose:
            print_date("Saving output...")
        # save the output
        out_mesh.save(args.output)
        if args.verbose:
            print_date("Done")
        return os.EX_OK
    else:
        print_date("Rescaling functionality for this filetype yet to be implemented!")
        return os.EX_OK


def construct_transformation_matrix(args):
    """Construct the transformation matrix

    :param args: parsed arguments
    :type args: :py:class:`argparse.ArgumentParser`
    :return: transform
    :rtype: :py:class:`numpy.ndarray`
    """
    # original params
    lengths = numpy.array(args.lengths, dtype=numpy.float32)
    indices = numpy.array(args.indices, dtype=numpy.int32)
    origin = numpy.array(args.origin, dtype=numpy.float32)
    # derived params
    voxel_size = numpy.divide(lengths, indices)
    transform = numpy.array([
        [voxel_size[0], 0, 0, origin[0]],
        [0, voxel_size[1], 0, origin[1]],
        [0, 0, voxel_size[2], origin[2]],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)
    return transform


def transform_stl_mesh(mesh, transform):
    """Rescale the given STL mesh by the given transform

    :param mesh: an STL mesh
    :type mesh: :py:class:`numpy.ndarray`
    :param transform: numpy array with ``shape = (4, 4)``
    :type transform: :py:class:`numpy.ndarray`
    :return: an STL mesh transformed
    :rtype: :py:class:`numpy.ndarray`
    """
    # the rotation sub-matrix of the transformation matrix
    rotation = transform[0:3, 0:3]
    # output mesh
    # we need to copy the data out
    out_mesh = Mesh(numpy.copy(mesh.data), remove_empty_areas=False)
    # perform the rotation part of the transformation
    for i in range(3):
        out_mesh.vectors[:, i] = numpy.dot(rotation, out_mesh.vectors[:, i].T).T
    # now perform translations
    out_mesh.x = out_mesh.x + transform[0, 3]
    out_mesh.y += transform[1, 3]
    out_mesh.z += transform[2, 3]
    return out_mesh
