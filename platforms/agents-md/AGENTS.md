# Pixeltable — Multimodal AI Data Infrastructure

Pixeltable is an open-source Python library providing declarative data infrastructure for multimodal AI applications. It unifies storage, transformation, indexing, and retrieval across images, video, audio, and documents in a table-based interface.

**Install:** `pip install pixeltable` (requires Python >= 3.10)
**Docs:** https://docs.pixeltable.com/ | **GitHub:** https://github.com/pixeltable/pixeltable

## Core Patterns

### Tables and Column Types

```python
import pixeltable as pxt

pxt.create_dir('project', if_exists='ignore')

t = pxt.create_table('project.data', {
    'title': pxt.String,
    'content': pxt.String,
    'image': pxt.Image,
    'video': pxt.Video,
    'audio': pxt.Audio,
    'doc': pxt.Document,
    'metadata': pxt.Json,
    'score': pxt.Float,
}, if_exists='ignore')
```

Types: `String`, `Int`, `Float`, `Bool`, `Image`, `Video`, `Audio`, `Document`, `Json`, `Array`, `Timestamp`, `Date`, `UUID`, `Binary`. Use `pxt.Required[pxt.String]` for non-nullable.

### Auto-Generated Keys

```python
from pixeltable.functions.uuid import uuid7

t = pxt.create_table('project.items', {
    'content': pxt.String,
    'uuid': uuid7(),
    'timestamp': pxt.Timestamp,
}, primary_key=['uuid'], if_exists='ignore')
```

### Inserting Data

```python
t.insert([
    {'title': 'Doc 1', 'content': 'Hello'},
    {'title': 'Doc 2', 'content': 'World'},
])
t.insert(title='Doc 3', content='Single row')
t.insert(source='data.csv')
```

### Computed Columns

Transformations that run automatically on new/updated data:

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
results = t.where(t.score > 0.8).select(t.title).collect()
results = t.order_by(t.score, asc=False).limit(10).collect()
page2 = t.order_by(t.score).limit(10, offset=10).collect()
df = t.collect().to_pandas()

# To Pydantic models (for API responses)
from pydantic import BaseModel
class Result(BaseModel):
    title: str
    score: float
items = list(t.select(title=t.title, score=t.score).collect().to_pydantic(Result))
```

### Views and Iterators

Split rows into sub-rows for chunking, frame extraction, etc.:

```python
from pixeltable.functions.document import document_splitter
from pixeltable.functions.video import frame_iterator

chunks = pxt.create_view('project.chunks', t,
    iterator=document_splitter(t.doc, separators='token_limit', limit=300),
    if_exists='ignore')

frames = pxt.create_view('project.frames', t,
    iterator=frame_iterator(t.video, fps=1.0),
    if_exists='ignore')
```

### Embedding Indexes and Similarity Search

```python
from pixeltable.functions.huggingface import clip, sentence_transformer

embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')
t.add_embedding_index('content', embedding=embed_fn, if_exists='ignore')

sim = t.content.similarity(string='search query')
results = t.order_by(sim, asc=False).limit(5).select(t.title, t.content, sim).collect()

# Multimodal (CLIP): text-to-image search
embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('image', embedding=embed_fn, if_exists='ignore')
sim = t.image.similarity(string='a photo of a cat')
```

### UDFs and Query Functions

```python
@pxt.udf
def clean_text(text: str) -> str:
    return text.strip().lower()

@pxt.query
def search_docs(query_text: str, limit: int = 10):
    sim = t.content.similarity(string=query_text)
    return t.order_by(sim, asc=False).limit(limit).select(t.title, t.content, sim)
```

### Tool-Calling Agent Pipeline

```python
from pixeltable.functions.anthropic import messages, invoke_tools

tools = pxt.tools(web_search, search_docs)

agent = pxt.create_table('project.agent', {
    'prompt': pxt.String, 'timestamp': pxt.Timestamp,
    'system_prompt': pxt.String, 'max_tokens': pxt.Int,
    'temperature': pxt.Float,
}, if_exists='ignore')

agent.add_computed_column(
    response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': agent.prompt}]}],
        tools=tools, tool_choice=tools.choice(required=True),
        max_tokens=agent.max_tokens,
        model_kwargs={'system': agent.system_prompt, 'temperature': agent.temperature},
    ), if_exists='ignore')

agent.add_computed_column(
    tool_output=invoke_tools(tools, agent.response), if_exists='ignore')

agent.add_computed_column(
    answer=agent.response.content[0].text, if_exists='ignore')
```

## AI Provider Integrations

Built-in functions in `pixeltable.functions.*`:

| Provider | Module | Key Functions |
|----------|--------|---------------|
| OpenAI | `openai` | `chat_completions`, `embeddings`, `image_generations`, `speech`, `transcriptions` |
| Anthropic | `anthropic` | `messages`, `invoke_tools` |
| Gemini | `gemini` | `generate_content`, `invoke_tools` |
| Hugging Face | `huggingface` | `clip`, `sentence_transformer`, `detr_for_object_detection` |
| Together | `together` | `chat_completions`, `embeddings`, `image_generations` |
| Fireworks | `fireworks` | `chat_completions`, `embeddings` |
| Ollama | `ollama` | `chat_completions`, `embeddings` |
| Mistral | `mistralai` | `chat_completions`, `embeddings` |
| Groq | `groq` | `chat_completions`, `invoke_tools` |
| DeepSeek | `deepseek` | `chat_completions` |
| OpenRouter | `openrouter` | `chat_completions` |
| Bedrock | `bedrock` | `converse`, `invoke_tools` |
| Jina AI | `jina` | `embeddings`, `rerank` |
| BFL FLUX | `bfl` | `generate`, `edit`, `expand`, `fill` |
| RunwayML | `runwayml` | `text_to_video`, `image_to_video` |

Also: Replicate, Voyage AI, Twelve Labs, fal.ai, Reve, Fabric, llama.cpp, Whisper, WhisperX, YOLOX.

**Output patterns**: OpenAI-compatible → `.choices[0].message.content`. Anthropic → `.content[0].text`. Image generation (BFL, Reve) → returns `pxt.Image` directly.

## Import/Export

```python
t = pxt.create_table('dir.data', source='data.csv')
t = pxt.create_table('dir.data', source='data.csv',
    schema_overrides={'image_col': pxt.Image})

from pixeltable.io import import_huggingface_dataset, import_pandas, export_parquet
from pixeltable.io.sql import export_sql
export_sql(t, 'table_name', db_connect_str='sqlite:///data.db')
```

## Critical Rules

- **Always** use `if_exists='ignore'` for idempotent operations
- Use `on_error='ignore'` for fault-tolerant inserts
- Error inspection: `t.where(t.col.errortype != None).select(t.col.errormsg).collect()`
- Retry failed columns: `t.recompute_columns(columns=['col'], where=t.col.errortype != None)`
- FastAPI endpoints: use `def` not `async def` (Pixeltable is synchronous)
- Pixeltable IS the data layer — no ORM needed
- Anthropic messages use list-of-blocks format: `[{'type': 'text', 'text': val}]`

## Resources

- [Documentation](https://docs.pixeltable.com/)
- [GitHub](https://github.com/pixeltable/pixeltable)
- [Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) — Full-stack FastAPI + React + deployment templates
- [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- **LLM-optimized docs**: [pixeltable.com/llms.txt](https://www.pixeltable.com/llms.txt) | [docs.pixeltable.com/llms.txt](https://docs.pixeltable.com/llms.txt) | [llms-full.txt](https://docs.pixeltable.com/llms-full.txt)
