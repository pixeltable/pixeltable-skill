# Pixeltable Core API Reference

Complete reference for table operations, querying, computed columns, views, embedding indexes, UDFs, tools, and configuration.

## Contents

- [Table Creation](#table-creation) (basic, primary key, UUID, from source)
- [Querying](#querying) (select, where, order by, pandas, Pydantic)
- [Computed Columns](#computed-columns)
- [Views](#views) (filtered, document chunking, video frames, string splitting, audio splitting)
- [Built-in Functions](#built-in-image-functions) (image, video, string)
- [Embedding Indexes](#embedding-indexes) (add index, similarity search, distance metrics)
- [UDFs](#udfs) (basic, optional args, batch, aggregate, retrieval)
- [Update and Delete](#update-and-delete)
- [Table Operations](#table-operations)
- [Snapshots](#snapshots)
- [Tools and Agents](#tools-and-agents) (create tools, agent pipeline, MCP)
- [Configuration](#configuration)
- [Performance Tips](#performance-tips)

---

## Table Creation

### Basic Table

```python
import pixeltable as pxt

t = pxt.create_table('dir.table_name', {
    'col1': pxt.String,
    'col2': pxt.Int,
    'col3': pxt.Float,
    'col4': pxt.Bool,
    'col5': pxt.Image,
    'col6': pxt.Video,
    'col7': pxt.Audio,
    'col8': pxt.Document,
    'col9': pxt.Json,
    'col10': pxt.Array[(3, 4), pxt.Float],  # 3x4 float array
    'col11': pxt.Timestamp,
    'col12': pxt.Date,
    'col13': pxt.UUID,
    'col14': pxt.Binary,
}, if_exists='ignore')
```

### Table with Primary Key

```python
t = pxt.create_table('dir.table', {
    'id': pxt.Required[pxt.String],
    'data': pxt.String,
}, primary_key=['id'], if_exists='ignore')
```

### Table with Auto-Generated UUID Primary Key

Production-ready pattern using uuid7() for automatic unique IDs:

```python
from pixeltable.functions.uuid import uuid7

t = pxt.create_table('dir.items', {
    'content': pxt.String,
    'uuid': uuid7(),            # auto-generated on insert
    'timestamp': pxt.Timestamp,
}, primary_key=['uuid'], if_exists='ignore')

# No need to provide uuid when inserting
from datetime import datetime
t.insert([{'content': 'Hello', 'timestamp': datetime.now()}])
```

### Table from Data Source

```python
t = pxt.create_table('dir.from_csv', source='data.csv')
t = pxt.create_table('dir.from_parquet', source='data.parquet')
t = pxt.create_table('dir.data', source='data.csv',
    schema_overrides={'image_col': pxt.Image, 'doc_col': pxt.Document})
```

## Querying

### Select

```python
results = t.collect()                                          # all columns
results = t.select(t.col1, t.col2).collect()                  # specific columns
results = t.select(t.col1, doubled=t.col2 * 2).collect()      # with expressions
```

### Where (Filter)

```python
results = t.where(t.col2 > 10).select(t.col1).collect()
results = t.where((t.col2 > 10) & (t.col1 != 'exclude')).collect()
results = t.where(t.col1.like('%pattern%')).collect()
```

### Order By / Limit / Count / Sample

```python
results = t.order_by(t.col2, asc=False).limit(10).collect()
total = t.count()
filtered = t.where(t.score > 0.5).count()

# Pagination with offset
page2 = t.order_by(t.col2).limit(10, offset=10).collect()

# Random sample (reproducible with seed)
sample = t.sample(n=100, seed=42).select(t.col1, t.col2).collect()
```

### To Pandas

```python
df = t.select(t.col1, t.col2).collect().to_pandas()
```

### To Pydantic

Convert query results directly to Pydantic models for API responses:

```python
from pydantic import BaseModel

class ItemResponse(BaseModel):
    title: str
    score: float
    content: str | None = None

# Column names in select() must match Pydantic field names
items = list(
    t.select(title=t.title, score=t.score, content=t.content)
    .collect()
    .to_pydantic(ItemResponse)
)
```

### Inserting Pydantic Models

```python
from pydantic import BaseModel
from datetime import datetime

class AgentRow(BaseModel):
    prompt: str
    timestamp: datetime
    system_prompt: str = "You are a helpful assistant."
    max_tokens: int = 1024

row = AgentRow(prompt="Explain quantum computing", timestamp=datetime.now())
t.insert([row])
```

### Head / Tail

```python
first_5 = t.head(5)
last_5 = t.tail(5)
```

## Computed Columns

```python
# Simple expression
t.add_computed_column(upper_name=t.name.upper(), if_exists='ignore')

# Using a UDF
t.add_computed_column(result=my_udf(t.input_col), if_exists='ignore')

# Using an AI provider
from pixeltable.functions.openai import chat_completions
t.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': t.text}],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore'
)

# Drop column
t.drop_column('column_name')

# Recompute failed or outdated columns (critical for error recovery)
t.recompute_columns(columns=['summary'])
t.recompute_columns(columns=['summary'], where=t.summary.errortype != None)
```

## Views

### Filtered View

```python
v = pxt.create_view('dir.active', t.where(t.is_active == True), if_exists='ignore')
```

### Document Chunking

```python
from pixeltable.functions.document import document_splitter

# By token limit
chunks = pxt.create_view('dir.chunks', t,
    iterator=document_splitter(t.doc, separators='token_limit', limit=300),
    if_exists='ignore')

# By sentence
chunks = pxt.create_view('dir.sentences', t,
    iterator=document_splitter(t.doc, separators='sentence'),
    if_exists='ignore')

# By heading
chunks = pxt.create_view('dir.headings', t,
    iterator=document_splitter(t.doc, separators='heading'),
    if_exists='ignore')

# By page (PDF)
chunks = pxt.create_view('dir.pages', t,
    iterator=document_splitter(t.doc, separators='page'),
    if_exists='ignore')

# Combined: page + sentence (recommended for PDFs)
chunks = pxt.create_view('dir.chunks', t,
    iterator=document_splitter(t.doc, separators='page, sentence'),
    if_exists='ignore')

# Combined: heading + token limit
chunks = pxt.create_view('dir.chunks', t,
    iterator=document_splitter(t.doc, separators='heading,token_limit', limit=500),
    if_exists='ignore')

# With metadata
chunks = pxt.create_view('dir.chunks', t,
    iterator=document_splitter(t.doc, separators='sentence', metadata='title,heading,page'),
    if_exists='ignore')

# With image extraction (PDF page separator only)
chunks = pxt.create_view('dir.chunks', t,
    iterator=document_splitter(t.doc, separators='page', elements=['text', 'image']),
    if_exists='ignore')
```

### Video Frame Extraction

```python
from pixeltable.functions.video import frame_iterator

# All frames
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video), if_exists='ignore')

# At specific FPS
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video, fps=1.0), if_exists='ignore')

# Exact number of frames
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video, num_frames=10), if_exists='ignore')

# Keyframes only (most efficient for visual search)
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video, keyframes_only=True), if_exists='ignore')
```

Output columns: `frame` (PIL Image), `frame_idx`, `pos_msec`, `pos_frame`

### String Splitting

```python
from pixeltable.functions.string import string_splitter

# Split text into sentences
sentences = pxt.create_view('dir.sentences', t,
    iterator=string_splitter(text=t.content, separators='sentence'),
    if_exists='ignore')
```

Output columns: `text`

### Audio Splitting

```python
from pixeltable.functions.audio import audio_splitter

# Split audio into 30-second chunks
audio_chunks = pxt.create_view('dir.audio_chunks', t,
    iterator=audio_splitter(audio=t.audio, duration=30.0),
    if_exists='ignore')
```

Output columns: `audio_chunk`

## Built-in Image Functions

```python
from pixeltable.functions import image as pxt_image

# Thumbnail generation
t.add_computed_column(
    thumb=pxt_image.thumbnail(t.image, size=(320, 320)),
    if_exists='ignore')

# Base64 encoding (useful for API responses and Anthropic vision)
t.add_computed_column(
    b64=pxt_image.b64_encode(t.image),
    if_exists='ignore')

# Combined: thumbnail + base64 (common pattern for APIs)
t.add_computed_column(
    thumbnail=pxt_image.b64_encode(
        pxt_image.thumbnail(t.image, size=(320, 320))
    ),
    if_exists='ignore')

# Base64 with explicit format
t.add_computed_column(
    png_b64=pxt_image.b64_encode(t.image, 'png'),
    if_exists='ignore')
```

## Built-in Image Functions (Additional)

```python
from pixeltable.functions.image import draw_bounding_boxes

# Draw detection results on images (pairs with DETR/YOLOX output)
t.add_computed_column(
    annotated=draw_bounding_boxes(t.image, t.detections),
    if_exists='ignore')
```

## Built-in Video Functions

```python
from pixeltable.functions.video import extract_audio, resize, crop, concat_videos, with_audio

# Extract audio track from video
t.add_computed_column(
    audio=extract_audio(t.video, format='mp3'),
    if_exists='ignore')

# Resize video
t.add_computed_column(
    resized=resize(t.video, width=640, height=480),
    if_exists='ignore')

# Crop video region
t.add_computed_column(
    cropped=crop(t.video, x=100, y=100, w=400, h=300),
    if_exists='ignore')

# Concatenate two videos
t.add_computed_column(
    combined=concat_videos(t.intro_video, t.main_video),
    if_exists='ignore')

# Replace audio track on a video
t.add_computed_column(
    with_new_audio=with_audio(t.video, t.narration),
    if_exists='ignore')
```

## Built-in String Functions

```python
from pixeltable.functions import string as pxt_str

# String length
t.add_computed_column(text_len=pxt_str.len(t.content), if_exists='ignore')
```

## Embedding Indexes

### Add Index

```python
from pixeltable.functions.huggingface import clip, sentence_transformer

# CLIP (multimodal: text + image)
embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('image_col', embedding=embed_fn, if_exists='ignore')

# Sentence Transformers (text)
embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')
t.add_embedding_index('text_col', embedding=embed_fn, if_exists='ignore')

# Sentence Transformers (multilingual, high quality, recommended for production)
embed_fn = sentence_transformer.using(model_id='intfloat/multilingual-e5-large-instruct')
t.add_embedding_index('text_col', string_embed=embed_fn, if_exists='ignore')

# OpenAI embeddings
from pixeltable.functions.openai import embeddings
t.add_embedding_index('text_col', embedding=embeddings.using(model='text-embedding-3-small'), if_exists='ignore')
```

### Similarity Search

```python
# Text
sim = t.text_col.similarity(string='search query')
results = t.order_by(sim, asc=False).limit(10).select(t.text_col, sim).collect()

# Text with threshold filter
sim = t.text_col.similarity(string='search query')
results = t.where(sim > 0.5).order_by(sim, asc=False).limit(10).select(t.text_col, sim).collect()

# Image with text (multimodal)
sim = t.image_col.similarity(string='a red car')
results = t.order_by(sim, asc=False).limit(5).select(t.image_col, sim).collect()

# Image with image
sim = t.image_col.similarity(image='path/to/query.jpg')
results = t.order_by(sim, asc=False).limit(5).select(t.image_col, sim).collect()
```

### Distance Metrics

```python
t.add_embedding_index('col', embedding=fn, metric='cosine')  # default
t.add_embedding_index('col', embedding=fn, metric='ip')      # inner product
t.add_embedding_index('col', embedding=fn, metric='l2')      # euclidean
```

## B-Tree Indexes

For efficient range queries and equality lookups on non-embedding columns:

```python
# Add B-tree index for fast filtering
t.add_btree_index('category', if_exists='ignore')
t.add_btree_index('timestamp', if_exists='ignore')

# Drop an index
t.drop_index('index_name')
```

## UDFs

### Basic

```python
@pxt.udf
def my_function(x: str) -> str:
    return x.upper()
```

### With Optional Args

```python
from typing import Optional

@pxt.udf
def safe_process(value: Optional[str], default: str = '') -> str:
    return value if value is not None else default
```

### Batch UDF

```python
from pixeltable.func import Batch

@pxt.udf(batch_size=32)
def batch_process(texts: Batch[str]) -> Batch[list[float]]:
    return model.encode(texts).tolist()
```

### Aggregate UDF

```python
@pxt.uda
class MyAggregator(pxt.Aggregator):
    def __init__(self):
        self.sum = 0
        self.count = 0

    def update(self, val: int) -> None:
        self.sum += val
        self.count += 1

    def value(self) -> float:
        return self.sum / self.count if self.count > 0 else 0.0
```

### Retrieval UDF (for AI Tool Use)

```python
lookup_fn = pxt.retrieval_udf(t, name='lookup_items', description='Look up items by name',
    parameters=['name'], limit=5)
```

### Custom Iterator

Define custom iterators that produce multiple output rows from a single input:

```python
@pxt.iterator
class SlidingWindowIterator:
    """Produce overlapping windows from a text."""
    def __init__(self, text: str, window_size: int = 100, stride: int = 50):
        self.text = text
        self.window_size = window_size
        self.stride = stride

    def __next__(self) -> dict:  # yields {'window': str}
        ...
```

### List Iterator

Split a list/array column into one row per element:

```python
from pixeltable.functions import list_iterator

# Explode a JSON array column into individual rows
items = pxt.create_view('dir.items', t,
    iterator=list_iterator(t.tags),
    if_exists='ignore')
```

## Update and Delete

```python
t.update({'score': 1.0}, where=t.category == 'important')
t.delete(where=t.is_active == False)
```

## Table Operations

```python
t.rename_column('old_name', 'new_name')
t.add_column(new_col=pxt.String)
t.drop_column('col_name')
t.describe()
t.columns()

# Directory management
pxt.list_dirs()
pxt.list_tables()
contents = pxt.get_dir_contents('my_dir')
```

## Recompute Columns

Re-run computed columns on existing rows. Critical for retrying after API errors or rate limits:

```python
# Recompute all rows for a column
t.recompute_columns(columns=['summary'])

# Recompute only failed rows (most common pattern)
t.recompute_columns(columns=['summary'], where=t.summary.errortype != None)

# Recompute specific rows matching a condition
t.recompute_columns(columns=['label'], where=t.category == 'pending')
```

## Snapshots and Version History

Point-in-time copies of tables:

```python
snap = pxt.create_snapshot('dir.snap_v1', t, if_exists='ignore')
# Query the snapshot like any table
snap.select(snap.col1).collect()

# View table version history
versions = t.get_versions()
```

## Tools and Agents

### Create Tools from UDFs and Query Functions

```python
@pxt.udf
def web_search(keywords: str) -> str:
    """Search the web for information."""
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        results = list(ddgs.news(keywords=keywords, max_results=5))
        return '\n'.join(f"{r['title']}: {r['body']}" for r in results) if results else 'No results.'

@pxt.query
def search_docs(query_text: str):
    """Search documents by semantic similarity."""
    sim = chunks.text.similarity(string=query_text)
    return chunks.order_by(sim, asc=False).limit(10).select(chunks.text, sim)

tools = pxt.tools(web_search, search_docs)
```

### Full Tool-Calling Agent Pipeline

The agent pipeline uses chained computed columns. Inserting a row triggers the entire pipeline:

```python
from pixeltable.functions.anthropic import messages, invoke_tools

agent = pxt.create_table('project.agent', {
    'prompt': pxt.String,
    'timestamp': pxt.Timestamp,
    'initial_system_prompt': pxt.String,
    'final_system_prompt': pxt.String,
    'max_tokens': pxt.Int,
    'temperature': pxt.Float,
}, if_exists='ignore')

# Step 1: Initial LLM call with tool selection
agent.add_computed_column(
    initial_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': agent.prompt}]}],
        tools=tools,
        tool_choice=tools.choice(required=True),
        max_tokens=agent.max_tokens,
        model_kwargs={
            'system': agent.initial_system_prompt,
            'temperature': agent.temperature,
        },
    ),
    if_exists='ignore',
)

# Step 2: Execute the tools the LLM selected
agent.add_computed_column(
    tool_output=invoke_tools(tools, agent.initial_response),
    if_exists='ignore',
)

# Step 3: RAG context retrieval
agent.add_computed_column(
    doc_context=search_docs(agent.prompt),
    if_exists='ignore',
)

# Step 4: Assemble context with a UDF
agent.add_computed_column(
    context=assemble_context(agent.prompt, agent.tool_output, agent.doc_context),
    if_exists='ignore',
)

# Step 5: Final LLM call with full context
agent.add_computed_column(
    final_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': agent.context}]}],
        max_tokens=agent.max_tokens,
        model_kwargs={
            'system': agent.final_system_prompt,
            'temperature': agent.temperature,
        },
    ),
    if_exists='ignore',
)

# Step 6: Extract answer text
agent.add_computed_column(
    answer=agent.final_response.content[0].text,
    if_exists='ignore',
)
```

### Using the Agent Pipeline

```python
from datetime import datetime

agent.insert([{
    'prompt': 'What are the latest developments in quantum computing?',
    'timestamp': datetime.now(),
    'initial_system_prompt': 'Identify the best tool(s) to answer the query.',
    'final_system_prompt': 'Provide a clear answer. Cite sources when possible.',
    'max_tokens': 1024,
    'temperature': 0.7,
}])

result = agent.order_by(agent.timestamp, asc=False).limit(1).select(agent.answer).collect()
```

### MCP Integration

```python
udfs = pxt.mcp_udfs('http://localhost:8080/sse')
```

---

## Data Sharing and Replication

Share tables across teams or environments:

```python
# Publish a table version (makes it shareable)
t.publish()

# Replicate a published table (creates a local synchronized copy)
replica = pxt.replicate('dir.local_copy', source_table_uri)

# Sync changes
replica.pull()   # fetch latest from source
replica.push()   # push local changes to source
```

## Export to SQL Databases

```python
from pixeltable.io.sql import export_sql

# Export full table to SQLite
export_sql(t, 'my_table', db_connect_str='sqlite:///data.db')

# Export filtered query with column rename
export_sql(
    t.where(t.score > 0.8).select(product_name=t.name, price=t.price),
    'filtered_products',
    db_connect_str='sqlite:///data.db',
)

# Append to existing SQL table
export_sql(t, 'products', db_connect_str=connection_string, if_exists='insert')

# Replace existing SQL table
export_sql(t, 'products', db_connect_str=connection_string, if_exists='replace')

# Cloud databases (PostgreSQL, Snowflake, etc.)
export_sql(t, 'products', db_connect_str='postgresql+psycopg://user:pass@host:5432/db')
```

---

## Configuration

### API Keys

```python
# Via init
pxt.init({'openai.api_key': 'sk-...', 'anthropic.api_key': 'sk-ant-...'})

# Via environment variables (recommended)
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY / GEMINI_API_KEY,
# TOGETHER_API_KEY, FIREWORKS_API_KEY, MISTRAL_API_KEY, GROQ_API_KEY,
# DEEPSEEK_API_KEY, VOYAGE_API_KEY, REPLICATE_API_TOKEN, HF_AUTH_TOKEN,
# OPENROUTER_API_KEY, FAL_API_KEY, REVE_API_KEY, TWELVELABS_API_KEY,
# BEDROCK_API_KEY
```

### config.toml

Located at `~/.pixeltable/config.toml`:

```toml
[pixeltable]
file_cache_size_g = 250
time_zone = "America/Los_Angeles"
hide_warnings = true
verbosity = 2

[openai]
api_key = 'sk-...'

# Per-model rate limits (requests per minute)
[openai.rate_limits]
gpt-4o = 500
gpt-4o-mini = 1000
tts-1 = 50
dall-e-3 = 10

[anthropic]
api_key = 'sk-ant-...'

[mistral]
api_key = 'my-mistral-key'
rate_limit = 600

# Azure OpenAI
[openai]
base_url = 'https://my-deployment.openai.azure.com/'
api_version = '2024-02-01'
```

### Rate Limiting

Default: 600 requests per minute per provider. Configure in `config.toml`:

```toml
# Single rate limit for all models of a provider
[fireworks]
rate_limit = 300

# Per-model rate limits
[openai.rate_limits]
gpt-4o = 500
gpt-4o-mini = 1000
```

Custom resource pools for non-built-in APIs:

```python
@pxt.udf(resource_pool='request-rate:my_service')
def call_custom_api(prompt: str) -> str:
    return requests.post('https://my-api.com/generate', json={'prompt': prompt}).json()['text']
```

### Media Destinations (Cloud Storage)

Store media files in S3, GCS, Azure, or other cloud storage instead of locally:

```toml
# config.toml — global default
[pixeltable]
input_media_dest = "s3://my-bucket/input/"
output_media_dest = "s3://my-bucket/output/"
```

```bash
# Or via environment variables
export PIXELTABLE_INPUT_MEDIA_DEST="s3://my-bucket/input/"
export PIXELTABLE_OUTPUT_MEDIA_DEST="s3://my-bucket/output/"
```

```python
# Per-column destination (overrides global default)
t.add_computed_column(
    thumbnail=pxt_image.thumbnail(t.image, size=(256, 256)),
    media_destination='s3://my-bucket/thumbnails/',
    if_exists='ignore',
)
```

Supported providers: Amazon S3, Google Cloud Storage (`gs://`), Azure Blob Storage (`wasbs://`), Cloudflare R2, Backblaze B2, Tigris.

## Performance Tips

- Batch inserts for efficiency
- Use `on_error='ignore'` to continue past row failures
- Use `batch_size` in `@pxt.udf(batch_size=32)` for GPU models
- Embedding indexes use HNSW for fast approximate nearest neighbor search
- Use `t.insert(source='file.csv')` instead of loading into memory for large datasets
- Use `keyframes_only=True` in `frame_iterator` for efficient video processing
- Use `thumbnail()` + `b64_encode()` for API-friendly image responses
- Configure rate limits in `config.toml` to avoid 429 errors on provider APIs
- Use `recompute_columns(where=t.col.errortype != None)` to retry only failed rows
- Use `add_btree_index()` on columns used frequently in `where()` filters
