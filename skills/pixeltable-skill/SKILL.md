---
name: pixeltable
description: >
  Build multimodal AI apps with Pixeltable. One application file (app.py)
  declares TableModel tables and FastAPIRouter routes. Apply with pxt schema
  update. Serve with pxt service update. Use computed columns instead of
  LangChain, pandas-as-store, or a separate vector DB. Use when building RAG,
  processing images/video/audio/documents, or serving an API. Do NOT use for
  general Python or direct PostgreSQL administration.
license: Apache-2.0
allowed-tools: []
metadata:
  author: Pixeltable
  version: 2.6.0
  type: documentation
  executes-code: false
  category: data-infrastructure
  tags: [multimodal, ai, data, tables, embeddings, rag, udf, video, audio, images, documents, agents, tools, fastapi, declarative, computed-columns, vector-search]
  documentation: https://docs.pixeltable.com/
  support: https://github.com/pixeltable/pixeltable/discussions
  priority: 6
  pathPatterns: ["**/*.py"]
  importPatterns: ["pixeltable", "import pixeltable as pxt", "from pixeltable"]
  bashPatterns: ['^\s*pxt(?:\s|$)']
  promptSignals:
    phrases: ["pixeltable", "computed column", "embedding index", "add_embedding_index", "TableModel", "create_view", "document_splitter", "invoke_tools", "pxt schema", "pxt service", "pxt shell", "pxt errors", "pxt dashboard"]
    minScore: 6
---

## STOP

If you find yourself importing any of these, you are off-path:

1. **Do not use LangChain / LlamaIndex / Haystack / LangGraph.** Chunking is `document_splitter`. Search is `.similarity()`. Tools are `pxt.tools()` + `invoke_tools()`.
2. **Do not use pandas as a working store.** Tables are the store. `.collect().to_pandas()` is export only.
3. **Do not write `for row in ...:` loops calling models.** Wrap the call in a computed column.
4. **Do not install a separate vector database.** In an app, `__indexes__ = [pxt.EmbeddingIndex(...)]` on the model. In a notebook, `t.add_embedding_index(col, embedding=fn)`. Search with `.similarity(string=query)`.
5. **Do not write `while not done:` agent loops.** Insert a row. The computed-column chain runs.

See [anti-patterns.md](references/anti-patterns.md).

## Starting a new project

```bash
uvx pixeltable-new myapp
cd myapp && uv sync
pxt schema update app.py pipeline
pxt service update app.py pipeline
```

No HTTP: `uvx pixeltable-new myapp --batch`, then `pxt schema update app.py pipeline` and `python pipeline.py`.

`pipeline` is a catalog directory, not a folder on disk. The scaffold writes `pixeltable.toml`. If you copied files by hand, `pxt init` first. Schema does not start HTTP. Service does not create tables.

Do not download vertical templates. Add tables in `app.py`. [cli.md](references/cli.md).

## The application file

Write this. Then `pxt schema update app.py pipeline`. Then insert.

```python
from __future__ import annotations

import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()
embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')


class Documents(TableModel, name='documents'):
    title: pxt.String
    body: pxt.String
    uuid = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)


class Sentences(
    TableModel,
    name='sentences',
    base=Documents,
    iterator=pxtf.string.string_splitter(Documents.body, separators='sentence'),
):
    __indexes__ = [pxt.EmbeddingIndex(text, embedding=embed_fn, name='sentences_embed')]


@pxt.query
def search_documents(query_text: str, limit: int = 10):
    sim = Sentences.text.similarity(string=query_text)
    return (
        Sentences.where(sim > 0.3)
        .order_by(sim, asc=False)
        .select(Sentences.text, title=Sentences.title, score=sim)
        .limit(limit)
    )


api = FastAPIRouter(name='pipeline', prefix='/api')
api.add_insert_route(
    Documents, path='/ingest/document', inputs=[Documents.title, Documents.body],
    outputs=[Documents.title],
)
api.add_query_route(path='/search', query=search_documents, method='post')
```

Annotation is a stored column. Assignment is a computed column. Optional is `T | None`. Primary key is `pxt.Column(..., primary_key=True)`. Indexes on the model. `from pixeltable.serving import FastAPIRouter`.

Already have FastAPI: `app.include_router(api)` after schema update. Call `pxt.get_table()` inside custom handlers.

Full route example: [workflows.md](references/workflows.md).

## Apps vs notebooks

- **Apps:** `app.py` + `pxt schema update` + `pxt service update`. Indexes on the model.
- **Notebooks / REPL:** `pxt.create_table()`, `add_computed_column()`, `add_embedding_index()`. The appendix below uses that form.

## Where to look

| Need | Open |
|------|------|
| Apply, serve, inspect | [cli.md](references/cli.md) |
| Types, views, UDFs, export | [core-api.md](references/core-api.md) |
| Provider import and output shape | [providers.md](references/providers.md) |
| FastAPIRouter | [workflows.md](references/workflows.md) |
| Wrong stack | [anti-patterns.md](references/anti-patterns.md) |

Add video, audio, agents, or a UI by editing `app.py` (iterators: `frame_iterator`, `audio_splitter`, `document_splitter`). Do not paste a second apply path.

## Critical warnings

1. `openai.vision` does not exist. Use `chat_completions` with `image_url` blocks.
2. Cast to `pxt.String` before embedding AI outputs: `.text.astype(pxt.String)`.
3. `if_exists='ignore'` will not fix a wrong column. `drop_column()` then recreate.
4. `from pixeltable.functions.video import frame_iterator`, not `FrameIterator`.
5. `t.col.similarity(string=query)`, not positional.

## Notebook / REPL appendix

```python
import pixeltable as pxt

pxt.create_dir('my_project', if_exists='ignore')
t = pxt.create_table('my_project.documents', {
    'title': pxt.String,
    'content': pxt.String,
    'image': pxt.Image,
    'video': pxt.Video,
    'audio': pxt.Audio,
    'doc': pxt.Document,
}, if_exists='ignore')
```

Types are non-nullable by default. Optional is `T | None`. Do not use `pxt.Required`.

```python
from pixeltable.functions.uuid import uuid7

t = pxt.create_table('my_project.items', {
    'content': pxt.String,
    'uuid': uuid7(),
}, primary_key=['uuid'], if_exists='ignore')
```

Insert: `t.insert([{...}])`. Computed column:

```python
from pixeltable.functions.openai import chat_completions

t.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': t.content}],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore',
)
```

Views: `document_splitter`, `frame_iterator` (from `pixeltable.functions.video`), `string_splitter`, `audio_splitter`. Notebook indexes: `t.add_embedding_index('content', embedding=embed_fn, if_exists='ignore')`.

Query: `t.where(...).select(...).collect()`. Similarity: `t.content.similarity(string=query)`. In `@pxt.query`, alias as `score=sim`.

UDFs are recorded as a module path relative to the project root (`app.excerpt`). Hosted runtime: `pxt db update-runtime`.

Always `if_exists='ignore'` on notebook `create_*` / `add_*`. Failed cells: `t.recompute_columns(columns=['summary'], where=t.summary.errortype != None)`.

## Common pitfalls

| Wrong | Correct |
|-------|---------|
| `openai.vision(...)` | `chat_completions` with `image_url` |
| `from pixeltable.iterators import FrameIterator` | `from pixeltable.functions.video import frame_iterator` |
| Index a Json transcript column | `.text.astype(pxt.String)` first |
| Re-run with `if_exists='ignore'` to fix logic | `drop_column` then recreate |
| `similarity(query)` | `similarity(string=query)` |
| `pxt.Required[pxt.String]` | Non-nullable by default. Optional: `T \| None` |
| `.select(..., sim=sim)` in `@pxt.query` | `score=sim` |
| TOML routes or a retired serve CLI | `FastAPIRouter` + `pxt schema update` + `pxt service update` |
| `add_embedding_index()` in `app.py` | `__indexes__` on the TableModel |

## pxt CLI

```bash
pxt init
pxt schema update app.py pipeline
pxt service update app.py pipeline
pxt ls -l
pxt errors pipeline/documents
pxt dashboard
```

[cli.md](references/cli.md).

## Resources

- [Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit)
- [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- [Docs](https://docs.pixeltable.com/llms-full.txt)
