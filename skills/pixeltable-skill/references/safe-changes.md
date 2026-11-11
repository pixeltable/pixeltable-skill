# Changing a project safely

The catalog contains the user's data: uploaded media, human decisions, and model outputs that took
time and money to compute. A catalog directory is not a build artifact, and dropping it to start over
is never the development loop.

## Ask first

Show the user what will happen and get a yes before any of these:

- `pxt drop`, `pxt drop-dir`, `pxt schema prune`, `pxt revert`, or `t.delete()` of rows you did not
  insert yourself in this session;
- any command with `--allow-destructive`;
- adding a computed column that calls a paid model to a table that has rows: it runs once per
  existing row. Say how many rows (`pxt count PATH`) and which model;
- `pxt recompute` of a column that calls a paid model, directly or through its dependents (recompute
  cascades unless given `--no-cascade`);
- resolving an UNSUPPORTED change by renaming or dropping a column that has data.

Get the plan without applying it: `pxt schema diff app.py TARGET` (or `pxt schema update ... -n`),
`pxt recompute ... -n`. `-f` skips the prompt for a plan with the user's approval, or for an additive
change. It is not a default to add to every command, and it does not belong in a README's
instructions.

## A development loop that destroys nothing

- Develop in a scratch catalog directory: `pxt schema update app.py my_app_dev`. The same application
  file can target several directories. Drop the scratch directory when you need a clean slate; never
  drop the user's.
- Write seed scripts so they can run twice: `insert(rows, if_exists='ignore')` inserts only the keys that
  are missing ([schema-design.md](schema-design.md#9-loading-data-more-than-once)).
- Try a new expression with `select()` on existing rows before adding it as a column
  ([expressions.md](expressions.md#trying-an-expression)). Limit the rows when it calls a model.
- Do not put test rows into the user's tables. If you must, delete exactly those rows afterwards and
  say so.

## Changes that need a manual step

| Change | What Pixeltable does | Do |
|--------|---------------------|----|
| Edit a UDF's body | `pxt schema diff` shows nothing; stored values keep the old logic | `pxt recompute PATH COL...` for the columns that call it. Ask first if they, or their dependents, call a paid model |
| Edit a computed column's expression, same type | A safe alter; existing rows keep the old values | `schema update` prints the `pxt recompute` command. Ask before running it on a paid column |
| Make a column nullable (`T` to `T \| None`) | A safe alter, unless a non-nullable computed column depends on it: then UNSUPPORTED | Nothing, for the safe alter |
| Change a column's type, make it required, or change `stored=` | UNSUPPORTED: the whole update applies nothing | Stop and give the user the options. Renaming drops the old values, and a computed column under the new name recomputes. A new column can live next to the old one |
| Change a view's iterator | Cannot be migrated in place | A new view under a new name. The old view stays until the user agrees to drop it |
| Add a primary key | Impossible on an existing table | Design it in from the start ([schema-design.md](schema-design.md#2-a-primary-key-at-creation)) |
| Any schema change while a service runs | Its routes answer 409 | `pxt service update app.py TARGET -f` |

## Report what changed

End every task with a list of your catalog changes:
- tables created, altered or dropped;
- rows inserted, updated or deleted, and by which command;
- columns recomputed, and the number of model calls.
