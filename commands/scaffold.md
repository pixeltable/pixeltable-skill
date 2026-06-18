---
description: Scaffold a new Pixeltable project from an official template or structural pattern.
argument-hint: "[template-or-pattern] [project-name]"
---

Scaffold a new Pixeltable project using the official `pixeltable-new` generator.

Arguments: `$ARGUMENTS`

Steps:

1. Run `uvx pixeltable-new --list` FIRST to see the patterns and templates available on the installed version. Never invent or guess a name — only use one that appears in that output. There are two kinds:
   - **Structural patterns** (`serving` (default), `backend`, `batch`) — bare API/pipeline scaffolds. Always available.
   - **Application templates** — a full app (schema + API/UI) for a use case, each layered on a pattern. Current set: `knowledge-base`, `chat-agent`, `audio-transcription`, `video-search`, `media-indexing`, `image-dataset`, `full-stack-showcase`.

2. Choose a target by use case. Each template maps to a pattern; if the template is unavailable on this version, the pattern is your fallback:
   - "RAG app" / docs+images+video+audio upload + unified search + Q&A → `knowledge-base` → fallback `--backend`.
   - chatbot / tool-calling agent / persistent memory / MCP → `chat-agent` → fallback `--backend`.
   - audio / podcast / transcription + summarization → `audio-transcription` → fallback `--backend`.
   - video frames / detection / transcription / temporal search → `video-search` → fallback default `serving`.
   - enterprise media / S3 ingest / process all modalities / export → `media-indexing` → fallback `--batch`.
   - ML dataset / auto-annotate / curate / version / PyTorch export → `image-dataset` → fallback `--batch`.
   - complete reference app (Gemini + DETR + Whisper, React UI) → `full-stack-showcase` → fallback `--backend`.
   - headless API, no specific template fit → `--backend` directly.
   - one-shot ingest-compute-export → `--batch` directly.
   - unsure → default `serving`.

3. Pick a fresh project directory name (the generator refuses to write into an existing directory). Then generate:

```bash
uvx pixeltable-new --template knowledge-base my-rag-app   # template
uvx pixeltable-new my-app --backend                       # structural pattern, no --template
```

4. If the `--template` command reports an unknown name or "No files found" / "restructured" (a version skew between the installed `pixeltable-new` and the starter kit), re-check `--list` and use a listed name, or run the mapped structural pattern instead. Do NOT retry guessed template names, and do NOT hand-write the app yourself. If the directory already exists, choose a new name rather than deleting the user's existing directory without asking.

5. State clearly which template or pattern you actually used (and, if you fell back, why). Then follow the **Next steps** the generator prints to run it (templates: `uv sync` → `uv run python app.py`; backend: `uv sync` → `uv run python setup_pixeltable.py` → `uv run uvicorn main:app --reload`), and suggest the next computed columns the user is likely to add. Do NOT hand-write boilerplate the scaffold already provides.
