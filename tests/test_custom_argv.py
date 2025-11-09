# test_argman_optional.py (or a new test_custom_argv.py)

import unittest
import sys
import io
from argman import ArgMan


class TestArgManCustomArgv(unittest.TestCase):

    def setUp(self):
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_custom_argv_basic_parsing(self):
        """Test parsing with a custom argv list."""
        custom_argv = ['myapp', '--num', '42', 'input.txt']
        am = ArgMan(argv=custom_argv)
        am.arg_int(long='num')
        am.arg_pos('input_file')
        args = am.parse()
        self.assertEqual(args.num, 42)
        self.assertEqual(args.input_file, 'input.txt')
        self.assertEqual(sys.argv, self.original_argv)

    def test_custom_argv_with_short_flag(self):
        """Test parsing short flags with custom argv."""
        custom_argv = ['tool', '-v', '-n', '10']
        am = ArgMan(argv=custom_argv)
        am.arg_bool(short='v', long='verbose')
        am.arg_int(short='n', long='number')
        args = am.parse()
        self.assertTrue(args.verbose)
        self.assertTrue(args.v)
        self.assertEqual(args.number, 10)
        self.assertEqual(args.n, 10)

    def test_custom_argv_with_bool_default_true_and_no_flag(self):
        """Test boolean arg with default=True remains True with custom argv if flag not present."""
        custom_argv = ['tool', 'arg1']
        am = ArgMan(argv=custom_argv)
        am.arg_bool(long='debug', default=True)
        am.arg_pos('pos_arg')
        args = am.parse()
        self.assertTrue(args.debug)
        self.assertEqual(args.pos_arg, 'arg1')

    def test_custom_argv_with_bool_default_true_and_flag(self):
        """Test boolean arg with default=True remains True when flag is present (ArgMan behavior)."""
        custom_argv = ['tool', '--debug', 'arg1']
        am = ArgMan(argv=custom_argv)
        am.arg_bool(long='debug', default=True)
        am.arg_pos('pos_arg')
        args = am.parse()
        self.assertTrue(args.debug)
        self.assertEqual(args.pos_arg, 'arg1')

    def test_custom_argv_with_bool_default_true_and_no_flag_false(self):
        """Test boolean arg with default=True becomes False with --no-<flag> using custom argv."""
        custom_argv = ['tool', '--no-debug', 'arg1']
        am = ArgMan(argv=custom_argv)
        am.arg_bool(long='debug', default=True)
        am.arg_pos('pos_arg')
        args = am.parse()
        self.assertFalse(args.debug)
        self.assertEqual(args.pos_arg, 'arg1')

    def test_custom_argv_empty_list(self):
        """Test parsing with an empty custom argv list."""
        custom_argv = ['myapp']
        am = ArgMan(argv=custom_argv)
        am.arg_int(long='num', default=5)
        am.arg_str(long='mode', default='dev')
        args = am.parse()
        self.assertEqual(args.num, 5)
        self.assertEqual(args.mode, 'dev')

    def test_custom_argv_with_list(self):
        """Test parsing list arguments with custom argv."""
        custom_argv = ['myapp', '--files', 'a.txt', '--files', 'b.txt', '--nums', '1', '--nums', '2']
        am = ArgMan(argv=custom_argv)
        am.arg_list(long='files', item_type=str)
        am.arg_list(long='nums', item_type=int)
        args = am.parse()
        self.assertEqual(args.files, ['a.txt', 'b.txt'])
        self.assertEqual(args.nums, [1, 2])

    def test_custom_argv_with_help(self):
        """Test that --help works correctly with custom argv."""
        custom_argv = ['myapp', '--help']
        am = ArgMan(argv=custom_argv)
        am.arg_int(long='num')
        capture_out = io.StringIO()
        sys.stdout = capture_out
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        output = capture_out.getvalue() + capture_err.getvalue()
        self.assertIn('myapp', output)
        self.assertIn('--num', output)

    def test_custom_argv_with_unknown_arg(self):
        """Test that unknown arguments raise an error correctly with custom argv."""
        custom_argv = ['myapp', '--unknown', 'value']
        am = ArgMan(argv=custom_argv)
        am.arg_int(long='num')
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        error_output = capture_err.getvalue()
        self.assertIn("Unknown argument '--unknown'", error_output)

    def test_custom_argv_with_subcommand(self):
        """Test subcommand parsing with custom argv."""
        custom_argv = ['myapp', 'sub1', '--subarg', 'val', 'pos_sub']
        am = ArgMan(argv=custom_argv)
        sub_cmd = am.add_cmd('sub1')
        sub_cmd.arg_str(long='subarg')
        sub_cmd.arg_pos('pos_sub')
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'sub1')
        self.assertTrue(hasattr(args, 'sub1'))
        self.assertEqual(args.sub1.subarg, 'val')
        self.assertEqual(args.sub1.pos_sub, 'pos_sub')

    def test_custom_argv_with_subcommand_unknown(self):
        """Test unknown subcommand error with custom argv."""
        custom_argv = ['myapp', 'unknown_sub', '--arg', 'val']
        am = ArgMan(argv=custom_argv)
        known_cmd = am.add_cmd('known_sub')
        known_cmd.arg_bool(long='flag')
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        error_output = capture_err.getvalue()
        self.assertIn("Unknown argument 'unknown_sub'", error_output)

    def test_custom_argv_program_name_override(self):
        """Test that custom argv sets program name correctly, and can be overridden by prog."""
        custom_argv = ['custom_script.py', '--arg', 'val']
        am_default_prog = ArgMan(argv=custom_argv)
        am_custom_prog = ArgMan(argv=custom_argv, prog='overridden_name')
        self.assertEqual(am_default_prog.program, 'custom_script.py')
        self.assertEqual(am_custom_prog.program, 'overridden_name')
        am_default_prog.arg_str(long='arg')
        am_custom_prog.arg_str(long='arg')
        args_default = am_default_prog.parse()
        args_custom = am_custom_prog.parse()
        self.assertEqual(args_default.arg, 'val')
        self.assertEqual(args_custom.arg, 'val')

    def test_custom_argv_does_not_use_sys_argv(self):
        """Test that parsing uses custom argv, not sys.argv."""
        sys.argv = ['sys_app', '--sys_flag', 'sys_val']
        custom_argv = ['custom_app', '--custom_arg', 'custom_val']
        am = ArgMan(argv=custom_argv)
        am.arg_str(long='custom_arg')
        am.arg_str(long='sys_flag', default='default_sys')
        args = am.parse()
        self.assertEqual(args.custom_arg, 'custom_val')
        self.assertEqual(args.sys_flag, 'default_sys')


if __name__ == '__main__':
    unittest.main()
