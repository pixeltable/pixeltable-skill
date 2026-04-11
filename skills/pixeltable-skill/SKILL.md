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
  search, data processing workflow, or tool-calling agent. Do NOT use for
  general Python questions unrelated to Pixeltable or for database administration
  of PostgreSQL directly.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.0.0
  category: data-infrastructure
  tags: [multimodal, ai, data, tables, embeddings, rag, udf, video, audio, images, documents, agents, tools, fastapi]
  documentation: https://docs.pixeltable.com/
  support: https://github.com/pixeltable/pixeltable/discussions
---

## What is Pixeltable?

Pixeltable is an open-source Python library providing **declarative data infrastructure** for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration of data across images, video, audio, and documents in a single table-based interface.

**Install:** `pip install pixeltable` (requires Python >= 3.10)

**Docs:** https://docs.pixeltable.com/ | **GitHub:** https://github.com/pixeltable/pixeltable

## Task Router

Jump to the right section based on what you're building:

| If the user wants to... | Read |
|--------------------------|------|
| Create tables, insert data, query | **Core Concepts** (below) and [core-api.md](reference/core-api.md) |
| Add AI-powered columns (summarize, classify, embed) | **Computed Columns** (below) and [providers.md](reference/providers.md) |
| Chunk documents, extract video frames, split audio | **Views and Iterators** (below) and [core-api.md → Views](reference/core-api.md#views) |
| Build semantic search / embedding indexes | **Embedding Indexes** (below) and [core-api.md → Embedding Indexes](reference/core-api.md#embedding-indexes) |
| Build a RAG pipeline | [workflows.md → RAG Pipeline](reference/workflows.md#rag-pipeline) |
| Build a tool-calling agent | **Tool-Calling Agent Pipeline** (below) and [workflows.md → Tool-Calling Agent](reference/workflows.md#tool-calling-agent-full-production-example) |
| Build an agent with persistent memory | [agents-memory-mcp.md](reference/agents-memory-mcp.md) — chat history, knowledge bank, user scoping |
| Use MCP tools with an agent | [agents-memory-mcp.md → Adding MCP Tools](reference/agents-memory-mcp.md#adding-mcp-tools) |
| Use `invoke_tools()` with OpenAI, Groq, Gemini, Bedrock | [agents-memory-mcp.md → Multi-Provider](reference/agents-memory-mcp.md#multi-provider-invoke_tools) |
| Build a video RAG agent (video + search + agent) | [video-rag-agents.md](reference/video-rag-agents.md) — dedicated combined recipe |
| Process video (frames, transcription, visual search) | [workflows.md → Video Analysis Pipeline](reference/workflows.md#video-analysis-pipeline) |
| Process images (classify, tag, search) | [workflows.md → Image Classification and Search](reference/workflows.md#image-classification-and-search) |
| Process audio (transcribe, summarize) | [workflows.md → Audio Transcription](reference/workflows.md#audio-transcription-and-analysis) |
| Wrangle data for ML training (label, version, export) | [ml-data-pipeline.md](reference/ml-data-pipeline.md) — ingest, enrich, snapshot, PyTorch export |
| Export to PyTorch, Parquet, or pandas | [ml-data-pipeline.md → Export](reference/ml-data-pipeline.md#export-for-training) |
| Look up structured data with `retrieval_udf` | [ml-data-pipeline.md → Retrieval UDFs](reference/ml-data-pipeline.md#retrieval-udfs-for-structured-data-lookup) |
| Compare multiple AI providers | [workflows.md → Multi-Provider Comparison](reference/workflows.md#multi-provider-comparison) |
| Build a FastAPI web app | [workflows.md → FastAPI App Pattern](reference/workflows.md#fastapi-app-pattern) |
| Write UDFs or query functions | **UDFs** / **Query Functions** (below) and [core-api.md → UDFs](reference/core-api.md#udfs) |
| Use `pxt.tools()` and `invoke_tools()` for agents | **Tool-Calling Agent Pipeline** (below) and [core-api.md → Tools and Agents](reference/core-api.md#tools-and-agents) |
| Look up a specific provider's import and output shape | [providers.md → Quick Reference](reference/providers.md#quick-reference) |

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

### Tables with Auto-Generated Keys

Use `uuid7()` for auto-generated primary keys (recommended for production):

```python
from pixeltable.functions.uuid import uuid7

t = pxt.create_table('my_project.items', {
    'content': pxt.String,
    'uuid': uuid7(),           # auto-generated on insert
    'timestamp': pxt.Timestamp,
}, primary_key=['uuid'], if_exists='ignore')
```

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

# From a Pydantic model (great for FastAPI integration)
from pydantic import BaseModel
class ItemRow(BaseModel):
    title: str
    content: str
    score: float

t.insert([ItemRow(title='Doc 4', content='From Pydantic', score=0.9)])
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

# Convert results to Pydantic models (great for API responses)
from pydantic import BaseModel
class SearchResult(BaseModel):
    title: str
    score: float

items = list(
    t.select(title=t.title, score=t.score).collect().to_pydantic(SearchResult)
)
```

### Views and Iterators

Views split rows into multiple sub-rows. Essential for document chunking, video frame extraction, audio splitting, and text splitting.

```python
from pixeltable.functions.document import document_splitter
from pixeltable.functions.video import frame_iterator
from pixeltable.functions.string import string_splitter
from pixeltable.functions.audio import audio_splitter

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

# Split text into sentences
sentences = pxt.create_view(
    'my_project.sentences', t,
    iterator=string_splitter(t.content, separators='sentence'),
    if_exists='ignore'
)

# Split audio into 30-second chunks
audio_chunks = pxt.create_view(
    'my_project.audio_chunks', t,
    iterator=audio_splitter(audio=t.audio, duration=30.0),
    if_exists='ignore'
)

# Filtered view (no iterator needed)
active = pxt.create_view(
    'my_project.active', t.where(t.is_active == True),
    if_exists='ignore'
)
```

### Embedding Indexes and Similarity Search

```python
from pixeltable.functions.huggingface import clip, sentence_transformer

embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('content', embedding=embed_fn, if_exists='ignore')

# Search
sim = t.content.similarity(string='search query')
results = t.order_by(sim, asc=False).limit(5).select(t.title, t.content, sim).collect()

# Image search with text (multimodal CLIP)
sim = t.image.similarity(string='a photo of a cat')
results = t.order_by(sim, asc=False).limit(5).select(t.image, sim).collect()
```

### Built-in Image and Video Functions

```python
from pixeltable.functions import image as pxt_image
from pixeltable.functions.video import extract_audio

# Image thumbnails and encoding
t.add_computed_column(
    thumbnail=pxt_image.b64_encode(
        pxt_image.thumbnail(t.image, size=(320, 320))
    ),
    if_exists='ignore'
)

# Extract audio from video
t.add_computed_column(
    audio=extract_audio(t.video, format='mp3'),
    if_exists='ignore'
)
```

### User-Defined Functions (UDFs)

```python
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()

@pxt.udf
def safe_length(text: str | None) -> str:
    return 0 if text is None else len(text)

t.add_computed_column(cleaned=clean_text(t.content), if_exists='ignore')
```

### Query Functions

Reusable query functions that can also be used as agent tools:

```python
@pxt.query
def search_documents(query_text: str, limit: int = 10):
    sim = t.content.similarity(string=query_text)
    return t.order_by(sim, asc=False).limit(limit).select(t.title, t.content, sim)

results = search_documents('machine learning').collect()
```

## Tool-Calling Agent Pipeline

Pixeltable can orchestrate a full tool-calling agent as a chain of computed columns. Inserting a row triggers the entire pipeline automatically.

```python
import pixeltable as pxt
from pixeltable.functions.anthropic import messages, invoke_tools
from datetime import datetime

# 1. Define tools from UDFs and @pxt.query functions (defined earlier via @pxt.udf / @pxt.query)
tools = pxt.tools(
    web_search,            # @pxt.udf
    search_documents,      # @pxt.query
)

# Helper UDF to assemble context for the final LLM call
@pxt.udf
def assemble_context(question: str, tool_outputs: list | None, doc_context: list | None) -> str:
    tool_str = str(tool_outputs) if tool_outputs else 'N/A'
    doc_str = '\n'.join(
        f"- {item.get('text', '')}" for item in (doc_context or []) if isinstance(item, dict)
    ) or 'N/A'
    return f"QUESTION: {question}\n\n[TOOL RESULTS]\n{tool_str}\n\n[DOCUMENTS]\n{doc_str}"

# 2. Create the agent table
agent = pxt.create_table('my_project.agent', {
    'prompt': pxt.String,
    'timestamp': pxt.Timestamp,
    'system_prompt': pxt.String,
    'max_tokens': pxt.Int,
    'temperature': pxt.Float,
}, if_exists='ignore')

# 3. Initial LLM call with tools
agent.add_computed_column(
    initial_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': agent.prompt}]}],
        tools=tools,
        tool_choice=tools.choice(required=True),
        max_tokens=agent.max_tokens,
        model_kwargs={'system': agent.system_prompt, 'temperature': agent.temperature},
    ),
    if_exists='ignore',
)

# 4. Execute the tools the LLM chose
agent.add_computed_column(
    tool_output=invoke_tools(tools, agent.initial_response),
    if_exists='ignore',
)

# 5. RAG context retrieval
agent.add_computed_column(
    doc_context=search_documents(agent.prompt),
    if_exists='ignore',
)

# 6. Final LLM call with all context
agent.add_computed_column(
    context=assemble_context(agent.prompt, agent.tool_output, agent.doc_context),
    if_exists='ignore',
)

agent.add_computed_column(
    final_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': agent.context}]}],
        max_tokens=agent.max_tokens,
        model_kwargs={'system': agent.system_prompt, 'temperature': agent.temperature},
    ),
    if_exists='ignore',
)

# 7. Extract answer
agent.add_computed_column(
    answer=agent.final_response.content[0].text,
    if_exists='ignore',
)

# Usage: insert a row to trigger the full pipeline
agent.insert([{'prompt': 'What is quantum computing?', 'timestamp': datetime.now(),
               'system_prompt': 'You are a helpful assistant.', 'max_tokens': 1024}])
result = agent.where(agent.prompt == 'What is quantum computing?').select(agent.answer).collect()
```

## AI Provider Integrations

Built-in functions for 25+ providers in `pixeltable.functions.*`:

| Provider | Module | Key Functions |
|----------|--------|---------------|
| OpenAI | `openai` | `chat_completions` (supports multimodal/vision via messages), `embeddings`, `image_generations`, `speech`, `transcriptions` |
| Anthropic | `anthropic` | `messages`, `invoke_tools` |
| Gemini | `gemini` | `generate_content`, `invoke_tools` |
| Hugging Face | `huggingface` | `clip`, `sentence_transformer`, `detr_for_object_detection` |
| Together | `together` | `chat_completions`, `embeddings`, `image_generations` |
| Fireworks | `fireworks` | `chat_completions`, `embeddings` |
| Ollama | `ollama` | `chat_completions`, `embeddings` |
| Mistral | `mistralai` | `chat_completions`, `embeddings` |
| Groq | `groq` | `chat_completions`, `invoke_tools` |
| DeepSeek | `deepseek` | `chat_completions` |
| Replicate | `replicate` | `run` |
| Voyage AI | `voyageai` | `embed` |
| Bedrock | `bedrock` | `converse`, `invoke_tools` |
| OpenRouter | `openrouter` | `chat_completions` |
| Whisper | `whisper` | `transcribe` (local transcription) |
| WhisperX | `whisperx` | `transcribe` (local, with speaker diarization) |
| Twelve Labs | `twelvelabs` | `embed` (video understanding) |
| Jina AI | `jina` | `embeddings`, `rerank` |
| BFL FLUX | `bfl` | `generate`, `edit`, `expand`, `fill` (image generation/editing) |
| RunwayML | `runwayml` | `text_to_video`, `image_to_video`, `text_to_image`, `video_to_video` |
| fal.ai | `fal` | `run` (execute any fal.ai model) |
| Reve | `reve` | `create`, `edit`, `remix` (image generation) |
| Microsoft Fabric | `fabric` | `chat_completions`, `embeddings` (Azure OpenAI via Fabric) |
| llama.cpp | `llama_cpp` | `create_chat_completion` (local GGUF models) |
| YOLOX | `yolox` | `yolox` (object detection) |

## Import/Export

```python
# From CSV / Parquet
t = pxt.create_table('dir.from_csv', source='data.csv')
t = pxt.create_table('dir.from_parquet', source='data.parquet')

# With schema overrides (remap columns to media types)
t = pxt.create_table('dir.data', source='data.csv',
    schema_overrides={'image_col': pxt.Image, 'doc_col': pxt.Document})

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

# Snapshots (point-in-time copy)
snap = pxt.create_snapshot('my_project.snapshot_v1', t, if_exists='ignore')

# Update and delete
t.update({'score': 1.0}, where=t.category == 'important')
t.delete(where=t.is_active == False)
```

## Building Apps with Pixeltable

When building production applications (e.g., FastAPI + React), follow these patterns:

**Pixeltable IS the data layer** — no ORM, no SQLAlchemy. Pixeltable handles storage, indexing, transformation, and retrieval.

**Schema-as-code** — Define the entire data model in a single setup file. Run once to initialize.

**Sync endpoints** — FastAPI endpoints should use `def` (not `async def`). Pixeltable operations are synchronous; Uvicorn runs them in a thread pool automatically.

**Thin routers** — Business logic lives in `@pxt.udf` and `@pxt.query` functions, not in endpoint handlers. Routers just insert rows, collect results, and return responses.

**`to_pydantic()` for responses** — Convert Pixeltable query results directly to Pydantic models for type-safe API responses.

**Insert-triggers-pipeline** — For the agent pattern, inserting a row triggers the entire computed column chain. The endpoint just inserts and reads back the answer.

For a complete reference implementation, see the [Pixeltable App Template](https://github.com/pixeltable/pixeltable-app-template).

## Companion Resources

- **App Template** — [pixeltable/pixeltable-app-template](https://github.com/pixeltable/pixeltable-app-template): Full-stack FastAPI + React reference app with multimodal search, document/image/video pipelines, and a tool-calling agent.
- **MCP Server** — [pixeltable/mcp-server-pixeltable-developer](https://github.com/pixeltable/mcp-server-pixeltable-developer): Interactive exploration of Pixeltable tables, queries, and Python REPL via Model Context Protocol.
- **Core AGENTS.md** — [pixeltable/pixeltable/AGENTS.md](https://github.com/pixeltable/pixeltable/blob/main/AGENTS.md): Full SDK reference for contributing to Pixeltable itself.
- **LLM-Optimized Docs** — For deeper context beyond this skill, fetch these URLs directly:
  - [pixeltable.com/llms.txt](https://www.pixeltable.com/llms.txt) — Product overview and site map
  - [docs.pixeltable.com/llms.txt](https://docs.pixeltable.com/llms.txt) — Documentation index
  - [docs.pixeltable.com/llms-full.txt](https://docs.pixeltable.com/llms-full.txt) — Complete documentation (large)
  - Any docs page as markdown: append `.md` to any URL (e.g., `https://docs.pixeltable.com/overview/pixeltable.md`)

## Additional Reference

**Core API**: Tables, querying, views, embeddings, UDFs, tools, config → See [reference/core-api.md](reference/core-api.md)

**AI Providers**: OpenAI, Anthropic, Gemini, HuggingFace, Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, OpenRouter, Whisper, Voyage AI → See [reference/providers.md](reference/providers.md)

**Workflows**: RAG, video analysis, image classification, audio transcription, multi-provider comparison, tool-calling agents, FastAPI apps, export → See [reference/workflows.md](reference/workflows.md)

**Video RAG Agent**: Combined video processing + transcript/frame retrieval + tool-calling agent in one pipeline → See [reference/video-rag-agents.md](reference/video-rag-agents.md)

**Agent with Memory and MCP**: Persistent chat history, knowledge bank, user scoping, MCP tool integration, multi-provider invoke_tools → See [reference/agents-memory-mcp.md](reference/agents-memory-mcp.md)

**ML Data Pipeline**: Ingest multimodal data, enrich with AI models, version with snapshots, export to PyTorch/Parquet/pandas → See [reference/ml-data-pipeline.md](reference/ml-data-pipeline.md)
