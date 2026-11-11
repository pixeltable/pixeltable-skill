---
name: pixeltable
description: >
  Build multimodal AI apps with Pixeltable. One application file (app.py)
  declares TableModel tables and FastAPIRouter routes. Create tables with
  pxt schema update. Start HTTP with pxt service update. Insert a row or
  POST to try the app. Use computed columns instead of LangChain,
  pandas-as-store, or a separate vector DB. Use when building RAG or
  tool-calling agents, processing images/video/audio/documents, or serving an
  API. Do NOT use for general Python or direct PostgreSQL administration.
license: Apache-2.0
allowed-tools: []
metadata:
  author: Pixeltable
  version: 2.12.0
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

See [anti-patterns.md](references/anti-patterns.md) (6 macros).

## What is Pixeltable?

A database for multimodal AI applications: an app's tables, processing pipeline and API all live in it.

- **A transactional database.** Many users and processes read and write at once; each insert, update
  and delete is atomic; single-row operations are fast. Serve requests from the tables directly: no
  cache, no second datastore, no locks in app code.
- **Multimodal values are column types.** `Image`, `Video`, `Audio`, `Document` and `Array` columns take
  files and arrays directly, and Pixeltable stores and fetches the files. Do not store paths as strings
  or copy files yourself.
- **Computed columns are the pipeline.** A computed column is evaluated when its row arrives, within the
  same atomic operation, and stored. Model calls, parsing and scoring are columns, not workers, scripts or
  loops over rows. A failed cell keeps its error; `pxt recompute --errors-only` reruns only those cells.
- **Embedding indexes are declarative,** like a B-tree index: Pixeltable embeds new and changed rows and
  keeps one model per index. No vector database, no embedding job.
- **Iterator views** split each row into chunks, frames, segments or pages, and stay current as the base
  table changes. No child table filled by code.

Unlike a relational database, it has no foreign keys, CHECK constraints or multi-statement transactions,
and no computed column writes to another table. A computed column is recomputed only when its row's inputs
change, not when other rows or the clock change. [conventional-design.md](references/conventional-design.md)
has the pattern for each of these.

## Before you write app.py

1. **Translate the spec.** Workers, job queues, status columns, retries, metrics tables and cron jobs
   each have a Pixeltable equivalent: [conventional-design.md](references/conventional-design.md). Do
   not build them literally. An aggregate per base row over a view, such as each video's mean frame
   score, goes in a second table keyed like the base, with a `@pxt.query` column: the aggregate-table
   pattern there.
2. **Design the schema.** Entities, primary keys, types, nullability, and what is stored, computed or
   queried: [schema-design.md](references/schema-design.md). Keys, types and nullability are hard to
   change once a table has rows.
3. **Write derived values as expressions.** A UDF is for one step that has no expression form:
   [expressions.md](references/expressions.md). Before writing one, run `pxt functions --search <task>`
   and `pxt functions --on <Type>` to find what ships. Python's own operations do not work on a column:
   no f-strings, `str()`, `is None`, `and`, `or` or `not`.
4. **Treat the catalog as the user's data.** Show the plan and ask before you drop, revert, pass
   `--allow-destructive`, or add or recompute a paid model column on existing rows. Iterate in a
   scratch catalog directory: [safe-changes.md](references/safe-changes.md).

## Starting a new project

One application file (`app.py`) is the backend.

```bash
pip install 'pixeltable[serve]'   # Python 3.11+
pxt init
pxt service example --out app.py
pxt schema check app.py
pxt schema update app.py my_app
pxt service update app.py my_app -f   # -f: an agent has no TTY to answer the prompt
pxt service list                      # the URL of each service
```

- `pxt schema update` creates and changes the tables declared in `app.py`. It does not start HTTP.
- `pxt service update` starts the HTTP services. Run it again after each schema change.
- The last argument (`my_app`) is a directory in the catalog, not a folder on disk.
- Try the pipeline before the routes: insert a sample row and select it, or open `pxt dashboard`.
  Computed columns run on insert.
- `pxt schema example --brief --out app.py` writes the models without routes.
- Do not run `python app.py`; the `pxt` commands load it.

The same file deploys to Pixeltable Cloud, with `pxt://org:db` as the last argument: `pxt guide cloud`.
Flags, prompts, provider keys and the daemon: `pxt guide cli`, `pxt guide providers` and `pxt COMMAND --help`.

First run: [Quickstart](https://docs.pixeltable.com/overview/quick-start). Why: [Why Pixeltable](https://docs.pixeltable.com/overview/pixeltable).

## The application file

`pxt service example --out app.py` writes this shape. Edit it, then run `pxt schema update app.py my_app`.

```python
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()


@pxt.udf
def excerpt(text: str, n: int = 12) -> str:
    return text if len(text) <= n else f'{text[:n]}...'


class Docs(TableModel, name='docs'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    title: pxt.String
    body: pxt.String | None
    title_upper = pxtf.string.upper(title)
    summary = excerpt(title)


ingest = FastAPIRouter(name='ingest')
ingest.add_insert_route(
    Docs, path='/docs', inputs=[Docs.title, Docs.body],
    outputs=[Docs.id, Docs.title_upper, Docs.summary],
)
```

An annotation is a stored column, an assignment a computed column, and `T | None` a nullable column.
Indexes go in `__indexes__` on the model. Add video, audio, agents or a UI by editing `app.py`, and
change the catalog only with `pxt schema update`: `app.py` creates no tables when imported. Do not add
Hugging Face or spaCy unless the user asked.

## Apps vs notebooks

- **Apps:** `app.py` + `pxt schema update` + `pxt service update`. Indexes on the model.
- **Notebooks / REPL:** `pxt.create_table()`, `add_computed_column()`, `add_embedding_index()`.
  `pxt guide tables` shows both forms.

## Where to look

Read the guide of an area before writing code in it. The guides ship with the installed Pixeltable and
state how that release behaves: what its APIs do, their defaults, errors and known issues. Where this
skill and a guide disagree, the guide is right.

| Need | Open |
|------|------|
| Turn a spec's workers, queues and status columns into tables and columns | [conventional-design.md](references/conventional-design.md) |
| Keys, types, nullability, references, history | [schema-design.md](references/schema-design.md) |
| Expressions, and when to write a UDF | [expressions.md](references/expressions.md) |
| Drops, recomputes, schema changes on a project with data | [safe-changes.md](references/safe-changes.md) |
| Wrong stack | [anti-patterns.md](references/anti-patterns.md) |
| How this release behaves in one area | `pxt guide` lists the areas; `pxt guide tables` prints one |
| What a function or a command takes | `pxt functions --search <text>`, `pxt functions --on <Type>`, `pxt COMMAND --help` |

The areas: tables, expressions, queries, views, indexes, udfs, json, providers, serving, cli, cloud.
`pxt skills install` also copies the guides into `guides/` next to this file.

## Resources

- [Quickstart](https://docs.pixeltable.com/overview/quick-start)
- [CLI](https://docs.pixeltable.com/platform/cli)
- [Developer MCP](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- [Cloud MCP](https://pixeltable.com/developers/mcp-cloud) (optional; reads and operates Cloud)
- [Docs](https://docs.pixeltable.com/llms-full.txt)
