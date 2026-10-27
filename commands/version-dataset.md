---
description: >
  Version training datasets like code: table history, time travel, revert,
  and named snapshots. Use for data versioning, dataset versioning, dataset
  curation snapshots, or reproducing the rows used for a training run.
argument-hint: "[table path, e.g. my_app/docs]"
---

Version a Pixeltable table like code (history, time travel, snapshots, revert). Request: `$ARGUMENTS`

Load the `dataset-versioning` skill and the `pixeltable` skill. Versioning is built in. Do not add a separate dataset-versioning store for these tables.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md) and apply a table with `pxt schema update`.

2. Inspect and snapshot. `revert` is irreversible: dry-run first.

```bash
pxt history my_app/docs
pxt revert my_app/docs -n
pxt revert my_app/docs -f
```

```python
import pixeltable as pxt

t = pxt.get_table('my_app.docs')
t.history()
v1 = pxt.get_table('my_app.docs:1')  # read-only time travel
baseline = pxt.create_snapshot('my_app.docs_baseline', t, if_exists='ignore')
```

3. You cannot revert past version 0 or past a version a snapshot still references. Use snapshots for milestones (a training run, a curated set). Use revert only to undo the latest mistake.

4. Report the current version (`t.get_versions()[0]['version']` or `pxt history`) and any snapshot path you created.
