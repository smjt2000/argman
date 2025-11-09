# test_subcommands.py
import unittest
import sys
import io
from argman import ArgMan, ArgParseError


class TestArgManSubcommands(unittest.TestCase):

    def setUp(self):
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        sys.argv = self.original_argv

    def test_subcommand_basic_parsing(self):
        """Test basic subcommand parsing with arguments."""
        sys.argv = ['myapp', 'helper', '--num', '42']
        am = ArgMan()
        am.arg_bool(long='verbose')
        helper_cmd = am.add_cmd('helper')
        helper_cmd.arg_int(long='num')
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'helper')
        self.assertTrue(hasattr(args, 'helper'))
        self.assertEqual(args.helper.num, 42)

    def test_subcommand_with_positional_args(self):
        """Test subcommand parsing with positional arguments."""
        sys.argv = ['myapp', 'process', 'input.txt', 'output.txt']
        am = ArgMan()
        process_cmd = am.add_cmd('process')
        process_cmd.arg_pos('input_file', _type=str)
        process_cmd.arg_pos('output_file', _type=str, required=False)
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'process')
        self.assertTrue(hasattr(args, 'process'))
        self.assertEqual(args.process.input_file, 'input.txt')
        self.assertEqual(args.process.output_file, 'output.txt')

    def test_subcommand_default_values(self):
        """Test subcommand arguments with default values."""
        sys.argv = ['myapp', 'config']
        am = ArgMan()
        config_cmd = am.add_cmd('config')
        config_cmd.arg_str(long='mode', default='dev')
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'config')
        self.assertTrue(hasattr(args, 'config'))
        self.assertEqual(args.config.mode, 'dev')

    def test_root_command_only(self):
        """Test parsing when only root arguments are provided, no subcommand."""
        sys.argv = ['myapp', '--global-opt', 'value']
        am = ArgMan()
        am.arg_str(long='global-opt')
        cmd = am.add_cmd('unused_cmd')
        cmd.arg_int(long='cmd_arg')
        args = am.parse()
        self.assertEqual(args.global_opt, 'value')
        self.assertIsNone(getattr(args, 'sub_cmd', None))
        self.assertFalse(hasattr(args, 'unused_cmd'))

    def test_unknown_subcommand_error(self):
        """Test that an unknown subcommand raises an error."""
        sys.argv = ['myapp', 'unknown_cmd']
        am = ArgMan()
        known_cmd = am.add_cmd('known_cmd')
        known_cmd.arg_bool(long='flag')
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        error_output = capture_err.getvalue()
        self.assertIn("Unknown argument 'unknown_cmd'", error_output)

    def test_subcommand_optional_args_provided(self):
        """Test subcommand with optional arguments (defined by defaults) when provided."""
        sys.argv = ['myapp', 'config', '--mode', 'prod', '--timeout', '60', '--debug']
        am = ArgMan()
        cmd = am.add_cmd('config')
        cmd.arg_str(long='mode', default='dev')
        cmd.arg_int(long='timeout', default=30)
        cmd.arg_bool(long='debug', default=False)

        args = am.parse()

        self.assertEqual(args.sub_cmd, 'config')
        self.assertTrue(hasattr(args, 'config'))
        self.assertEqual(args.config.mode, 'prod')
        self.assertEqual(args.config.timeout, 60)
        self.assertTrue(args.config.debug)

    def test_subcommand_optional_args_not_provided(self):
        """Test subcommand with optional arguments (defined by defaults) when not provided (defaults used)."""
        sys.argv = ['myapp', 'config']
        am = ArgMan()
        cmd = am.add_cmd('config')
        cmd.arg_str(long='mode', default='dev')
        cmd.arg_int(long='timeout', default=30)
        cmd.arg_bool(long='debug', default=False)

    def test_subcommand_optional_list_args_provided(self):
        """Test subcommand with optional list arguments when provided."""
        sys.argv = ['myapp', 'build', '--flags', 'flag1', '--flags', 'flag2']
        am = ArgMan()
        cmd = am.add_cmd('build')
        cmd.arg_list(long='flags', item_type=str, default=[])
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'build')
        self.assertTrue(hasattr(args, 'build'))
        self.assertEqual(args.build.flags, ['flag1', 'flag2'])

    def test_subcommand_optional_list_args_not_provided(self):
        """Test subcommand with optional list arguments when not provided (defaults used)."""
        sys.argv = ['myapp', 'build']
        am = ArgMan()
        cmd = am.add_cmd('build')
        cmd.arg_list(long='flags', item_type=str, default=[])
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'build')
        self.assertTrue(hasattr(args, 'build'))
        self.assertEqual(args.build.flags, [])

    def test_subcommand_mixed_required_pos_and_optional_args(self):
        """Test subcommand with required positional and optional (flag) arguments."""
        sys.argv = ['myapp', 'run', 'my_script.py', '--count', '5', '--verbose']
        am = ArgMan()
        cmd = am.add_cmd('run')
        cmd.arg_pos('script', _type=str, required=True)
        cmd.arg_int(long='count', default=1)
        cmd.arg_bool(long='verbose', default=False)
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'run')
        self.assertTrue(hasattr(args, 'run'))
        self.assertEqual(args.run.script, 'my_script.py')
        self.assertEqual(args.run.count, 5)
        self.assertTrue(args.run.verbose)

    def test_subcommand_optional_arg_after_required_pos(self):
        """Test subcommand where optional arg comes after required positional."""
        sys.argv = ['myapp', 'run', 'my_script.py', '--count', '5']
        am = ArgMan()
        cmd = am.add_cmd('run')
        cmd.arg_pos('script', _type=str, required=True)  # Required positional
        cmd.arg_int(long='count', default=1)
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'run')
        self.assertTrue(hasattr(args, 'run'))
        self.assertEqual(args.run.script, 'my_script.py')
        self.assertEqual(args.run.count, 5)

    def test_subcommand_basic_parsing_corrected(self):
        """Test basic subcommand parsing with arguments, focusing on defaults for optional."""
        sys.argv = ['myapp', 'helper', '--num', '42']
        am = ArgMan()
        am.arg_bool(long='global_verbose', default=False)
        helper_cmd = am.add_cmd('helper')
        helper_cmd.arg_int(long='num', default=0)
        args = am.parse()
        self.assertEqual(args.sub_cmd, 'helper')
        self.assertTrue(hasattr(args, 'helper'))
        self.assertEqual(args.helper.num, 42)
        self.assertFalse(args.global_verbose)

    def test_subcommand_global_flag_before_name_fails(self):
        """Test that global flags before subcommand name fails with current dispatch."""
        sys.argv = ['myapp', '--global-verbose', 'helper', '--num', '42']
        am = ArgMan()
        am.arg_bool(long='global-verbose', default=False)
        helper_cmd = am.add_cmd('helper')
        helper_cmd.arg_int(long='num', default=0)
        capture_err = io.StringIO()
        sys.stderr = capture_err
        with self.assertRaises(SystemExit):
            am.parse()
        sys.stderr = sys.__stderr__
        error_output = capture_err.getvalue()
        self.assertIn("Unknown argument 'helper'", error_output)


if __name__ == '__main__':
    unittest.main()
