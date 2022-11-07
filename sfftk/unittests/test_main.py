"""
test_py

Unit tests for convert subcommand
"""
import glob
import json
import os
import sys
from io import StringIO

from sfftkrw import SFFSegmentation, SFFTransformationMatrix
from sfftkrw.unittests import Py23FixTestCase

from . import TEST_DATA_PATH
from .. import BASE_DIR
from .. import sff as Main
from ..core.parser import parse_args, cli

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-06-10'

user = 'test_user'
password = 'test'
host = 'localhost'
port = '4064'


class TestMain_handle_convert(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMain_handle_convert, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def setUp(self):
        super(TestMain_handle_convert, self).setUp()

    def tearDown(self):
        super(TestMain_handle_convert, self).tearDown()
        for s in glob.glob(os.path.join(TEST_DATA_PATH, '*.sff')):
            os.remove(s)
        for s in glob.glob(os.path.join(TEST_DATA_PATH, '*.json')):
            os.remove(s)
        for s in glob.glob(os.path.join(TEST_DATA_PATH, '*.hff')):
            os.remove(s)

    def test_subtype(self):
        """Sometimes a file extension is ambiguous; this tests the disambiguation menu"""
        sys.stdin = StringIO('0')  # SuRVoS
        args, configs = parse_args(
            'convert -o {output} {input} --config-path {config}'.format(
                output=os.path.join(TEST_DATA_PATH, 'test_data.sff'),
                input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.h5'),
                config=self.config_fn,
            ),
            use_shlex=True,
        )
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)

    def test_ilastik(self):
        """Test that we can convert .h5 for ilastik"""
        sys.stdin = StringIO('1')  # ilastik
        args, configs = parse_args('convert -o {output} {input} --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_ilastik.h5'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry for JSON
        sys.stdin = StringIO('1')  # ilastik
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_ilastik.h5'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_single_binary_mask(self):
        """Test that we can convert a single binary mask"""
        # with geometry
        input_ = os.path.join(TEST_DATA_PATH, 'segmentations', 'mergeable_1.map')
        output = os.path.join(TEST_DATA_PATH, 'test_data.sff')
        args, configs = cli(f'convert -o {output} {input_} --config-path {self.config_fn}')
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(1, len(sff_files))
        # without geometry
        output = os.path.join(TEST_DATA_PATH, 'test_data.json')
        args, configs = cli(f'convert -o {output} {input_} --exclude-geometry --config-path {self.config_fn}')
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_multiple_binary_mask(self):
        """Test that we can convert a set of binary masks"""
        # with geometry
        input_ = [
            os.path.join(TEST_DATA_PATH, 'segmentations', 'mergeable_1.map'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'mergeable_2.map'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'mergeable_3.map'),
        ]
        output = os.path.join(TEST_DATA_PATH, 'test_data.sff')
        args, configs = cli(f"convert -m -o {output} {' '.join(input_)} --config-path {self.config_fn}")
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(1, len(sff_files))
        # without geometry
        output = os.path.join(TEST_DATA_PATH, 'test_data.json')
        args, configs = cli(
            f'convert -m -o {output} {" ".join(input_)} --exclude-geometry --config-path {self.config_fn}')
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_merged_mask(self):
        """Test that we can convert a merged mask"""
        # with geometry
        input_ = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.mrc')
        input_labels = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.json')
        output = os.path.join(TEST_DATA_PATH, 'test_data.sff')
        args, configs = cli(f"convert -o {output} {input_} --label-tree {input_labels} --config-path {self.config_fn}")
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(1, len(sff_files))
        # without geometry
        output = os.path.join(TEST_DATA_PATH, 'test_data.json')
        args, configs = cli(
            f'convert -o {output} {input_} --label-tree {input_labels} --exclude-geometry --config-path {self.config_fn}')
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_seg(self):
        """Test that we can convert .seg"""
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.seg'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry for JSON
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.seg'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_seg_with_image(self):
        """Test using --image to extract the transform from the image"""
        args, configs = parse_args('convert -o {} {} --image {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'emd_1832.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'emd_1832.seg'),
            os.path.join(TEST_DATA_PATH, 'images', 'emd_1832.map'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        seg = SFFSegmentation.from_file(sff_files[0])
        # we know what the transform should be
        self.assertEqual(
            SFFTransformationMatrix(
                id=0, rows=3, cols=4,
                data="5.699999809265137 0.0 0.0 -182.39999389648438 0.0 5.699999809265137 0.0 -182.39999389648438 "
                     "0.0 0.0 5.699999809265137 -182.39999389648438"
            ),
            seg.transform_list[0]
        )
        self.assertEqual(1, len(seg.transforms))  # and there is only one transform
        # with --exclude-geometry for JSON
        args, configs = parse_args(
            'convert -o {output} {input} --exclude-geometry --image {image} --config-path {config}'.format(
                output=os.path.join(TEST_DATA_PATH, 'emd_1832.json'),
                input=os.path.join(TEST_DATA_PATH, 'segmentations', 'emd_1832.seg'),
                image=os.path.join(TEST_DATA_PATH, 'images', 'emd_1832.map'),
                config=self.config_fn,
            ), use_shlex=True
        )
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        self.assertEqual(len(sff_files), 1)
        seg = SFFSegmentation.from_file(sff_files[0])
        self.assertEqual(
            SFFTransformationMatrix(
                id=0, rows=3, cols=4,
                data="5.699999809265137 0.0 0.0 -182.39999389648438 0.0 5.699999809265137 0.0 -182.39999389648438 "
                     "0.0 0.0 5.699999809265137 -182.39999389648438"
            ),
            seg.transform_list[0]
        )
        self.assertEqual(1, len(seg.transforms))
        # now let's use a 'wrong' image to compute a different transformation matrix
        # we would expect that there will still be only one tx having the new values
        args, configs = parse_args('convert -o {} {} --image {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'emd_1832.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'emd_1832.seg'),
            os.path.join(TEST_DATA_PATH, 'images', 'emd_5625.map'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        seg = SFFSegmentation.from_file(sff_files[0])
        # we know what the transform should be
        self.assertEqual(
            SFFTransformationMatrix(
                id=0, rows=3, cols=4,
                data="4.230000087193081 0.0 0.0 -118.44000244140626 0.0 4.230000087193081 0.0 -118.44000244140626 "
                     "0.0 0.0 4.230000087193081 -118.44000244140626"
            ),
            seg.transform_list[0]
        )
        self.assertEqual(1, len(seg.transforms))  # and there is only one transform

    def test_mod(self):
        """Test that we can convert .mod"""
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry option for JSON
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_file = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_file[0], 'r') as f:
            data = json.load(f)
        # ensure that the mesh_list is empty
        self.assertEqual(len(data['segment_list'][0]['mesh_list']), 0)
        self.assertEqual(len(data['segment_list'][0]['shape_primitive_list']), 0)

    def test_am(self):
        """Test that we can convert .am"""
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.am'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry for JSON
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.am'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_stl(self):
        """Test that we can convert .stl"""
        args, configs = parse_args('convert -o {output} {input} --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.stl'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_file = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_file), 1)
        # with --exclude-geometry option for JSON
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.stl'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_file = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_file[0], 'r') as f:
            data = json.load(f)
        # ensure that the mesh_list is empty
        self.assertEqual(len(data['segment_list'][0]['mesh_list']), 0)

    def test_surf(self):
        """Test that we can convert .surf"""
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.surf'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry option for JSON
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.surf'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_file = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_file[0], 'r') as f:
            data = json.load(f)
        # ensure that the mesh_list is empty
        self.assertEqual(len(data['segment_list'][0]['mesh_list']), 0)

    def test_survos(self):
        """Test that we can convert SuRVoS (.h5) files"""
        sys.stdin = StringIO('0')
        args, configs = parse_args('convert -o {output} {input} --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.h5'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
        # with --exclude-geometry for JSON
        sys.stdin = StringIO('0')
        args, configs = parse_args('convert -o {output} {input} --exclude-geometry --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.h5'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.json'))
        with open(sff_files[0], 'r') as f:
            data = json.load(f)
        self.assertIsNone(data['segment_list'][0]['three_d_volume'])

    def test_unknown(self):
        """Test that unknown fails"""
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.xxx'),
            self.config_fn,
        ), use_shlex=True)
        with self.assertRaises(ValueError):
            Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 0)

    def test_sff(self):
        """Test that we can convert .sff"""
        # first convert from some other format e.g. .mod
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        # then convert to .hff
        args, configs = parse_args('convert {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_hff(self):
        """Test that we can convert .hff"""
        # first convert from some other format e.g. .mod
        args, configs = parse_args('convert -o {} {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        # then convert to .sff
        args, configs = parse_args('convert {} -o {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_json(self):
        """Test that we can convert .json"""
        # first convert from some other format e.g. .mod
        args, configs = parse_args('convert -o {output} {input} --config-path {config}'.format(
            output=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            input=os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        # then convert to .sff
        args, configs = parse_args('convert {input} -o {output} --config-path {config}'.format(
            input=os.path.join(TEST_DATA_PATH, 'test_data.json'),
            output=os.path.join(TEST_DATA_PATH, 'test_data.sff'),
            config=self.config_fn,
        ), use_shlex=True)
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)


"""
:TODO: view .hff, .json
"""


class TestMain_handle_view(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMain_handle_view, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_read_am(self):
        """Test that we can view .am"""
        args, configs = parse_args('view {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.am'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_map(self):
        """Test that we can view .map"""
        args, configs = parse_args('view {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_view_transform_from_map(self):
        """Test that we can view the transform from a MAP image"""
        # ssv
        args, configs = parse_args('view {} --transform --print-ssv --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map'),
            self.config_fn,
        ), use_shlex=True)
        sys.stdout = StringIO()
        Main.handle_view(args, configs)
        self.assertRegex(sys.stdout.getvalue(), r"^(\d+\.\d+[ ]*){12}$")
        # csv
        args, configs = parse_args('view {} --transform --print-csv --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map'),
            self.config_fn,
        ), use_shlex=True)
        sys.stdout = StringIO()
        Main.handle_view(args, configs)
        self.assertRegex(sys.stdout.getvalue(), r"^(\d+\.\d+[,]*){12}$")
        # array
        args, configs = parse_args('view {} --transform --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map'),
            self.config_fn,
        ), use_shlex=True)
        sys.stdout = StringIO()
        Main.handle_view(args, configs)
        self.assertRegex(sys.stdout.getvalue(), r"(?m)^[[].*?(\d+\.\d*)*.*?[]]$")

    def test_read_mod(self):
        """Test that we can view .mod"""
        args, configs = parse_args('view {} --config-path {} --show-chunks'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_seg(self):
        """Test that we can view .seg"""
        args, configs = parse_args('view {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.seg'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_surf(self):
        """Test that we can view .surf"""
        args, configs = parse_args('view {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.surf'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_unknown(self):
        """Test that we cannot view unknown"""
        args, configs = parse_args('view {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.xxx'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_view(args, configs))


class TestMain_handle_notes(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMain_handle_notes, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_list(self):
        """Test that we can list notes"""
        args, configs = parse_args('notes list {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_notes_list(args, configs))

    def test_show(self):
        """Test that we can list notes"""
        args, configs = parse_args('notes show -i 15559 {} --config-path {}'.format(
            os.path.join(TEST_DATA_PATH, 'sff', 'v0.8', 'emd_1014.sff'),
            self.config_fn,
        ), use_shlex=True)
        self.assertEqual(0, Main.handle_notes_show(args, configs))

    def test_search(self):
        """Test that we can list notes"""
        args, configs = parse_args('notes search "mitochondria" --config-path {}'.format(self.config_fn),
                                   use_shlex=True)
        # 0 = search OK
        # 65 =
        status = Main.handle_notes_search(args, configs)
        self.assertTrue(
            status == 0 or
            status == 65
        )
        if status == 65:
            self.stderr("Warning: unable to run test on response due to API issue")


class TestMain_handle_prep(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMain_handle_prep, cls).setUpClass()
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def setUp(self):
        super(TestMain_handle_prep, self).setUp()
        self.test_data = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map')

    def tearDown(self):
        super(TestMain_handle_prep, self).tearDown()
        os.remove(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_prep.map'))

    def test_ccp4_binmap(self):
        """Test that we can prepare a CCP4 map by binning"""
        args, configs = parse_args('prep binmap -v {}'.format(self.test_data), use_shlex=True)
        self.assertEqual(0, Main.handle_prep(args, configs))
