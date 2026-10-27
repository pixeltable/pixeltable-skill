---
name: incremental-ml-pipeline
description: >
  Build an ML or data pipeline that only recomputes new or changed rows.
  Declare work as computed columns; inserts run the chain for new rows only.
  Use when batch-running an LLM over a table, processing images, video,
  audio, and documents together, or avoiding a full refresh of an ML
  pipeline. Covers incremental pipelines, computed columns, and multimodal
  data pipelines. Existing values stay until you recompute. Load the
  pixeltable skill for the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill when a pipeline should process only new or changed rows
instead of rerunning the whole dataset. Each computed column records
what it reads. An insert computes the new rows. An update recomputes
dependents of the columns you changed. A changed expression applies to
new rows; existing values stay until `t.recompute_columns(...)` or
`pxt recompute`.

Wrap model calls in computed columns. Do not write `for row in ...:`
loops that call models.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.openai import chat_completions

pxt.create_dir('ml', if_exists='ignore')
items = pxt.create_table(
    'ml.items', {'content': pxt.String}, if_exists='ignore',
)
items.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': items.content}],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore',
)
items.insert([{'content': 'a new document'}])
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
