"""
``sfftk.core.prep``
==========================

This module consists of preparation utilities to condition segmentation files prior to conversion.
"""
import asyncio
import re
import sys
import json

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
            return 65
        if args.verbose:
            print_date('Writing header data...')
        mrc2.header.cella = mrc.header.cella
        mrc2.flush()
        mrc2.close()
        if args.verbose:
            print_date('Binarising complete!')
    return 0


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
            return 65
        if args.verbose:
            print_date("Saving output...")
        # save the output
        out_mesh.save(args.output)
        if args.verbose:
            print_date("Done")
        return 0
    else:
        print_date("Rescaling functionality for this filetype yet to be implemented!")
        return 0


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


async def _mask_is_binary(mask, verbose=False):
    """Corouting to check whether individual masks are binary"""
    from ..readers.mapreader import Map
    this_map = Map(mask)
    if verbose:
        print_date(f"info: assessing {mask}...")
    # if a mask is binary but not with non-zero value of 1 fix this
    if 1 not in this_map._voxel_values:
        if verbose:
            print_date(f"info: fixing {mask} with voxel values {this_map._voxel_values}...")
        this_map.fix_mask(mask_value=1)
    return this_map.is_mask


async def _check_masks_binary(args, configs):
    """Corourite to run the event loop for all masks"""
    awaitables = list()
    for mask in args.masks:
        awaitables.append(_mask_is_binary(mask, verbose=args.verbose))
    return await asyncio.gather(*awaitables)


def _masks_all_binary(args, configs):
    """Check whether all masks are binary"""
    """Validate that all masks are binary masks"""
    # todo: for small files read all data
    # todo: for large files only read the first X bytes
    # todo: give the user the option to read full files for large files
    if sys.version_info.minor > 6:
        all_binary = asyncio.run(_check_masks_binary(args, configs))
    else:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        all_binary = loop.run_until_complete(_check_masks_binary(args, configs))
        loop.close()
    return all(all_binary)


def _masks_no_overlap(args, configs):
    """Checks that all segments do not overlap"""
    # make all binary
    # current_data = None
    from ..readers.mapreader import Map
    previous_mask = None
    for mask in args.masks:
        this_map = Map(mask)
        if 'current_data' not in locals():
            current_data = numpy.zeros(this_map.voxels.shape)
        # if current_data is None:
        #     current_data = this_map.voxels
        #     continue
        # add all volumes
        current_data += this_map.voxels
        if numpy.amax(current_data) > 1:
            print_date(f"warning: segment overlap between mask {mask} and {previous_mask}")
        previous_mask = mask
    # the max should be 1
    max_voxel_value = numpy.amax(current_data)
    return max_voxel_value == 1


def _mergemask(args, configs) -> [numpy.ndarray, dict]:
    """The mergemask workhorse which does the actual merging"""
    from ..readers.mapreader import Map
    import pathlib
    label_dict = dict()
    for label, mask in enumerate(args.masks, start=1):
        this_map = Map(mask)
        if 'output_mask' not in locals():
            output_mask = numpy.zeros(this_map.voxels.shape, dtype=numpy.int8)
        output_mask += this_map.voxels * label
        label_dict[pathlib.Path(mask).name] = label
    return output_mask, label_dict


def mergemask(args, configs):
    """Merge two or more (max 255) masks into one with a distinct label for each mask

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return: exit status
    :rtype: int
    """
    # some sanity checks
    # ensure that the files are binary
    if not _masks_all_binary(args, configs):
        print_date(f"error: one or more masks are non-binary; use --verbose to view details")
        return 65
    # todo: allow cases where one or more files are non-binary
    # ensure that they don't overlap each other
    if not _masks_no_overlap(args, configs):
        print_date(f"error: one or more masks overlap; use --verbose to view details")
        return 65
    # now we can merge masks
    if args.verbose:
        print_date(f"info: proceeding to merge masks...")
    merged_mask, label_dict = _mergemask(args, configs)
    if args.verbose:
        print_date(f"info: merge complete...")
    if args.verbose:
        print_date(f"info: attempting to write output ti {args.output_prefix}.{args.mask_extension}...")
    try:
        with mrcfile.new(f"{args.output_prefix}.{args.mask_extension}", overwrite=args.overwrite) as mrc:
            mrc.set_data(merged_mask)
    except ValueError:
        print_date(f"error: the file already exists; use --overwrite to overwrite the existing merged_mask or set a "
                   f"new output prefix using --output-prefix")
        return 64
    else:  # only create the label file if no exception is raised in creating the mask
        if args.verbose:
            print_date(f"info: attempting to write label file {args.output_prefix}.txt...")
        # create the mask metadata
        mask_metdata = dict()
        mask_metdata['mask_to_label'] = dict()
        for mask_name, mask_label in label_dict.items():
            mask_metdata['mask_to_label'][mask_name] = mask_label
        with open(f"{args.output_prefix}.json", 'w') as label_file:
            json.dump(mask_metdata, label_file, indent=4)
    if args.verbose:
        print_date(f"info: merge complete!")
    return 0
