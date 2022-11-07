"""
:py:mod:`sfftk.sff` is the main entry point for performing command-line operations.
"""
import os
import re
import sys

from sfftkrw import sffrw
from sfftkrw.core import _dict_iter_values
from sfftkrw.core.print_tools import print_date

from .core.parser import _get_file_extension

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = '2017-02-15'
__updated__ = '2018-02-23'


def handle_prep_mergemask(args, configs):
    """Handle `prep mergemask`

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    if all(map(lambda mask: re.search(r'.*\.(map|mrc|rec)$', mask, re.IGNORECASE), args.masks)):
        from .core.prep import mergemask
        return mergemask(args, configs)
    return 65


def handle_prep(args, configs):
    """Handle `prep` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    if args.prep_subcommand == 'binmap':
        if re.match(r'.*\.(map|mrc|rec)$', args.from_file, re.IGNORECASE):
            from .core.prep import bin_map
            return bin_map(args, configs)
        else:
            print_date("No prep protocol for file type {}".format(args.from_file))
            return 65
    elif args.prep_subcommand == 'transform':
        if re.match(r'.*\.(stl)$', args.from_file, re.IGNORECASE):
            from .core.prep import transform
            return transform(args, configs)
        else:
            print_date("No prep protocol for file type {}".format(args.from_file))
            return 65
    elif args.prep_subcommand == 'mergemask':
        return handle_prep_mergemask(args, configs)


def handle_convert(args, configs):  # @UnusedVariable
    """
    Handle `convert` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    try:
        if args.multi_file:
            raise ValueError
        # .h5 is ambiguous, so we check whether we are referring to an EMDB-SFF file
        ext = _get_file_extension(args.from_file)
        if ext == 'h5' and args.subtype_index != 2:
            raise ValueError
        # if no ValueError is raised we assume we are dealing with an EMDB-SFF file
        # we delegate handling to sfftk-rw
        return sffrw.handle_convert(args)
    except (ValueError, KeyError):
        if args.multi_file:
            if re.match(r'.*\.(map|mrc|rec)$', args.from_file[0], re.IGNORECASE):
                from .formats.map import BinaryMaskSegmentation
                seg = BinaryMaskSegmentation(args.from_file)
            elif re.match(r'.*\.stl$', args.from_file[0], re.IGNORECASE):
                from .formats.stl import STLSegmentation
                seg = STLSegmentation(args.from_file)
            else:
                raise ValueError("Unknown file type '{}'".format(', '.join(args.from_file)))
        else:
            if re.match(r'.*\.mod$', args.from_file, re.IGNORECASE):
                if args.verbose:
                    print_date("Converting from IMOD file {}".format(args.from_file))
                from .formats.mod import IMODSegmentation
                seg = IMODSegmentation(args.from_file)
                if not seg.has_mesh_or_shapes:
                    print_date("IMOD segmentation missing meshes or shapes. Please add meshes using imodmesh utility")
                    return 1
                if args.verbose:
                    print_date("Created IMODSegmentation object")
            elif re.match(r'.*\.seg$', args.from_file, re.IGNORECASE):
                from .formats.seg import SeggerSegmentation
                seg = SeggerSegmentation(args.from_file, top_level=not args.all_levels)
            elif re.match(r'.*\.surf$', args.from_file, re.IGNORECASE):
                from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
                seg = AmiraHyperSurfaceSegmentation(args.from_file)
            elif re.match(r'.*\.am$', args.from_file, re.IGNORECASE):
                from .formats.am import AmiraMeshSegmentation
                seg = AmiraMeshSegmentation(args.from_file)
            elif re.match(r'.*\.(map|mrc|rec)$', args.from_file, re.IGNORECASE):
                if args.label_tree is not None:  # merged mask
                    from .formats.map import MergedMaskSegmentation
                    seg = MergedMaskSegmentation(args.from_file, label_tree=args.label_tree)
                else:  # single binary mask
                    from .formats.map import BinaryMaskSegmentation
                    seg = BinaryMaskSegmentation([args.from_file])
            elif re.match(r'.*\.stl$', args.from_file, re.IGNORECASE):
                from .formats.stl import STLSegmentation
                seg = STLSegmentation([args.from_file])
            elif re.match(r'.*\.h5$', args.from_file, re.IGNORECASE):
                ext = _get_file_extension(args.from_file)
                # this is how we handle extension disambiguation
                # the subtype index values are according to the sfftk.core.parser.EXTENSION_SUBTYPE_INDICES dict
                if args.subtype_index > -1:
                    if args.subtype_index == 0:
                        from .formats.survos import SuRVoSSegmentation
                        seg = SuRVoSSegmentation(args.from_file)
                    elif args.subtype_index == 1:
                        from .formats.ilastik import IlastikSegmentation
                        seg = IlastikSegmentation(args.from_file)
                else:
                    print_date("Ambiguous file extension '{ext}'. Please select the right type or use the "
                               "--subtype-index <value> option".format(ext=ext))
                    return 64
            else:
                raise ValueError("Unknown file type %s" % args.from_file)
        # now get the transform
        transform = None
        if args.image:
            from .readers.mapreader import compute_transform
            transform = compute_transform(args.image)
        sff_seg = seg.convert(details=args.details, verbose=args.verbose,
                              transform=transform)  # convert according to args
        # export as args.format
        if args.verbose:
            print_date("Exporting to {}".format(args.output))
        sff_seg.export(args.output, args)
        if args.verbose:
            print_date("Done")

    return 0


def handle_notes_search(args, configs):
    """Handle `search` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes import find
    # query
    resource = find.SearchResource(args, configs)
    # fixme: use print_date
    print(resource)
    # search
    result = resource.search()
    if result is not None:
        # fixme: use print_date
        print(result)
        return 0
    else:
        return 65


def handle_notes_list(args, configs):
    """Handle `list` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes.view import list_notes
    status = list_notes(args, configs)
    return status


def handle_notes_show(args, configs):
    """Handle `show` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes.view import show_notes
    status = show_notes(args, configs)
    return status


def _handle_notes_modify(args, configs):
    """Handle creation of temporary file as either SFF, HFF or JSON

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    temp_file = configs['__TEMP_FILE']
    temp_file_ref = configs['__TEMP_FILE_REF']
    print_date("Temporary file shorthand to use: {}".format(temp_file_ref))
    if args.sff_file == temp_file_ref:
        if os.path.exists(temp_file):
            args.sff_file = temp_file
        else:
            print_date(
                "Temporary file {} does not exist. Try invoking an edit ('add', 'edit', 'del') "
                "action on a valid EMDB-SFF file.".format(temp_file),
                stream=sys.stdout
            )
            sys.exit(65)
    else:
        if os.path.exists(temp_file):
            print_date("Found temp file {}. Either run 'save' or 'trash' to \
discard changes before working on another file.".format(temp_file), stream=sys.stdout)
            sys.exit(65)
        else:
            if re.match(r'.*\.sff$', temp_file, re.IGNORECASE):
                # copy the actual file to the temp file
                import shutil
                print_date("Modifications to be made.", stream=sys.stdout)
                print_date("Copying {} to temp file {}...".format(args.sff_file, temp_file), stream=sys.stdout)
                shutil.copy(args.sff_file, temp_file)
                args.sff_file = temp_file
            elif re.match(r'.*\.json$', temp_file, re.IGNORECASE):
                if args.config_path:
                    cmd = "convert -v {} -o {} -x --config-path {}".format(args.sff_file, temp_file, args.config_path)
                elif args.shipped_configs:
                    cmd = "convert -v {} -o {} -x --shipped-configs".format(args.sff_file, temp_file)
                else:
                    cmd = "convert -v {} -x -o {}".format(args.sff_file, temp_file)
                from .core.parser import parse_args
                _args, _configs = parse_args(cmd, use_shlex=True)
                if not _args:
                    sys.exit(64)
                handle_convert(_args, configs)  # convert
                args.sff_file = temp_file
            elif re.match(r'.*\.hff$', temp_file, re.IGNORECASE):
                if args.config_path:
                    cmd = "convert -v {} -o {} --config-path {}".format(args.sff_file, temp_file, args.config_path)
                elif args.shipped_configs:
                    cmd = "convert -v {} -o {} --shipped-configs".format(args.sff_file, temp_file)
                else:
                    cmd = "convert -v {} -o {}".format(args.sff_file, temp_file)
                from .core.parser import parse_args  # @Reimport
                _args, _configs = parse_args(cmd, use_shlex=True)
                if not _args:
                    # todo: fix this (only main() can call sys.exit())
                    sys.exit(64)
                handle_convert(_args, configs)  # convert
                args.sff_file = temp_file
    return args


def handle_notes_add(args, configs):
    """Handle `add` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import add_note
    return add_note(args, configs)


def handle_notes_edit(args, configs):
    """Handle `edit` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import edit_note
    return edit_note(args, configs)


def handle_notes_del(args, configs):
    """Handle `del` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import del_note
    return del_note(args, configs)


def handle_notes_copy(args, configs):
    """Handle `copy` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import copy_notes
    return copy_notes(args, configs)


def handle_notes_clear(args, configs):
    """Handle `copy` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import clear_notes
    return clear_notes(args, configs)


def handle_notes_merge(args, configs):
    """Handle `merge` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes.modify import merge
    return merge(args, configs)


def handle_notes_save(args, configs):
    """Handle the `save` subcommand` of the `notes` subcommand`

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes.modify import save
    return save(args, configs)


def handle_notes_trash(args, configs):
    """Handle the `trash` subcommand` of the `notes` subcommand`

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    from sfftk.notes.modify import trash
    return trash(args, configs)


def handle_notes(args, configs):
    """Handle `notes` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    if args.notes_subcommand == "search":
        return handle_notes_search(args, configs)
    elif args.notes_subcommand == "list":
        return handle_notes_list(args, configs)
    elif args.notes_subcommand == "show":
        return handle_notes_show(args, configs)
    elif args.notes_subcommand == "add":
        return handle_notes_add(args, configs)
    elif args.notes_subcommand == "edit":
        return handle_notes_edit(args, configs)
    elif args.notes_subcommand == "del":
        return handle_notes_del(args, configs)
    elif args.notes_subcommand == "copy":
        return handle_notes_copy(args, configs)
    elif args.notes_subcommand == "clear":
        return handle_notes_clear(args, configs)
    elif args.notes_subcommand == "merge":
        return handle_notes_merge(args, configs)
    elif args.notes_subcommand == "save":
        return handle_notes_save(args, configs)
    elif args.notes_subcommand == "trash":
        return handle_notes_trash(args, configs)


def handle_view(args, configs):  # @UnusedVariable
    """Handle `view` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    # fixme: use print_date
    try:
        sffrw.handle_view(args)
    except ValueError:
        if re.match(r'.*\.mod$', args.from_file, re.IGNORECASE):
            from .formats.mod import IMODSegmentation
            seg = IMODSegmentation(args.from_file)
            print("*" * 50)
            print("IMOD Segmentation version {}".format(seg.header.version))
            print("Segmentation name: {}".format(seg.header.name))
            print("Format: IMOD")
            mesh_count = 0
            for objt in _dict_iter_values(seg.header.objts):
                mesh_count += objt.meshsize
            if mesh_count > 0:
                print("Auxiliary descriptors: meshes")
            print("Pixel size: {}".format(seg.header.pixsize))
            print("Pixel units: {}".format(seg.header.named_units))
            print("xmax, ymax, zmax: {}".format((seg.header.xmax, seg.header.ymax, seg.header.zmax)))
            print("No. of segments: {}".format(len(seg.segments)))
            print("*" * 50)
            print(seg)
            print("*" * 50)
            if args.show_chunks:
                from .readers import modreader
                if args.verbose:
                    modreader.print_model(args.from_file)
                else:
                    modreader.show_chunks(args.from_file)
        elif re.search(r'.*\.(map|mrc|rec)$', args.from_file, re.IGNORECASE):
            if args.transform:  # we're dealing with an image
                print_date("Image space to physical space transform CCP4 MAP")
                from .readers.mapreader import compute_transform
                transform = compute_transform(args.from_file)
                if args.print_csv:
                    print_date("Print type: CSV (use -h/--help for other formats)")
                    print(','.join(map(str, transform.flatten().tolist())))
                elif args.print_ssv:
                    print_date("Print type: SSV (use -h/--help for other formats)")
                    print(' '.join(map(str, transform.flatten().tolist())))
                else:
                    print_date("Print type: numpy arrray (use -h/--help for other formats)")
                    print(transform)
            else:  # we're dealing with a mask/segmentation
                # todo: replace with BinaryMaskSegmentation
                from .formats.map import MapSegmentation
                seg = MapSegmentation([args.from_file], header_only=True)
                print("*" * 50)
                print("CCP4 Mask Segmentation")
                print("*" * 50)
                # fixme: use _str
                print(str(seg.segments[0].annotation._map_obj))
                print("*" * 50)
        elif re.match(r'.*\.stl$', args.from_file, re.IGNORECASE):
            print("*" * 50)
            print("STL Segmentation")
            print("*" * 50)
        else:
            print_date("Not implemented view for files of type .{}".format(args.from_file.split('.')[-1]), sys.stderr)
    return 0


def handle_config(args, configs):
    """Handle `view` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    if args.config_subcommand == "get":
        from .core.configs import get_configs
        return get_configs(args, configs)
    elif args.config_subcommand == "set":
        from .core.configs import set_configs
        return set_configs(args, configs)
    elif args.config_subcommand == "del":
        from .core.configs import del_configs
        return del_configs(args, configs)


def _module_test_runner(mod, args):
    """Module test runner

    :param module mod: the module where the tests will be found
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(mod)
    if not args.dry_run:
        unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0


def _testcase_test_runner(tc, args):
    """TestCase test runner

    :param tc: test case
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(tc)
    if not args.dry_run:
        unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0


def _discover_test_runner(path, args, top_level_dir=None):
    """Test runner that looks for tests in *path*

    :param str path: path to search for tests
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param str top_level_dir: the name of the top level directory (default: None)
    :return exit_status: exit status
    :rtype exit_status: int
    """
    import unittest
    suite = unittest.TestLoader().discover(path, top_level_dir=top_level_dir)
    if not args.dry_run:
        unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0


def handle_tests(args, configs):
    """Handle `test` subcommand

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return exit_status: exit status
    :rtype exit_status: int
    """
    if 'all' in args.tool:
        # sfftk-rw tests
        sffrw.handle_tests(args)
        # sfftk tests
        from .unittests import test_main
        _module_test_runner(test_main, args)
        _discover_test_runner("sfftk.unittests", args)
    else:
        if 'main' in args.tool:
            sffrw.handle_tests(args)
        if 'core' in args.tool:
            sffrw.handle_tests(args)
        if 'schema' in args.tool:
            sffrw.handle_tests(args)
        if 'all_sfftk' in args.tool:
            from .unittests import test_main
            _module_test_runner(test_main, args)
            _discover_test_runner("sfftk.unittests", args)
        if 'main_sfftk' in args.tool:
            from .unittests import test_main
            _module_test_runner(test_main, args)
        if 'formats' in args.tool:
            from .unittests import test_formats
            _module_test_runner(test_formats, args)
        if 'readers' in args.tool:
            from .unittests import test_readers
            _module_test_runner(test_readers, args)
        if 'notes' in args.tool:
            from .unittests import test_notes
            _module_test_runner(test_notes, args)
        return 0


def main():
    try:
        from .core.parser import parse_args
        args, configs = parse_args(sys.argv[1:])
        # missing args
        if args != 0 and isinstance(args, int):
            return args
        elif args == 0:  # e.g. show version has no error but has no handler either
            return 0
        # subcommands
        if args.subcommand == 'prep':
            return handle_prep(args, configs)
        elif args.subcommand == 'convert':
            return handle_convert(args, configs)
        elif args.subcommand == 'notes':
            return handle_notes(args, configs)
        elif args.subcommand == "view":
            return handle_view(args, configs)
        elif args.subcommand == "config":
            return handle_config(args, configs)
        elif args.subcommand == "tests":
            return handle_tests(args, configs)

    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
