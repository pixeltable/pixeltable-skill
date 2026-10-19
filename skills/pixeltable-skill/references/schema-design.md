# Designing the schema

Settle these points before the first `pxt schema update`. Keys, types and nullability cannot change
in place later, and a wrong choice is fixed by migrating data, not by editing a line.

## 1. One table per entity

- An entity is a business object: a recording, a trip, a sample, a station, a review.
- A detail with many rows per parent and no life of its own is an iterator view of the parent (chunks,
  frames, segments, pages), or a typed Json list on the parent (the stops of one trip).
- Records that people create on their own schedule get their own table, with the parent's key as a
  column: assignments, review decisions, chat turns.
- One wide table for several entities, or one table per screen, is wrong.

## 2. A primary key at creation

- Use the natural key when the business already has a stable, unique id (`accession_no`, `trip_id`,
  an image file name): `code = pxt.Column(type=pxt.String, primary_key=True)`.
- Otherwise use a surrogate: `id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)`. The insert
  route's `outputs` (or `insert(..., return_rows=True)`) return the new id. Do not add a second
  "token" column to find the row again.
- A primary key cannot be added to an existing table. Without one there are no update or delete
  routes, no `batch_update`, and no `pxt get` or `pxt errors`.
- Inserting a duplicate key raises.

## 3. Types

- Every value used for filtering, grouping, sorting or joining is its own typed column, not a field
  inside Json.
- Timestamps are `pxt.Timestamp`; ISO strings with an offset are accepted at insert. Store UTC and
  convert when reading: `departs_at.astimezone(tz).hour`. Calendar dates are `pxt.Date`. Never store
  either as a String: strings sort and compare as text.
- Lists are `pxt.Json[list[str]]`, parsed once at insert, not comma- or pipe-separated strings that
  every UDF splits again.
- Nested payloads are Json typed with a TypedDict, so paths return typed values (see
  [expressions.md](expressions.md#json)).

## 4. Nullability

- `T` means every row has a value, and an insert without one fails. `T | None` means the value can be
  missing: an optional cover image, a sample that has not arrived yet.
- Changing nullability later is UNSUPPORTED. A field that becomes "required from now on" on a table
  with old rows is `T | None`, plus validation on new inserts.
- A non-nullable UDF parameter skips the call for a null argument, so a nullable column feeding it
  yields null without an error. Annotate the parameter `T | None` when the UDF should see the null.

## 5. Stored, computed or queried

| The value | Kind |
|-----------|------|
| What the outside world tells you: inputs, uploads, human decisions | stored (an annotation) |
| What you derive from the row's own values | computed (an assignment) |
| What depends on the current time, on other rows or on another table | queried (`@pxt.query`) |

Overdue, age, "in the last 2 days", counts, rates, rankings and per-parent totals are queries. A
stored copy goes stale the moment the clock or the other rows move. Pass "now" as a query parameter:

```python
@pxt.query
def overdue(now: datetime.datetime) -> pxt.Query:
    late = now.posix_timestamp() - Assignments.received_at.posix_timestamp() > Assignments.target_hours * 3600
    return Assignments.where((Assignments.status != 'done') & late).select(...)
```

## 6. References between tables

Store the other row's key, not its attributes: an assignment stores `station_code`, not the station's
name or capacity, which would go stale on the assignment when the station changes. Read the
attributes at query time:

```python
Assignments.join(Stations, on=Assignments.station_code == Stations.code).select(
    Assignments.id, Stations.name, Stations.capacity
)
```

Pixeltable has no foreign keys, so nothing checks that `station_code` exists. Check it in the route
handler, and say in your report that only the handler enforces it.

## 7. History

- Pixeltable versions every table: `pxt history PATH`, `pxt revert PATH`, `t.history()`. A revert
  undoes the last N operations on that one table, for everyone.
- Undoing one actor's changes after other people have made theirs is impossible with versions, and so
  is an audit trail per row. Use an append-only events table instead, one row per decision with who
  and when. Derive the current state at query time, and mark a reversal with a column (`revoked_at`)
  instead of deleting the row.
- A list of past values inside the current row (`history: [...]`) is wrong: it cannot be queried,
  indexed or undone per actor.

## 8. Validation

There are no CHECK or foreign-key constraints. A computed column whose UDF raises rejects the insert
and stores nothing, so a validating UDF works as a constraint:

```python
@pxt.udf
def checked_priority(priority: str) -> str:
    if priority not in ('STAT', 'URGENT', 'ROUTINE'):
        raise ValueError(f'unknown priority {priority!r}')
    return priority


class Samples(TableModel, name='samples'):
    ...
    priority: pxt.String
    priority_ok = checked_priority(priority)
```

Checking a key in another table needs a lookup, which a UDF cannot do: check it in the route handler.

## 9. Loading data more than once

The primary key makes a repeated load fail on the first duplicate. To load only the new rows, ask for
the keys that already exist and insert the rest:

```python
existing = set(trips.where(trips.trip_id.isin(ids)).select(trips.trip_id).collect()['trip_id'])
trips.insert([r for r in rows if r['trip_id'] not in existing])
```

`batch_update(rows, if_not_exists='insert')` is an upsert, but it recomputes the dependent columns of
every matched row, changed or not, so a column that calls a paid model runs again.

## 10. Creation time

There is no `now()` default. The client sends `created_at`, or a zero-argument UDF computes it at
insert:

```python
@pxt.udf
def utc_now() -> pxt.Timestamp:
    return datetime.datetime.now(datetime.timezone.utc)


class Samples(TableModel, name='samples'):
    ...
    created_at = pxt.Column(value=utc_now())
```

The column has no inputs, so updates never recompute it. An explicit `pxt recompute` of
`created_at` would overwrite it.

## 11. Indexes

`pxt.BtreeIndex(col)` on columns used for lookups (a user id, a status, a foreign key);
`pxt.EmbeddingIndex` for similarity search. Both go in `__indexes__`.

## 12. Claims and other races

Writes to one table are serialized. An update whose `where` includes the expected state is a
compare-and-set; its `num_rows` reports whether it won:

```python
status = assignments.update(
    {'status': 'claimed', 'claimed_by': tech},
    where=(assignments.id == assignment_id) & (assignments.status == 'queued'),
)
if status.num_rows == 0:
    raise HTTPException(409, 'already claimed')
```

`add_update_route` takes no such condition, so a claim needs a custom handler. Reading the row first
and updating it afterwards is a race.
