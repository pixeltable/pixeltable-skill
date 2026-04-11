# Pixeltable AI Provider Reference

Complete examples for all 15+ built-in AI provider integrations. All functions live in `pixeltable.functions.*`.

## Quick Reference

Use this table to find the correct import, function, and output accessor for each provider:

| Provider | Import | Function | Extract answer |
|----------|--------|----------|----------------|
| OpenAI | `from pixeltable.functions.openai import chat_completions` | `chat_completions(messages=..., model='gpt-4o-mini')` | `.choices[0].message.content` |
| OpenAI Embeddings | `from pixeltable.functions.openai import embeddings` | `embeddings(input=..., model='text-embedding-3-small')` | `.data[0].embedding` |
| OpenAI TTS | `from pixeltable.functions.openai import speech` | `speech(input=..., model='tts-1', voice='alloy')` | *(returns Audio directly)* |
| OpenAI Transcription | `from pixeltable.functions.openai import transcriptions` | `transcriptions(audio=..., model='whisper-1')` | `.text` |
| OpenAI DALL-E | `from pixeltable.functions.openai import image_generations` | `image_generations(prompt=..., model='dall-e-3')` | `.data[0].url` |
| Anthropic | `from pixeltable.functions.anthropic import messages` | `messages(messages=..., model='claude-sonnet-4-20250514', max_tokens=1024)` | `.content[0].text` |
| Gemini | `from pixeltable.functions.gemini import generate_content` | `generate_content(contents=..., model='gemini-2.0-flash')` | *(returns text directly)* |
| Together | `from pixeltable.functions.together import chat_completions` | `chat_completions(messages=..., model='meta-llama/...')` | `.choices[0].message.content` |
| Fireworks | `from pixeltable.functions.fireworks import chat_completions` | `chat_completions(messages=..., model='accounts/fireworks/...')` | `.choices[0].message.content` |
| Ollama | `from pixeltable.functions.ollama import chat_completions` | `chat_completions(messages=..., model='llama3.1')` | `.choices[0].message.content` |
| Mistral | `from pixeltable.functions.mistralai import chat_completions` | `chat_completions(messages=..., model='mistral-large-latest')` | `.choices[0].message.content` |
| Groq | `from pixeltable.functions.groq import chat_completions` | `chat_completions(messages=..., model='llama-3.1-70b-versatile')` | `.choices[0].message.content` |
| DeepSeek | `from pixeltable.functions.deepseek import chat_completions` | `chat_completions(messages=..., model='deepseek-chat')` | `.choices[0].message.content` |
| OpenRouter | `from pixeltable.functions.openrouter import chat_completions` | `chat_completions(messages=..., model='anthropic/claude-sonnet-4-20250514')` | `.choices[0].message.content` |
| Hugging Face CLIP | `from pixeltable.functions.huggingface import clip` | `clip.using(model_id='openai/clip-vit-base-patch32')` | *(use as embedding index)* |
| Hugging Face ST | `from pixeltable.functions.huggingface import sentence_transformer` | `sentence_transformer.using(model_id='all-MiniLM-L6-v2')` | *(use as embedding index)* |
| Whisper (Local) | `from pixeltable.functions.whisper import transcribe` | `transcribe(audio=..., model='base')` | *(returns text directly)* |
| Voyage AI | `from pixeltable.functions.voyageai import embed` | `embed(input=..., model='voyage-2')` | *(returns embedding directly)* |

**Key patterns**: OpenAI-compatible providers (Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, OpenRouter) all return `.choices[0].message.content`. Anthropic returns `.content[0].text`. Embedding functions are used with `add_embedding_index()`, not accessed directly.

---

## Contents

- [OpenAI](#openai) (chat, embeddings, DALL-E, TTS, transcription)
- [Anthropic](#anthropic) (messages, tool calling)
- [Google Gemini](#google-gemini)
- [Together AI](#together-ai)
- [Fireworks](#fireworks)
- [Ollama](#ollama-local) (local inference)
- [Mistral AI](#mistral-ai)
- [Groq](#groq)
- [DeepSeek](#deepseek)
- [OpenRouter](#openrouter)
- [Hugging Face](#hugging-face) (CLIP, Sentence Transformers, DETR)
- [Whisper](#whisper-local) (local transcription)
- [Voyage AI](#voyage-ai)

---

## OpenAI

### Chat Completions

```python
from pixeltable.functions.openai import chat_completions

# Basic
t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='gpt-4o-mini'
    ).choices[0].message.content,
    if_exists='ignore',
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
    ).choices[0].message.content,
    if_exists='ignore',
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
    ).choices[0].message.content,
    if_exists='ignore',
)

# JSON mode
t.add_computed_column(
    structured=chat_completions(
        messages=[{'role': 'user', 'content': t.text}],
        model='gpt-4o-mini',
        response_format={'type': 'json_object'}
    ).choices[0].message.content,
    if_exists='ignore',
)
```

### Embeddings

```python
from pixeltable.functions.openai import embeddings

t.add_computed_column(
    embed=embeddings(input=t.text, model='text-embedding-3-small').data[0].embedding,
    if_exists='ignore',
)

# As index
t.add_embedding_index('text', embedding=embeddings.using(model='text-embedding-3-small'), if_exists='ignore')
```

### Image Generation (DALL-E)

```python
from pixeltable.functions.openai import image_generations

t.add_computed_column(
    generated=image_generations(prompt=t.description, model='dall-e-3', size='1024x1024').data[0].url,
    if_exists='ignore',
)
```

### Speech (TTS)

```python
from pixeltable.functions.openai import speech

t.add_computed_column(audio=speech(input=t.text, model='tts-1', voice='alloy'), if_exists='ignore')
```

### Transcription

```python
from pixeltable.functions.openai import transcriptions

t.add_computed_column(transcript=transcriptions(audio=t.audio_file, model='whisper-1').text, if_exists='ignore')
```

## Anthropic

```python
from pixeltable.functions.anthropic import messages

# Basic
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': t.prompt}]}],
        model='claude-sonnet-4-20250514',
        max_tokens=1024
    ).content[0].text,
    if_exists='ignore',
)

# With system prompt
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': t.prompt}]}],
        model='claude-sonnet-4-20250514',
        system='You are an expert analyst.',
        max_tokens=2048
    ).content[0].text,
    if_exists='ignore',
)

# With tool calling
from pixeltable.functions.anthropic import messages, invoke_tools

tools = pxt.tools(search_fn, lookup_fn)
t.add_computed_column(
    response=messages(
        messages=[{'role': 'user', 'content': [{'type': 'text', 'text': t.prompt}]}],
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

## Google Gemini

```python
from pixeltable.functions.gemini import generate_content

t.add_computed_column(response=generate_content(contents=t.prompt, model='gemini-2.0-flash'), if_exists='ignore')
```

## Together AI

```python
from pixeltable.functions.together import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## Fireworks

```python
from pixeltable.functions.fireworks import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='accounts/fireworks/models/llama-v3p1-70b-instruct'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## Ollama (Local)

```python
from pixeltable.functions.ollama import chat_completions, embeddings

# Chat
t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='llama3.1'
    ).choices[0].message.content,
    if_exists='ignore',
)

# Embeddings
t.add_computed_column(embed=embeddings(input=t.text, model='nomic-embed-text'), if_exists='ignore')
```

## Mistral AI

```python
from pixeltable.functions.mistralai import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='mistral-large-latest'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## Groq

```python
from pixeltable.functions.groq import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='llama-3.1-70b-versatile'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## DeepSeek

```python
from pixeltable.functions.deepseek import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='deepseek-chat'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## OpenRouter

```python
from pixeltable.functions.openrouter import chat_completions

t.add_computed_column(
    response=chat_completions(
        messages=[{'role': 'user', 'content': t.prompt}],
        model='anthropic/claude-sonnet-4-20250514'
    ).choices[0].message.content,
    if_exists='ignore',
)
```

## Hugging Face

### CLIP (Multimodal Embeddings)

```python
from pixeltable.functions.huggingface import clip

embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
t.add_embedding_index('image', embedding=embed_fn, if_exists='ignore')

sim = t.image.similarity(string='a photo of a dog')
results = t.order_by(sim, asc=False).limit(5).select(t.image, sim).collect()
```

### Sentence Transformers

```python
from pixeltable.functions.huggingface import sentence_transformer

embed_fn = sentence_transformer.using(model_id='all-MiniLM-L6-v2')
t.add_embedding_index('text', embedding=embed_fn, if_exists='ignore')

# For multilingual / high-quality (recommended for production)
embed_fn = sentence_transformer.using(model_id='intfloat/multilingual-e5-large-instruct')
t.add_embedding_index('text', string_embed=embed_fn, if_exists='ignore')
```

### Object Detection (DETR)

```python
from pixeltable.functions.huggingface import detr_for_object_detection

detect = detr_for_object_detection.using(model_id='facebook/detr-resnet-50')
t.add_computed_column(detections=detect(t.image, threshold=0.8), if_exists='ignore')
```

## Whisper (Local)

```python
from pixeltable.functions.whisper import transcribe

t.add_computed_column(transcript=transcribe(audio=t.audio, model='base'), if_exists='ignore')
```

## Voyage AI

```python
from pixeltable.functions.voyageai import embed

t.add_computed_column(embed=embed(input=t.text, model='voyage-2'), if_exists='ignore')
```
