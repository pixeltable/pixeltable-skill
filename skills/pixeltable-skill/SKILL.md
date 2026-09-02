---
name: pixeltable
description: >
  Build multimodal AI apps with Pixeltable. One application file (app.py)
  declares TableModel tables and FastAPIRouter routes. Loop: Declare
  (pxt schema update), Experiment (insert, dashboard, schema diff), Serve
  (pxt service update). Use computed columns instead of LangChain,
  pandas-as-store, or a separate vector DB. Use when building RAG,
  processing images/video/audio/documents, or serving an API. Do NOT use for
  general Python or direct PostgreSQL administration.
license: Apache-2.0
allowed-tools: []
metadata:
  author: Pixeltable
  version: 2.7.0
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

## What is Pixeltable?

One application file (`app.py`) is the backend. The loop is Declare, Experiment, Serve.

- **Declare:** `TableModel` in `app.py`, then `pxt schema update`. Creates tables. Does not start HTTP.
- **Experiment:** insert a sample, `.select()`, `pxt dashboard`, `pxt schema diff`. Compute runs on insert. After Serve: curl POST.
- **Serve:** `pxt service update` (local or `pxt://`). `pxt service list` prints the URL. `pxt service run` is local only.

Hosted packaging is `pxt db update` (image, workers). It is not Experiment.

First run: [Quickstart](https://docs.pixeltable.com/overview/quick-start). Why: [Why Pixeltable](https://docs.pixeltable.com/overview/pixeltable).

## Starting a new project

```bash
pip install 'pixeltable[serve]'
pxt init
pxt service example --out app.py
pxt schema update app.py my_app
pxt service update app.py my_app
```

`pxt service example` writes models plus a `FastAPIRouter`. Schema only (no HTTP): `pxt schema example --brief --out app.py`. Then edit `app.py` and re-apply. Full flags: [cli.md](references/cli.md).

`my_app` is a catalog directory, not a folder on disk. `pxt init` writes `pixeltable.toml`. Schema does not start HTTP. Service does not create tables.

Same file on Cloud: `pxt db update pxt://org:db`, then `pxt schema update app.py pxt://org:db`, then `pxt service update app.py pxt://org:db`. `pxt db update` packs the hosted image and workers; it is not Experiment. `pxt service run` is local only. Experiment on Cloud is dashboard insert plus `pxt schema diff`. [Cloud](https://docs.pixeltable.com/howto/deployment/cloud).

## The application file

Write this. Then `pxt schema update app.py my_app`. Then insert, or open `pxt dashboard`.

```python
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


api = FastAPIRouter(name='ingest', prefix='/api')
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

Add video, audio, agents, or a UI by editing `app.py` (iterators: `frame_iterator`, `audio_splitter`, `document_splitter`). Start from `pxt service example` or `pxt schema example`. Do not invent a second apply path.

## API traps

| Wrong | Correct |
|-------|---------|
| `openai.vision(...)` | `chat_completions` with `image_url` |
| `from pixeltable.iterators import FrameIterator` | `from pixeltable.functions.video import frame_iterator` |
| `similarity(query)` | `similarity(string=query)` |
| Re-run with `if_exists='ignore'` to fix logic | `drop_column` then recreate |
| `pxt.Required[pxt.String]` | Non-nullable by default. Optional: `T \| None` |
| `.select(..., sim=sim)` in `@pxt.query` | `score=sim` |
| TOML routes or a retired serve CLI | `FastAPIRouter` + `pxt schema update` + `pxt service update` |
| `add_embedding_index()` in `app.py` | `__indexes__` on the TableModel |

Extract the field (`.text`, `.choices[0].message.content`). Cast Json with `.astype(pxt.String)` only before embedding or concatenating.

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

UDFs are recorded as a module path relative to the project root (`app.excerpt`).

Always `if_exists='ignore'` on notebook `create_*` / `add_*`. Failed cells: `t.recompute_columns(columns=['summary'], where=t.summary.errortype != None)`.

## pxt CLI

```bash
pxt init
pxt service example --out app.py
pxt schema update app.py my_app
pxt service update app.py my_app
pxt ls -l
pxt errors my_app/documents
pxt dashboard
```

[cli.md](references/cli.md).

## Resources

- [Quickstart](https://docs.pixeltable.com/overview/quick-start)
- [CLI](https://docs.pixeltable.com/platform/cli)
- [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- [Docs](https://docs.pixeltable.com/llms-full.txt)
