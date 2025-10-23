# ArgMan

**ArgMan** is a lightweight argument manager for Python CLI tools —
a simple, zero-dependency alternative to `argparse`.

---

## Features

- Short & long aliases (`-n` / `--num`)
- Type-safe parsing (`int`, `float`, `str`, `bool`, `list`)
- Default values
- Boolean toggles
- Repeated arguments via `arg_list`
- Clean, testable API

---

## Defining Arguments

#### `arg_int(short=None, long=None, default=None, desc=None)`
Defines an integer argument.

#### `arg_float(short=None, long=None, default=None, desc=None)`
Defines a float argument.

#### `arg_str(short=None, long=None, default=None, desc=None)`
Defines a string argument.

#### `arg_bool(short=None, long=None, default=None, desc=None)`
Defines a boolean argument.

#### `arg_list(short=None, long=None, default=None, desc=None)`
Defines an multi-use argument collector.


## Usage
```python
from argman import ArgMan

am = ArgMan()
am.arg_int(short='n', long='num', default=5, desc='Number of nodes')
am.arg_float(short='r', long='rate', default=1.0, desc='Payment rate')
am.arg_str(short='a', long='author', default='John Doe', desc='Author name')
am.arg_bool(short='v', long='verbose', default=False, desc='Enable verbose output')
am.arg_list(short='f', long='files', desc='Input files')

args = am.parse()

print(args.n)       # args.num
print(args.rate)    # args.r
print(args.author)  # args.a
print(args.verbose) # args.v
print(args.files)   # args.f
```

### Run
```bash
python3 program.py -n 10 --rate 1.2 -a Mike -v -f file1.txt --files file2.txt
```

### Output
```
10
1.2
Mike
['file1.txt', 'file2.txt']
```

---

## Running Tests
```
python -m unittest discover tests
```

---

## Roadmap

### v0.1 — Core Functionality
- [x] Basic argument parsing
- [x] Short & long aliases
- [x] Type conversion (int, float, str, bool)
- [x] Default values
- [ ] Help message support
- [ ] Positional argument support

### v0.2 — Extended Features
- [x] arg_list (multi-use collector)
- [ ] Custom error messages
- [ ] Config file parsing
- [ ] Subcommands support (like git add / git commit)

### v0.3 — Docs & Publis
- [x] Add docstrings
- [ ] Publish to PyPI


---

## License
GPL-3.0 © 2025