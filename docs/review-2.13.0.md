# Pixeltable skill 2.13.0 review

Reviewed 2026-10-27. This bump is a **catalog and command discoverability** release. It does not
re-run the full 2.12.0 application-file trial against a new Pixeltable wheel.

## Verdict

Ship the task-named catalog skills and job-named commands. New snippets match current Pixeltable
docs and the `release` branch of `pixeltable/pixeltable` as of 2026-10-27. Core teaching claims in
`skills/pixeltable-skill/` still rest on [review-2.12.0.md](review-2.12.0.md) (Pixeltable 0.7.11).

## What this version adds

- Rewritten canonical `description` that leads with searcher language (multimodal RAG, video
  search, image similarity, embeddings stored with data, audio transcription search, agent memory,
  incremental pipelines, dataset versioning).
- Eight thin catalog skills under `skills/`: `multimodal-rag`, `video-search`,
  `image-similarity-search`, `audio-transcription-search`, `agent-memory`,
  `vector-database-alternative`, `incremental-ml-pipeline`, `dataset-versioning`.
- Job-named commands; `/pixeltable:scaffold` and `/pixeltable:add-provider` kept.

## Snippet sources (new catalog skills and commands)

Checked against https://docs.pixeltable.com (llms.txt, 2026-10-27) and GitHub
`pixeltable/pixeltable` `release`:

| Skill | Docs / source |
|---|---|
| multimodal-rag | `howto/cookbooks/agents/pattern-rag-pipeline`, `references/workflows.md` (`document_splitter`, `EmbeddingIndex`, `similarity(string=)`) |
| video-search | `howto/cookbooks/video/video-extract-frames`, `overview/how-it-works`, `platform/embedding-indexes` (`frame_iterator`, CLIP `embedding=`) |
| image-similarity-search | `howto/cookbooks/search/search-similar-images` (CLIP `clip.using(model_id=...)`) |
| audio-transcription-search | `howto/cookbooks/audio/audio-transcribe`, `howto/use-cases/audio-transcriptions`; `pixeltable.functions.whisper.transcribe(audio, *, model=)` |
| agent-memory | `howto/cookbooks/agents/pattern-agent-memory` |
| vector-database-alternative | `platform/embedding-indexes` |
| incremental-ml-pipeline | `overview/how-it-works` (insert computes new rows only) |
| dataset-versioning | `platform/version-control`, `howto/cookbooks/core/version-control-history`; `create_snapshot(..., if_exists=)`, `Table.history` / `revert`, `get_table('path:N')` |

Pixeltable changelog latest listed: **0.7.21** (2026-10-26). No snippet here depends on an API
removed between 0.7.11 and 0.7.21.

## What was not re-run

The 2.12.0 isolated `pxt schema update` / `pxt service update` matrix, provider-mock RAG app, and
tool-calling chain were not repeated. Do that before a Pixeltable-API teaching bump.

## Catalog publishing

This review does not submit, claim, or merge listings on skills.sh, SkillsMP, ClawHub, Tessl,
agentskill.sh, Skillstore, SkillHub, SkillKit, or hf-discover.
