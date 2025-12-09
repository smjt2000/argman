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


if __name__ == '__main__':
    unittest.main()
