import unittest
import sys
import io
from argman import ArgMan


class TestArgMan(unittest.TestCase):

    def setUp(self):
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_default_values(self):
        """Arguments should return their default values if not passed."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_int(long='num', default=3)
        args = parser.parse()
        self.assertEqual(args.num, 3)

    def test_alias_access(self):
        """Short and long aliases should reference the same value."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_int(short='n', long='num', default=5)
        args = parser.parse()
        self.assertEqual(args.n, args.num)
        args.n = 10
        self.assertEqual(args.num, 10)

    def test_parse_int(self):
        """Should correctly parse integer argument from argv."""
        sys.argv = ['prog', '--num', '42']
        parser = ArgMan()
        parser.arg_int(short='n', long='num', default=0)
        args = parser.parse()
        self.assertEqual(args.num, 42)

    def test_parse_float(self):
        """Should correctly parse float argument."""
        sys.argv = ['prog', '--rate', '3.14']
        parser = ArgMan()
        parser.arg_float(short='r', long='rate', default=0.0)
        args = parser.parse()
        self.assertAlmostEqual(args.rate, 3.14)

    def test_parse_str(self):
        """Should correctly parse string argument."""
        sys.argv = ['prog', '--name', 'John']
        parser = ArgMan()
        parser.arg_str(short='n', long='name', default='anon')
        args = parser.parse()
        self.assertEqual(args.name, 'John')

    def test_parse_list_multiple(self):
        """Should correctly collect multiple values into a list."""
        sys.argv = ['prog', '--files', 'a.txt', '--files', 'b.txt', '--files', 'c.txt']
        parser = ArgMan()
        parser.arg_list(short='f', long='files', default=[])
        args = parser.parse()
        self.assertEqual(args.files, ['a.txt', 'b.txt', 'c.txt'])

    def test_default_list_value(self):
        """List argument should default to an empty list if not provided."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_list(long='items', default=[])
        args = parser.parse()
        self.assertEqual(args.items, [])

    def test_arg_list_with_item_type(self):
        """arg_list should cast each value to the specified type."""
        sys.argv = ['prog', '--nums', '1', '--nums', '2', '--nums', '3']
        parser = ArgMan()
        parser.arg_list(short='n', long='nums', item_type=int)
        args = parser.parse()
        self.assertEqual(args.nums, [1, 2, 3])
        self.assertTrue(all(isinstance(x, int) for x in args.nums))

    def test_arg_list_with_item_type_type_error(self):
        """Should raise ValueError if a list item cannot be cast to the given type."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', '--nums', '1', '--nums', 'oops']
        parser = ArgMan()
        parser.arg_list(long='nums', item_type=int)
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("should be of type int", capture_err.getvalue())

    def test_parse_bool_flag(self):
        """Boolean flag should toggle when present."""
        sys.argv = ['prog', '--run']
        parser = ArgMan()
        parser.arg_bool(short='r', long='run', default=False)
        args = parser.parse()
        self.assertTrue(args.run)

    def test_parse_multiple_bool_flags(self):
        """Boolean flag should toggle when present."""
        sys.argv = ['prog', '-rp']
        parser = ArgMan()
        parser.arg_bool(short='r', long='run', default=False)
        parser.arg_bool(short='p', long='print', default=False)
        args = parser.parse()
        self.assertTrue(args.run)
        self.assertTrue(args.print)

    def test_missing_value_error(self):
        """Should raise ValueError if a non-bool argument is missing a value."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', '--num']
        parser = ArgMan()
        parser.arg_int(long='num', default=0)
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Missing value for argument `--num`", capture_err.getvalue())

    def test_unknown_argument(self):
        """Unknown arguments should not break the parser."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', '--unknown', '5']
        parser = ArgMan()
        parser.arg_int(long='num', default=1)
        with self.assertRaises(SystemExit):
            args = parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Unknown argument `--unknown`", capture_err.getvalue())  # unaffected


if __name__ == '__main__':
    unittest.main()
