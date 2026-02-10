---
name: pixeltable-skill
description: >
  Expert assistant for building multimodal AI applications with Pixeltable.
  Use when the user asks to create tables, insert data, add computed columns,
  build views, set up embedding indexes, perform similarity search, write UDFs,
  import/export data (CSV, Parquet, Hugging Face), process images, video, audio,
  or documents, or integrate with AI providers like OpenAI, Anthropic, Gemini,
  Hugging Face, Together, Fireworks, Ollama, and more. Also use when the user
  asks "how do I use Pixeltable" or wants to build a RAG pipeline, multimodal
  search, or data processing workflow. Do NOT use for general Python questions
  unrelated to Pixeltable or for database administration of PostgreSQL directly.
license: MIT
metadata:
  author: Pixeltable
  version: 1.0.0
  category: data-infrastructure
  tags: [multimodal, ai, data, tables, embeddings, rag, udf, video, audio, images, documents]
  documentation: https://docs.pixeltable.com/
  support: https://github.com/pixeltable/pixeltable/discussions
---

## What is Pixeltable?

Pixeltable is an open-source Python library providing **declarative data infrastructure** for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration of data across images, video, audio, and documents in a single table-based interface.

**Install:** `pip install pixeltable`

**Docs:** https://docs.pixeltable.com/ | **GitHub:** https://github.com/pixeltable/pixeltable

## Core Concepts

### Tables and Column Types

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
    'metadata': pxt.Json,
    'score': pxt.Float,
    'count': pxt.Int,
    'is_active': pxt.Bool,
    'created_at': pxt.Timestamp,
}, if_exists='ignore')
```

Available types: `String`, `Int`, `Float`, `Bool`, `Image`, `Video`, `Audio`, `Document`, `Json`, `Array`, `Timestamp`, `Date`, `UUID`, `Binary`. Use `pxt.Required[pxt.String]` for non-nullable.

### Inserting Data

```python
# Multiple rows
t.insert([
    {'title': 'Doc 1', 'content': 'Hello world', 'score': 0.95},
    {'title': 'Doc 2', 'content': 'Goodbye world', 'score': 0.85},
])

# Single row (keyword syntax)
t.insert(title='Doc 3', content='Another doc', score=0.75)

# From file
t.insert(source='path/to/data.csv')
```

### Computed Columns

Transformations that run automatically on new/updated data. The heart of Pixeltable's declarative approach.

```python
from pixeltable.functions.openai import chat_completions

t.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': t.content}],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore'
)

t.add_computed_column(upper_title=t.title.upper(), if_exists='ignore')
```

### Querying

```python
results = t.select(t.title, t.score).collect()
results = t.where(t.score > 0.8).select(t.title, t.content).collect()
results = t.order_by(t.score, asc=False).limit(10).select(t.title).collect()
count = t.count()
df = t.select(t.title, t.score).collect().to_pandas()
```

### Views and Iterators

Views split rows into multiple sub-rows. Essential for document chunking and video frame extraction.

```python
from pixeltable.functions.document import document_splitter
from pixeltable.functions.video import frame_iterator

# Chunk documents into 300-token pieces
chunks = pxt.create_view(
    'my_project.doc_chunks', t,
    iterator=document_splitter(t.doc, separators='token_limit', limit=300),
    if_exists='ignore'
)

# Extract video frames at 1 fps
frames = pxt.create_view(
    'my_project.video_frames', t,
    iterator=frame_iterator(t.video, fps=1.0),
    if_exists='ignore'
)
```

### Embedding Indexes and Similarity Search

```python
from pixeltable.functions.huggingface import clip

embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('content', embedding=embed_fn, if_exists='ignore')

# Search
sim = t.content.similarity(string='search query')
results = t.order_by(sim, asc=False).limit(5).select(t.title, t.content, sim).collect()

# Image search with text (multimodal CLIP)
sim = t.image.similarity(string='a photo of a cat')
results = t.order_by(sim, asc=False).limit(5).select(t.image, sim).collect()
```

### User-Defined Functions (UDFs)

```python
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()

@pxt.udf
def safe_length(text: Optional[str]) -> int:
    return 0 if text is None else len(text)

t.add_computed_column(cleaned=clean_text(t.content))
```

### Query Functions

```python
@pxt.query
def search_documents(query_text: str, limit: int = 10):
    sim = t.content.similarity(string=query_text)
    return t.order_by(sim, asc=False).limit(limit).select(t.title, t.content, sim)

results = search_documents('machine learning').collect()
```

## AI Provider Integrations

Built-in functions for 15+ providers in `pixeltable.functions.*`:

| Provider | Module | Key Functions |
|----------|--------|---------------|
| OpenAI | `openai` | `chat_completions`, `embeddings`, `image_generations`, `speech`, `transcriptions`, `vision` |
| Anthropic | `anthropic` | `messages` |
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
| Twelve Labs | `twelvelabs` | video understanding |

## Import/Export

```python
# From CSV / Parquet
t = pxt.create_table('dir.from_csv', source='data.csv')
t = pxt.create_table('dir.from_parquet', source='data.parquet')

# From Hugging Face
from pixeltable.io import import_huggingface_dataset
import datasets
ds = datasets.load_dataset('squad', split='train[:1000]')
t = import_huggingface_dataset('dir.squad', ds)

# From pandas
from pixeltable.io import import_pandas
t = import_pandas('dir.from_df', df)

# Export
from pixeltable.io import export_parquet
export_parquet(t, 'output/')
```

## Idempotent Operations

CRITICAL: Always use idempotent flags to prevent errors on re-runs:

```python
pxt.create_dir('my_dir', if_exists='ignore')
pxt.create_table('my_dir.table', schema, if_exists='ignore')
t.add_computed_column(col=expr, if_exists='ignore')
t.add_embedding_index('col', embedding=fn, if_exists='ignore')
```

## Error Handling

```python
status = t.insert(rows, on_error='ignore')
print(f'Inserted: {status.num_rows}, Errors: {status.num_excs}')
error_rows = t.where(t.summary.errortype != None).select(t.title, t.summary.errormsg).collect()
```

## Table Management

```python
pxt.list_tables()
t = pxt.get_table('my_project.my_table')
pxt.drop_table('my_project.my_table')
pxt.drop_dir('my_project', force=True)
t.describe()
t.columns()
```

## Additional Reference

For complete API signatures, all provider examples, and end-to-end workflow templates (RAG, video analysis, image classification, audio transcription, multi-provider comparison), see `API_REFERENCE.md` in this skill directory. Claude will load it automatically when needed.
