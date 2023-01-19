"""
``sfftk.core.prep``
==========================

This module consists of preparation utilities to condition segmentation files prior to conversion.
"""
import asyncio
import json
import pathlib
import re
import sys
from typing import List

import mrcfile
import numpy
import numpy.lib.mixins
from sfftkrw.core import _str
from sfftkrw.core.print_tools import print_date
from stl import Mesh

from sfftk.readers.mapreader import Map


def _label_generator():
    yield from (*range(1, 128), *range(-128, 0))


class MergedMask:
    """This class describes a special mask used to perform mask merging. It automatically handles
    complex cases involving mask overlaps by constucting a label tree showing the relations
    between masks. The trivial case of non-overlapping overlaps will have all labels children of
    the root label (0).

    There are only three ways that an overlap can happen.

    1. no overlap is the trivial case - no elements are shared between masks;
    2. complete overlap: one set of elements is completely contained in another set;
    3. partial overlap: some elements are shared.

    For this functionality to work we need several functions:

    - vectorised addition of masks to the merged mask;
    - a way to decide the next label to use, which is not necessary the current label plus one;
    - a way to capture the relationship between labels

    Consider the simple exercise of merging the following non-trivial (overlapping) masks:

    .. code:: python

        mask1 = [0, 1, 0, 0]
        mask2 = [0, 1, 0, 0]
        mask3 = [0, 0, 1, 0]
        mask4 = [0, 1, 1, 1]
        mask5 = [1, 0, 0, 0]
        mask6 = [1, 0, 1, 0]

    We will build our merged mask by successively adding each mask to the empty mask: ``[0, 0, 0, 0]``.

    We assume that all masks are positive binary with values ``0`` (background) and ``1`` (elements of interest).

    At each iteration, will set a new label to be used. This label will identify the particular mask. Therefore,
    we multiply the mask by the label.

    Because elements can overlap, we need a way to keep track of labels so that we can record when we have to
    assign labels that indicate either complete or partial overlap. We, therefore, examine the resulting labels and
    from this infer the relationships between labels. To do this, we have a set of admitted labels as well as a set of
    new labels. By comparing these sets and taking into account the current label, we can determine the label for
    elements resulting from overlap and which labels they relate to.

    .. code-block:: python

        merged_mask = [0, 0, 0, 0] # the internal value of MergedMask's array
        label = 1
        label_set = {}
        label_tree = dict()
        # mask 1
        merged_mask = merged_mask + [0, 1, 0, 0] * 1 # => [0, 1, 0, 0]
        label_set = {1}
        label_tree[1] = 0 # 1 is a child of the root (0) => {1: 0}
        new_labels = {}
        label = numpy.amax(merged_mask) + 1 = 2
        # mask 2
        merged_mask = [0, 1, 0, 0] + [0, 1, 0, 0] * 2 = [0, 3, 0, 0]
        label_set = {1, 2}
        label_tree[2] = 0 # => {1: 0, 2: 0}
        new_labels = {3}
        label_tree[3] = [1, 2] # 3 is a child of 1 and 2 (overlap) => {1: 0, 2: 0, 3: [1, 2]}
        label_set = {1, 2, 3}
        label = numpy.amax(merged_mask) + 1 = 4
        # mask 3
        merged_mask = [0, 3, 0, 0] + [0, 0, 1, 0] * 4 = [0, 3, 4, 0]
        label_set = {1, 2, 3, 4}
        label_tree[4] = 0 # => {1: 0, 2: 0, 3: [1, 2], 4: 0}
        new_labels = {}
        label = numpy.amax(merge_mask) + 1 = 5
        # mask 4
        merged_mask = [0, 3, 4, 0] + [0, 1, 1, 1] * 5 = [0, 8, 9, 5]
        label_set = {1, 2, 3, 4, 5}
        label_tree[5] = 0 # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0}
        new_labels = {8, 9}
        label_tree[8] = [3, 5]
        label_tree[9] = [4, 5] # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0, 8: [3, 5], 9: [4, 5]}
        label = numpy.amax(merge_mask) + 1 = 10
        # mask 5
        merged_mask = [0, 8, 9, 5] + [0, 1, 1, 1] * 10 = [10, 18, 19, 15]
        label_set = {1, 2, 3, 4, 5, 10}
        label_tree[10] = 0 # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0, 8: [3, 5], 9: [4, 5], 10: 0}
        new_labels = {15, 18, 19}
        label_tree[15] = [5, 10]
        label_tree[18] = [8, 10]
        label_tree[19] = [9, 10] # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0, 8: [3, 5], 9: [4, 5], 10: 0, 15: [5, 10], 18: [8, 10], 19: [9, 10]}
        label_set = {1, 2, 3, 4, 5, 10, 15, 18, 19}
        label = numpy.amax(merge_mask) + 1 = 20
        # mask 6
        merged_mask = [10, 18, 19, 15] + [1, 0, 1, 0] * 20 = [30, 18, 39, 15]
        label_set = {1, 2, 3, 4, 5, 10, 15, 18, 19, 20}
        label_tree[20] = 0 # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0, 8: [3, 5], 9: [4, 5], 10: 0, 15: [5, 10], 18: [8, 10], 19: [9, 10], 20: 0}
        new_labels = {30, 39}
        label_tree[30] = [10, 20]
        label_tree[39] = [19, 20] # => {1: 0, 2: 0, 3: [1, 2], 4: 0, 5: 0, 8: [3, 5], 9: [4, 5], 10: 0, 15: [5, 10], 18: [8, 10], 19: [9, 10], 20: 0, 30: [10, 20], 39: [19, 20]}
        label_set = {1, 2, 3, 4, 5, 10, 15, 18, 19, 20, 30, 39}
        label = numpy.amax(merge_mask) + 1 = 40

    Objects of this class have a number of important properties germane to working with collation of masks:

    - they know what the next label value is implicitly;
    - they handle iterative addition of masks to construct the merged mask;
    - they keep track of the label tree;

    The internal array instantiation is lazy---it is only created once we know the size of the
    masks to be merged.

    Using a ``MergedMask`` object converts the complexity of the above into the following:

    .. code-block:: python

        merged_mask = MergedMask()
        for mask in masks: # masks is a list of n-dimensional binary-valued arrays
            merged_mask.merge(mask)

    Internally, merging is a vectorised addition of arrays by overloading the ``__add__``, ``__radd__``
    and ``__iadd__`` protocols. However, it is safest to use the :py:func:`MergeMask.merge()` method because
    ``numpy`` arrays also implement the addition protocols meaning that ``__radd__`` fails.

    Once the masks have been merged, we can now interrogate the merged mask for some attributes:

    .. code-block:: python

        merged_mask.label # the next label to be used; autoincremented appropriately
        merged_mask.label_tree # the hiearchy of labels (complex tree of labels)
        merged_mask.mask_to_label # the relations between masks and labels
    """

    def __init__(self, data=None, dtype=numpy.dtype('int16'), mask_name_prefix="mask_", zfill=4):
        # we could use int8 but the overflow leads to negative numbers which break the flow
        # using int16 gives us a positive upper ceiling of 32k, much higher than 127 for int8
        self._label = 1  # initial label value
        self._label_tree = dict()
        self._label_set = set()
        self._dtype = dtype
        self._data = data
        self._mask_to_label = dict()
        self._mask_id = 1
        self._mask_name_prefix = mask_name_prefix
        self._zfill = zfill
        self._mask_name = None

    def _init_data(self, mask: numpy.ndarray):
        """Private method to initialise MergedMask based on a provide mask"""
        # validate mask
        unique_values = numpy.unique(mask)
        try:
            assert len(unique_values) == 2 and 0 in unique_values and 1 in unique_values
        except AssertionError:
            raise ValueError(f"non-binary mask with values: {unique_values}")
        if not isinstance(mask, numpy.ndarray):
            raise TypeError("mask must be a numpy.ndarray object")
        # instantiate self._data as zeros of the right dimension
        if self._data is None:
            self._data = numpy.zeros(mask.shape, self._dtype)

    def __repr__(self):
        """Representation"""
        return f"{self.__class__.__qualname__}(data={self.data}, dtype={self._dtype})"

    def __array__(self):
        """Numpy array interface"""
        return self._data

    @property
    def shape(self):
        if self._data is not None:
            return self._data.shape
        return

    @property
    def data(self):
        return self._data

    @property
    def dtype(self):
        return self._dtype

    @property
    def label(self):
        return self._label

    @property
    def label_tree(self):
        return self._label_tree

    @property
    def label_set(self):
        return self._label_set

    @property
    def mask_to_label(self):
        return self._mask_to_label

    @property
    def mask_name(self):
        if self._mask_name is not None:
            return self._mask_name
        return f"{self._mask_name_prefix}{self._mask_id:0>{self._zfill}}"

    def merge(self, mask: numpy.ndarray, mask_name=None):
        """Merge the sequence of masks in the specified order"""
        # temporarily set self._mask_name
        self._mask_name = mask_name
        self += mask
        # reset _mask_name
        self._mask_name = None

    def _update_label(self):
        """Update the label to the next value to use"""
        # first, add the current label to the label set and the label tree
        self._label_set.add(self._label)
        self._label_tree[str(self._label)] = 0  # this is a direct child of the root (0, repr. background)
        self._mask_to_label[self.mask_name] = int(self._label)
        # get the new resulting labels: all those not already in the label set
        new_labels = set(numpy.unique(self._data)).difference(self._label_set.union([0]))
        # determine the parentage for each new label
        for new_label in new_labels:
            for _label in self._label_set:
                # since we added the content of the merged mask to the new mask then any new labels are sum of
                # current label and the label for the current mask i.e. new_label = previous_label + label;
                # we are only interested in associating the pair to the new label; the new_label now becomes
                # a leaf with parent nodes being the previous_label and the label for the last mask
                # we store them sorted
                if new_label == _label + self._label:
                    self._label_tree[str(new_label)] = sorted([int(new_label - _label), int(new_label - self._label)])
        # finally, we should not forget to now include the new labels into the label set
        self._label_set |= new_labels
        self._label = numpy.amax(self._data) + 1
        self._mask_id += 1

    def __add__(self, mask) -> 'MergedMask':
        self._init_data(mask)
        self._data += mask * self._label  # merge the current mask to the merged mask and label it uniquely
        self._update_label()
        return self

    def __radd__(self, mask) -> 'MergedMask':
        self._init_data(mask)
        self._data += mask * self._label  # merge the current mask to the merged mask and label it uniquely
        self._update_label()
        return self

    def __iadd__(self, mask) -> 'MergedMask':
        self._init_data(mask)
        self._data += mask * self._label  # merge the current mask to the merged mask and label it uniquely
        self._update_label()
        return self

    def __eq__(self, other):
        return numpy.array_equal(self.data, other.data) and self.shape == other.shape and self.dtype == other.dtype


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
    """Coroutine to check whether individual masks are binary"""
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


def check_mask_is_binary(fn, verbose=False):
    """Check whether a mask is binary or not

    :param str fn: map filename
    :param bool verbose: verbosity flag
    :return: boolean, True if binary mask
    :rtype: bool
    """
    if sys.version_info.minor > 6:
        is_binary = asyncio.run(_mask_is_binary(fn, verbose=verbose))
    else:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        is_binary = loop.run_until_complete(_mask_is_binary(fn, verbose=verbose))
        loop.close()
    return is_binary


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
            break
        previous_mask = mask
    # the max should be 1
    max_voxel_value = numpy.amax(current_data)
    return max_voxel_value == 1


def _mergemask(masks: List[str]) -> 'MergedMask':
    """The mergemask workhorse which does the actual merging"""
    from ..readers.mapreader import Map
    import pathlib
    merged_mask = MergedMask()  # everything is initialised from the first mask since masks are homogeneous
    for mask in masks:
        this_map = Map(mask)
        merged_mask.merge(this_map.voxels, mask_name=pathlib.Path(mask).name)
    return merged_mask  # that's it!


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
    # fail fast: ensure the output does not exist
    outfile = pathlib.Path(f"{args.output_prefix}.{args.mask_extension}")
    if not args.overwrite and outfile.exists():
        print_date(f"error: the file already exists; use --overwrite to overwrite the existing merged_mask or set a "
                   f"new output prefix using --output-prefix")
        return 64
    # ensure that the files are binary
    if args.skip_assessment:
        print_date("info: skipping mask assessment; assuming all masks are binary...")
    elif not _masks_all_binary(args, configs) and not args.skip:
        print_date(f"error: one or more masks are non-binary; use --verbose to view details")
        return 65
    # todo: allow cases where one or more files are non-binary
    # ensure that they don't overlap each other
    if not _masks_no_overlap(args, configs) and not args.allow_overlap:
        print_date(f"error: one or more masks overlap; use --verbose to view details")
        print_date(f"info: if overlapping segments are expected re-run with the --allow-overlap argument; "
                   f"see 'sff prep mergemask' for more information")
        return 65
    # now we can merge masks
    if args.verbose:
        print_date(f"info: proceeding to merge masks...")
    merged_mask = _mergemask(args.masks)
    if args.verbose:
        print_date(f"info: merge complete...")
    if args.verbose:
        print_date(f"info: attempting to write output to '{args.output_prefix}.{args.mask_extension}'...")
    with mrcfile.new(f"{args.output_prefix}.{args.mask_extension}", overwrite=args.overwrite) as mrc:
        with mrcfile.open(args.masks[0]) as one_mask:
            mrc.set_data(merged_mask.data)
            mrc.voxel_size = one_mask.voxel_size
    if args.verbose:
        print_date(f"info: attempting to write mask metadata below to '{args.output_prefix}.json'...")
    # create the mask metadata
    mask_metadata = dict()
    mask_metadata['mask_to_label'] = merged_mask.mask_to_label
    mask_metadata['label_tree'] = merged_mask.label_tree
    data = json.dumps(mask_metadata, indent=4)
    with open(f"{args.output_prefix}.json", 'w') as label_file:
        if args.verbose:
            print_date(f"info: mask metadata:\n{data}")
        print(data, file=label_file)
    if args.verbose:
        print_date(f"info: merge complete!")
    return 0
