# How to do it

Define arguments

Parse arguments

Use arguments

## First step

```python
from argman import ArgMan

am = ArgMan()
```

---

## Second step(define arguments)

Explanation [here](#Argument-types).

---

## Third step(parse arguments)

```python
args = am.parse()
```

---

# Argument types

#### `arg_int(short=None, long=None, default=None, desc=None)`

```python
am.arg_int(short='n', long='num', default=5, desc='Number of items')
args = am.parse()
print(args.num)
print(args.n)
```

Run:

```shell
python app.py --num 10
# or
python app.py -n 10
```

Output:

```
10  # args.num
10  # args.n
```

---

#### `arg_float(short=None, long=None, default=None, desc=None)`

```python
am.arg_float(short='r', long='rate', default=1.0, desc='Interest rate')
args = am.parse()
print(args.rate)
print(args.r)
```

Run:

```shell
python app.py --rate 2.5
```

Output:

```
2.5  # args.rate
2.5  # args.r
```

---

#### `arg_str(short=None, long=None, default=None, desc=None)`

```python
am.arg_str(short='a', long='author', default='anon', desc='Author name')
args = am.parse()
print(args.author)
print(args.a)
```

Run:

```shell
python app.py --author Mike
```

Output:

```
Mike  # args.author
Mike  # args.a
```

---

#### `arg_bool(short=None, long=None, default=False, desc=None)`

```python
am.arg_bool(short='v', long='verbose', default=False, desc='Enable verbose mode')
args = am.parse()
print(args.verbose)
print(args.v)
```

Run:

```shell
python app.py --verbose
# or
python app.py -v
```

Output:

```
True  # args.verbose
True  # args.v
```

If ```default=True```, use ```--no-verbose``` to disable:

```python
am.arg_bool(long='color', default=True)
# --color → True, --no-color → False
```

---

#### `arg_list(short=None, long=None, default=None, item_type=str, desc=None)`

```python
am.arg_list(short='f', long='files', default=[], desc='Input files')
am.arg_list(long='nums', item_type=int, desc='Numbers')
args = am.parse()
print(args.files)
print(args.nums)
```

Run:

```shell
python app.py --files a.txt --files b.txt --nums 1 --nums 2 --nums 3
```

Output:

```
['a.txt', 'b.txt']  # args.files
[1, 2, 3]  # args.nums
```

---

#### `arg_pos(name, *, required=True, default=None, _type=str, desc=None)`

```python
am.arg_pos('input', _type=str, desc='Input file')
am.arg_pos('count', _type=int, required=False, default=1)
args = am.parse()
print(args.input)
print(args.count)
```

Run:

```shell
python app.py data.txt 5
```

Output:

```
data.txt  # args.input
5  # args.count
```

> Required positional args must be defined before optional ones.