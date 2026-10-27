---
description: >
  Transcribe a pile of audio or video files and make the transcripts
  searchable. Use for audio transcription search, speech-to-text then
  search, podcast indexing, or Whisper transcription plus embeddings.
argument-hint: "[audio-dir-or-urls]"
---

Transcribe audio (or video soundtracks) and make the transcripts searchable. Request: `$ARGUMENTS`

Load the `audio-transcription-search` skill and the `pixeltable` skill. Transcribe in a computed column. Do not write a transcribe-then-load-into-vector-DB pipeline.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Split long files, transcribe with Whisper, and index the text:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
embed_fn = pxtf.openai.embeddings.using(model='text-embedding-3-small')


class AudioFiles(TableModel, name='audio_files'):
    audio: pxt.Audio


class Segments(
    TableModel,
    name='segments',
    base=AudioFiles,
    iterator=pxtf.audio.audio_splitter(AudioFiles.audio, duration=30.0),
):
    transcript = pxtf.whisper.transcribe(audio_segment, model='tiny.en').text  # type: ignore[name-defined]
    __indexes__ = [pxt.EmbeddingIndex(transcript, embedding=embed_fn, name='transcript_idx')]


@pxt.query
def search_transcripts(query_text: str):
    sim = Segments.transcript.similarity(string=query_text)
    return Segments.order_by(sim, asc=False).select(
        Segments.transcript, score=sim
    ).limit(10)
```

3. Apply with `pxt schema update app.py my_app`. Insert audio or video files. Local Whisper needs `openai-whisper`. The index needs `OPENAI_API_KEY`. Hosted alternative: `pxtf.openai.transcriptions(audio, model='whisper-1').text`.

4. Show how to insert one file and search the transcript.
