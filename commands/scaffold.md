---
description: Scaffold a new Pixeltable project from an official template or structural pattern.
argument-hint: "[template-or-pattern] [project-name]"
---

Scaffold a new Pixeltable project using the official `pixeltable-new` generator.

Arguments: `$ARGUMENTS`

Steps:

1. Pick the right starting point. If the user named a use case, map it to a template; otherwise use a structural pattern:
   - Templates (each builds on a structural pattern):
     - `knowledge-base` — document RAG, web UI + API
     - `chat-agent` — tool-calling agent with memory, web UI + API
     - `audio-transcription` — transcribe + summarize, web UI + API
     - `full-stack-showcase` — complete reference app, web UI + API
     - `video-search` — frame extraction + visual search, API only
     - `media-indexing` — ingest/enrich pipeline, API + batch
     - `image-dataset` — labeling/versioning/export, API + batch
   - Structural patterns:
     - default — declarative serving pattern
     - `--backend` — FastAPI API scaffold (headless)
     - `--batch` — batch processing script with `export_sql`

2. If unsure which exists, run `uvx pixeltable-new --list` first.

3. Generate. Examples:

```bash
uvx pixeltable-new --template knowledge-base my-kb
uvx pixeltable-new my-app --backend
```

4. After scaffolding, summarize the generated layout, how to run it, and the next computed columns the user is likely to add. Do NOT hand-write boilerplate that the template already provides.
