---
description: Scaffold a new Pixeltable project from an official template or structural pattern.
argument-hint: "[template-or-pattern] [project-name]"
---

Scaffold a new Pixeltable project using the official `pixeltable-new` generator.

Arguments: `$ARGUMENTS`

Steps:

1. ALWAYS run `uvx pixeltable-new --list` FIRST to get the authoritative list of templates and patterns. Never invent or guess a template name — only use a name that appears in that output. (Current templates: `multimodal-rag`, `video-intel`, `agent`, `audio-intel`, `content-pipeline`, `data-lab`; structural patterns: `serving` (default), `backend`, `batch`. The `--list` output is the source of truth and may change between releases.)

2. Map the user's request to the closest listed option:
   - A "RAG app" / multimodal search / docs+images+video+audio Q&A → `multimodal-rag` (serving + backend).
   - A chatbot / tool-calling agent / persistent memory / MCP → `agent`.
   - Audio / podcast / transcription + summarization → `audio-intel`.
   - Video frames / detection / transcription / search → `video-intel`.
   - Enterprise media processing / S3 ingest / export to a DB → `content-pipeline` (batch).
   - ML dataset engineering / auto-annotate / version / PyTorch export → `data-lab` (batch).
   - A headless API with no specific template fit → structural pattern `--backend`.
   - A one-shot pipeline / ingest-compute-export → structural pattern `--batch`.
   - Unsure → default structural pattern (declarative `serving`).
   If the chosen name is not in the `--list` output, pick the nearest listed name; do NOT retry with a fabricated `--template` value.

3. Generate using a verified name. Examples:

```bash
uvx pixeltable-new --template multimodal-rag my-rag-app   # template
uvx pixeltable-new my-app --backend                       # structural pattern, no --template
```

4. If a `--template` fetch fails, fall back to the closest structural pattern (`--backend` / `--batch` / default) instead of guessing another template name. State clearly which template or pattern you actually used and why.

5. After scaffolding, summarize the generated layout, how to run it, and the next computed columns the user is likely to add. Do NOT hand-write boilerplate that the template already provides.
