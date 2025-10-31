# Customizing ArgMan

You can customize ArgMan’s behavior by passing options to its constructor:

## `prog` (str, optional)

Sets the program name used in help output.

Default: `sys.argv[0]`

Example:

```python
am = ArgMan(prog='mytool')

```

## `exit_on_err` (bool, optional)

If `True` (default): on parsing error, print help and exit with code 1.

If `False`: raise `ArgParseError` instead (useful for testing or embedding).

Example:

```python
am = ArgMan(exit_on_err=False)
try:
    args = am.parse()
except ArgParseError as e:
    print("Custom error:", e)
```

## `custom_errors` (dict[str, str], optional)

Override default error messages using semantic keys.

Each message can contain named placeholders like `{arg_name}`, `{type_name}`, etc.

Example:

```python
custom = {
    'unknown_long': "I don't know '--{arg_name}'. Try --help!",
    'missing_value_long': "Oops! '--{arg_name}' needs a value."
}
am = ArgMan(custom_errors=custom)
```

Available Error Keys:

```
'no_short_or_long'
'short_not_one_char'
'long_less_than_two_chars'
'positional_default_type_mismatch'
'required_after_optional'
'optional_default_type_mismatch'
'short_with_equal_sign'
'unknown_short_in_cluster'
'short_cluster_no_bool'
'unknown_single_short'
'missing_value_short'
'value_type_mismatch'
'list_item_type_mismatch'
'unknown_long'
'missing_value_long'
'unknown_positional'
'positional_type_mismatch'
'parse_unreachable'
'missing_positional_header'
'missing_positional_item'
```

Placeholders used in each message are documented in the source. Unused placeholders are safely ignored.

---

All options are optional. You can use any combination:

```python
am = ArgMan(
    prog='myapp',
    exit_on_err=False,
    custom_errors={'unknown_long': "What is '--{arg_name}'?"}
)
```