---
description: >
  Build an ML or data pipeline that only computes new or changed rows:
  computed columns, views, and indexes stay up to date on insert. Use for
  incremental pipelines, batch LLM inference over a table, or multimodal
  data pipelines without a full recompute.
argument-hint: "[what to compute per row]"
---

Build an incremental ML or data pipeline (only new or changed rows are computed). Request: `$ARGUMENTS`

Load the `incremental-ml-pipeline` skill and the `pixeltable` skill. Wrap the model in a computed column. Do not write `for row in ...:` loops calling models, and do not add Prefect or Celery for this.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare the transformation as a computed column as the `incremental-ml-pipeline` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert rows: only those rows are computed. An update recomputes dependents of the columns you changed. A new computed column runs on every existing row. After editing an expression, `pxt schema update` keeps old values until `pxt recompute my_app/docs summary -f`. Confirm the provider import in [providers.md](../skills/pixeltable-skill/references/providers.md).

4. Show how to insert one row and `collect()` the computed column.
