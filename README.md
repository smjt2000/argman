# ArgMan

A lightweight, zero-dependency argument parser for Python CLI tools — simple, testable, and intuitive.

![ArgMan example code](https://raw.githubusercontent.com/smjt2000/argman/main/assets/ArgMan.png)
---

## Features

- Short (`-v`) and long (`--verbose`) flags
- Type-safe parsing: `int`, `float`, `str`, `bool`, `list`
- Default values and boolean toggles
- Repeated arguments with `arg_list`
- Automatic `--no-flag` for booleans
- Positional arguments
- `--arg=value` and `--` terminator support
- Clean help and error messages
- Config file support (JSON) via `load_config()`
- Export parsed args via `dump_args()`
- Choices validation(`choices=[...]`)
- Custom validation(`validator=...`)
- Relation between arguments: `requires`, `conflicts`

---

## Documentation

Usage examples and API reference: [docs/](https://github.com/smjt2000/argman/tree/main/docs)

---

## Installation

You can install __ArgMan__ directly from [PyPi](https://pypi.org/project/argman/):

```shell
pip install argman
```

## Running Tests

```bash
python -m unittest discover tests
```

## Roadmap

v0.1 — Core Functionality

- [x] Complete

v0.2 — Extended Features

- [x] `arg_list`, `--no-flag`, `--arg=value`, `--` support
- [x] Custom error messages
- [x] config files(`load_config`, `dump_args`)
- [x] subcommands(~~one level, must be first argument~~ can be nested now)
- [x] custom `argv` support(e.g., `ArgMan(argv=['prog', '--num', '5'])`)

v0.3 — Docs & Publish

- [x] Docs ready
- [x] Publish to PyPI

v0.4 — Validation & Customization

- [x] Choices: Limit argument values to a predefined set of allowed options.
- [x] Validators: Define custom checks for argument values (e.g., range, format).
- [x] Dependencies: Specify relationships between arguments (`requires`, `conflicts`).
- [ ] Formatters: Apply custom transformations to parsed argument values (e.g., `str.lower`).

## License

LGPL-3.0 © 2025