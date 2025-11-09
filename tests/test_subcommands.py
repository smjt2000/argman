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


if __name__ == '__main__':
    unittest.main()
