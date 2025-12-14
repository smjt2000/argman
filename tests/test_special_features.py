import unittest
import sys
import io
from argman import ArgMan, ArgParseError


class TestArgMan(unittest.TestCase):
    def setUp(self):
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_requires_success(self):
        """Test that required args are accepted when provided."""
        argv = ['prog', '--input', 'file.txt', '--output', 'out.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='output')
        am.requires('input', ['output'])
        args = am.parse()
        self.assertEqual(args.input, 'file.txt')
        self.assertEqual(args.output, 'out.txt')

    def test_requires_failure(self):
        """Test that missing required args raise error."""
        argv = ['prog', '--input', 'file.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='output')
        am.requires('input', ['output'])
        with self.assertRaises(ArgParseError):
            am.parse()

    def test_requires_not_triggered(self):
        """Test that requires is not checked if main arg is not used."""
        argv = ['prog', '--output', 'out.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='output')
        am.requires('input', ['output'])
        args = am.parse()
        self.assertEqual(args.output, 'out.txt')

    def test_conflicts_success(self):
        """Test that args are accepted when conflicting args are absent."""
        argv = ['prog', '--input', 'file.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='legacy')
        am.conflicts('input', ['legacy'])
        args = am.parse()
        self.assertEqual(args.input, 'file.txt')

    def test_conflicts_failure(self):
        """Test that conflicting args raise error when both are provided."""
        argv = ['prog', '--input', 'file.txt', '--legacy', 'old.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='legacy')
        am.conflicts('input', ['legacy'])
        with self.assertRaises(ArgParseError):
            am.parse()

    def test_conflicts_not_triggered(self):
        """Test that conflicts is not checked if main arg is not used."""
        argv = ['prog', '--legacy', 'old.txt']
        am = ArgMan(argv=argv)
        am.arg_str(long='input')
        am.arg_str(long='legacy')
        am.conflicts('input', ['legacy'])
        args = am.parse()
        self.assertEqual(args.legacy, 'old.txt')

    def test_requires_and_conflicts_together(self):
        """Test requires and conflicts used together."""
        argv = ['prog', '--mode', 'fast', '--speed', '10']
        am = ArgMan(argv=argv)
        am.arg_str(long='mode')
        am.arg_int(long='speed')
        am.arg_bool(long='safe')
        am.requires('mode', ['speed'])
        am.conflicts('mode', ['safe'])
        args = am.parse()
        self.assertEqual(args.mode, 'fast')
        self.assertEqual(args.speed, 10)

    def test_conflict_arg_not_defined_raises_error(self):
        """Test defining conflict with undefined arg raises ValueError."""
        am = ArgMan()
        am.arg_str(long='input')
        with self.assertRaises(ValueError) as cm:
            am.conflicts('input', ['undefined_arg'])
        self.assertIn("Argument 'undefined_arg' not found", str(cm.exception))

    def test_formatter_str_lower(self):
        """Test str formatter with str.lower."""
        sys.argv = ['prog', '--name', 'ALICE']
        am = ArgMan()
        am.arg_str(long='name', formatter=str.lower)
        args = am.parse()
        self.assertEqual(args.name, 'alice')

    def test_formatter_str_strip(self):
        """Test str formatter with str.strip."""
        sys.argv = ['prog', '--tag', ' beta ']
        am = ArgMan()
        am.arg_str(long='tag', formatter=str.strip)
        args = am.parse()
        self.assertEqual(args.tag, 'beta')

    def test_formatter_int_clamp(self):
        """Test int formatter that clamps negative values to zero."""
        sys.argv = ['prog', '--count', '-5']
        am = ArgMan()
        am.arg_int(long='count', formatter=lambda x: max(0, x))
        args = am.parse()
        self.assertEqual(args.count, 0)

    def test_formatter_float_round(self):
        """Test float formatter that rounds to 2 decimals."""
        sys.argv = ['prog', '--rate', '3.14159']
        am = ArgMan()
        am.arg_float(long='rate', formatter=lambda x: round(x, 2))
        args = am.parse()
        self.assertEqual(args.rate, 3.14)

    def test_formatter_list_strip(self):
        """Test list formatter applied per item."""
        sys.argv = ['prog', '--exclude', ' a ', '--exclude', ' b ']
        am = ArgMan()
        am.arg_list(long='exclude', item_type=str, formatter=str.strip)
        args = am.parse()
        self.assertEqual(args.exclude, ['a', 'b'])

    def test_formatter_default_not_formatted(self):
        """Test that default values are NOT formatted."""
        sys.argv = ['prog']
        am = ArgMan()
        am.arg_str(long='mode', default='PROD', formatter=str.lower)
        args = am.parse()
        self.assertEqual(args.mode, 'PROD')

    def test_formatter_raises_error_short(self):
        """Test formatter error handling for short flag."""
        sys.argv = ['prog', '-n', 'invalid']
        am = ArgMan()

        def fail_formatter(x):
            raise ValueError("Bad input")

        am.arg_str(short='n', long='name', formatter=fail_formatter)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Formatting failed for '-n': Bad input", capture_err.getvalue())

    def test_formatter_raises_error_long(self):
        """Test formatter error handling for long flag."""
        sys.argv = ['prog', '--name', 'invalid']
        am = ArgMan()

        def fail_formatter(x):
            raise RuntimeError("Oops")

        am.arg_str(long='name', formatter=fail_formatter)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        self.assertIn("Formatting failed for '--name': Oops", capture_err.getvalue())

    def test_formatter_with_choices(self):
        """Test formatter runs after choices validation."""
        sys.argv = ['prog', '--env', 'DEV']
        am = ArgMan()
        am.arg_str(long='env', choices=['DEV', 'PROD'], formatter=str.lower)
        args = am.parse()
        self.assertEqual(args.env, 'dev')

    def test_formatter_with_validator(self):
        """Test formatter runs after validator."""
        sys.argv = ['prog', '--count', '10']
        am = ArgMan()

        def positive(x): return x > 0

        am.arg_int(long='count', validator=positive, formatter=lambda x: x * 2)
        args = am.parse()
        self.assertEqual(args.count, 20)


if __name__ == '__main__':
    unittest.main()
