---
name: vector-database-alternative
description: >
  Store embeddings alongside your data instead of running a separate vector
  DB. Add an embedding index on a table column and search with similarity.
  Use when you want vector search next to the source rows, without a
  standalone vector database to keep in sync. Covers embeddings, vector
  search, semantic search, and chunking-plus-embeddings stored with your
  data. Inserts and updates maintain the index. Load the pixeltable skill
  for the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.13.0
---

## When to use

Use this skill when the question is where to store embeddings next to
the data they came from. Pixeltable keeps an embedding index on the
table. Inserts add entries; updates and recomputes replace them, so the
index matches the column.

This is not a drop-in of a hosted vector service. It is an index on
your table. Do not add a separate vector database for this job.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.openai import embeddings

pxt.create_dir('kb', if_exists='ignore')
docs = pxt.create_table(
    'kb.docs', {'body': pxt.String}, if_exists='ignore',
)
docs.add_embedding_index(
    'body',
    embedding=embeddings.using(model='text-embedding-3-small'),
    if_exists='ignore',
)
sim = docs.body.similarity(string='query')
docs.order_by(sim, asc=False).limit(10).select(
    docs.body, score=sim,
).collect()
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
