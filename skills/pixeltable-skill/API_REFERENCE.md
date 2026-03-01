# Pixeltable API Reference

Complete reference for all Pixeltable APIs, provider integrations, and workflow patterns. This file is loaded by Claude on demand when detailed API information is needed.

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

### Order By / Limit / Count

```python
results = t.order_by(t.col2, asc=False).limit(10).collect()
total = t.count()
filtered = t.where(t.score > 0.5).count()
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

## Built-in Video Functions

```python
from pixeltable.functions.video import extract_audio

# Extract audio track from video
t.add_computed_column(
    audio=extract_audio(t.video, format='mp3'),
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
lookup_fn = pxt.retrieval_udf(t, name='lookup_items', description='Look up items by name')
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
```

## Snapshots

Point-in-time copies of tables:

```python
snap = pxt.create_snapshot('dir.snap_v1', t, if_exists='ignore')
# Query the snapshot like any table
snap.select(snap.col1).collect()
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
        messages=[{'role': 'user', 'content': agent.prompt}],
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
        messages=[{'role': 'user', 'content': agent.context}],
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

## AI Provider Examples

### OpenAI

#### Chat Completions

```python
from pixeltable.functions.openai import chat_completions

# Basic
t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='gpt-4o-mini'
    ).choices[0].message.content
)

# With system message
t.add_computed_column(
    response=chat_completions(
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': t.prompt}
        ],
        model='gpt-4o',
        max_tokens=1000,
        temperature=0.7
    ).choices[0].message.content
)

# Vision (image analysis)
t.add_computed_column(
    description=chat_completions(
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Describe this image.'},
                {'type': 'image_url', 'image_url': {'url': t.image}}
            ]
        }],
        model='gpt-4o'
    ).choices[0].message.content
)

# JSON mode
t.add_computed_column(
    structured=chat_completions(
        messages=[{'role': 'user', 'content': t.text}],
        model='gpt-4o-mini',
        response_format={'type': 'json_object'}
    ).choices[0].message.content
)
```

#### Embeddings

```python
from pixeltable.functions.openai import embeddings

t.add_computed_column(
    embed=embeddings(input=t.text, model='text-embedding-3-small').data[0].embedding
)

# As index
t.add_embedding_index('text', embedding=embeddings.using(model='text-embedding-3-small'))
```

#### Image Generation (DALL-E)

```python
from pixeltable.functions.openai import image_generations

t.add_computed_column(
    generated=image_generations(prompt=t.description, model='dall-e-3', size='1024x1024').data[0].url
)
```

#### Speech (TTS)

```python
from pixeltable.functions.openai import speech

t.add_computed_column(audio=speech(input=t.text, model='tts-1', voice='alloy'))
```

#### Transcription

```python
from pixeltable.functions.openai import transcriptions

t.add_computed_column(transcript=transcriptions(audio=t.audio_file, model='whisper-1').text)
```

### Anthropic

```python
from pixeltable.functions.anthropic import messages

# Basic
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': t.prompt}]}],
        model='claude-sonnet-4-20250514',
        max_tokens=1024
    ).content[0].text
)

# With system prompt
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': t.prompt}]}],
        model='claude-sonnet-4-20250514',
        system='You are an expert analyst.',
        max_tokens=2048
    ).content[0].text
)

# With tool calling
from pixeltable.functions.anthropic import messages, invoke_tools

tools = pxt.tools(search_fn, lookup_fn)
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='claude-sonnet-4-20250514',
        tools=tools,
        tool_choice=tools.choice(required=True),
        max_tokens=1024,
    ),
    if_exists='ignore',
)
t.add_computed_column(
    tool_results=invoke_tools(tools, t.response),
    if_exists='ignore',
)
```

### Google Gemini

```python
from pixeltable.functions.gemini import generate_content

t.add_computed_column(response=generate_content(contents=t.prompt, model='gemini-2.0-flash'))
```

### Together AI

```python
from pixeltable.functions.together import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
    ).choices[0].message.content
)
```

### Fireworks

```python
from pixeltable.functions.fireworks import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='accounts/fireworks/models/llama-v3p1-70b-instruct'
    ).choices[0].message.content
)
```

### Ollama (Local)

```python
from pixeltable.functions.ollama import chat_completions, embeddings

# Chat
t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='llama3.1'
    ).choices[0].message.content
)

# Embeddings
t.add_computed_column(embed=embeddings(input=t.text, model='nomic-embed-text'))
```

### Mistral AI

```python
from pixeltable.functions.mistralai import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='mistral-large-latest'
    ).choices[0].message.content
)
```

### Groq

```python
from pixeltable.functions.groq import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='llama-3.1-70b-versatile'
    ).choices[0].message.content
)
```

### DeepSeek

```python
from pixeltable.functions.deepseek import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='deepseek-chat'
    ).choices[0].message.content
)
```

### OpenRouter

```python
from pixeltable.functions.openrouter import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='anthropic/claude-sonnet-4-20250514'
    ).choices[0].message.content
)
```

### Hugging Face

#### CLIP (Multimodal Embeddings)

```python
from pixeltable.functions.huggingface import clip

embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('image', embedding=embed_fn)

sim = t.image.similarity(string='a photo of a dog')
results = t.order_by(sim, asc=False).limit(5).select(t.image, sim).collect()
```

#### Sentence Transformers

```python
from pixeltable.functions.huggingface import sentence_transformer

embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')
t.add_embedding_index('text', embedding=embed_fn)

# For multilingual / high-quality (recommended for production)
embed_fn = sentence_transformer.using(model_id='intfloat/multilingual-e5-large-instruct')
t.add_embedding_index('text', string_embed=embed_fn)
```

#### Object Detection (DETR)

```python
from pixeltable.functions.huggingface import detr_for_object_detection

detect = detr_for_object_detection.using(model_id='facebook/detr-resnet-50')
t.add_computed_column(detections=detect(t.image, threshold=0.8))
```

### Whisper (Local)

```python
from pixeltable.functions.whisper import transcribe

t.add_computed_column(transcript=transcribe(audio=t.audio, model='base'))
```

### Voyage AI

```python
from pixeltable.functions.voyageai import embed

t.add_computed_column(embed=embed(input=t.text, model='voyage-2'))
```

---

## End-to-End Workflows

### RAG Pipeline

```python
import pixeltable as pxt
from pixeltable.functions.document import document_splitter
from pixeltable.functions.openai import chat_completions, embeddings

pxt.create_dir('rag', if_exists='ignore')

docs = pxt.create_table('rag.documents', {
    'doc': pxt.Document,
    'title': pxt.String,
}, if_exists='ignore')

chunks = pxt.create_view('rag.chunks', docs,
    iterator=document_splitter(docs.doc, separators='token_limit', limit=300, metadata='title,heading'),
    if_exists='ignore')

chunks.add_computed_column(
    embed=embeddings(input=chunks.text, model='text-embedding-3-small').data[0].embedding,
    if_exists='ignore')
chunks.add_embedding_index('text',
    embedding=embeddings.using(model='text-embedding-3-small'),
    if_exists='ignore')

docs.insert([
    {'doc': 'path/to/document.pdf', 'title': 'My Document'},
    {'doc': 'https://example.com/page.html', 'title': 'Web Page'},
])

@pxt.query
def retrieve(question: str, top_k: int = 5):
    sim = chunks.text.similarity(string=question)
    return chunks.order_by(sim, asc=False).limit(top_k).select(chunks.text, chunks.title, sim)

context = retrieve('What is machine learning?').collect()
```

### Video Analysis Pipeline

```python
import pixeltable as pxt
from pixeltable.functions.video import frame_iterator, extract_audio
from pixeltable.functions.audio import audio_splitter
from pixeltable.functions.string import string_splitter
from pixeltable.functions.openai import chat_completions, transcriptions
from pixeltable.functions.huggingface import clip, sentence_transformer
from pixeltable.functions import image as pxt_image

pxt.create_dir('video', if_exists='ignore')

videos = pxt.create_table('video.library', {
    'video': pxt.Video, 'title': pxt.String
}, if_exists='ignore')

# 1. Keyframe extraction + CLIP visual search
frames = pxt.create_view('video.frames', videos,
    iterator=frame_iterator(videos.video, keyframes_only=True),
    if_exists='ignore')

frames.add_computed_column(
    thumbnail=pxt_image.b64_encode(
        pxt_image.thumbnail(frames.frame, size=(320, 320))),
    if_exists='ignore')

frames.add_embedding_index('frame',
    embedding=clip.using(model_id='openai/clip-vit-base-patch32'),
    if_exists='ignore')

# 2. Audio extraction -> transcription -> sentence embedding
videos.add_computed_column(
    audio=extract_audio(videos.video, format='mp3'),
    if_exists='ignore')

audio_chunks = pxt.create_view('video.audio_chunks', videos,
    iterator=audio_splitter(audio=videos.audio, duration=30.0),
    if_exists='ignore')

audio_chunks.add_computed_column(
    transcription=transcriptions(
        audio=audio_chunks.audio_chunk, model='whisper-1'),
    if_exists='ignore')

sentences = pxt.create_view('video.sentences',
    audio_chunks.where(audio_chunks.transcription != None),
    iterator=string_splitter(
        text=audio_chunks.transcription.text, separators='sentence'),
    if_exists='ignore')

embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')
sentences.add_embedding_index('text', string_embed=embed_fn, if_exists='ignore')

# 3. Describe frames with vision LLM
frames.add_computed_column(
    description=chat_completions(
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Describe this video frame in one sentence.'},
                {'type': 'image_url', 'image_url': {'url': frames.frame}}
            ]
        }],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore')

# Visual search
sim = frames.frame.similarity(string='person riding a bicycle')
results = frames.order_by(sim, asc=False).limit(10).select(
    frames.frame, frames.description, sim).collect()

# Transcript search
@pxt.query
def search_transcripts(query_text: str):
    sim = sentences.text.similarity(query_text)
    return sentences.where(sim > 0.7).order_by(sim, asc=False).select(
        sentences.text, source_video=sentences.video, sim=sim
    ).limit(20)
```

### Image Classification and Search

```python
import pixeltable as pxt
from pixeltable.functions.openai import chat_completions
from pixeltable.functions.huggingface import clip
from pixeltable.functions import image as pxt_image

pxt.create_dir('images', if_exists='ignore')

catalog = pxt.create_table('images.catalog', {
    'image': pxt.Image, 'filename': pxt.String,
}, if_exists='ignore')

catalog.add_computed_column(
    thumbnail=pxt_image.b64_encode(
        pxt_image.thumbnail(catalog.image, size=(320, 320))),
    if_exists='ignore')

catalog.add_computed_column(
    tags=chat_completions(
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'List 5 descriptive tags as a comma-separated list.'},
                {'type': 'image_url', 'image_url': {'url': catalog.image}}
            ]
        }],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore')

embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
catalog.add_embedding_index('image', embedding=embed_fn, if_exists='ignore')

sim = catalog.image.similarity(string='sunset over the ocean')
results = catalog.order_by(sim, asc=False).limit(5).select(
    catalog.image, catalog.tags, sim).collect()
```

### Audio Transcription and Analysis

```python
import pixeltable as pxt
from pixeltable.functions.openai import transcriptions, chat_completions

pxt.create_dir('audio', if_exists='ignore')

recordings = pxt.create_table('audio.recordings', {
    'audio': pxt.Audio, 'speaker': pxt.String,
}, if_exists='ignore')

recordings.add_computed_column(
    transcript=transcriptions(audio=recordings.audio, model='whisper-1').text,
    if_exists='ignore')

recordings.add_computed_column(
    summary=chat_completions(
        messages=[
            {'role': 'system', 'content': 'Summarize in 2-3 sentences.'},
            {'role': 'user', 'content': recordings.transcript}
        ],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore')
```

### Multi-Provider Comparison

```python
import pixeltable as pxt
from pixeltable.functions.openai import chat_completions as openai_chat
from pixeltable.functions.anthropic import messages as anthropic_msg
from pixeltable.functions.together import chat_completions as together_chat

pxt.create_dir('compare', if_exists='ignore')
prompts = pxt.create_table('compare.prompts', {'prompt': pxt.String}, if_exists='ignore')

prompts.add_computed_column(
    openai=openai_chat(
        messages=[{'role': 'user', 'content': prompts.prompt}], model='gpt-4o-mini'
    ).choices[0].message.content, if_exists='ignore')

prompts.add_computed_column(
    anthropic=anthropic_msg(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': prompts.prompt}]}],
        model='claude-sonnet-4-20250514', max_tokens=1024
    ).content[0].text, if_exists='ignore')

prompts.add_computed_column(
    llama=together_chat(
        messages=[{'role': 'user', 'content': prompts.prompt}],
        model='meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
    ).choices[0].message.content, if_exists='ignore')

prompts.insert([{'prompt': 'Explain quantum computing simply.'}])
results = prompts.select(
    prompts.prompt, prompts.openai, prompts.anthropic, prompts.llama).collect()
```

### Tool-Calling Agent (Full Production Example)

Complete agent pipeline as used in the Pixeltable App Template:

```python
import pixeltable as pxt
from pixeltable.functions.anthropic import messages, invoke_tools
from pixeltable.functions.huggingface import sentence_transformer, clip
from pixeltable.functions.document import document_splitter
from pixeltable.functions import image as pxt_image
from datetime import datetime

pxt.create_dir('app', if_exists='ignore')

# --- Data pipelines ---
documents = pxt.create_table('app.documents', {'document': pxt.Document}, if_exists='ignore')
chunks = pxt.create_view('app.chunks', documents,
    iterator=document_splitter(documents.document,
        separators='page, sentence', metadata='title,heading,page'),
    if_exists='ignore')

embed_fn = sentence_transformer.using(model_id='intfloat/multilingual-e5-large-instruct')
chunks.add_embedding_index('text', string_embed=embed_fn, if_exists='ignore')

images = pxt.create_table('app.images', {'image': pxt.Image}, if_exists='ignore')
images.add_computed_column(
    thumbnail=pxt_image.b64_encode(pxt_image.thumbnail(images.image, size=(320, 320))),
    if_exists='ignore')
images.add_embedding_index('image',
    embedding=clip.using(model_id='openai/clip-vit-base-patch32'), if_exists='ignore')

# --- Query functions (become tools + RAG context) ---
@pxt.query
def search_documents(query_text: str):
    sim = chunks.text.similarity(query_text)
    return chunks.where(sim > 0.5).order_by(sim, asc=False).select(
        chunks.text, sim=sim).limit(20)

@pxt.query
def search_images(query_text: str):
    sim = images.image.similarity(query_text)
    return images.where(sim > 0.25).order_by(sim, asc=False).select(
        encoded_image=pxt_image.b64_encode(
            pxt_image.thumbnail(images.image, size=(224, 224)), 'png'),
        sim=sim).limit(5)

@pxt.udf
def web_search(keywords: str) -> str:
    """Search the web using DuckDuckGo."""
    from duckduckgo_search import DDGS
    with DDGS() as ddgs:
        results = list(ddgs.news(keywords=keywords, max_results=5))
        return '\n'.join(
            f"{r['title']}: {r['body']}" for r in results
        ) if results else 'No results.'

@pxt.udf
def assemble_context(question: str, tool_outputs: list | None, doc_context: list | None) -> str:
    tool_str = str(tool_outputs) if tool_outputs else 'N/A'
    doc_str = '\n'.join(
        f"- {item.get('text', '')}" for item in (doc_context or []) if isinstance(item, dict)
    ) or 'N/A'
    return f"QUESTION: {question}\n\n[TOOL RESULTS]\n{tool_str}\n\n[DOCUMENTS]\n{doc_str}"

# --- Agent pipeline ---
tools = pxt.tools(web_search, search_documents)

agent = pxt.create_table('app.agent', {
    'prompt': pxt.String,
    'timestamp': pxt.Timestamp,
    'system_prompt': pxt.String,
    'max_tokens': pxt.Int,
    'temperature': pxt.Float,
}, if_exists='ignore')

agent.add_computed_column(
    initial_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': agent.prompt}],
        tools=tools,
        tool_choice=tools.choice(required=True),
        max_tokens=agent.max_tokens,
        model_kwargs={'system': agent.system_prompt, 'temperature': agent.temperature},
    ), if_exists='ignore')

agent.add_computed_column(tool_output=invoke_tools(tools, agent.initial_response), if_exists='ignore')
agent.add_computed_column(doc_context=search_documents(agent.prompt), if_exists='ignore')
agent.add_computed_column(
    context=assemble_context(agent.prompt, agent.tool_output, agent.doc_context),
    if_exists='ignore')

agent.add_computed_column(
    final_response=messages(
        model='claude-sonnet-4-20250514',
        messages=[{'role': 'user', 'content': agent.context}],
        max_tokens=agent.max_tokens,
        model_kwargs={'system': 'Answer based on context. Cite sources.', 'temperature': agent.temperature},
    ), if_exists='ignore')

agent.add_computed_column(answer=agent.final_response.content[0].text, if_exists='ignore')

# --- Usage ---
agent.insert([{
    'prompt': 'What are the latest AI breakthroughs?',
    'timestamp': datetime.now(),
    'system_prompt': 'Use tools to gather information, then answer.',
    'max_tokens': 1024,
    'temperature': 0.7,
}])
result = agent.order_by(agent.timestamp, asc=False).limit(1).select(agent.answer).collect()
```

### Local LLM Pipeline (Ollama)

```python
import pixeltable as pxt
from pixeltable.functions.ollama import chat_completions, embeddings

pxt.create_dir('local', if_exists='ignore')
t = pxt.create_table('local.data', {'text': pxt.String}, if_exists='ignore')

t.add_computed_column(
    analysis=chat_completions(
        messages=[{'role': 'user', 'content': 'Analyze: ' + t.text}],
        model='llama3.1'
    ).choices[0].message.content, if_exists='ignore')

t.add_embedding_index('text',
    embedding=embeddings.using(model='nomic-embed-text'),
    if_exists='ignore')

t.insert([{'text': 'Machine learning fundamentals'}])
sim = t.text.similarity(string='neural networks')
results = t.order_by(sim, asc=False).limit(5).select(t.text, sim).collect()
```

### FastAPI App Pattern

Production-ready pattern for web apps with Pixeltable:

```python
# setup_pixeltable.py -- Run once to initialize schema
import pixeltable as pxt
from pixeltable.functions.uuid import uuid7
from pixeltable.functions.document import document_splitter
from pixeltable.functions.huggingface import sentence_transformer

pxt.drop_dir('app', force=True)
pxt.create_dir('app', if_exists='ignore')

documents = pxt.create_table('app.documents', {
    'document': pxt.Document,
    'uuid': uuid7(),
    'timestamp': pxt.Timestamp,
}, primary_key=['uuid'], if_exists='ignore')

chunks = pxt.create_view('app.chunks', documents,
    iterator=document_splitter(
        documents.document, separators='page, sentence',
        metadata='title,heading,page'),
    if_exists='ignore')

embed_fn = sentence_transformer.using(
    model_id='intfloat/multilingual-e5-large-instruct')
chunks.add_embedding_index('text', string_embed=embed_fn, if_exists='ignore')

@pxt.query
def search_documents(query_text: str):
    sim = chunks.text.similarity(query_text)
    return chunks.where(sim > 0.5).order_by(sim, asc=False).select(
        chunks.text, sim=sim, title=chunks.title
    ).limit(20)
```

```python
# main.py -- FastAPI app (use def, not async def)
from fastapi import FastAPI
from pydantic import BaseModel
import pixeltable as pxt

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    text: str
    sim: float
    title: str | None = None

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]

@app.post("/api/search", response_model=SearchResponse)
def search(body: SearchRequest):                    # sync, not async
    table = pxt.get_table('app.chunks')
    sim = table.text.similarity(body.query)
    result = (
        table.where(sim > 0.3)
        .order_by(sim, asc=False)
        .select(text=table.text, sim=sim, title=table.title)
        .limit(20)
        .collect()
    )
    items = list(result.to_pydantic(SearchResult))  # direct conversion
    return SearchResponse(query=body.query, results=items)
```

### Export Workflow

```python
from pixeltable.io import export_parquet, export_lancedb

# To Parquet
export_parquet(t, 'output/my_data/')

# Query result to Parquet
query = t.where(t.score > 0.8).select(t.title, t.content, t.score)
export_parquet(query, 'output/filtered/')

# To pandas
df = t.select(t.title, t.content).collect().to_pandas()
df.to_csv('output/data.csv', index=False)

# To LanceDB
export_lancedb(t.select(t.content, t.embed), 'lancedb/', 'vectors')
```

---

## Configuration

```python
# Via init
pxt.init({'openai.api_key': 'sk-...', 'anthropic.api_key': 'sk-ant-...'})

# Via environment variables
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, TOGETHER_API_KEY,
# FIREWORKS_API_KEY, MISTRAL_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY,
# VOYAGE_API_KEY, REPLICATE_API_TOKEN, HF_TOKEN, OPENROUTER_API_KEY
```

## Performance Tips

- Batch inserts for efficiency
- Use `on_error='ignore'` to continue past row failures
- Use `batch_size` in `@pxt.udf(batch_size=32)` for GPU models
- Embedding indexes use HNSW for fast approximate nearest neighbor search
- Use `t.insert(source='file.csv')` instead of loading into memory for large datasets
- Use `keyframes_only=True` in `frame_iterator` for efficient video processing
- Use `thumbnail()` + `b64_encode()` for API-friendly image responses

## Companion Resources

- **App Template**: [pixeltable/pixeltable-app-template](https://github.com/pixeltable/pixeltable-app-template) -- Full-stack FastAPI + React reference app
- **MCP Server**: [pixeltable/mcp-server-pixeltable-developer](https://github.com/pixeltable/mcp-server-pixeltable-developer) -- Interactive Pixeltable exploration via MCP
- **Core AGENTS.md**: [pixeltable/pixeltable/AGENTS.md](https://github.com/pixeltable/pixeltable/blob/main/AGENTS.md) -- Contributing to Pixeltable itself
- **Docs**: [docs.pixeltable.com](https://docs.pixeltable.com/) | [SDK Reference](https://docs.pixeltable.com/sdk/latest/pixeltable)
