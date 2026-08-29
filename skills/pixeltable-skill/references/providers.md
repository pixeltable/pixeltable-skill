# Pixeltable AI Provider Reference

Functions live in `pixeltable.functions.*`. Use this table for import and output shape. In an app, embeddings go on `__indexes__`. In a notebook, `add_embedding_index()`.

## Quick Reference

| Provider | Import | Function | Extract answer |
|----------|--------|----------|----------------|
| OpenAI | `from pixeltable.functions.openai import chat_completions` | `chat_completions(messages=..., model='gpt-4o-mini')` | `.choices[0].message.content` |
| OpenAI Embeddings | `from pixeltable.functions.openai import embeddings` | `embeddings(input=..., model='text-embedding-3-small')` | `.data[0].embedding` |
| OpenAI TTS | `from pixeltable.functions.openai import speech` | `speech(input=..., model='tts-1', voice='alloy')` | *(returns Audio directly)* |
| OpenAI Transcription | `from pixeltable.functions.openai import transcriptions` | `transcriptions(audio=..., model='whisper-1')` | `.text` |
| OpenAI DALL-E | `from pixeltable.functions.openai import image_generations` | `image_generations(prompt=..., model='dall-e-3')` | `.data[0].url` |
| Anthropic | `from pixeltable.functions.anthropic import messages` | `messages(messages=..., model='claude-sonnet-4-20250514', max_tokens=1024)` | `.content[0].text` |
| Gemini | `from pixeltable.functions.gemini import generate_content, embed_content` | `generate_content(contents=..., model='gemini-2.5-flash')` | *(returns text directly)* |
| Together | `from pixeltable.functions.together import chat_completions` | `chat_completions(messages=..., model='meta-llama/...')` | `.choices[0].message.content` |
| Fireworks | `from pixeltable.functions.fireworks import chat_completions` | `chat_completions(messages=..., model='accounts/fireworks/...')` | `.choices[0].message.content` |
| Ollama | `from pixeltable.functions.ollama import chat, generate, embed` | `chat(messages=..., model='llama3.1')` | `.message.content` |
| Mistral | `from pixeltable.functions.mistralai import chat_completions` | `chat_completions(messages=..., model='mistral-large-latest')` | `.choices[0].message.content` |
| Groq | `from pixeltable.functions.groq import chat_completions` | `chat_completions(messages=..., model='llama-3.1-70b-versatile')` | `.choices[0].message.content` |
| DeepSeek | `from pixeltable.functions.deepseek import chat_completions` | `chat_completions(messages=..., model='deepseek-chat')` | `.choices[0].message.content` |
| OpenRouter | `from pixeltable.functions.openrouter import chat_completions` | `chat_completions(messages=..., model='anthropic/claude-sonnet-4-20250514')` | `.choices[0].message.content` |
| Hugging Face CLIP | `from pixeltable.functions.huggingface import clip` | `clip.using(model_id='openai/clip-vit-base-patch32')` | *(use as embedding index)* |
| Hugging Face ST | `from pixeltable.functions.huggingface import sentence_transformer` | `sentence_transformer.using(model_id='all-MiniLM-L6-v2')` | *(use as embedding index)* |
| Whisper (Local) | `from pixeltable.functions.whisper import transcribe` | `transcribe(audio=..., model='base')` | *(returns text directly)* |
| WhisperX (Local) | `from pixeltable.functions.whisperx import transcribe` | `transcribe(audio=..., model='large-v2', diarize=True)` | *(returns JSON with segments)* |
| Voyage AI | `from pixeltable.functions.voyageai import embed` | `embed(input=..., model='voyage-2')` | *(returns embedding directly)* |
| Jina AI | `from pixeltable.functions.jina import embeddings` | `embeddings(text=..., model='jina-embeddings-v3')` | *(use as embedding index)* |
| Twelve Labs | `from pixeltable.functions.twelvelabs import embed` | `embed(video_segment=..., model_name='marengo3.0')` | *(use as video embedding index)* |
| BFL FLUX | `from pixeltable.functions.bfl import generate` | `generate(prompt=..., width=1024, height=1024)` | *(returns Image directly)* |
| RunwayML | `from pixeltable.functions.runwayml import text_to_video` | `text_to_video(prompt=..., model='gen4.5')` | `.astype(pxt.Video)` |
| fal.ai | `from pixeltable.functions.fal import run` | `run(input=json, app='fal-ai/flux/schnell')` | *(returns JSON)* |
| Reve | `from pixeltable.functions.reve import create` | `create(prompt=...)` | *(returns Image directly)* |
| Fabric | `from pixeltable.functions.fabric import chat_completions` | `chat_completions(messages=..., model='gpt-4.1')` | `.choices[0].message.content` |
| llama.cpp | `from pixeltable.functions.llama_cpp import create_chat_completion` | `create_chat_completion(messages=..., repo_id='...', repo_filename='*q5_k_m.gguf')` | `.choices[0].message.content` |
| vLLM (Local) | `from pixeltable.functions.vllm import chat_completions, generate` | `chat_completions(messages=..., model='Qwen/Qwen2.5-0.5B-Instruct')` | *(returns VllmRequestOutput dict)* |
| YOLOX | `from pixeltable.functions.yolox import yolox` | `yolox(image=...)` | *(returns detection JSON)* |
| Replicate | `from pixeltable.functions.replicate import run` | `run(input=json, model='owner/model')` | *(returns JSON)* |
| Bedrock | `from pixeltable.functions.bedrock import converse` | `converse(messages=..., model='...')` | `.output.message.content[0].text` |

OpenAI-compatible providers return `.choices[0].message.content`. Anthropic returns `.content[0].text`. Image generation (BFL, Reve) returns `pxt.Image`.
