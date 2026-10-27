---
name: audio-transcription-search
description: >
  Transcribe a pile of audio files and make the transcripts searchable. Use
  when converting speech to text, indexing podcasts or calls, or searching
  recordings by what was said. Covers audio transcription search, Whisper,
  transcript embeddings, and semantic search over speech. Long files can be
  split into segments with audio_splitter before transcription. Video files
  work too: extract_audio, then transcribe. Load the pixeltable skill for
  the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill to transcribe audio (or the audio track of a video) and
search by meaning, not only keywords. Whisper runs locally
(`pip install openai-whisper`). OpenAI `transcriptions` is the hosted
alternative.

For long files, create a view with `audio_splitter` (for example
`duration=30.0`) and transcribe `audio_segment`. Sentence splitting of
the transcript needs spaCy.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer

pxt.create_dir('audio_lib', if_exists='ignore')
audio = pxt.create_table(
    'audio_lib.files', {'audio': pxt.Audio}, if_exists='ignore',
)
audio.add_computed_column(
    transcription=whisper.transcribe(
        audio=audio.audio, model='base.en',
    ),
    if_exists='ignore',
)
audio.add_computed_column(
    text=audio.transcription.text.astype(pxt.String),
    if_exists='ignore',
)
audio.add_embedding_index(
    'text',
    embedding=sentence_transformer.using(
        model_id='sentence-transformers/all-MiniLM-L6-v2',
    ),
    if_exists='ignore',
)
sim = audio.text.similarity(string='the topic you heard')
audio.order_by(sim, asc=False).limit(5).select(
    audio.text, score=sim,
).collect()
```

Notebook or REPL form (`if_exists='ignore'` so it is re-runnable). For an
HTTP app, load the `pixeltable` skill and declare the same columns on a
`TableModel` with indexes in `__indexes__`, then `pxt schema update`.

## Full guidance

This skill is a thin catalog entry. Load the `pixeltable` skill for the
application file, CLI, providers, serving, and anti-patterns:
`skills/pixeltable-skill/SKILL.md` in this repo.

Install: `npx skills add pixeltable/pixeltable-skill`.
Docs: https://docs.pixeltable.com/
