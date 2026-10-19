# Expressions

A model body runs once, when Python defines the class. A column name in it is a reference to the
column, not a value, and each assignment builds an expression that Pixeltable evaluates for every
row, now and on every future insert. Python code that runs on the spot sees the reference, not the
data. Write derived values as expressions; a UDF is for one step that has no expression form.

## Python that stores a constant

These pass `pxt schema check`, raise nothing, and store the same value in every row:

| Wrong | Stores | Correct |
|-------|--------|---------|
| `f'Describe {product}'` | the text `Describe product` | `pxtf.string.format('Describe {}', product)` or `'Describe ' + product` |
| `str(product)`, `'%s' % product`, `'{}'.format(product)` | the column's name | as above |
| `note is None`, `note is not None` | `False`, `True` | `note == None`, `note != None` |

## Python that raises

`and`, `or`, `not`, `if ... else`, `min()`, `max()`, `len()` and `for` over a column raise. Use `&`,
`|`, `~`, the functions below, and for a branch see [Conditionals](#conditionals).

## Operators

- Arithmetic `+ - * / // %` on numbers, `+` on strings, comparisons, `&`, `|`, `~`.
- `x == None`, `x != None`, `x.isin(['12', '33'])`, `round(x, 1)`, `x.astype(pxt.Float)`.
- Timestamps take no `+` or `-`. For a duration, subtract `ts.posix_timestamp()` values (seconds as
  Float); on Dates, `d.add_days(n)`.

## Json

Type a Json column with a TypedDict and its paths return typed values:

```python
class Stop(TypedDict):
    name: str
    delay: float


class Trips(TableModel, name='trips'):
    trip_id = pxt.Column(type=pxt.String, primary_key=True)
    stops: pxt.Json[list[Stop]]
    tags: pxt.Json[list[str]]
    first_stop = stops[0].name                              # String
    last_delay = stops[-1].delay                            # Float
    all_delays = stops['*'].delay                           # list of Float
    late_stops = stops.filter(lambda s: s.delay > 5.0)      # list of Stop
    n_late = stops.filter(lambda s: s.delay > 5.0).len()    # Int
    worst_stop = stops.sort(lambda s: s.delay, asc=False)[0].name
    max_delay = stops.map(lambda s: s.delay).max()
    on_time = (stops[-1].delay >= -1.0) & (stops[-1].delay <= 5.0)
    rush = tags.contains('rush')
```

- Paths: `.field`, `['key']`, `[0]`, `[-1]`, slices, `['*']` for every element.
- `map`, `filter` and `sort` take a lambda over one element. Inside the lambda the same rules apply,
  so combine conditions with `&` and `|`.
- Methods: `len`, `get(key, default)`, `contains`, `keys`, `values`, `items`, `sum`, `min`, `max`,
  `mean`, `count`, `flatten`, `concat`, `merge`, `is_empty`. `pxtf.json.dumps(x)` gives a String.
- A Json field that contains a string becomes a String with `.astype(pxt.String)`, before string
  functions or `+`.
- An untyped `pxt.Json` column returns untyped Json from every path. Model output (`chat_completions`,
  `messages`) is untyped: extract the needed field once, then cast it.

## Strings, times and media

- Strings: `pxtf.string.format('{} @ {}', a, b)`, `a + ' / ' + b`, `pxtf.string.join(', ', items)`,
  and methods such as `upper`, `lower`, `strip`, `replace`, `split`, `contains`, `startswith`, `len`,
  `wrap`. `note.split().len()` counts words.
- Timestamps: `.year`, `.month`, `.day`, `.hour`, `.minute`, `.second` are properties, written without
  parentheses. Methods include `astimezone('America/Los_Angeles')`, `strftime(fmt)`, `isoformat()`,
  `weekday()` and `posix_timestamp()`. Local hour: `departs_at.astimezone(tz).hour`.
- Images: `.width`, `.height`, `.size`, `.mode` are properties. Methods include `resize((w, h))`,
  `thumbnail((w, h))`, `rotate(deg)`, `convert('L')`, `crop(box)` and `get_metadata()`.
- Video: `extract_frame(timestamp=...)`, `get_metadata()`, `get_duration()`, `clip`, `crop`,
  `resize`, `extract_audio`, `with_audio`, `overlay_text`, `concat_videos` and more in
  `pixeltable.functions.video`. Audio: `pixeltable.functions.audio`.
- Before writing a UDF, list what ships: `[n for n in dir(pxtf.video) if not n.startswith('_')]`,
  then `help(pxtf.video.crop)`. The same goes for `image`, `audio`, `string`, `json`, `timestamp`,
  `vision` and each provider module.

## Conditionals

Pixeltable has no conditional, coalesce or lookup expression. Write the smallest UDF that does that
one step, with nullable parameters where the inputs can be null, and keep everything around it in
expressions:

```python
@pxt.udf
def coalesce(override: str | None, fallback: str | None) -> str | None:
    return override if override is not None else fallback


@pxt.udf
def delay_band(delay: float | None) -> str:
    if delay is None:
        return 'unknown'
    return 'late' if delay > 5.0 else 'on time'


class Trips(TableModel, name='trips'):
    ...
    band = delay_band(stops[-1].delay)      # not a UDF that also extracts the field
```

## When a UDF is the right tool

- Domain logic with no expression form: geometry, a regex parser, a scoring rule.
- One step: one row's values in, one value out. Five derived values are five columns, not one UDF that
  returns a dict.
- Never write a UDF for these:
  - field extraction, arithmetic, formatting or list filtering;
  - a loop over frames, chunks or pages, which is an iterator view;
  - loading a model that has a shipped wrapper (`pxtf.huggingface`, `pxtf.whisper`, ...);
  - reading another table: `pxt.get_table()` inside a UDF fails.
- Put UDFs in a module file (`app.py` or `udfs.py`). Pixeltable refuses a UDF defined in the main
  module of a script.
- A UDF that returns a Video, Audio or Document returns a file path. Pixeltable records that path and
  does not copy the file unless the column has `destination=`, so a file in a temporary directory is
  lost later. Prefer the shipped media functions, which manage their output files.

## Trying an expression

Evaluate a candidate on existing rows before adding it as a column; nothing is stored:

```python
t = pxt.get_table('my_app/trips')
t.select(t.trip_id, band=delay_band(t.stops[-1].delay)).limit(5).collect()
```

Or bind the models and use the class: `import app; app.TableModel.bind_all('my_app')`, then
`app.Trips.select(...).collect()`. Limit the rows when the expression calls a paid model.

Calling a `@pxt.query` function from Python returns an expression, not rows. In a script, write the
query against the bound model class instead, or call the route.
