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

2. Split long files, transcribe with Whisper, and index the text as the `audio-transcription-search` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert audio or video files. Local Whisper needs `openai-whisper`. The index needs `OPENAI_API_KEY`. Hosted alternative: `pxtf.openai.transcriptions(audio, model='whisper-1').text`.

4. Show how to insert one file and search the transcript.
