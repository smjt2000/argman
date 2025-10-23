import unittest
import sys
from argman import ArgMan


class TestArgMan(unittest.TestCase):

    def setUp(self):
        # هر تست یه نمونه تازه از ArgMan داره
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_default_values(self):
        """Arguments should return their default values if not passed."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_int(long='num', default=3)
        args =parser.parse()
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
        sys.argv = ['prog', '--nums', '1', '--nums', 'oops']
        parser = ArgMan()
        parser.arg_list(long='nums', item_type=int)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_parse_bool_flag(self):
        """Boolean flag should toggle when present."""
        sys.argv = ['prog', '--run']
        parser = ArgMan()
        parser.arg_bool(short='r', long='run', default=False)
        args = parser.parse()
        self.assertTrue(args.run)

    def test_missing_value_error(self):
        """Should raise ValueError if a non-bool argument is missing a value."""
        sys.argv = ['prog', '--num']
        parser = ArgMan()
        parser.arg_int(long='num', default=0)
        with self.assertRaises(ValueError):
            parser.parse()

    def test_unknown_argument(self):
        """Unknown arguments should not break the parser."""
        sys.argv = ['prog', '--unknown', '5']
        parser = ArgMan()
        parser.arg_int(long='num', default=1)
        args = parser.parse()
        self.assertEqual(args.num, 1)  # unaffected


if __name__ == '__main__':
    unittest.main()
