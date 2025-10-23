# ArgMan

**ArgMan** is a lightweight argument manager for Python CLI tools —
a simple, zero-dependency alternative to `argparse`.

---

## Example

```python
from argman import ArgMan

am = ArgMan()
am.arg_int(short='n', long='num', default=5, desc='Number of nodes')
am.arg_bool(short='v', long='verbose', default=False, desc='Enable verbose output')

args = am.parse()
print(args.num, args.verbose)
```
### Run
```
python script.py --num 10 -v
```
### Output
```python
10 True
```

---

## Features

- Short & long aliases (`-n` / `--num`)
- Type-safe parsing (`int`, `float`, `str`, `bool`, `list`)
- Default values
- Boolean toggles
- Repeated arguments via `arg_list`
- Clean, testable API

---

## Running Tests
```
python -m unittest discover tests
```

---

## License
GPL-3.0 © 2025