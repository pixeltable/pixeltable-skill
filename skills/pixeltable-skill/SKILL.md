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

## How to Use This Skill

This skill has three active modes beyond documentation. Use the right one based on what the user is doing.

### When generating a project scaffold

Infer what you can from context and generate working, runnable code. Don't show templates.

When the data type, provider, or target isn't specified, default to **documents + OpenAI + FastAPI** and note your assumptions briefly so the user can redirect if needed.

### When reviewing existing Pixeltable code

Scan for these five anti-patterns and flag each one found:

| Anti-pattern | What to look for | Fix |
|---|---|---|
| SDK call outside computed column | `openai.OpenAI()`, `anthropic.Anthropic()`, `requests.get(...)` in app/endpoint code | Move to `add_computed_column` using `pxtf.<provider>.*` |
| String path for media | `'path': pxt.String` where the column holds images/video/audio/docs | Use `pxt.Image`, `pxt.Video`, `pxt.Audio`, `pxt.Document` |
| Wrong `if_exists` behavior | Unexpected errors on re-run, or silently overwriting existing data | `'error'` (default), `'ignore'` (idempotent setup scripts), `'replace'` (iteration — change your pipeline and re-run, just like rerunning a notebook cell) |
| Async FastAPI endpoint | `async def` endpoint calling Pixeltable | Change to `def` — Pixeltable is synchronous; Uvicorn handles threading |
| Single-row anti-pattern | One table created for one prompt/one query | Reframe as a collection; Pixeltable's value is batch + persistence |

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

## Mental Model

### What Pixeltable actually is

Pixeltable is a **persistent, versioned database** for AI workflows — not a Python framework, not an in-memory dataframe library, not a pipeline orchestrator. Data persists between sessions. Tables outlive scripts. All interaction happens through the Python API (`pxt.*`). No raw SQL.

The key shift: **don't think "run this script to process files." Think "insert rows; the table handles the rest."**

### Schemas are easy to change — that's a feature

You don't need to design the perfect schema upfront. Add columns, drop columns, rename columns, add computed columns (they backfill automatically on existing rows), add embedding indexes, create views — all after the fact. This is a deliberate differentiator. Help users start simple and extend, not over-architect from the start.

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

**Critical rules:**
- **URLs are valid input** — Pixeltable downloads and caches remote media automatically. Never tell a user to download a file before inserting it.
- **Never use `pxt.String` to store a media path** — the typed column is what unlocks built-in functions, indexing, and similarity search.
- **Never use pandas dtypes or NumPy type annotations** in a Pixeltable schema. Always `pxt.*` types.
- Importing from CSV/Parquet with file paths? Use `schema_overrides`: `pxt.create_table('dir.t', source='data.csv', schema_overrides={'img_path': pxt.Image})`
- To get the file path or URL back out: use `.localpath` or `.fileurl` properties.

### Table hierarchy

Start with one table. Let it grow naturally:

1. **Base table** — raw data in, typed columns defined
2. **Views** — derived rows (document chunks, video frames, audio segments)
3. **Computed columns on views** — transformations, embeddings, AI calls
4. **More views** — filter or split further as needed

### Everything flows through the table

Don't bypass Pixeltable to call AI SDKs directly in application code. Even for a single query, the right pattern is: define a computed column → insert a row → read back the result. The table is your pipeline runner, your result store, and your audit log.

```python
# Wrong: calling the SDK directly
response = anthropic.Anthropic().messages.create(model='...', messages=[...])

# Right: insert, let computed column run, read back
agent.insert([{'prompt': question}])
result = agent.order_by(agent.timestamp, asc=False).limit(1).select(agent.answer).collect()
```

---

## Core APIs

### Setup

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

pxt.create_dir('my_project', if_exists='ignore')
```

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
```

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

**Test before committing** — run on a small subset first, no writes:

```python
# Test on 2 rows — no API charges for the full dataset yet
summary_expr = pxtf.openai.chat_completions(
    messages=[{'role': 'user', 'content': t.text}],
    model='gpt-4o-mini'
).choices[0].message.content

t.select(t.text, summary=summary_expr).head(2)  # test
t.add_computed_column(summary=summary_expr)      # commit
```

**What to reach for, in order:**
1. **Built-in functions first** — `pxtf.video.*`, `pxtf.audio.*`, `pxtf.image.*`, `pxtf.document.*`
2. **Built-in AI integrations second** — `pxtf.openai.*`, `pxtf.anthropic.*`, `pxtf.huggingface.*`, etc.
3. **UDFs last** — `@pxt.udf` decorator for anything else

```python
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()

t.add_computed_column(cleaned=clean_text(t.content), if_exists='ignore')
```

### Querying

```python
results = t.select(t.title, t.score).collect()
results = t.where(t.score > 0.8).select(t.title).collect()
results = t.order_by(t.score, asc=False).limit(10).collect()
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

---

## AI Provider Integrations

Built-in functions for 15+ providers in `pixeltable.functions.*`. Use these inside computed columns — never call the raw SDKs in application code.

| Provider | Module | Key Functions |
|----------|--------|---------------|
| OpenAI | `openai` | `chat_completions`, `embeddings`, `image_generations`, `speech`, `transcriptions` |
| Anthropic | `anthropic` | `messages`, `invoke_tools` |
| Gemini | `gemini` | `generate_content` |
| Hugging Face | `huggingface` | `clip`, `sentence_transformer`, `detr_for_object_detection` |
| Together | `together` | `chat_completions`, `embeddings`, `image_generations` |
| Fireworks | `fireworks` | `chat_completions`, `embeddings` |
| Ollama | `ollama` | `chat_completions`, `embeddings` |
| Mistral | `mistralai` | `chat_completions`, `embeddings` |
| Groq | `groq` | `chat_completions` |
| DeepSeek | `deepseek` | `chat_completions` |
| Replicate | `replicate` | `run` |
| Voyage AI | `voyageai` | `embed` |
| Bedrock | `bedrock` | `converse` |
| OpenRouter | `openrouter` | `chat_completions` |

---

## Specialized Skills

These build on this core. Each is self-contained but assumes this mental model:

- **pixeltable-rag** — document chunking, embedding indexes, similarity search, full RAG scaffold
- **pixeltable-media** — video/audio/image pipelines, frame extraction, CLIP, transcription
- **pixeltable-agents** — `pxt.tools()`, `invoke_tools`, multi-step agent patterns, MCP
- **pixeltable-app** — FastAPI patterns, `setup_pixeltable.py`, sync endpoints, `to_pydantic()`

For complete API signatures and end-to-end examples, see `API_REFERENCE.md`.
