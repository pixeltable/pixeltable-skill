---
description: Scaffold a new Pixeltable project from an official template or structural pattern.
argument-hint: "[template-or-pattern] [project-name]"
---

Scaffold a new Pixeltable project using the official `pixeltable-new` generator.

Arguments: `$ARGUMENTS`

Steps:

1. Run `uvx pixeltable-new --list` FIRST to see the current patterns and templates. Never invent or guess a name — only use one that appears in that output. There are two kinds:
   - **Structural patterns** (`serving` (default), `backend`, `batch`) — these always work and are the reliable path.
   - **Application templates** (e.g. `multimodal-rag`, `agent`, `audio-intel`, `video-intel`, `content-pipeline`, `data-lab`) — full schema + app + UI layered on a pattern. These depend on the starter-kit being in sync and CAN currently fail to fetch ("No files found" / "starter kit may have been restructured").

2. Choose a target. Each template maps to a pattern; if the template is unavailable, the pattern is your fallback:
   - "RAG app" / multimodal search / docs+images+video+audio Q&A → `multimodal-rag` → fallback `--backend`.
   - chatbot / tool-calling agent / persistent memory / MCP → `agent` → fallback `--backend`.
   - audio / podcast / transcription + summarization → `audio-intel` → fallback `--backend`.
   - video frames / detection / transcription / search → `video-intel` → fallback default `serving`.
   - enterprise media / S3 ingest / export to a DB → `content-pipeline` → fallback `--batch`.
   - ML dataset / auto-annotate / version / PyTorch export → `data-lab` → fallback `--batch`.
   - headless API, no specific template fit → `--backend` directly.
   - one-shot ingest-compute-export → `--batch` directly.
   - unsure → default `serving`.

3. Pick a fresh project directory name (the generator refuses to write into an existing directory). Then generate:

```bash
uvx pixeltable-new --template multimodal-rag my-rag-app   # template (try first if requested)
uvx pixeltable-new my-app --backend                       # structural pattern, no --template
```

4. If the `--template` command fails with "No files found" / "restructured", immediately run the mapped structural pattern instead. Do NOT retry other template names, and do NOT hand-write the app yourself. If the directory already exists, choose a new name rather than deleting the user's existing directory without asking.

5. State clearly which template or pattern you actually used (and, if you fell back, why). Then summarize the generated layout, how to run it (`uv sync` → `uv run python setup_pixeltable.py` → `uv run uvicorn main:app --reload`), and the next computed columns the user is likely to add. Do NOT hand-write boilerplate the scaffold already provides.
