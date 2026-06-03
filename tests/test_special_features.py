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

    def test_single_group_one_arg(self):
        """Single group with one argument should be created successfully."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.group_args('Numbers', ['num'])
        self.assertIn('Numbers', am.groups)
        self.assertEqual(am.groups['Numbers'].args, ['num'])

    def test_single_group_multiple_args(self):
        """Single group with multiple arguments should contain all of them."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('General', ['num', 'name'])
        self.assertEqual(am.groups['General'].args, ['num', 'name'])

    def test_multiple_groups(self):
        """Multiple groups defined sequentially should all exist."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.arg_bool(long='verbose', default=False)
        am.group_args('Numbers', ['num'])
        am.group_args('General', ['name', 'verbose'])
        self.assertIn('Numbers', am.groups)
        self.assertIn('General', am.groups)

    def test_group_with_description(self):
        """Group description should be stored correctly."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.group_args('Numbers', ['num'], desc='Numeric options')
        self.assertEqual(am.groups['Numbers'].desc, 'Numeric options')

    def test_group_using_short_name(self):
        """Short name should be accepted when referencing an argument."""
        am = ArgMan()
        am.arg_int(short='n', long='num', default=1)
        am.group_args('Numbers', ['n'])
        self.assertIn('num', am.groups['Numbers'].args)

    def test_group_using_long_name(self):
        """Long name should be accepted when referencing an argument."""
        am = ArgMan()
        am.arg_int(short='n', long='num', default=1)
        am.group_args('Numbers', ['num'])
        self.assertIn('num', am.groups['Numbers'].args)

    def test_all_args_grouped(self):
        """All arguments in custom groups means default group is not in help output."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('All', ['num', 'name'])
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        self.assertNotIn('Options:', capture_out.getvalue())

    def test_partial_grouping_default_group_appears(self):
        """Ungrouped arguments should appear under the default group in help."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('Numbers', ['num'])
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        output = capture_out.getvalue()
        self.assertIn('Numbers:', output)
        self.assertIn('Options:', output)

    def test_default_group_appears_last(self):
        """Default group section should appear after all custom groups in help."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('Numbers', ['num'])
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        output = capture_out.getvalue()
        self.assertGreater(output.index('Options:'), output.index('Numbers:'))

    def test_group_order_preserved(self):
        """Groups should appear in the order they were defined."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.arg_bool(long='verbose', default=False)
        am.group_args('AAA', ['num'])
        am.group_args('BBB', ['name'])
        am.group_args('CCC', ['verbose'])
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        output = capture_out.getvalue()
        self.assertLess(output.index('AAA:'), output.index('BBB:'))
        self.assertLess(output.index('BBB:'), output.index('CCC:'))

    # ─── group_name Validation ─────────────────────────────────────

    def test_empty_group_name_raises(self):
        """Empty group name should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('', ['num'])

    def test_whitespace_only_group_name_raises(self):
        """Whitespace-only group name should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('   ', ['num'])

    def test_leading_whitespace_group_name_raises(self):
        """Group name with leading whitespace should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args(' Numbers', ['num'])

    def test_trailing_whitespace_group_name_raises(self):
        """Group name with trailing whitespace should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('Numbers ', ['num'])

    def test_duplicate_group_name_raises(self):
        """Defining two groups with the same name should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('General', ['num'])
        with self.assertRaises(ValueError):
            am.group_args('General', ['name'])

    def test_group_name_same_as_default_group_raises(self):
        """Group name equal to default_group should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('Options', ['num'])

    def test_custom_default_group_name_conflict_raises(self):
        """Group name equal to custom default_group should raise ValueError."""
        am = ArgMan(default_group='General')
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('General', ['num'])

    # ─── args List Validation ──────────────────────────────────────
    def test_empty_args_list_raises(self):
        """Empty args list should raise ValueError."""
        am = ArgMan()
        with self.assertRaises(ValueError):
            am.group_args('Empty', [])

    def test_unknown_arg_name_raises(self):
        """Unknown argument name in args list should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('General', ['unknown'])

    def test_duplicate_name_in_list_raises(self):
        """Duplicate argument name in args list should raise ValueError."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('Numbers', ['num', 'num'])

    def test_short_and_long_alias_duplicate_raises(self):
        """Short and long name of the same argument in list should raise ValueError."""
        am = ArgMan()
        am.arg_int(short='n', long='num', default=1)
        with self.assertRaises(ValueError):
            am.group_args('Numbers', ['n', 'num'])

    def test_already_grouped_arg_raises(self):
        """Argument already in a group should raise ValueError when grouped again."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.group_args('Numbers', ['num'])
        with self.assertRaises(ValueError):
            am.group_args('Again', ['num'])

        # ─── Help Output ───────────────────────────────────────────────

    def test_grouped_arg_appears_under_group(self):
        """Argument should appear under its group section in help."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1, desc='A number')
        am.group_args('Numbers', ['num'])
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        output = capture_out.getvalue()
        numbers_pos = output.index('Numbers:')
        num_pos = output.index('--num')
        self.assertGreater(num_pos, numbers_pos)

    def test_group_description_appears_in_help(self):
        """Group description should appear in help output."""
        am = ArgMan(argv=['prog', '--help'])
        am.arg_int(long='num', default=1)
        am.group_args('Numbers', ['num'], desc='All numeric options')
        capture_out = io.StringIO()
        sys.stdout = capture_out
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.stdout
        self.assertIn('All numeric options', capture_out.getvalue())

        # ─── Integration ───────────────────────────────────────────────

    def test_groups_do_not_affect_parsing(self):
        """Grouping arguments should not change parsed values."""
        am = ArgMan(argv=['prog', '--num', '42', '--name', 'John'])
        am.arg_int(long='num', default=1)
        am.arg_str(long='name', default='anon')
        am.group_args('General', ['num', 'name'])
        args = am.parse()
        self.assertEqual(args.num, 42)
        self.assertEqual(args.name, 'John')

    def test_subcommand_has_independent_groups(self):
        """Subcommand groups should be independent from parent groups."""
        am = ArgMan()
        am.arg_int(long='num', default=1)
        am.group_args('Parent Group', ['num'])
        cmd = am.add_cmd('run')
        cmd.arg_str(long='mode', default='fast')
        cmd.group_args('Command Group', ['mode'])
        self.assertIn('Parent Group', am.groups)
        self.assertNotIn('Command Group', am.groups)
        self.assertIn('Command Group', cmd.groups)
        self.assertNotIn('Parent Group', cmd.groups)


if __name__ == '__main__':
    unittest.main()
