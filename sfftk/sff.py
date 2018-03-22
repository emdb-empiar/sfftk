#!/usr/local/bin/python2.7
# encoding: utf-8
# sff.py
"""
sfftk.sff -- Toolkit to handle operations for EMDB-SFF files

sfftk.sff is the main entry point for performing command-line operations.
"""
import os
import re
import shlex
import sys

from . import schema
from .core.print_tools import print_date

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = '2017-02-15'
__updated__ = '2018-02-23'


def handle_convert(args, configs):  # @UnusedVariable
    """
    Handle `convert` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    if re.match(r'.*\.mod$', args.from_file, re.IGNORECASE):
        if args.verbose:
            print_date("Converting from IMOD file {}".format(args.from_file))
        from .formats.mod import IMODSegmentation
        seg = IMODSegmentation(args.from_file, re.IGNORECASE)
        if not seg.has_mesh_or_shapes:
            print_date("IMOD segmentation missing meshes or shapes. Please add meshes using imodmesh utility")
            return 1
        if args.verbose:
            print_date("Created IMODSegmentation object")
    elif re.match(r'.*\.seg$', args.from_file, re.IGNORECASE):
        from .formats.seg import SeggerSegmentation
        seg = SeggerSegmentation(args.from_file, top_level=args.top_level_only)
    elif re.match(r'.*\.surf$', args.from_file, re.IGNORECASE):
        from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
        seg = AmiraHyperSurfaceSegmentation(args.from_file)
    elif re.match(r'.*\.am$', args.from_file, re.IGNORECASE):
        from .formats.am import AmiraMeshSegmentation
        seg = AmiraMeshSegmentation(args.from_file)
    elif re.match(r'.*\.map$', args.from_file, re.IGNORECASE):
        from .formats.map import MapSegmentation
        seg = MapSegmentation(args.from_file)
    elif re.match(r'.*\.stl$', args.from_file, re.IGNORECASE):
        from .formats.stl import STLSegmentation
        seg = STLSegmentation(args.from_file)
    elif re.match(r'.*\.sff$', args.from_file, re.IGNORECASE):
        if args.verbose:
            print_date("Converting from EMDB-SFf (XML) file {}".format(args.from_file))
        seg = schema.SFFSegmentation(args.from_file)
    elif re.match(r'.*\.hff$', args.from_file, re.IGNORECASE):
        if args.verbose:
            print_date("Converting from EMDB-SFF (HDF5) file {}".format(args.from_file))
        seg = schema.SFFSegmentation(args.from_file)
        if args.verbose:
            print_date("Created SFFSegmentation object")
    elif re.match(r'.*\.json$', args.from_file, re.IGNORECASE):
        if args.verbose:
            print_date("Converting from EMDB-SFF (JSON) file {}".format(args.from_file))
        seg = schema.SFFSegmentation(args.from_file)
        if args.verbose:
            print_date("Created SFFSegmentation object")
    else:
        raise ValueError("Unknown file type %s" % args.from_file)
    # export (convert first if needed)
    if isinstance(seg, schema.SFFSegmentation):
        sff_seg = seg  #  no conversion needed
        if args.primary_descriptor is not None:
            sff_seg.primaryDescriptor = args.primary_descriptor
        if args.details is not None:
            sff_seg.details = args.details
    else:
        sff_seg = seg.convert(args)  # convert according to args
    # export as args.format
    if args.verbose:
        print_date("Exporting to {}".format(args.output))
    sff_seg.export(args.output)
    if args.verbose:
        print_date("Done")

    return 0


def handle_notes_search(args, configs):
    """Handle `search` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes import find
    # query
    resource = find.SearchResource(args, configs)
    # search
    results = resource.search()
    # view
    print results
    return os.EX_OK


def handle_notes_list(args, configs):
    """Handle `list` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes.view import list_notes
    status = list_notes(args, configs)
    print_date("\033[0;0m\r", incl_date=False, newline=False)
    return status


def handle_notes_show(args, configs):
    """Handle `show` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes.view import show_notes
    status = show_notes(args, configs)
    print_date("\033[0;0m\r", incl_date=False, newline=False)
    return status


def _handle_notes_modify(args, configs):
    """Handle creation of temporary file as either SFF, HFF or JSON
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    temp_file = configs['__TEMP_FILE']
    temp_file_ref = configs['__TEMP_FILE_REF']
    print_date("Temporary file shorthand to use: {}".format(temp_file_ref))
    if args.sff_file == temp_file_ref:
        if os.path.exists(temp_file):
            args.sff_file = temp_file
        else:
            print_date("Temporary file {} does not exist. \
Try invoking an edit ('add', 'edit', 'del') action on a valid EMDB-SFF file.".format(temp_file), stream=sys.stdout)
            sys.exit(1)
    else:
        if os.path.exists(temp_file):
            print_date("Found temp file {}. Either run 'save' or 'trash' to \
discard changes before working on another file.".format(temp_file), stream=sys.stdout)
            sys.exit(1)
        else:
            print_date("\033[92m\r", incl_date=False, newline=False)
            if re.match(r'.*\.sff$', temp_file, re.IGNORECASE):
                # copy the actual file to the temp file
                import shutil
                print_date("Modifications to be made.", stream=sys.stdout)
                print_date("Copying {} to temp file {}...".format(args.sff_file, temp_file), stream=sys.stdout)
                shutil.copy(args.sff_file, temp_file)
                args.sff_file = temp_file
            elif re.match(r'.*\.json$', temp_file, re.IGNORECASE):
                if args.config_path:
                    cmd = shlex.split(
                        "convert -v {} -o {} --config-path {}".format(args.sff_file, temp_file, args.config_path))
                elif args.shipped_configs:
                    cmd = shlex.split("convert -v {} -o {} --shipped-configs".format(args.sff_file, temp_file))
                else:
                    cmd = shlex.split("convert -v {} -o {}".format(args.sff_file, temp_file))
                from .core.parser import parse_args
                _args, _configs = parse_args(cmd)
                handle_convert(_args, configs)  # convert
                args.sff_file = temp_file
            elif re.match(r'.*\.hff$', temp_file, re.IGNORECASE):
                if args.config_path:
                    cmd = shlex.split(
                        "convert -v {} -o {} --config-path {}".format(args.sff_file, temp_file, args.config_path))
                elif args.shipped_configs:
                    cmd = shlex.split("convert -v {} -o {} --shipped-configs".format(args.sff_file, temp_file))
                else:
                    cmd = shlex.split("convert -v {} -o {}".format(args.sff_file, temp_file))
                from .core.parser import parse_args  # @Reimport
                _args, _configs = parse_args(cmd)
                handle_convert(_args, configs)  # convert
                args.sff_file = temp_file
    return args


def handle_notes_add(args, configs):
    """Handle `add` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import add_note
    return add_note(args, configs)


def handle_notes_edit(args, configs):
    """Handle `edit` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import edit_note
    return edit_note(args, configs)


def handle_notes_del(args, configs):
    """Handle `del` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import del_note
    return del_note(args, configs)


def handle_notes_copy(args, configs):
    """Handle `copy` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import copy_notes
    return copy_notes(args, configs)


def handle_notes_clear(args, configs):
    """Handle `copy` subcommand of `notes` subcommand

    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    args = _handle_notes_modify(args, configs)
    from sfftk.notes.modify import clear_notes
    return clear_notes(args, configs)


def handle_notes_merge(args, configs):
    """Handle `merge` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes.modify import merge
    return merge(args, configs)


def handle_notes_save(args, configs):
    """Handle the `save` subcommand` of the `notes` subcommand`
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes.modify import save
    return save(args, configs)


def handle_notes_trash(args, configs):
    """Handle the `trash` subcommand` of the `notes` subcommand`
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    from sfftk.notes.modify import trash
    return trash(args, configs)


def handle_notes(args, configs):
    """Handle `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
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
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    if re.match(r'.*\.sff$', args.from_file, re.IGNORECASE):
        seg = schema.SFFSegmentation(args.from_file)
        print "*" * 50
        print "EMDB-SFF Segmentation version {}".format(seg.version)
        print "Segmentation name: {}".format(seg.name)
        print "Format: XML"
        print "Primary descriptor: {}".format(seg.primaryDescriptor)
        print "No. of segments: {}".format(len(seg.segments))
        print "*" * 50
    elif re.match(r'.*\.hff$', args.from_file, re.IGNORECASE):
        seg = schema.SFFSegmentation(args.from_file)
        print "*" * 50
        print "EMDB-SFF Segmentation version {}".format(seg.version)
        print "Segmentation name: {}".format(seg.name)
        print "Format: HDF5"
        print "Primary descriptor: {}".format(seg.primaryDescriptor)
        print "No. of segments: {}".format(len(seg.segments))
        print "*" * 50
    elif re.match(r'.*\.json$', args.from_file, re.IGNORECASE):
        seg = schema.SFFSegmentation(args.from_file)
        print "*" * 50
        print "EMDB-SFF Segmentation version {}".format(seg.version)
        print "Segmentation name: {}".format(seg.name)
        print "Format: JSON"
        print "Primary descriptor: {}".format(seg.primaryDescriptor)
        print "No. of segments: {}".format(len(seg.segments))
        print "*" * 50
    elif re.match(r'.*\.mod$', args.from_file, re.IGNORECASE):
        from .formats.mod import IMODSegmentation
        seg = IMODSegmentation(args.from_file)
        print "*" * 50
        print "IMOD Segmentation version {}".format(seg.header.version)
        print "Segmentation name: {}".format(seg.header.name)
        print "Format: IMOD"
        print "Primary descriptor: {}".format('contours')
        mesh_count = 0
        for objt in seg.header.objts.itervalues():
            mesh_count += objt.meshsize
        if mesh_count > 0:
            print "Auxiliary descriptors: meshes"
        print "Pixel size: {}".format(seg.header.pixsize)
        print "Pixel units: {}".format(seg.header.units)
        print "xmax, ymax, zmax: {}".format((seg.header.xmax, seg.header.ymax, seg.header.zmax))
        print "No. of segments: {}".format(len(seg.segments))
        print "*" * 50
        if args.show_chunks:
            from .readers import modreader
            modreader.show_chunks(args.from_file)
    elif re.match(r'.*\.map$', args.from_file, re.IGNORECASE):
        from .formats.map import MapSegmentation
        seg = MapSegmentation(args.from_file)
        print "*" * 50
        print "CCP4/MAP Mask Segmentation"
        print "*" * 50
        print str(seg._segmentation)
        print "*" * 50
    else:
        print >> sys.stderr, "Not implemented view for files of type .{}".format(args.from_file.split('.')[-1])
    return 0


def handle_config(args, configs):
    """Handle `view` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    if args.config_subcommand == "list":
        from .core.configs import list_configs
        return list_configs(args, configs)
    elif args.config_subcommand == "get":
        from .core.configs import get_configs
        return get_configs(args, configs)
    elif args.config_subcommand == "set":
        from .core.configs import set_configs
        return set_configs(args, configs)
    elif args.config_subcommand == "del":
        from .core.configs import del_configs
        return del_configs(args, configs)
    elif args.config_subcommand == "clear":
        from .core.configs import clear_configs
        return clear_configs(args, configs)


def _module_test_runner(mod, args):
    """Module test runner 
    
    :param module mod: the module where the tests will be found
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    import unittest
    suite = unittest.TestLoader().loadTestsFromModule(mod)
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
    unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0


def _discover_test_runner(path, args):
    """Test runner that looks for tests in *path*
    
    :param str path: path to search for tests
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    import unittest
    suite = unittest.TestLoader().discover(path)
    unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
    return 0


def handle_tests(args, configs):
    """Handle `test` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Configs``
    :return int status: status
    """
    if isinstance(args.tool, str):
        from .unittests import test_main
        _module_test_runner(test_main, args)
        _discover_test_runner("sfftk.unittests", args)
    else:
        if 'main' in args.tool:
            from .unittests import test_main
            _module_test_runner(test_main, args)
        if 'core' in args.tool:
            from .unittests import test_core
            _module_test_runner(test_core, args)
        if 'schema' in args.tool:
            from .unittests import test_schema
            _module_test_runner(test_schema, args)
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
        if not args:
            return 1
        # subcommands
        if args.subcommand == 'convert':
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
        ### handle keyboard interrupt ###
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
