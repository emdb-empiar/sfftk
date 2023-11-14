import argparse
import pathlib
import shlex
import sys
import unittest

from sfftk.readers import starreader


def convert_motive_list_to_relion_star(args):
    # how we will translate the fields; preserve the column order
    translate_header = {
        '_motl_idx': '_rlnMotlIdx',  #
        '_tomo_num': '_rlnTomoNum',  #
        '_object': '_rlnObject',  #
        '_subtomo_num': '_rlnSubtomoNum',  #
        '_halfset': '_rlnHalfset',  #
        '_orig_x': '_rlnCoordinateX',  #
        '_orig_y': '_rlnCoordinateY',  #
        '_orig_z': '_rlnCoordinateZ',  #
        '_score': '_rlnScore',  #
        '_x_shift': '_rlnOriginXAngstrom',  #
        '_y_shift': '_rlnOriginYAngstrom',  #
        '_z_shift': '_rlnOriginZAngstrom',  #
        '_phi': '_rlnAngleRot',  #
        '_psi': '_rlnAnglePsi',  #
        '_the': '_rlnAngleTilt',  #
        '_class': '_rlnClass',  #
    }

    reader = starreader.StarReader(verbose=args.verbose)
    reader.parse(args.motive_list)

    _header = reader.tables['default'].header
    for original_name, new_name in translate_header.items():
        _header = _header.replace(original_name, new_name)

    # print(f"\ndata_{reader.name}\n", file=sys.stdout)
    # print(_header, file=sys.stdout)
    # print('', file=sys.stdout)
    # for row in reader.tables['default']:
    #     print(row.raw_data(), file=sys.stdout)

π
def main():
    parser = argparse.ArgumentParser(description="Convert a motive list to a relion star file")
    parser.add_argument("motive_list", type=pathlib.Path, help="The name of the motive list file.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose mode")
    parser.add_argument('-c', '--add-column', action='append', help="Add a column with the specified value to the output star file")
    args = parser.parse_args()
    print(args)
    print(f"add_column: {args.add_column}")
    try:
        assert args.motive_list.exists()
    except AssertionError:
        print(f"{args.motive_list} does not exist", file=sys.stderr)
        return 1
    convert_motive_list_to_relion_star(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())


class Tests(unittest.TestCase):
    TEST_DATA_PATH = pathlib.Path(__file__).parent.parent / 'test_data'
    def test_with_args(self):
        sys.argv = shlex.split(f"motivelist_to_relionstar.py {self.TEST_DATA_PATH / 'misc/motivelist.star'}")
        print(sys.argv, file=sys.stderr)
        _exit = main()
        self.assertEqual(0, _exit)

    def test_no_args(self):
        sys.argv = ['motivelist_to_relionstar.py']
        with self.assertRaises(SystemExit):
            main()
