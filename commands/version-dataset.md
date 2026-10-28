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

2. Show the history and create the snapshot as the `dataset-versioning` skill shows. Run `pxt history my_app/docs` to list versions. Do not revert in this step.

3. Revert only when the user asks to undo a specific change. Dry-run with `pxt revert my_app/docs -n`, confirm with the user, then run `pxt revert my_app/docs -f`. Revert is irreversible. You cannot revert past version 0 or past a version a snapshot still references. Use snapshots for milestones (a training run, a curated set).

4. Report the current version (`pxt history`) and any snapshot path you created.
