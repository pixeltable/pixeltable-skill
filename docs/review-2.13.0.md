# Pixeltable skill 2.13.0 review

Reviewed 2026-10-27. Scope is catalog discovery: a keyword-rich teaching-skill
description, eight thin task-named skills under `skills/`, and matching
manifest / installer / README updates. This is not a full re-verify of every
API claim in 2.12.0.

The last full teaching-skill pass remains [review-2.12.0.md](review-2.12.0.md)
against Pixeltable 0.7.11. Snippets in the new skills were checked against
Pixeltable **0.7.21** (PyPI, 2026-10-26), docs.pixeltable.com, and upstream
source (`pixeltable/pixeltable` tag `v0.7.21`).

## Verdict

Ready for review as a draft. The teaching skill's `description` now opens with
the job words people type. Each discovery skill is a short pointer: when to use,
one notebook-form snippet, then load `pixeltable`. No catalog was published,
claimed, or submitted.

## Why

A 2026-10-27 catalog baseline (20 ordinary task queries on 9 skill catalogs)
surfaced Pixeltable in **0** of those searches. Direct "pixeltable" search still
finds it. Rankers weight skill `name` and `description` heavily; winners are
task-named skills such as `video-frame-extraction`, `agent-memory`, and
`dataset-curation`.

## New skills

| Folder / `name` | Job | Snippet checked against |
|---|---|---|
| `multimodal-rag` | RAG over PDFs, slide decks, images | `document_splitter` + `add_embedding_index` ([doc-chunk-for-rag](https://docs.pixeltable.com/howto/cookbooks/text/doc-chunk-for-rag), [workflows.md](../skills/pixeltable-skill/references/workflows.md)) |
| `video-search` | Frames + CLIP similarity | `frame_iterator` + CLIP `embedding=` ([video-extract-frames](https://docs.pixeltable.com/howto/cookbooks/video/video-extract-frames), [core-api.md](../skills/pixeltable-skill/references/core-api.md) indexes) |
| `image-similarity-search` | CLIP image / text-to-image search | [search-similar-images](https://docs.pixeltable.com/howto/cookbooks/search/search-similar-images) |
| `audio-transcription-search` | Whisper + transcript embeddings | [audio-transcribe](https://docs.pixeltable.com/howto/cookbooks/audio/audio-transcribe), [audio-transcriptions](https://docs.pixeltable.com/howto/use-cases/audio-transcriptions); `.astype(pxt.String)` before embed per teaching skill |
| `agent-memory` | Memory table + recall query | [pattern-agent-memory](https://docs.pixeltable.com/howto/cookbooks/agents/pattern-agent-memory) |
| `vector-database-alternative` | Embeddings on the table | [embedding-indexes](https://docs.pixeltable.com/platform/embedding-indexes); wording is store-alongside, not "replaces X" |
| `incremental-ml-pipeline` | Computed columns, new rows only | [how-it-works](https://docs.pixeltable.com/overview/how-it-works) "When computed columns run" |
| `dataset-versioning` | History, time travel, snapshot | [version-control-history](https://docs.pixeltable.com/howto/cookbooks/core/version-control-history); `create_snapshot(..., if_exists='ignore')` in `globals.py` |

SDK facts confirmed in `v0.7.21` source:

- `add_embedding_index(..., if_exists='ignore')`
- `create_table` / `create_view` / `create_dir` / `create_snapshot` accept `if_exists='ignore'`
- `similarity(string=...)` (keyword, not positional)
- `frame_iterator(..., fps=1.0)` emits `frame` and `frame_attrs`
- `whisper.transcribe(audio=..., model='base.en')`

## Validation

- `python3 scripts/validate_plugin.py`: OK (9 skills)
- `python3 tests/test_hooks.py` and `python3 tests/test_integrations.py`: OK
- `npx skills add . --list`: 9 skills
- `npx plugins discover .`: `pixeltable` with 9 skills
- `npx skills-ref validate` on each discovery skill: valid
- `npx skills-ref validate skills/pixeltable-skill`: **fails**, pre-existing: directory `pixeltable-skill` vs frontmatter name `pixeltable`. Not changed here (install paths and the skills.sh `@pixeltable` id depend on it)

## What was not done

- No Tessl / Skillstore / agentskill.sh / hf-discover / ClawHub publish
- No live `pxt schema update` of the new snippets in this environment
- No re-run of the 20-query catalog scorecard (that needs a merge, then a crawl)

## How to undo

Close this PR, or revert the merge commit on `main`.
