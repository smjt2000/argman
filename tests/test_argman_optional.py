import unittest
import sys
import io
from argman import ArgMan, ArgParseError


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
        """Boolean flag should set value to True."""
        sys.argv = ['prog', '--run']
        parser = ArgMan()
        parser.arg_bool(short='r', long='run', default=False)
        args = parser.parse()
        self.assertTrue(args.run)

    def test_parse_multiple_bool_flags(self):
        """Boolean flag should set value to True."""
        sys.argv = ['prog', '-rp']
        parser = ArgMan()
        parser.arg_bool(short='r', long='run', default=False)
        parser.arg_bool(short='p', long='print', default=True)
        args = parser.parse()
        self.assertTrue(args.run)
        self.assertTrue(args.print)

    def test_bool_no_flag(self):
        """boolean flag with '--no-flag' should set value to False."""
        sys.argv = ['prog', '--no-verbose']
        parser = ArgMan()
        parser.arg_bool(long='verbose', default=True)
        args = parser.parse()
        self.assertFalse(args.verbose)

    def test_equal_sign(self):
        """Should set value correctly"""
        sys.argv = ['prog', '--file=a.txt']
        parser = ArgMan()
        parser.arg_str(long='file', short='f')
        args = parser.parse()
        self.assertEqual(args.file, 'a.txt')
        self.assertEqual(args.f, 'a.txt')

    def test_equal_sign_short(self):
        """Should raise error"""
        sys.argv = ['prog', '-f=a.txt']
        parser = ArgMan(exit_on_err=False)
        parser.arg_str(long='file', short='f')
        with self.assertRaises(ArgParseError) as cm:
            parser.parse()
        exception = cm.exception
        self.assertIn("Short option '-f' does not support '=' syntax.", str(exception))

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
        self.assertIn("Missing value for argument '--num'", capture_err.getvalue())

    def test_unknown_argument(self):
        """Unknown arguments should not break the parser."""
        capture_err = io.StringIO()
        sys.stderr = capture_err
        sys.argv = ['prog', '--unknown', '5']
        parser = ArgMan()
        parser.arg_int(long='num', default=1)
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Unknown argument '--unknown'", capture_err.getvalue())  # unaffected

    def test_bool_no_flag_requires_long(self):
        """--no-flag is only generated if long name is provided."""
        sys.argv = ['prog', '--no-quiet']
        parser = ArgMan()
        # Define boolean with ONLY short name
        parser.arg_bool(short='q', default=True)
        # --no-quiet should be unknown because no long name was given
        with self.assertRaises(SystemExit):
            parser.parse()

    def test_bool_default_true_without_flag(self):
        """Boolean with default=True remains True if flag not passed."""
        sys.argv = ['prog']
        parser = ArgMan()
        parser.arg_bool(long='debug', default=True)
        args = parser.parse()
        self.assertTrue(args.debug)

    def test_bool_default_true_with_flag(self):
        """Boolean with default=True stays True when flag is passed."""
        sys.argv = ['prog', '--debug']
        parser = ArgMan()
        parser.arg_bool(long='debug', default=True)
        args = parser.parse()
        self.assertTrue(args.debug)

    def test_mix_short_long(self):
        """Mix short and long arguments."""
        sys.argv = ['prog', '-v', '--file=output.txt', '-n', '5']
        parser = ArgMan()
        parser.arg_bool(short='v', long='verbose', default=False)
        parser.arg_str(short='f', long='file', default='')
        parser.arg_int(short='n', long='num', default=0)
        args = parser.parse()
        self.assertTrue(args.verbose)
        self.assertEqual(args.file, 'output.txt')
        self.assertEqual(args.num, 5)

    def test_short_with_value(self):
        """Short argument with space-separated value."""
        sys.argv = ['prog', '-f', 'data.csv']
        parser = ArgMan()
        parser.arg_str(short='f', long='file', default='')
        args = parser.parse()
        self.assertEqual(args.f, 'data.csv')

    def test_empty_value_equal_sign(self):
        """--arg= with empty value."""
        sys.argv = ['prog', '--name=']
        parser = ArgMan()
        parser.arg_str(long='name', default='default')
        args = parser.parse()
        self.assertEqual(args.name, '')

    def test_unknown_in_short_cluster(self):
        """Error message should include original cluster."""
        sys.argv = ['prog', '-vxq']
        parser = ArgMan()
        parser.arg_bool(short='v', default=False)
        parser.arg_bool(short='q', default=False)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            parser.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("-x", capture_err.getvalue())
        self.assertIn("-vxq", capture_err.getvalue())

    def test_custome_error(self):
        msg = 'you should provide a name!'
        custom_error = {
            'no_short_or_long': msg
        }
        sys.argv = ['prog']
        parser = ArgMan(custom_errors=custom_error)
        with self.assertRaises(ValueError) as cm:
            parser.arg_bool(default=False)
        self.assertIn(msg, str(cm.exception))

    def test_choices_valid_value_int(self):
        """Test arg_int with choices accepts a valid value."""
        sys.argv = ['prog', '--num', '10']
        am = ArgMan()
        am.arg_int(long='num', choices=[5, 10, 15])
        args = am.parse()
        self.assertEqual(args.num, 10)

    def test_choices_invalid_value_int(self):
        """Test arg_int with choices rejects an invalid value."""
        sys.argv = ['prog', '--num', '7']
        am = ArgMan()
        am.arg_int(long='num', choices=[5, 10, 15])
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Value for '--num' must be in", capture_err.getvalue())

    def test_choices_valid_value_str(self):
        """Test arg_str with choices accepts a valid value."""
        sys.argv = ['prog', '--mode', 'prod']
        am = ArgMan()
        am.arg_str(long='mode', choices=['dev', 'test', 'prod'])
        args = am.parse()
        self.assertEqual(args.mode, 'prod')

    def test_choices_invalid_value_str(self):
        """Test arg_str with choices rejects an invalid value."""
        sys.argv = ['prog', '--mode', 'stage']
        am = ArgMan()
        am.arg_str(long='mode', choices=['dev', 'test', 'prod'])
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Value for '--mode' must be in", capture_err.getvalue())

    def test_choices_list_valid_item(self):
        """Test arg_list with choices accepts valid items."""
        sys.argv = ['prog', '--env', 'dev', '--env', 'test']
        am = ArgMan()
        am.arg_list(long='env', item_type=str, choices=['dev', 'test', 'prod'])
        args = am.parse()
        self.assertEqual(args.env, ['dev', 'test'])

    def test_choices_list_invalid_item(self):
        """Test arg_list with choices rejects an invalid item."""
        sys.argv = ['prog', '--env', 'dev', '--env', 'stage']
        am = ArgMan()
        am.arg_list(long='env', item_type=str, choices=['dev', 'test', 'prod'])
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Value for '--env' must be in", capture_err.getvalue())

    def test_choices_with_default_valid(self):
        """Test that default value is checked against choices at definition time."""
        am = ArgMan()
        # This should work
        am.arg_str(long='mode', default='dev', choices=['dev', 'prod'])

    def test_choices_with_default_invalid(self):
        """Test that invalid default raises ValueError at definition time."""
        am = ArgMan()
        with self.assertRaises(ValueError) as cm:
            am.arg_str(long='mode', default='stage', choices=['dev', 'prod'])
        self.assertIn("Default value must be in choices", str(cm.exception))

    def test_choices_not_list_or_tuple(self):
        """Test that non-list/tuple choices raise error at definition."""
        am = ArgMan()
        with self.assertRaises(ValueError) as cm:
            am.arg_int(long='num', choices="5,10")
        self.assertIn("Choices must be list or tuple", str(cm.exception))

    def test_validator_not_callable_raises_error(self):
        """Validator must be callable; non-callable should raise at definition."""
        am = ArgMan()
        with self.assertRaises(ValueError) as cm:
            am.arg_int(long='port', validator="not a function")
        self.assertIn("Validator should be a callable object", str(cm.exception))

    def test_default_fails_validator_raises_error(self):
        """Default value must satisfy the validator at definition time."""
        am = ArgMan()

        def positive(x): return x > 0

        with self.assertRaises(ValueError) as cm:
            am.arg_int(long='count', default=-5, validator=positive)
        self.assertIn("Default value must pass the validation", str(cm.exception))

    def test_valid_input_passes_validator(self):
        """Valid input should pass custom validator."""
        sys.argv = ['prog', '--port', '8080']
        am = ArgMan()

        def valid_port(x): return 1 <= x <= 65535

        am.arg_int(long='port', validator=valid_port)
        args = am.parse()
        self.assertEqual(args.port, 8080)

    def test_invalid_input_fails_validator_short(self):
        """Invalid input should fail with short-flag error message."""
        sys.argv = ['prog', '-p', '99999']
        am = ArgMan()

        def valid_port(x): return 1 <= x <= 65535

        am.arg_int(short='p', long='port', validator=valid_port)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Validation failed for '-p' (99999)", capture_err.getvalue())

    def test_validator_raises_exception(self):
        """Validator that raises exception should be caught and re-raised as ArgParseError."""
        sys.argv = ['prog', '--age', '-5']
        am = ArgMan()

        def validate_age(x):
            if x < 0:
                raise ValueError("Age cannot be negative")
            return True

        am.arg_int(long='age', validator=validate_age)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__


if __name__ == '__main__':
    unittest.main()
