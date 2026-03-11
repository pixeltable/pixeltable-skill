---
name: pixeltable-skill
description: >
  Core foundation for building AI applications with Pixeltable. Always active
  when working in a Pixeltable project. Use when the user asks how to use
  Pixeltable, creates tables, inserts data, adds computed columns, writes UDFs,
  or integrates with AI providers. Also triggers for "how do I use Pixeltable,"
  general Pixeltable questions, debugging Pixeltable errors, or reviewing existing
  Pixeltable code. Specialized skills (pixeltable-rag, pixeltable-media,
  pixeltable-agents, pixeltable-app) extend this foundation — this skill is
  always the base layer.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.0.0
  category: data-infrastructure
  tags: [multimodal, ai, data, tables, computed-columns, udf, embeddings, agents, fastapi]
  documentation: https://docs.pixeltable.com/
  support: https://github.com/pixeltable/pixeltable/discussions
---

## Mental Model

### What Pixeltable actually is

Pixeltable is a **persistent, versioned database** for AI workflows — not a Python framework, not an in-memory dataframe library, not a pipeline orchestrator. Data persists between sessions. Tables outlive scripts. All interaction happens through the Python API (`pxt.*`). No raw SQL.

The key shift: **don't think "run this script to process files." Think "insert rows; the table handles the rest."**

### Schemas are easy to change

No need for a perfect schema upfront. Add/drop/rename columns, add computed columns (auto-backfill on existing rows), add embedding indexes, create views — all after the fact. Start simple and extend.

### The type system

Media is a first-class citizen. Types are always capitalized.

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
- Never use `pxt.String` for media paths — the typed column (`pxt.Image`, etc.) unlocks built-in functions, indexing, and similarity search.
- Never use pandas dtypes or NumPy type annotations — always `pxt.*` types.
- To get a path back out: `.localpath` or `.fileurl` properties.

### Tables, views, and computed columns

**Tables** hold your raw data with typed columns. They can also have computed columns directly — they're not just for raw data.

**Views** are derived from a table in three ways:
- With an **iterator** — splits rows into sub-rows (document chunks, video frames, audio segments)
- As a **filtered subset** — `pxt.create_view('dir.active', t.where(t.is_active == True))`
- As a **sample** — for testing on a subset

**Computed columns** can go on any table or view. They run automatically on insert and cascade: when you insert into a parent table, all views and their computed columns update automatically.

### Everything flows through the table

This is a hard boundary, not a suggestion. Don't bypass Pixeltable to call AI SDKs directly, and don't call `@pxt.udf` functions as regular Python functions. If you defined a UDF or a computed column, it runs through the table. The table is your pipeline runner, your result store, and your audit log.

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

---

## How to Use This Skill

### When the user is new to Pixeltable

No existing `import pixeltable` in the project, or they ask "get started," "try Pixeltable," or "what is Pixeltable" — generate a single runnable script immediately. Include `# pip install pixeltable` at the top. Tailor to what they mentioned; default to a simple example if unclear. Let the working code speak — explain concepts as inline comments, not as a lecture before the code.

### When generating a project scaffold

Guide the user toward the right Pixeltable patterns by understanding their use case. Work through this conversationally — don't dump all four questions at once.

1. **Data** — Identify the type (documents, images, video, audio, text) and where it lives. If it's remote (S3, HTTP), they don't need to download it — Pixeltable references and caches lazily.
2. **Processing** — Match their needs to built-in functions before suggesting custom UDFs. Pixeltable includes all PIL/Pillow image operations, document splitters, frame extractors, audio splitters, string operations, and more. Use iterators to break data into sub-rows (chunks, frames, segments).
3. **AI models** — Not just generation — also embeddings, transcription, object detection, classification. All available as built-in integrations via computed columns. Cloud providers need API keys (env vars, config file, or `getpass`); local models (Ollama, Whisper, Hugging Face) don't.
4. **Search** — No separate vector database needed. An embedding model + `add_embedding_index` + `.similarity()` gives them semantic search directly on their table.

Generate working, runnable code as soon as you have enough context. Don't show templates — write real files.

### When you see Pixeltable code (always scan automatically)

Whenever the user shares or points to Pixeltable code for any reason — asking for help, asking to modify, pasting a snippet — silently scan for these anti-patterns. If found, flag concisely at the end of your response. Don't lecture.

| Anti-pattern | What to look for | Fix |
|---|---|---|
| SDK call outside computed column | `openai.OpenAI()`, `anthropic.Anthropic()`, `requests.get(...)` in app/endpoint code | Move to `add_computed_column` using `pxtf.<provider>.*` |
| String path for media | `'path': pxt.String` where the column holds images/video/audio/docs | Use `pxt.Image`, `pxt.Video`, `pxt.Audio`, `pxt.Document` |
| Wrong `if_exists` behavior | Unexpected errors on re-run, or silently overwriting existing data | `'error'` (default), `'ignore'` (idempotent setup scripts), `'replace'` (iteration — change your pipeline and re-run, just like rerunning a notebook cell) |
| Async FastAPI endpoint | `async def` endpoint calling Pixeltable | Change to `def` — Pixeltable is synchronous; Uvicorn handles threading |
| Single-row anti-pattern | One table created for one prompt/one query | Reframe as a collection; Pixeltable's value is batch + persistence |
| Custom UDF for built-in | Hand-written UDF that duplicates a built-in (image resize, text splitting, transcription, etc.) | Replace with `pxtf.*` built-in — check `pxtf.image.*`, `pxtf.video.*`, `pxtf.audio.*`, `pxtf.document.*` first |
| Defensive wrappers | try/except blocks, manual retries, subprocess isolation around Pixeltable calls | Remove — Pixeltable handles errors internally. Use `on_error='ignore'` + `recompute_columns` instead |
| Calling a UDF outside the table | Defining `@pxt.udf` then calling it as a regular Python function in app code | Everything flows through the table — UDFs run as computed columns, not standalone functions |

### When debugging a Pixeltable error

Follow this diagnosis tree:

**Computed column errors** → use `on_error='ignore'` on the column, inspect, then retry:
```python
# Add column with graceful error handling
t.add_computed_column(analysis=my_fn(t.doc), on_error='ignore', if_exists='ignore')

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

**Similarity search raises an error** → `add_embedding_index` was never called on that column — `.similarity()` requires an index.

**Similarity search returns fewer results than expected** → `.similarity()` returns a score expression — the number of results you get back is determined by the query operators you chain onto it (`.where()`, `.limit()`, `.order_by()`). Start by running the query without any filters to see all rows and their raw scores, then add filters from there.

**Type errors** → call `t.describe()` to see the actual schema.

**`@pxt.query` function not found** → it's not stored in Pixeltable. It must be redefined in every Python process that uses it — both in setup and in the app.

---

## Pixeltable Patterns

### Setup

```python
# pip install pixeltable
import pixeltable as pxt
import pixeltable.functions as pxtf

pxt.create_dir('my_project', if_exists='ignore')
```

Always use `pxtf.*` for built-in functions (e.g. `pxtf.openai.chat_completions`, `pxtf.image.thumbnail`, `pxtf.document.document_splitter`). Avoid explicit imports like `from pixeltable.functions.openai import chat_completions` — the `pxtf` namespace makes the modality clear and keeps imports clean.

### API keys

Pixeltable auto-discovers credentials. Three options: environment variables (`export OPENAI_API_KEY=sk-...`), config file (`~/.pixeltable/config.toml`), or `getpass` for interactive sessions. No code changes needed — just set the key and Pixeltable finds it.

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
}, if_exists='ignore')

# With primary key
t = pxt.create_table('my_project.items', {
    'content': pxt.String,
    'uuid': pxtf.uuid.uuid7(),
    'created_at': pxt.Timestamp,
}, primary_key=['uuid'], if_exists='ignore')

# From CSV/Parquet — auto-infer schema, override media columns
t = pxt.create_table('my_project.data', source='data.csv',
    schema_overrides={'image_path': pxt.Image, 'audio_path': pxt.Audio})
```

Inspect any table's schema with `t.describe()` — shows columns, types, computed column definitions, and iterator sources.

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

### Computed columns

Run automatically on every new row. Can chain — each column can reference previously defined computed columns. **Cascading is automatic:** when a computed column updates, any downstream columns that depend on it update too.

```python
t.add_computed_column(
    summary=pxtf.openai.chat_completions(
        messages=[{'role': 'user', 'content': t.content}],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore'
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

**What to reach for, in order** — this matters. Skipping to UDFs means writing custom code for things Pixeltable already does:

1. **Built-in functions** — `pxtf.image.*`, `pxtf.video.*`, `pxtf.audio.*`, `pxtf.document.*`, etc.
2. **AI integrations** — `pxtf.openai.*`, `pxtf.anthropic.*`, `pxtf.huggingface.*`, etc.
3. **Custom `@pxt.udf`** — only for logic that doesn't exist in the built-ins

```python
# Wrong: custom UDF for something built-in
@pxt.udf
def make_thumbnail(img: PIL.Image.Image) -> PIL.Image.Image:
    return img.resize((320, 320))

# Right: use the built-in
t.add_computed_column(thumb=pxtf.image.thumbnail(t.image, size=(320, 320)))

# Right: custom UDF for genuinely custom logic
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()
t.add_computed_column(cleaned=clean_text(t.content), if_exists='ignore')
```

### AI providers

Pixeltable integrates 15+ AI providers — foundation model providers (OpenAI, Anthropic, Gemini, Mistral), inference platforms (Together, Fireworks, Groq, Replicate, OpenRouter, fal.ai, Bedrock), Hugging Face, and Ollama for local inference. All follow the same pattern: `pxtf.<provider>.*` through computed columns. Providers with remote APIs need API keys; local inference (Ollama, some Hugging Face models) doesn't. See [docs.pixeltable.com](https://docs.pixeltable.com/) for the full list of providers and their available functions.

### Querying

Queries are lazy — `.select()`, `.where()`, `.order_by()`, `.limit()` build an expression. Call `.collect()` to materialize results. Shortcuts: `t.head(n)` and `t.tail(n)` collect immediately.

```python
results = t.select(t.title, t.score).collect()
results = t.where(t.score > 0.8).select(t.title).collect()
results = t.order_by(t.score, asc=False).limit(10).collect()
t.head(5)                      # quick peek — shortcut for select + limit + collect
df = t.collect().to_pandas()

# For FastAPI responses
items = list(t.select(title=t.title, score=t.score).collect().to_pydantic(MyModel))
```

### Query functions

`@pxt.query` turns a function into a reusable, parameterized query — commonly used for similarity search and as agent tools. **It is not stored in Pixeltable.** Redefine it in every Python process that uses it (both `setup_pixeltable.py` and `main.py`).

```python
@pxt.query
def retrieve(question: str, top_k: int = 5):
    sim = chunks.text.similarity(question)
    return chunks.order_by(sim, asc=False).limit(top_k).select(chunks.text, sim)

# Use directly
results = retrieve('What is RAG?').collect()

# Or pass to pxt.tools() for agent use
tools = pxt.tools(retrieve)
```
