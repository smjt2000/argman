from collections import OrderedDict
from dataclasses import dataclass
import sys
import json


@dataclass
class _Arg:
    short: str = None
    long: str = None
    type: type = None
    item_type: type = str
    default: int | float | str | list = None
    parsed: bool = False
    desc: str = None


@dataclass
class _PosArg:
    name: str
    type: type = str
    default: int | float | str = None
    required: bool = False
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


_DEFAULT_ERRORS = {
    'no_short_or_long': "At least one of 'short' or 'long' must be provided",
    'short_not_one_char': "Short name must be a single character",
    'long_less_than_two_chars': "Long name must be at least 2 characters",
    'positional_default_type_mismatch': "Type of default value should be the same as defined type",
    'required_after_optional': "Required positional argument cannot be defined after an optional one. All required arguments must come first.",
    'optional_default_type_mismatch': "default must be a {type_name}",
    'short_with_equal_sign': "Short option '{option}' does not support '=' syntax. Use space-separated values.",
    'unknown_short_in_cluster': "Unknown argument '-{arg_name}' in '-{cluster}'",
    'short_cluster_no_bool': "Option '-{arg_name}' requires an argument and cannot be clustered with other short options.",
    'unknown_single_short': "Unknown argument '-{arg_name}'",
    'missing_value_short': "Missing value for argument '-{arg_name}'",
    'value_type_mismatch': "Value should be a {type_name} for argument '-{arg_name}'.",
    'list_item_type_mismatch': "Value '{value}' should be of type {type_name}",
    'unknown_long': "Unknown argument '--{arg_name}'",
    'missing_value_long': "Missing value for argument '--{arg_name}'",
    'unknown_positional': "Unknown argument '{arg_name}'",
    'positional_type_mismatch': "Type mismatch for '{arg_name}' (expected {type_name})",
    'parse_unreachable': "Unreachable '{arg_name}'",
    'missing_positional_header': "Missing required arguments:",
    'missing_positional_item': "    {arg_name}",
    'unknown_in_config': "Unknown argument '{arg_name}' in file '{file}'"
}


class ArgMan:
    def __init__(self, prog=None, exit_on_err=True, custom_errors=None):
        self.program = prog or sys.argv[0]
        self.exit_on_err = exit_on_err
        self.argv = sys.argv[1:]
        self.argc = len(self.argv)
        self.pos_only = False
        self.error_messages = _DEFAULT_ERRORS
        self.args: dict[str, _Arg] = {}
        self.pos_args: OrderedDict[str, _PosArg] = OrderedDict()
        self.aliases: dict[str, str] = {}
        self.result = _ArgResult(self.aliases)
        if custom_errors:
            self.error_messages.update(custom_errors)

    def __set_arg(self, _type: type, short: str = None, long: str = None, default=None, desc=None, item_type=None):
        """
        Internal helper for registering an argument.
        """
        if short is None and long is None:
            raise ValueError(self.error_messages['no_short_or_long'])
        if short is not None and (not isinstance(short, str) or len(short) != 1):
            raise ValueError(self.error_messages['short_not_one_char'])
        if long is not None and (not isinstance(long, str) or len(long) < 2):
            raise ValueError(self.error_messages['long_less_than_two_chars'])
        _long = long
        if _long is not None:
            _long = _long.replace('-', '_')
        main_name = long or short
        arg = _Arg(
            short=short, long=_long, type=_type,
            default=default, desc=desc, item_type=item_type
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
                if arg.type is list:
                    name += f' <{arg.type.__name__}[{arg.item_type.__name__}]>'
                else:
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
        if self.exit_on_err:
            print(message, file=sys.stderr)
            self._print_help()
            exit(1)
        raise ArgParseError(message)

    def load_config(self, file_path: str):
        try:
            with open(file_path) as f:
                args = json.load(f)
            for name in args:
                value = args[name]
                arg_name = self.aliases.get(name)
                if arg_name is None:
                    msg = self.error_messages['unknown_in_config']
                    msg = msg.format(arg_name=name, file=file_path)
                    raise ArgParseError(msg)
                arg = self.args.get(arg_name)
                if arg.parsed:
                    continue
                if not isinstance(value, arg.type):
                    try:
                        value = arg.type(value)
                    except ValueError:
                        msg = self.error_messages['value_type_mismatch']
                        msg = msg.format(type_name=arg.type.__name__, arg_name=name)
                        raise ArgParseError(msg)
                if arg.short:
                    setattr(self.result, arg.short, value)
                if arg.long:
                    setattr(self.result, arg.long, value)
        except ArgParseError as e:
            raise ArgParseError(str(e))

    def arg_pos(self, name: str, *, required=True, default=None, _type=str, desc=None):
        """
        Define a positional argument.

        Args:
            name (str): Name of the argument variable.
            required (bool, optional): Whether the argument must be provided. Defaults to True.
            default (any, optional): Default value for the argument if not provided.
            _type (type, optional): Type to which the argument value should be converted. Defaults to str.
            desc (str, optional): Description for the argument, used in help messages.

        Raises:
            ValueError:
                - If the argument is required but no default value is provided.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_pos('input_path', required=False, desc='Path to the input file')
            >>> args = am.parse()
            >>> print(args.input_path)
        """
        if default is not None and not isinstance(default, _type):
            raise ValueError(self.error_messages['positional_default_type_mismatch'])
        if required is True:
            no_req = [name for name, arg in self.pos_args.items() if not arg.required]
            if no_req:
                raise ValueError(self.error_messages['required_after_optional'])
        arg = _PosArg(
            name=name, type=_type,
            default=default, desc=desc,
            required=required
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
            msg = self.error_messages['optional_default_type_mismatch'].format(type_name='int')
            raise TypeError(msg)
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
            msg = self.error_messages['optional_default_type_mismatch'].format(type_name='number')
            raise TypeError(msg)
        self.__set_arg(float, short, long, float(default), desc)
        return None

    def arg_str(self, *, short: str = None, long: str = None, default=None, desc=None):
        """
        Defines an optional string argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-a`).
            long (str, optional): Long name for the argument (e.g., `--author`).
            default (str, required): Default str value for the argument.
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
        if default is not None and not isinstance(default, str):
            msg = self.error_messages['optional_default_type_mismatch'].format(type_name='str')
            raise TypeError(msg)
        self.__set_arg(str, short, long, default, desc)
        return None

    def arg_bool(self, *, short: str = None, long: str = None, default=False, desc=None):
        """
        Defines an optional boolean argument.

        Args:
            short (str, optional): Short name for the argument (e.g., `-r`).
            long (str, optional): Long name for the argument (e.g., `--run`).
            default (bool, required): Default bool value for the argument.
            desc (str, optional): Description for the argument, used in help messages.

        Behavior:
            - If `default=False` (default), the flag enables the feature:
            `--run` → `run = True`.
            - If `default=True`, the flag still enables the feature (`--verbose` → `verbose = True`),
            and a negation flag `--no-<long>` is **automatically added** to disable it:
            `--no-verbose` → `verbose = False`.
            - The `--no-<long>` negation flag is **only generated if `long` is provided**.
            Short-only boolean flags (e.g., `-v` with no `--verbose`) cannot be negated.

        Raises:
            TypeError: If the provided default value is not a bool.
            ValueError: If neither `short` nor `long` is provided, or if name lengths are invalid.

        Examples:
            >>> am = ArgMan()
            >>> am.arg_bool(short='r', long='run', default=False, desc='Run the program')
            >>> am.arg_bool(long='verbose', default=True, desc='Enable verbose output')
            >>> args = am.parse()
            >>> print(args.run)      # False by default, True if --run is passed
            >>> print(args.verbose)  # True by default, False if --no-verbose is passed
        """
        if not isinstance(default, bool):
            msg = self.error_messages['optional_default_type_mismatch'].format(type_name='bool')
            raise TypeError(msg)
        self.__set_arg(bool, short, long, default, desc)
        if default is True and long is not None:
            no_long = f"no-{long}"
            self.aliases[no_long] = long
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
                msg = self.error_messages['optional_default_type_mismatch'].format(type_name='list')
                raise TypeError(msg)
        self.__set_arg(list, short, long, default, desc, item_type)
        return None

    # TODO: make this function work without length check, to make it smaller
    # TODO: better handling jumps and issues
    def _parse_short_arg(self, short_arg: str, next_arg: str = None):
        if '=' in short_arg:
            msg = self.error_messages['short_with_equal_sign'].format(option=short_arg.split('=')[0])
            raise ArgParseError(msg)
        jump = 0
        name = short_arg.removeprefix('-')
        if len(name) > 1:
            jump = 1
            i = 0
            while i < len(name):
                arg_name = name[i]
                alias = self.aliases.get(arg_name)
                if alias is None:
                    msg = self.error_messages['unknown_short_in_cluster'].format(arg_name=arg_name, cluster=name)
                    raise ArgParseError(msg)
                arg = self.args.get(alias)
                if arg.type is bool:
                    arg_value = True
                    i += 1
                else:
                    msg = self.error_messages['short_cluster_no_bool'].format(arg_name=arg_name)
                    raise ArgParseError(msg)

                setattr(self.result, arg.short, arg_value)
                if arg.long is not None:
                    setattr(self.result, arg.long, arg_value)
        else:
            arg_name = self.aliases.get(name)
            if arg_name is None:
                msg = self.error_messages['unknown_single_short'].format(arg_name=name)
                raise ArgParseError(msg)
            arg = self.args.get(arg_name)
            if arg.type is bool:
                arg_value = True
                jump = 1
                setattr(self.result, arg.short, arg_value)
                if arg.long:
                    setattr(self.result, arg.long, arg_value)
                arg.parsed = True
                return jump
            else:
                if next_arg is None:
                    msg = self.error_messages['missing_value_short'].format(arg_name=name)
                    raise ArgParseError(msg)
                arg_value = next_arg
                jump = 2
            if arg.type is not list:
                try:
                    arg_value = arg.type(next_arg)
                except ValueError:
                    msg = self.error_messages['value_type_mismatch'].format(type_name=arg.type.__name__,
                                                                            arg_name=name)
                    raise ArgParseError(msg)
            else:
                values = getattr(self.result, arg_name, [])
                if not arg.parsed:
                    values = arg.default
                try:
                    casted_value = arg.item_type(arg_value)
                except ValueError:
                    msg = self.error_messages['list_item_type_mismatch'].format(
                        value=arg_value,
                        type_name=arg.item_type.__name__
                    )
                    raise ArgParseError(msg)
                values.append(casted_value)
                arg_value = values
            setattr(self.result, arg.short, arg_value)
            if arg.long is not None:
                setattr(self.result, arg.long, arg_value)
            arg.parsed = True
        return jump

    def _parse_long_arg(self, long_arg: str, next_arg: str = None):
        jump = 1
        name = long_arg.removeprefix('--')
        arg_name = self.aliases.get(name)
        if arg_name is None:
            msg = self.error_messages['unknown_long'].format(arg_name=name)
            raise ArgParseError(msg)
        arg = self.args.get(arg_name)
        if arg.type is bool:
            if long_arg.startswith('--no-'):
                arg_value = False
            else:
                arg_value = True
            setattr(self.result, arg.long, arg_value)
            if arg.short:
                setattr(self.result, arg.short, arg_value)
            arg.parsed = True
            return jump
        if next_arg is None:
            msg = self.error_messages['missing_value_long'].format(arg_name=name)
            raise ArgParseError(msg)
        arg_value = next_arg
        jump = 2
        if arg.type is not list:
            try:
                arg_value = arg.type(next_arg)
                setattr(self.result, arg.long, arg_value)
                if arg.short:
                    setattr(self.result, arg.short, arg_value)
                arg.parsed = True
            except ValueError:
                msg = self.error_messages['value_type_mismatch'].format(type_name=arg.type.__name__, arg_name=name)
                raise ArgParseError(msg)
        else:
            values = getattr(self.result, arg_name, [])
            if not arg.parsed:
                values = arg.default
            try:
                casted_value = arg.item_type(arg_value)
            except ValueError:
                msg = self.error_messages['list_item_type_mismatch'].format(
                    value=arg_value,
                    type_name=arg.item_type.__name__
                )
                raise ArgParseError(msg)
            values.append(casted_value)
            setattr(self.result, arg.long, values)
            if arg.short:
                setattr(self.result, arg.short, values)
            arg.parsed = True
        return jump

    def _parse_pos_arg(self, arg):
        if len(self.pos_args) < 1:
            msg = self.error_messages['unknown_positional'].format(arg_name=arg)
            raise ArgParseError(msg)
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
                msg = self.error_messages['unknown_positional'].format(arg_name=arg)
                raise ArgParseError(msg)
        try:
            value = _arg.type(arg)
        except ValueError:
            msg = self.error_messages['positional_type_mismatch'].format(
                arg_name=_arg.name,
                type_name=_arg.type.__name__
            )
            raise ArgParseError(msg)
        setattr(self.result, name, value)

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

        i = 0
        while i < len(self.argv):
            arg = self.argv[i]
            if self.pos_only:
                i += 1
                try:
                    self._parse_pos_arg(arg)
                    continue
                except ArgParseError as e:
                    self._print_err(str(e))

            if arg == '--help':
                self._print_help()
                exit(0)

            if arg == '--':
                self.pos_only = True
                i += 1
                continue
            if arg.startswith('--'):
                if '=' in arg:
                    arg, next_arg = arg.split('=', 1)
                    try:
                        self._parse_long_arg(arg, next_arg)
                        i += 1
                        continue
                    except ArgParseError as e:
                        self._print_err(str(e))
                else:
                    next_arg = self.argv[i + 1] if i + 1 < len(self.argv) else None
                    try:
                        jump = self._parse_long_arg(arg, next_arg)
                        i += jump
                        continue
                    except ArgParseError as e:
                        self._print_err(str(e))
            elif arg.startswith('-'):
                next_arg = None
                if i + 1 < len(self.argv):
                    next_arg = self.argv[i + 1]
                try:
                    jump = self._parse_short_arg(arg, next_arg)
                    i += jump
                    continue
                except ArgParseError as e:
                    self._print_err(str(e))
            else:
                i += 1
                try:
                    self._parse_pos_arg(arg)
                    continue
                except ArgParseError as e:
                    self._print_err(str(e))

            msg = self.error_messages['parse_unreachable'].format(arg_name=arg)
            raise AssertionError(msg)
        missing = [n for n, a in self.pos_args.items() if not a.parsed and a.required and not a.default]
        if len(missing) > 0:
            header = self.error_messages['missing_positional_header']
            msg = self.error_messages['missing_positional_item']
            message = header
            message += '\n'.join([msg.format(arg_name=name) for name in missing])
            self._print_err(message)
        return self.result
