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
import struct
import sys
import tempfile

from sfftk.core.configs import get_configs

from . import schema
from .core.print_tools import print_date


configs = get_configs()
    
__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = '2017-02-15'



"""
:TODO: add details!!!
"""

def create_mod(seg):
    """Convert EMDB-SFF contourList segmentation to IMOD binary format
    
    :param seg: EMDB-SFF segmentation object
    :type seg: sfftk.schema.SFFSegmentation
    :return str bindata: binary packed string
    """
    bindata = struct.pack('>8s', 'IMODV1.2') # header
    bindata += struct.pack('>128s', seg.name.ljust(128)) # name
    if seg.boundingBox.xmax is not None:
        bindata += struct.pack('>3i', seg.boundingBox.xmax, seg.boundingBox.ymax, seg.boundingBox.zmax) # xmax, ymax, zmax
    bindata += struct.pack('>i', len(seg.segments)) # objsize
    flags = [0] * 32
    flags[-13] = 1 # Bit 13 on : mat1 and mat3 are stored as bytes
    flags[-14] = 1 # Bit 14 on : otrans has image origin values
    flags[-15] = 1 # Bit 15 on : current tilt angles are stored correctly
    flags[-16] = 1 # Bit 16 on : model last viewed on Y/Z flipped or rotated image
    bindata += struct.pack('>I', int("".join(map(str, flags)), 2)) # flags
    bindata += struct.pack('>i', 1) # drawmode
    bindata += struct.pack('>i', 2) # mousemode
    bindata += struct.pack('>i', 136) # blacklevel
    bindata += struct.pack('>i', 195) # whitelevel
    bindata += struct.pack('>3f', 0, 0, 0) # xoffset, yoffset, zoffset
    bindata += struct.pack('>3f', 1.0, 1.0, 1.5) # xscale, yscale, zscale
    bindata += struct.pack('>i', 1) # object
    bindata += struct.pack('>i', 20) # contour
    bindata += struct.pack('>i', -1) # point
    bindata += struct.pack('>i', 3) # res
    bindata += struct.pack('>i', 128) # thresh
    bindata += struct.pack('>f', 2.20196008682) # pixsize
    bindata += struct.pack('>i', -9) # units
    bindata += struct.pack('>i', 600936520) # csum
    bindata += struct.pack('>3f', 0, 0, 0) # alpha, beta, gamma
    # objts
    for segment in seg.segments:
        bindata += struct.pack('>4s', 'OBJT')
        bindata += struct.pack('>64s', 'segment_{}'.format(segment.id).ljust(64)) # name
        bindata += struct.pack('>16I', *([0] * 16)) # extra
        bindata += struct.pack('>I', len(segment.contours)) # contsize
        flags = [0] * 32
        flags[-9] = 1 # contours have scattered points
        flags[-11] = 1 # do not draw contours in 3D
        flags[-12] = 1 # Use stored values to modify drawing
        bindata += struct.pack('>I', int("".join(map(str, flags)), 2)) # flags
        bindata += struct.pack('>i', 0) # axis
        bindata += struct.pack('>i', 1) # drawmode
        red, green, blue, alpha = segment.colour.rgba.value
        bindata += struct.pack('>3f', red, green, blue) # red, green, blue
        bindata += struct.pack('>i', 0) # pdrawsize
        bindata += struct.pack('>B', 1) # symbol
        bindata += struct.pack('>B', 3) # symsize
        bindata += struct.pack('>B', 1) # linewidth2
        bindata += struct.pack('>B', 1) # linewidth
        bindata += struct.pack('>B', 0) # linesty
        bindata += struct.pack('>B', 0) # symflags
        bindata += struct.pack('>B', 0) # sympad
        bindata += struct.pack('>B', int(100 - alpha*100)) # trans
        bindata += struct.pack('>i', 0) # meshsize
        bindata += struct.pack('>i', 0) # surfsize
        # conts
        for contour in segment.contours:
            bindata += struct.pack('>4s', 'CONT')
            bindata += struct.pack('>i', len(contour)) # psize
            bindata += struct.pack('>I', 0) # flags
            bindata += struct.pack('>i', 0) # time
            bindata += struct.pack('>i', 0) # surf
            points = list()
            for point in contour.points:
                points += [point.x, point.y, point.z]
            bindata += struct.pack('>{}f'.format(3*len(contour)), *points) # pt
    # minx
    data_array = map(float, seg.transforms[0].data_array.flatten().tolist())
    bindata += struct.pack('>4s', 'MINX')
    bindata += struct.pack('>i', 72) # bytes
    bindata += struct.pack('>3f', 0.0, 0.0, 0.0) # oscale
    bindata += struct.pack('>3f', data_array[3],data_array[7], data_array[11]) # otrans
    bindata += struct.pack('>3f', 0.0, 0.0, 0.0) # orot
    bindata += struct.pack('>3f', data_array[0],data_array[5], data_array[10]) # cscale
    bindata += struct.pack('>3f', data_array[3],data_array[7], data_array[11]) # ctrans
    bindata += struct.pack('>3f', 0.0, 0.0, 0.0) # crot
    # ieof
    bindata += struct.pack('>4c', *list('IEOF'))
    return bindata

def run_imodmesh(mod_file):
    """Append meshes using imodmesh
    
    :param str mod_file: name of the IMOD file
    :return int status: exit status of command line execution of imodmesh
    """
    import subprocess
    status = subprocess.call("imodmesh -c -s -P 2 {}".format(mod_file).split(' '))
    return status

def handle_convert(args):
    """
    Handle `convert` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
            
    """
    :TODO: include `name`, `details` and other arguments to be passed to the `read_*` methods
    """
    if re.match(r'.*\.mod$', args.from_file, re.IGNORECASE):
        if args.verbose:
            print_date("Converting from IMOD file {}".format(args.from_file))
        from .formats.mod import IMODSegmentation
        seg = IMODSegmentation(args.from_file, re.IGNORECASE)
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
        # convert contours to meshes
        if args.contours_to_mesh:
            if args.verbose:
                print_date("Attempting converstion of contourList to meshList".format(args.from_file))
            pd = seg.primaryDescriptor
            if pd == "contourList":
                """
                :TODO: first check if there are populated meshes; if so only change the primaryDescriptor
                """
                mod = create_mod(seg)
                mod_file = tempfile.NamedTemporaryFile('w+b', dir=".", suffix=".mod", delete=False)
                with open(mod_file.name, 'wb') as m:
                    m.write(mod)
                run_imodmesh(mod_file.name)
                from .formats.mod import IMODSegmentation
                mod_seg = IMODSegmentation(mod_file.name)
                seg = mod_seg.convert()
                seg.primaryDescriptor = "meshList"
                seg.contours = None
            else:
                print_date("Error: wrong primary descriptor type ({}); should be 'contourList'".format(pd))
                return 1
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
        sff_seg = seg    # no conversion needed
    else:
        sff_seg = seg.convert(args) # convert according to args
    # export as args.format
    if args.verbose:
        print_date("Exporting to {}".format(args.output))
    sff_seg.export(args.output)
    if args.verbose:
        print_date("Done")
    
    return 0

def handle_notes_search(args):
    """Handle `search` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes import find
    # query
    query = find.SearchQuery(args)
    # search
    results = query.search()
    # view
    print_date("\033[0;33m\r", incl_date=False, newline=False)
    print results
    print_date("\033[0;0m\r", incl_date=False, newline=False)
    return 0

def handle_notes_list(args):
    """Handle `list` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes.view import list_notes
    status = list_notes(args)
    print_date("\033[0;0m\r", incl_date=False, newline=False)
    return status

def handle_notes_show(args):
    """Handle `show` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes.view import show_notes
    status = show_notes(args)
    print_date("\033[0;0m\r", incl_date=False, newline=False)
    return status

def _handle_notes_modify(args):
    """Handle creation of temporary file as either SFF, HFF or JSON
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
                cmd = shlex.split("convert -v {} -o {}".format(args.sff_file, temp_file))
                from .core.parser import parse_args
                _args = parse_args(cmd) 
                handle_convert(_args) # convert
                args.sff_file = temp_file
            elif re.match(r'.*\.hff$', temp_file, re.IGNORECASE):
                cmd = shlex.split("convert -v {} -o {}".format(args.sff_file, temp_file))
                from .core.parser import parse_args  # @Reimport
                _args = parse_args(cmd) 
                handle_convert(_args) # convert
                args.sff_file = temp_file
    return args

def handle_notes_add(args):
    """Handle `add` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    args = _handle_notes_modify(args)
    from sfftk.notes.modify import add_note
    return add_note(args)
                      
def handle_notes_edit(args):
    """Handle `edit` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    args = _handle_notes_modify(args)
    from sfftk.notes.modify import edit_note
    return edit_note(args)

def handle_notes_del(args):
    """Handle `del` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    args = _handle_notes_modify(args)
    from sfftk.notes.modify import del_note
    return del_note(args)

def handle_notes_merge(args):
    """Handle `merge` subcommand of `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes.modify import merge
    return merge(args)
    
def handle_notes_save(args):
    """Handle the `save` subcommand` of the `notes` subcommand`
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes.modify import save
    return save(args)

def handle_notes_trash(args):
    """Handle the `trash` subcommand` of the `notes` subcommand`
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    from sfftk.notes.modify import trash
    return trash(args)
      
def handle_notes(args):
    """Handle `notes` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
    """
    if args.notes_subcommand == "search":
        return handle_notes_search(args)
    elif args.notes_subcommand == "list":
        return handle_notes_list(args)
    elif args.notes_subcommand == "show":
        return handle_notes_show(args)
    elif args.notes_subcommand == "add":
        return handle_notes_add(args)
    elif args.notes_subcommand == "edit":
        return handle_notes_edit(args)
    elif args.notes_subcommand == "del":
        return handle_notes_del(args)
    elif args.notes_subcommand == "merge":
        return handle_notes_merge(args)
    elif args.notes_subcommand == "save":
        return handle_notes_save(args)
    elif args.notes_subcommand == "trash":
        return handle_notes_trash(args)

def handle_view(args):
    """Handle `view` subcommand
    
    :param args: parsed arguments
    :type args: `argparse.Namespace`
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

def main():
    try:
        from sfftk.core.parser import parse_args
        args = parse_args(sys.argv[1:])
        # missing args
        if not args:
            return 1  
        # subcommands
        if args.subcommand == 'convert':
            return handle_convert(args)
        if args.subcommand == 'notes':
            return handle_notes(args)
        if args.subcommand == "view":
            return handle_view(args)
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
    
