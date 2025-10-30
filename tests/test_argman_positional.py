import unittest
import sys
import io
from argman import ArgMan, ArgParseError


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
        self.assertIn("Type mismatch for 'year' (expected int)", capture_err.getvalue())

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
        self.assertIn("Unknown argument 'b.txt'", capture_err.getvalue())

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
        parser.arg_pos('input', desc='Input file path')
        parser.arg_pos('max', desc='Maximum file size in byte', _type=int)
        args = parser.parse()
        self.assertEqual(args.input, 'a.txt')
        self.assertEqual(args.max, 1000)

    def test_order_matters(self):
        """Ensure positional argument order is preserved and values are assigned correctly."""
        sys.argv = ['prog', 'a.txt', 'b.txt', 'mike', 'developer']
        parser = ArgMan()
        parser.arg_pos('input')
        parser.arg_pos('output')
        parser.arg_pos('name')
        parser.arg_pos('role')
        args = parser.parse()
        self.assertEqual(args.input, 'a.txt')
        self.assertEqual(args.output, 'b.txt')
        self.assertEqual(args.name, 'mike')
        self.assertEqual(args.role, 'developer')

    def test_required_after_optional_definition(self):
        """Defining required after optional raises ValueError."""
        parser = ArgMan()
        parser.arg_pos('input', required=False)
        with self.assertRaises(ValueError) as cm:
            parser.arg_pos('output', required=True)
        self.assertIn("Required positional argument cannot be defined after an optional one", str(cm.exception))

    def test_double_dash_with_extra_args(self):
        """-- followed by too many positionals raises error."""
        sys.argv = ['prog', '--', 'a.txt', 'b.txt', 'c.txt']
        parser = ArgMan()
        parser.arg_pos('file1')
        parser.arg_pos('file2')
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Unknown argument 'c.txt'", capture_err.getvalue())

    def test_long_name_with_dashes(self):
        """Long name with dashes works and aliases correctly."""
        sys.argv = ['prog', '--my-flag', '42']
        parser = ArgMan()
        parser.arg_int(long='my-flag', default=0)
        args = parser.parse()
        self.assertEqual(args.my_flag, 42)  # stored as my_flag
        # Note: you can't access via args['my-flag'], but that's fine

    def test_exit_on_err_false_mode(self):
        """When exit_on_err=False, errors raise ArgParseError."""
        sys.argv = ['prog', '--unknown']
        parser = ArgMan(exit_on_err=False)
        parser.arg_int(long='num', default=1)
        with self.assertRaises(ArgParseError) as cm:
            parser.parse()
        self.assertIn("Unknown argument", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
