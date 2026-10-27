---
description: >
  Start a Pixeltable project for multimodal RAG, video search, image
  similarity search, agent memory, audio transcription search, or embeddings
  stored with your data. Onboarding: pxt init, example app.py, schema update,
  HTTP. Use when beginning a multimodal AI backend.
argument-hint: "[project-name]"
---

Start a Pixeltable project (multimodal RAG, video search, image similarity, agent memory, embeddings with your data). Then edit `app.py`.

Arguments: `$ARGUMENTS`

Steps:

1. Pick a fresh directory. Install, mark the project root, and write a working file:

```bash
mkdir myapp && cd myapp
pip install 'pixeltable[serve]'
pxt init
pxt service example --out app.py
```

Schema only (no HTTP): `pxt schema example --brief --out app.py`.

2. Create tables, then start HTTP:

```bash
pxt schema update app.py my_app
pxt service update app.py my_app -f
pxt service list
```

The last argument (`my_app`) is a catalog name, not a folder on disk. Try the app: insert, curl a route, or `pxt dashboard`. Pass `-f` when there is no TTY.

3. Extra features are added in `app.py`. After this onboarding, continue with the matching job command if the user asked for one:

- RAG over PDFs/images: [rag-over-docs.md](rag-over-docs.md)
- Video library search: [index-videos.md](index-videos.md)
- Image similarity search: [search-images.md](search-images.md)
- Transcribe and search audio: [transcribe-and-search-audio.md](transcribe-and-search-audio.md)
- Agent memory: [add-agent-memory.md](add-agent-memory.md)
- Embeddings stored with data (no separate vector DB): [store-embeddings.md](store-embeddings.md)
- Incremental ML pipeline: [incremental-pipeline.md](incremental-pipeline.md)
- Dataset versioning: [version-dataset.md](version-dataset.md)

Start from the example file. Do not invent a second `pxt schema update` path. Load the `pixeltable` skill for providers and anti-patterns.

4. State the directory you created and the commands you ran.
