# Changelog

## v0.3.6 (2025-12-13)

- ### Fixed
    - Subcommand dispatch now correctly handles global flags before subcommand name. Commands like `app --verbose resize --width 100` are now parsed successfully, with global flags (`--verbose`) applied to the root parser and the subcommand (`resize`) dispatched correctly.

## v0.3.5 (2025-12-09)

- ### Fixed
    - Updated internal calls of '__set_arg' to use keyword arguments, eliminating a bug caused by positional argument
      misalignment.

## v0.3.4 (2025-12-09)

- ### Added
    - Argument dependencies: `requires()` method to enforce that if an argument is used, other specified arguments must
      also be provided.
    - Argument conflicts: `conflicts()` method to ensure that certain arguments cannot be used together (mutual
      exclusion).
    - Dedicated error messages for dependency violations:
        - `require_not_provided`: Clearly indicates missing required arguments.
        - `conflict_is_provided`: Clearly states which conflicting arguments were used together.

## v0.3.3 (2025-12-08)

- ### Added
    - Custom validators for all argument types (arg_int, arg_str, arg_list, etc.) via the validator parameter.
    - Validation of default values against custom validators at definition time.

- ### Changed
    - Refactored parsing logic: type conversion and validation are now encapsulated in `_Arg.convert()`,
      `_Arg.validate_choices()` and `_Arg.validate_custom()` methods.
    - Isolated value assignment: setting argument values (for short/long aliases) is now handled by a dedicated
      `__set_value` helper.
    - Internal code is cleaner, more modular, and easier to extend (e.g., for future formatters or advanced validation).

## v0.3.1 (2025-11-29)

- ### Added
    - `choices` validation for all optional argument types (arg_int, arg_str, etc.) to restrict allowed values.
- ### Changed
    - CLI parsing now validates values against `choices` at runtime with clear error messages.

## v0.3.0 (2025-11-09)

- ### Added
    - Support for subcommands via `add_cmd(name, desc)` method.

    - Ability to define custom argument lists using `argv` parameter in `ArgMan`.

    - `load_config(file_path)` method for loading arguments from a JSON file.

    - `dump_args(file_path=None)` method for exporting current argument state to JSON.

    - Custom error message system via `custom_errors` dictionary.

## v0.2.2 (2025-11-06)

- ### Added

    - Support for config files via `load_config(file_path)` method (JSON format).

    - `dump_args(file_path=None)` method to serialize parsed arguments to JSON (print to stdout or save to file).

    - Internal parsed tracking for arguments to enable safe config/CLI precedence handling.

## v0.2.1 (2025-10-31)

- ### Added

    - Support for custom error messages via the `custom_errors` parameter in ArgMan constructor.

    - Full set of default error messages with named placeholders for dynamic content.

    - All error messages (both setup-time and parse-time) now use the unified error system.


- ### Changed

    - Error messages are now fully customizable without modifying library code.

    - Internal error handling refactored to use semantic keys (e.g., 'unknown_long') instead of hardcoded strings.

---

## v0.2.0 (2025-10-30)

- ### Added

    - Core argument types: `arg_int`, `arg_float`, `arg_str`, `arg_bool`, `arg_list`, `arg_pos`.

    - Short (`-v`) and long (`--verbose`) aliases with validation.

    - Boolean negation via `--no-flag` (when `default=True` and long is provided).

    - `--arg=value` syntax support.

    - `--` terminator to switch to positional-only mode.

    - Positional argument ordering enforcement (required before optional).

    - Help message generation.

    - `exit_on_err` flag for testable error handling.


- ### License
    - LGPL-3.0-or-later