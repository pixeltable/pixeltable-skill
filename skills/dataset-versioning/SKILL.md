---
name: dataset-versioning
description: >
  Version training datasets like code: every insert, update, and schema
  change is a table version. Use when you need dataset versioning, data
  versioning, time travel, point-in-time snapshots, or to inspect and revert
  recent changes. Covers lineage and reproducible training sets. Query a
  historical version with get_table('path:N'). Snapshots freeze a named
  copy. revert() undoes the latest version and cannot be undone. Load the
  pixeltable skill for the CLI (pxt history, pxt revert) and the full app.py
  backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill to version a training or evaluation table the way you
version code: inspect history, query an old version, freeze a snapshot
before a load, or undo the latest change. Versioning is always on.
`revert()` permanently drops the latest version; it cannot revert past
version 0 or past a version a snapshot still references.

Time travel handles (`get_table('name:N')`) are read-only.

## Minimal pattern

```python
import pixeltable as pxt

pxt.create_dir('datasets', if_exists='ignore')
ds = pxt.create_table(
    'datasets.train',
    {'image': pxt.Image, 'label': pxt.String},
    if_exists='ignore',
)
ds.history()
baseline = pxt.create_snapshot(
    'datasets.train_v1', ds, if_exists='ignore',
)
ds_v0 = pxt.get_table('datasets/train:0')
```

Notebook or REPL form (`if_exists='ignore'` so it is re-runnable). For an
HTTP app, load the `pixeltable` skill and declare the same columns on a
`TableModel` with indexes in `__indexes__`, then `pxt schema update`.

## Full guidance

This skill is a thin catalog entry. Load the `pixeltable` skill for the
application file, CLI, providers, serving, and anti-patterns:
`skills/pixeltable-skill/SKILL.md` in this repo.

Install: `npx skills add pixeltable/pixeltable-skill`.
Docs: https://docs.pixeltable.com/
