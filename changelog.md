# Changelog

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