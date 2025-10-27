import unittest
import sys
import io
from argman import ArgMan


class TestArgMan(unittest.TestCase):

    def setUp(self):
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_default_type_mismatch(self):
        """Ensure ValueError is raised when default value type doesn't match defined _type."""
        sys.argv = ['prog']
        parser = ArgMan()
        with self.assertRaises(ValueError) as cm:
            parser.arg_pos('nodes', desc='Number of nodes', default='John Doe', _type=int)
        exception = cm.exception
        self.assertIn('Type of default value should be the same as defined type', str(exception))

    def test_value_type_mismatch(self):
        """Ensure SystemExit occurs with error when entered value type mismatches defined _type."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', 'here']
        parser = ArgMan()
        parser.arg_pos('year', desc='Year to check events', _type=int)
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn('Type mismatch for `year` (expected int)', capture_err.getvalue())

    def test_missing_required(self):
        """Ensure error is raised when a required positional argument is missing."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', 'a.txt']
        parser = ArgMan()
        parser.arg_pos('input', desc='Input file path')
        parser.arg_pos('output', desc='Output file path')
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn('Missing required arguments:', capture_err.getvalue())
        self.assertIn('    output', capture_err.getvalue())

    def test_more_than_enough(self):
        """Ensure parser exits with error when too many positional arguments are provided."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', 'a.txt', 'b.txt']
        parser = ArgMan()
        parser.arg_pos('input', desc='Input file path')
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn('Unknown argument `b.txt`', capture_err.getvalue())

    def test_return_default_value(self):
        """Ensure default value is returned when no input is provided for the argument."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_pos('max', desc='Maximum file size in byte', default=1000, _type=int)
        args = parser.parse()
        self.assertEqual(args.max, 1000)

    def test_return_entered_value(self):
        """Ensure entered positional values are correctly assigned to defined arguments."""
        sys.argv = ['prog', 'a.txt', '1000']
        parser = ArgMan()
        parser.arg_pos('input', desc='Input file path', num_as_str=False)
        parser.arg_pos('max', desc='Maximum file size in byte', _type=int)
        args = parser.parse()
        self.assertEqual(args.input, 'a.txt')
        self.assertEqual(args.max, 1000)

    def test_with_num_as_str(self):
        """Ensure numeric string input is accepted when num_as_str=True (default)."""
        sys.argv = ['prog', '06']
        parser = ArgMan()
        parser.arg_pos('month', desc='Month name')  # num_as_str=True is default
        args = parser.parse()
        self.assertEqual(args.month, 6)

    def test_without_num_as_str(self):
        """Ensure numeric string input causes error when num_as_str=False."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', '06']
        parser = ArgMan()
        parser.arg_pos('month', desc='Month name', num_as_str=False)
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn('Type mismatch for `month` (expected str)', capture_err.getvalue())

    def test_order_matters(self):
        """Ensure positional argument order is preserved and values are assigned correctly."""
        sys.argv = ['prog', 'a.txt', 'b.txt', 'mike', 'developer']
        parser = ArgMan()
        parser.arg_pos('input', num_as_str=False)
        parser.arg_pos('output', num_as_str=False)
        parser.arg_pos('name', num_as_str=False)
        parser.arg_pos('role', num_as_str=False)
        args = parser.parse()
        self.assertEqual(args.input, 'a.txt')
        self.assertEqual(args.output, 'b.txt')
        self.assertEqual(args.name, 'mike')
        self.assertEqual(args.role, 'developer')


if __name__ == '__main__':
    unittest.main()
