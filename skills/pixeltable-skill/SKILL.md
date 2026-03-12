---
name: pixeltable-skill
description: >
  Build persistent multimodal AI pipelines — images, video, audio, documents —
  with automatic computed columns, built-in vector search, and 15+ AI provider
  integrations (OpenAI, Anthropic, Gemini, Hugging Face, Ollama, and more). No
  separate vector database, no ETL, no glue code. Data lives in S3, HTTP, or
  local paths and Pixeltable handles the rest. Use when building Pixeltable
  projects, creating tables or schemas, adding computed columns, integrating AI
  providers, debugging Pixeltable errors, or reviewing Pixeltable code for
  anti-patterns.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.0.0
  category: data-infrastructure
  tags: [multimodal, ai, data, tables, computed-columns, udf, embeddings, vector-search, rag, image-processing, video-processing, audio-processing, document-pipeline, ai-pipeline]
  documentation: https://docs.pixeltable.com/
  support: https://github.com/pixeltable/pixeltable/discussions
---

## Mental Model

### What Pixeltable actually is

Pixeltable is a **persistent, versioned database** for AI workflows — a database where your AI pipeline is part of the schema. You create tables for your data, add columns that call AI models, and Pixeltable handles execution, caching, rate limits, retries, versioning, and search — so you write the logic, not the infrastructure. All interaction happens through the Python API (`pxt.*`). No raw SQL.

**Versioned** means every change to a table (inserts, updates, deletes, schema changes) is tracked, and every computed output is stored and retrievable. You can trace any output back to the inputs and model that produced it, compare results across prompt or model changes, and query any prior state of the table.

The key shift: **instead of writing a series of scripts that process your data and save results somewhere, you add columns to a table and the processing happens automatically — on every insert, for every future row.**

### Schemas are easy to change

No need for a perfect schema upfront. Add/drop/rename columns, add computed columns (auto-backfill on existing rows), add embedding indexes, create views — all after the fact. Start simple and extend.

### The type system

Media columns have dedicated types — don't use `pxt.String` for file paths that Pixeltable should process. Types are always capitalized.

| Type | Use for | Accepts |
|------|---------|---------|
| `pxt.Image` | Images | File paths, URLs |
| `pxt.Video` | Video files | File paths, URLs |
| `pxt.Audio` | Audio files | File paths, URLs |
| `pxt.Document` | PDFs, HTML, Markdown, DOCX | File paths, URLs |
| `pxt.Array` | Embeddings, tensors | NumPy arrays, e.g. `pxt.Array[(768,), pxt.Float]` |
| `pxt.Json` | Nested/arbitrary data | Dicts, lists — missing keys return `None`, not exceptions |
| `pxt.String`, `pxt.Int`, `pxt.Float`, `pxt.Bool` | Scalars | Python primitives |
| `pxt.Timestamp`, `pxt.Date`, `pxt.UUID` | Time, identifiers | Standard Python types |

### Data referencing — you don't move your data

Insert **references**, not files. Pixeltable downloads remote media automatically when it needs to process it — all media processing happens locally. Downloaded files and generated outputs (images, video, audio) are stored in `~/.pixeltable/media`; structured data lives in a managed Postgres instance at `~/.pixeltable`. You never need to move files around or manage the local copies — the data store is fully managed by Pixeltable.

Supported schemes: local paths, `file://`, `http://`, `https://`, `s3://` (AWS credentials), `gs://` (GCP credentials).

```python
t.insert([
    {'video': '/local/path/video.mp4'},                # local
    {'video': 'https://cdn.example.com/video.mp4'},    # HTTP
    {'video': 's3://my-bucket/videos/clip.mp4'},       # S3
])
```

**Rules:**
- If you want Pixeltable to manage, cache, and process media, use the dedicated types (`pxt.Image`, `pxt.Video`, `pxt.Audio`, `pxt.Document`) — these unlock built-in functions, indexing, and similarity search. Use `pxt.String` only when you need the path/URL as plain text metadata (e.g., for export). You can convert later with `col.astype(pxt.Image)`.
- Never use pandas dtypes or NumPy type annotations — always `pxt.*` types.
- To get a file path or URL back out of a media column: `.localpath` or `.fileurl` properties.

### Tables, views, and computed columns

**Tables** are where you insert data. Each column has a Pixeltable type.

**Views** are derived from a table in three ways:
- With an **iterator** — splits rows into sub-rows (document chunks, video frames, audio segments)
- As a **filtered subset** — `pxt.create_view('dir.active', t.where(t.is_active == True))`
- As a **sample** — `pxt.create_view('dir.sample', t.sample(n=100, seed=42))`

**Computed columns** can go on any table or view. You define them once — Pixeltable computes them on all existing rows immediately and on every future insert. There's no separate "run" step.

### Everything flows through the table

This is a hard boundary, not a suggestion. Don't bypass Pixeltable to call AI SDKs directly, and don't call `@pxt.udf` functions as regular Python functions. If you defined a UDF or a computed column, it runs through the table.

```python
# Wrong: calling the SDK directly
response = anthropic.Anthropic().messages.create(model='...', messages=[...])

# Wrong: calling a UDF as a regular function
@pxt.udf
def summarize(text: str) -> str: ...
result = summarize("some text")  # bypasses persistence, caching, error handling

# Right: define computed column, insert, read back
t.add_computed_column(summary=summarize(t.content))
t.insert([{'content': 'some text'}])
result = t.select(t.summary).collect()
```

### What the table handles for you

When processing runs through computed columns, Pixeltable automatically:
- **Only processes new rows on insert** — existing computed values are not reprocessed, so adding data to a table with expensive API columns doesn't re-run previous calls
- **Manages provider rate limits** — calls to OpenAI, Anthropic, etc. are throttled to stay within limits
- **Retries transient failures** — network errors, API timeouts, and rate-limit rejections are retried automatically

This is why "everything flows through the table" matters. Code that bypasses computed columns loses all three — and the user ends up writing retry loops, caching layers, and rate-limit handling that Pixeltable already provides.

---

## How to Use This Skill

### When the user is new to Pixeltable

No existing `import pixeltable` in the project, or they ask "get started," "try Pixeltable," or "what is Pixeltable" — generate a single runnable script immediately. Include `# pip install pixeltable` at the top. Tailor to what they mentioned; default to the image example below that demonstrates the core loop (create table → computed columns → insert → query) with zero API keys. Let the working code speak — explain concepts as inline comments, not as a lecture before the code.

**Default "get started" example** (use when the user's goal is unclear — no API key needed):
```python
# pip install pixeltable
import pixeltable as pxt
import pixeltable.functions as pxtf

pxt.create_dir('demo', if_exists='ignore')
t = pxt.create_table('demo.photos', {'image': pxt.Image})

# Computed columns run automatically — on insert and every future row
t.add_computed_column(thumb=pxtf.image.thumbnail(t.image, size=(320, 320)))
t.add_computed_column(rotated=t.image.rotate(90))

# URLs work directly — Pixeltable downloads and caches automatically
prefix = 'https://raw.githubusercontent.com/pixeltable/pixeltable/main/docs/resources/images'
t.insert([
    {'image': f'{prefix}/000000000030.jpg'},
    {'image': f'{prefix}/000000000034.jpg'},
    {'image': f'{prefix}/000000000042.jpg'},
])

# Everything is persisted — query anytime, even after restarting Python
t.select(t.image, t.thumb, t.rotated).collect()
```

If the user has an API key available, upgrade the example to include an AI computed column (e.g., image captioning with `pxtf.openai.chat_completions` + vision, or text summarization) — that's where Pixeltable's value really shows.

### When generating a project scaffold

Start by matching the user's goal to a Pixeltable pattern:

| User goal | Pattern |
|---|---|
| Document search / Q&A | Table → document_splitter view → embedding index → `.similarity()` |
| Image catalog / visual search | Table with `pxt.Image` → CLIP embedding index → `.similarity()` |
| Video understanding | Table → frame_iterator view → CLIP or vision LLM computed columns |
| Prompt/model comparison | Table with multiple provider computed columns (same input, different models) |
| Audio transcription + search | Table with `pxt.Audio` → transcription computed column → embedding index |
| Data labeling / classification | Table → AI computed column for labels → filtered views per category |
| RAG chatbot | Documents table → chunks view → embedding index → `@pxt.query` retrieval function |

Then refine by working through these conversationally — don't dump all four questions at once.

1. **Data** — Identify the type (documents, images, video, audio, text) and where it lives. If it's remote (S3, HTTP), they don't need to download it — Pixeltable downloads and caches remote media when it needs to process it (on insert or when a computed column accesses it).
2. **Processing** — Match their needs to built-in functions before suggesting custom UDFs. Pixeltable includes common PIL/Pillow image operations, document splitters, frame extractors, and audio splitters. Use iterators to break data into sub-rows (chunks, frames, segments).
3. **AI models** — Not just generation — also embeddings, transcription, object detection, classification. All available as built-in integrations via computed columns. Cloud providers need API keys (env vars, config file, or `getpass`); local models (Ollama, Hugging Face) don't.
4. **Search** — No separate vector database needed. An embedding model + `add_embedding_index` + `.similarity()` gives them semantic search directly on their table. The index updates incrementally when new rows are inserted — no re-indexing, no re-processing of existing data.

Generate working, runnable code as soon as you have enough context. Don't show templates — write real files.

### When you see Pixeltable code (always scan automatically)

Whenever the user shares or points to Pixeltable code for any reason — asking for help, asking to modify, pasting a snippet — silently scan for these anti-patterns. If found, flag concisely at the end of your response. Don't lecture.

| Anti-pattern | What to look for | Fix |
|---|---|---|
| SDK call outside computed column | `openai.OpenAI()`, `anthropic.Anthropic()`, `requests.get(...)` in app/endpoint code | Move to `add_computed_column` using `pxtf.<provider>.*` |
| String path for media | `'path': pxt.String` for columns that should be processed as media (not plain text metadata) | Use `pxt.Image`, `pxt.Video`, `pxt.Audio`, `pxt.Document` — these unlock built-in functions, indexing, and similarity |
| Wrong `if_exists` behavior | Unexpected errors on re-run, or silently overwriting existing data | `'error'` (default), `'ignore'` (idempotent setup scripts), `'replace'` (iteration — change your pipeline and re-run, just like rerunning a notebook cell) |
| Async FastAPI endpoint | `async def` endpoint calling Pixeltable | Change to `def` — Pixeltable is synchronous; Uvicorn handles threading |
| Single-row anti-pattern | One table created for one prompt/one query | Reframe as a collection; Pixeltable's value is batch + persistence |
| Custom UDF for built-in | Hand-written UDF that duplicates a built-in (image resize, text splitting, transcription, etc.) | Replace with `pxtf.*` built-in — check `pxtf.image.*`, `pxtf.video.*`, `pxtf.audio.*`, `pxtf.document.*` first |
| Defensive wrappers | try/except blocks, manual retries, rate-limit sleep loops, caching layers around Pixeltable calls | Remove — Pixeltable caches computed results, retries transient failures, and manages provider rate limits automatically. Use `on_error='ignore'` + `recompute_columns` for errors that need inspection |
| Calling a UDF outside the table | Defining `@pxt.udf` then calling it as a regular Python function in app code | Everything flows through the table — UDFs run as computed columns, not standalone functions |
| External tool for built-in capability | Adding Pinecone/Weaviate/ChromaDB for vector search, LangChain/LlamaIndex for chaining, or separate orchestrators | Pixeltable has built-in embedding indexes, similarity search, computed column chaining, and iterators — no external tools needed |
| Manual JSON parsing | `json.loads()`, manual key extraction, or post-processing scripts to parse AI API responses | Use Pixeltable JSON path expressions directly in computed columns and queries: `t.col['key']`, `t.col['*'].field`, `t.col[0].field`, `t.col[1:].field` |

### When debugging a Pixeltable error

Follow this diagnosis tree:

**Computed column errors** → use `on_error='ignore'` on the column, inspect, then retry:
```python
# Add (or replace) column with graceful error handling
t.add_computed_column(analysis=my_fn(t.doc), on_error='ignore', if_exists='replace')

# Find rows with errors
t.where(t.analysis.errortype != None).select(t.analysis.errortype, t.analysis.errormsg).collect()

# Retry only failed rows (cascade downstream by default)
t.recompute_columns(t.analysis, errors_only=True)

# Force recompute ALL rows (e.g. your function logic was wrong, not just transient failures)
t.recompute_columns(t.analysis)

# Recompute a specific subset of rows
t.recompute_columns(t.analysis, where=t.category == 'important')

# Recompute multiple columns at once (cascade=True is the default)
t.recompute_columns(t.analysis, t.summary)
```

**Insert failures** → use `on_error='ignore'` to get a status report:
```python
status = t.insert(rows, on_error='ignore')
print(f"Inserted: {status.num_rows}, Errors: {status.num_excs}")
```

**Type errors** → call `t.describe()` to see the actual schema.

---

## Pixeltable Patterns

### Setup

```python
# pip install pixeltable
import pixeltable as pxt
import pixeltable.functions as pxtf

pxt.create_dir('my_project', if_exists='ignore')
```

No server setup — `import pixeltable as pxt` handles everything (creates `~/.pixeltable`, starts an embedded Postgres instance).

Always use `pxtf.*` for built-in functions (e.g. `pxtf.openai.chat_completions`, `pxtf.image.thumbnail`, `pxtf.document.document_splitter`). Avoid explicit imports like `from pixeltable.functions.openai import chat_completions` — the `pxtf` namespace keeps function discovery easy and imports clean.

### API keys

Pixeltable auto-discovers credentials. Three options: environment variables (`export OPENAI_API_KEY=sk-...`), config file (`~/.pixeltable/config.toml`), or `getpass` for interactive sessions. No code changes needed — just set the key and Pixeltable finds it. The config file also handles provider/model rate limits and default destination buckets for both input and generated output media.

### `if_exists` options

`create_dir`, `create_table`, `add_computed_column`, and `add_embedding_index` all accept `if_exists=`:
- `'error'` (default) — fail explicitly if already exists
- `'ignore'` — skip silently; good for setup scripts you re-run
- `'replace'` — overwrite; **use this when iterating on a pipeline or changing upstream data**, the same way you'd just rerun a cell in a notebook

### Tables

```python
t = pxt.create_table('my_project.documents', {
    'title': pxt.String,
    'doc': pxt.Document,
})

# With primary key
t = pxt.create_table('my_project.items', {
    'content': pxt.String,
    'uuid': pxtf.uuid.uuid7(),
    'created_at': pxt.Timestamp,
}, primary_key=['uuid'])

# From CSV/Parquet — auto-infer schema, override media columns
t = pxt.create_table('my_project.data', source='data.csv',
    schema_overrides={'image_path': pxt.Image, 'audio_path': pxt.Audio})
```

Inspect any table's schema with `t.describe()` — shows columns, types, computed column definitions, and iterator sources.

### Views

Unlike computed columns (which add new values to existing rows), views create new row structures — splitting one row into many via an iterator, or filtering down to a subset. Iterators can only be used when creating a view.

**"I need to break data into smaller pieces"** → create a view with an **iterator**. Each piece becomes its own row that can have its own computed columns:
```python
chunks = pxt.create_view('project.chunks', docs,
    iterator=pxtf.document.document_splitter(docs.doc, separators='sentence', limit=300))

frames = pxt.create_view('project.frames', videos,
    iterator=pxtf.video.frame_iterator(videos.video, fps=1))
```

**"I need a subset of my data"** → filtered view:
```python
active = pxt.create_view('project.active', t.where(t.is_active == True))
```

**"I need a reproducible sample for testing"** → sample view:
```python
sample = pxt.create_view('project.sample', t.sample(n=100, seed=42))
```

Inserts to the parent table cascade through all views, their computed columns, and any embedding indexes automatically — new data is processed incrementally without re-indexing or re-processing existing rows.

### Inserting data

```python
t.insert([
    {'title': 'Doc 1', 'doc': 'path/to/file.pdf'},
    {'title': 'Doc 2', 'doc': 'https://example.com/report.pdf'},  # URL works directly
])
t.insert(title='Doc 3', doc='path/to/file.pdf')  # single row
t.insert(source='data.csv')  # from file
t.insert([MyModel(...)])  # from Pydantic
```

### Managing directories, tables, and columns

```python
# --- Directories ---
pxt.create_dir('my_dir/sub_dir')
pxt.list_dirs()                                      # list all directories
pxt.list_tables('my_dir')                            # list tables in a directory
pxt.move('old_dir', 'new_dir')                       # rename or relocate
pxt.drop_dir('my_dir/sub_dir')

# --- Tables ---
# Create: pxt.create_table(), pxt.create_view(), pxt.create_snapshot() — see above
tbl = pxt.get_table('my_dir.tbl')                    # get handle to existing table
tbl_v3 = pxt.get_table('my_dir.tbl:3')              # specific version (read-only)
tbl.count()                                          # row count
tbl.describe()                                       # schema, computed columns, dependencies
t.update({'score': 1.0}, where=t.category == 'important')
t.delete(where=t.is_active == False)
pxt.move('dir1.my_table', 'dir2.my_table')           # move between directories
pxt.drop_table('dir.my_table')                        # drop by catalog path
pxt.drop_table(t)                                     # drop by handle

# --- Columns ---
tbl.add_column(new_col=pxt.Int)                      # add a data column
tbl.add_computed_column(rotated=tbl.frame.rotate(90)) # add a computed column
tbl.add_embedding_index('img', embedding=embed_fn)   # add an embedding index
# Read: t.select(t.col), t.describe() — column reads are table-level operations
tbl.rename_column('old_name', 'new_name')
tbl.drop_column(tbl.col)
tbl.drop_embedding_index(column=tbl.img)
# Update column values: if_exists='replace' on add_computed_column,
#   recompute_columns, or insert new rows
```

### Computed columns

Defined once, computed automatically — on all existing rows (backfill) and every future insert. No invocation needed. Can chain — each column can reference previously defined computed columns. **Cascading is automatic:** on insert, all computed columns execute in dependency order. On `recompute_columns`, downstream dependent columns update too (`cascade=True` by default). Use `errors_only=True` to retry only failed rows, or `where=` to recompute a specific subset.

```python
t.add_computed_column(
    summary=pxtf.openai.chat_completions(
        messages=[{'role': 'user', 'content': t.content}],
        model='gpt-4o-mini'
    ).choices[0].message.content
)
```

**Workflow: test with `.head()`, then commit.** Test expressions on a few rows first, then commit once satisfied:

```python
expr = pxtf.openai.chat_completions(
    messages=[{'role': 'user', 'content': t.text}], model='gpt-4o-mini'
).choices[0].message.content

t.select(t.text, summary=expr).head(2)    # test on 2 rows
t.add_computed_column(summary=expr)        # commit to all rows
```

**"I need to process images / audio / documents"** → check built-in functions first. Pixeltable includes common PIL/Pillow image operations, document splitters, and audio splitters — check built-ins before writing your own:
```python
# Wrong: custom UDF for something built-in
@pxt.udf
def make_thumbnail(img: PIL.Image.Image) -> PIL.Image.Image:
    return img.resize((320, 320))

# Right: use the built-in
t.add_computed_column(thumb=pxtf.image.thumbnail(t.image, size=(320, 320)))
```

**"I need custom logic that doesn't exist as a built-in"** → write a `@pxt.udf` as a last resort:
```python
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()
t.add_computed_column(cleaned=clean_text(t.content))
```

### Embedding indexes and similarity search

No separate vector database. Add an embedding index to any text or image column, then query with `.similarity()`:

```python
# Add an embedding index
chunks.add_embedding_index(
    'text',
    embedding=pxtf.huggingface.sentence_transformer.using(model_id='all-MiniLM-L6-v2')
)

# Search
sim = chunks.text.similarity('how does authentication work?')
chunks.order_by(sim, asc=False).limit(5).select(chunks.text, sim).collect()
```

The index updates incrementally when new rows are inserted — no re-indexing needed.

### AI providers

Pixeltable integrates 15+ AI providers — foundation model providers (OpenAI, Anthropic, Gemini, Mistral), inference platforms (Together, Fireworks, Groq, Replicate, OpenRouter, fal.ai, Bedrock), Hugging Face, and Ollama for local inference. All follow the same pattern: `pxtf.<provider>.*` through computed columns. Providers with remote APIs need API keys; local inference (Ollama, some Hugging Face models) doesn't. See [docs.pixeltable.com](https://docs.pixeltable.com/) for the full list of providers and their available functions.

### Querying

Queries are lazy — `.select()`, `.where()`, `.order_by()`, `.limit()` build an expression. Call `.collect()` to materialize results. Shortcuts: `t.head(n)` and `t.tail(n)` collect immediately.

```python
results = t.select(t.title, t.score).collect()
results = t.where(t.score > 0.8).select(t.title).collect()
results = t.order_by(t.score, asc=False).limit(10).collect()
t.head(5)                      # quick peek — shortcut for select + limit + collect

# Sampling
t.sample(n=100).collect()                                  # random N rows
t.sample(fraction=0.1).collect()                           # random 10%
t.sample(fraction=0.1, stratify_by=t.category).collect()   # stratified
t.sample(n_per_stratum=2, stratify_by=t.category).collect() # N per group
```

### Version history

```python
t.describe()                                    # schema + computed column expressions + dependencies
t.history()                                     # all versions with timestamps and change types
prior = pxt.get_table('project.items:3')        # time-travel to version 3 (read-only)
tbl = pxt.get_table('project.items')
pxt.create_snapshot('project.before_retrain', tbl)      # named milestone
```

### Working with JSON responses

AI API responses are `pxt.Json` columns. Navigate them with path expressions directly in computed columns and queries — no `json.loads()` or manual parsing:

```python
# Access a key
t.select(t.response['choices'][0]['message']['content']).collect()

# Extract a field from every element in an array
t.select(t.scenes['*'].start_time).collect()

# Slice an array, then extract
t.select(t.scenes[1:].start_time).collect()

# Use in a computed column — parse once, use everywhere
t.add_computed_column(answer=t.response['choices'][0]['message']['content'])
```

### Exporting data

You can always get your data out of Pixeltable. Match the export method to what you need:

**"I need to analyze results in a notebook or pass data to another library"** → `.to_pandas()`
```python
df = t.where(t.score > 0.8).collect().to_pandas()
```

**"I'm building an API and need typed response objects"** → `.to_pydantic()`
```python
items = list(t.select(t.title, t.score).collect().to_pydantic(MyModel))
```

**"I need to share a dataset or feed it into an analytics pipeline"** → `export_parquet()`
```python
pxt.io.export_parquet(t, 'output.parquet')
pxt.io.export_parquet(t.where(t.label == 'cat'), 'cats.parquet')  # filtered
```

**"I need generated media (images, audio, etc.) to land in S3/GCS, not locally"** → `destination=` on computed columns
```python
t.add_computed_column(
    rotated=t.image.rotate(90),
    destination='s3://my-bucket/rotated/',  # or gs:// or local path
    if_exists='replace'
)
```


