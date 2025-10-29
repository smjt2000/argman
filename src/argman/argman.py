from collections import OrderedDict
from dataclasses import dataclass
import sys


@dataclass
class _Arg:
    short: str = None
    long: str = None
    type: type = None
    default: int | float | str | list = None
    num_as_str: bool = False
    desc: str = None


@dataclass
class _PosArg:
    name: str
    type: type = str
    default: int | float | str = None
    required: bool = False
    num_as_str: bool = True
    parsed: bool = False
    desc: str = None


class _ArgResult:
    def __init__(self, aliases: dict[str, str]):
        self.__dict__['_values'] = {}
        self.__dict__['_aliases'] = aliases

    def __getattr__(self, name):
        key = self._aliases.get(name, name)
        if key in self._values:
            return self._values[key]
        raise AttributeError(f"No such argument: {name}")

    def __setattr__(self, name, value):
        key = self._aliases.get(name, name)
        self._values[key] = value

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        return iter(self._values.items())

    def __repr__(self):
        args = ', '.join(f"{k}={v}" for k, v in self._values.items())
        return f"<ArgResult {args}>"


class ArgParseError(Exception):
    """Exception raised for errors in command-line argument parsing."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ArgMan:
    def __init__(self, prog=None):
        self.program = prog or sys.argv[0]
        self.argv = sys.argv[1:]
        self.argc = len(self.argv)
        self.args: dict[str, _Arg] = {}
        self.pos_args: OrderedDict[str, _PosArg] = OrderedDict()
        self.aliases: dict[str, str] = {}
        self.result = _ArgResult(self.aliases)

    def __set_arg(self, _type: type, short: str = None, long: str = None, default=None, desc=None, num_as_str=False):
        """
        Internal helper for registering an argument.
        """
        if short is None and long is None:
            raise ValueError("At least one of 'short' or 'long' must be provided")
        if long is not None:
            long = long.replace('-', '_')
        main_name = long or short
        arg = _Arg(
            short=short, long=long, type=_type,
            default=default, desc=desc, num_as_str=num_as_str
        )
        self.args[main_name] = arg
        setattr(self.result, main_name, default)
        if long:
            self.aliases[long] = main_name
        if short:
            self.aliases[short] = main_name
        return None

    def _print_help(self):
        NAME_MAX_LEN = 22

        def get_arg_name(arg):
            name = ''
            if arg.short and arg.long:
                name = f'-{arg.short}, --{arg.long}'
            elif arg.short:
                name = f'-{arg.short}'
            elif arg.long:
                name = f'--{arg.long}'
            if arg.type:
                name += f' <{arg.type.__name__}>'

            return name

        header = f"Usage: {self.program}"
        opt_poses = []
        req_poses = []
        for arg in self.pos_args.values():
            if arg.required:
                req_poses.append(arg)
            else:
                opt_poses.append(arg)

        if len(self.args) > 0:
            header += ' [OPTIONS]'
        if req_poses:
            text = ' '
            text += ' '.join([arg.name for arg in req_poses])
            header += text
        if opt_poses:
            text = ''
            for arg in opt_poses:
                text += f' [{arg.name}]'
            header += text
        print(header)
        if len(self.args) > 0:
            print("\nOptions:")
            for arg in self.args.values():
                NAME_MAX_LEN = max(NAME_MAX_LEN, len(get_arg_name(arg)))
            for arg in self.args.values():
                arg_name = get_arg_name(arg)
                print(f"  {arg_name:<{NAME_MAX_LEN}} : {arg.desc.capitalize() if arg.desc else 'No description'}")
        if len(req_poses) > 0 or len(opt_poses) > 0:
            print("\nArguments:")
            for arg in req_poses + opt_poses:
                arg_name = f'{arg.name} <{arg.type.__name__}>'
                text = f"  {arg_name:<{NAME_MAX_LEN}} : {arg.desc.capitalize() if arg.desc else 'No description'}"
                if arg.default is not None and not arg.required:
                    text += f' (optional, default: {arg.default})'
                elif arg.default is not None:
                    text += f' [default: {arg.default}]'
                elif not arg.required:
                    text += f' (optional)'
                print(text)

    def _print_err(self, message: str):
        print(message, file=sys.stderr)
        self._print_help()
        exit(1)

    def arg_pos(self, name: str, *, required=True, default=None, _type=str, num_as_str=True, desc=None):
        """
        Define a positional argument.

        Args:
            name (str): Name of the argument variable.
            required (bool, optional): Whether the argument must be provided. Defaults to True.
            default (any, optional): Default value for the argument if not provided.
            _type (type, optional): Type to which the argument value should be converted. Defaults to str.
            num_as_str (bool, optional): Determines wheter numeric inputs should be accepted as valid strings when `_type` is `str`.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            ValueError:
                - If the argument is required but no default value is provided.
                - If `-type` is `str` and `num_as_str=False`, and default value is numeric.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_pos('input_path', required=False, desc='Path to the input file')
            >>> args = am.parse()
            >>> print(args.input_path)
        """
        if default is not None and not isinstance(default, _type):
            if _type is str and not num_as_str:
                raise ValueError("Type of default value should be the same as defined type")
            if _type is not str:
                raise ValueError("Type of default value should be the same as defined type")
        arg = _PosArg(
            name=name, type=_type,
            default=default, desc=desc,
            required=required, num_as_str=num_as_str
        )
        self.pos_args[name] = arg
        setattr(self.result, name, default)
        return None

    def arg_int(self, *, short: str = None, long: str = None, default=None, desc=None):
        """
        Defines an optional integer argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-n`).
            long (str, optional): Long name for the argument (e.g., `--number`).
            default (int, required): Default integer value for the argument.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            TypeError: If the provided default value is not an integer.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_int(short='n', long='node', default=3, desc='Number of nodes')
            >>> args = am.parse()
            >>> print(args.node)
            3
        """
        if default is not None and not isinstance(default, int):
            raise TypeError("default must be an int")
        self.__set_arg(int, short, long, default, desc)
        return None

    def arg_float(self, *, short: str = None, long: str = None, default=None, desc=None):
        """
        Defines an optional float argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-r`).
            long (str, optional): Long name for the argument (e.g., `--rate`).
            default (float, required): Default float value for the argument.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            TypeError: If the provided default value is not a number.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_float(short='r', long='rate', default=1.0, desc='Payment rate')
            >>> args = am.parse()
            >>> print(args.rate)
            1.0
        """
        if default is not None and not isinstance(default, (float, int)):
            raise TypeError("default must be a number")
        self.__set_arg(float, short, long, float(default), desc)
        return None

    def arg_str(self, *, short: str = None, long: str = None, default=None, num_as_str=True, desc=None):
        """
        Defines an optional string argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-a`).
            long (str, optional): Long name for the argument (e.g., `--author`).
            default (str, required): Default str value for the argument.
            num_as_str (bool, optional): Determines wheter numeric inputs should be accepted as valid strings when `_type` is `str`.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            TypeError: If the provided default value is not an string.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_str(short='a', long='author', default='John Doe', desc='Author name')
            >>> args = am.parse()
            >>> print(args.author)
            'John Doe'
        """
        if default is not None and not isinstance(default, str) and not num_as_str:
            raise TypeError("default must be a str")
        self.__set_arg(str, short, long, default, desc, num_as_str)
        return None

    def arg_bool(self, *, short: str = None, long: str = None, default=False, desc=None):
        """
        Defines an optional boolean argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-r`).
            long (str, optional): Long name for the argument (e.g., `--run`).
            default (bool, required): Default bool value for the argument.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            TypeError: If the provided default value is not a bool.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_bool(short='r', long='run', default=False, desc='Run the program')
            >>> args = am.parse()
            >>> print(args.run)
            False
        """
        if not isinstance(default, bool):
            raise TypeError("default must be a bool")
        self.__set_arg(bool, short, long, default, desc)
        return None

    def arg_list(self, *, short: str = None, long: str = None, default=None, item_type: type = str, desc=None):
        """
        Defines an optional list argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-f`).
            long (str, optional): Long name for the argument (e.g., `--file`).
            default (list, optional): Default list value for the argument.
            desc (str, optional): Description for the argument, used in help messages.
            item_type (type, optional): Type to which each value should be converted (default: str).

        Raises:
            TypeError: If the provided default value is not a list.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_list(short='f', long='files', default=[], desc='List of input files')
            >>> # Simulating: python script.py --files a.txt --files b.txt
            >>> am.argv = ['--files', 'a.txt', '--files', 'b.txt']
            >>> args = am.parse()
            >>> print(args.files)
            ['a.txt', 'b.txt']
        """
        if default is None:
            default = list()
        else:
            if not isinstance(default, list):
                raise TypeError("default must be a list")
        self.__set_arg(list, short, long, default, desc)
        self.args[long or short].item_type = item_type  # noqa
        return None

    # TODO: make this function work without length check, to make it smaller
    # TODO: better handling jumps and issues
    def _parse_short_arg(self, short_arg: str, next_arg: str = None):
        jump = 0
        name = short_arg.removeprefix('-')
        if len(name) > 1:
            jump = 1
            i = 0
            while i < len(name):
                arg_name = name[i]
                arg_name = self.aliases.get(arg_name)
                if arg_name is None:
                    raise ArgParseError(f"Unknown argument '-{short_arg}'")
                arg = self.args.get(arg_name)
                if arg.type is bool:
                    arg_value = not arg.default
                    i += 1
                else:
                    raise ArgParseError(
                        f"Option '-{arg_name}' requires an argument and cannot be clustered with other short options.")

                if arg.short is not None:
                    setattr(self.result, arg.short, arg_value)
                if arg.long is not None:
                    setattr(self.result, arg.long, arg_value)
        else:
            arg_name = self.aliases.get(name)
            if arg_name is None:
                raise ArgParseError(f"Unknown argument '-{short_arg}'")
            arg = self.args.get(arg_name)
            if arg.type is bool:
                arg_value = not arg.default
                jump = 1
            else:
                if next_arg is None:
                    raise ArgParseError(f"Missing value for argument '-{short_arg}'")
                arg_value = next_arg
                jump = 2
            if arg.type is not list:
                if arg.type is not str:
                    try:
                        arg_value = arg.type(next_arg)
                    except ValueError:
                        raise ArgParseError(
                            f"Value should be a {arg.type.__name__}. argument `{arg.long or arg.short}`")
                else:
                    try:
                        for t in (float, int):
                            t(arg_value)
                            arg_value = str(arg_value)
                            if not arg.num_as_str:
                                raise ArgParseError(f"Value should be a str. argument `{arg.long or arg.short}`")
                    except ValueError:
                        pass
            else:
                values = getattr(self.result, arg_name, [])
                try:
                    casted_value = arg.item_type(arg_value)
                except Exception:
                    raise ArgParseError(f"Value '{arg_value}' should be of type {arg.item_type.__name__}")
                values.append(casted_value)
                arg_value = values
            if arg.short is not None:
                setattr(self.result, arg.short, arg_value)
            if arg.long is not None:
                setattr(self.result, arg.long, arg_value)
        return jump

    def _parse_long_arg(self):
        ...

    def _parse_pos_arg(self, arg):
        infered_type = str
        for t in (int, float):
            try:
                arg = t(arg)
                infered_type = t
                break
            except ValueError:
                pass
        if len(self.pos_args) < 1:
            return -1, None
        name = _arg = None

        req = [a for a in self.pos_args.values() if not a.parsed and a.required]
        non_req = [a for a in self.pos_args.values() if not a.parsed and not a.required]
        for a in req:
            name = a.name
            _arg = a
            self.pos_args[name].parsed = True
            break
        else:
            for a in non_req:
                name = a.name
                _arg = a
                self.pos_args[name].parsed = True
                break
            else:
                raise ArgParseError(f"Unknown argument `{arg}`")
        if not (infered_type is _arg.type):
            if not (_arg.type is str and _arg.num_as_str and infered_type in (int, float)):
                raise ArgParseError(f"Type mismatch for `{_arg.name}` (expected {_arg.type.__name__})")
        setattr(self.result, name, arg)

    def parse(self):
        """
        Parses the command-line arguments provided to the program.

        This method reads arguments from `sys.argv`, matches them against the
        defined options (via `arg_int`, `arg_float`, `arg_str`, or `arg_bool`),
        and returns an object containing the parsed results.
        Each argument value is automatically converted to its defined type.

        Returns:
            _ArgResult: An object with attributes corresponding to defined arguments,
            holding their parsed or default values.

        Raises:
            ValueError: If a non-boolean argument is missing a required value or if
            a value cannot be converted to the expected type.

        Example:
            >>> # Example usage
            >>> am = ArgMan()
            >>> am.arg_int(short='n', long='num', default=10, desc='Number of items')
            >>> am.arg_bool(short='v', long='verbose', default=False, desc='Enable verbose mode')
            >>> args = am.parse()
            >>> print(args.num, args.verbose)
            10 False
        """
        if len(self.argv) > 0 and self.argv[0] == '--help':
            self._print_help()
            exit(0)

        i = 0
        while i < len(self.argv):
            arg = self.argv[i]
            prefix = None
            if arg.startswith('--'):
                prefix = '--'
            elif arg.startswith('-'):
                prefix = '-'
            else:
                i += 1
                try:
                    self._parse_pos_arg(arg)
                    continue
                except ArgParseError as e:
                    self._print_err(str(e))

            if prefix == '-':
                next_arg = None
                if i + 1 < len(self.argv):
                    next_arg = self.argv[i + 1]
                try:
                    jump = self._parse_short_arg(arg, next_arg)
                    i += jump
                    continue
                except ArgParseError as e:
                    self._print_err(str(e))

            arg_name = arg.removeprefix(prefix)
            _arg_name = self.aliases.get(arg_name)
            if _arg_name is None:
                print(f"Unknown argument `{arg}`", file=sys.stderr)
                i += 1
                continue
            _arg = self.args.get(_arg_name)
            if _arg.type == bool:
                arg_value = not _arg.default
                i += 1
            else:
                if i + 1 >= len(self.argv):
                    self._print_err(f"Missing value for argument '{arg}'")
                arg_value = self.argv[i + 1]
                if _arg.type is not list:
                    if _arg.type is not str:
                        try:
                            arg_value = _arg.type(arg_value)
                        except ValueError:
                            self._print_err(f"Value should be a {_arg.type.__name__}. argument `{arg}`")
                    else:
                        try:
                            for t in (float, int):
                                t(arg_value)
                                arg_value = str(arg_value)
                            if not _arg.num_as_str:
                                self._print_err(f"Value should be a str. argument `{arg}`")
                        except ValueError:
                            pass
                i += 2

            if _arg.type is not list:
                if _arg.short is not None:
                    setattr(self.result, _arg.short, arg_value)
                if _arg.long is not None:
                    setattr(self.result, _arg.long, arg_value)
            else:
                values = getattr(self.result, _arg_name)
                if values is None:
                    values = []
                try:
                    casted_value = _arg.item_type(arg_value)  # noqa
                except Exception:
                    self._print_err(f"Value '{arg_value}' should be of type {_arg.item_type.__name__}")  # noqa
                values.append(casted_value)
                if _arg.short is not None:
                    setattr(self.result, _arg.short, values)
                if _arg.long is not None:
                    setattr(self.result, _arg.long, values)

        missing = [n for n, a in self.pos_args.items() if not a.parsed and a.required and not a.default]
        if len(missing) > 0:
            message = "Missing required arguments:\n"
            message += '\n'.join([f"    {name}" for name in missing])
            self._print_err(message)
        return self.result
