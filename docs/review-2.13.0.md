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
  incremental pipelines, dataset versioning). Every SKILL.md `description` is a single-line
  quoted string: SkillKit's parser reads folded YAML (`description: >`) as the literal `>`.
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

## Gotchas verified against Pixeltable 0.7.21 / `master`

Source-checked before writing. Dropped anything that did not match current code
(including the unreproduced `@pxt.query` over a view / base-table index claim).

| Claim | Source |
|---|---|
| `@pxt.udf` in a script's `__main__` / global namespace | `pixeltable/func/udf.py` `make_function`: `defined_in_script` raises; move to a named module. Notebooks get a session-only `__main__.` path. |
| `@pxt.query` in `__main__` | `pixeltable/func/query_template_function.py`: `function_path` is set only when `py_fn.__module__ != '__main__'`. |
| `order_by` on a Python UDF expression | `pixeltable/exec/sql_node.py` `_create_stmt`: `sql_elements.get(e).desc()` when `asc is False`; Python UDFs have `_to_sql` default `None` (`function.py` `__default_to_sql`). Descending is `None.desc()` (`AttributeError`); ascending passes `None` into `stmt.order_by` (no sort). Similarity expressions use `as_order_by_clause` and are fine. |
| OpenAI vision needs the image column | `pixeltable/functions/openai.py` `chat_completions`: serializes only when `image_url` is a `PIL.Image`. A fileurl string or `{'url': t.image}` is skipped. |
| `video_splitter` default `accurate` vs `extract_frame` | `pixeltable/functions/video/iterators.py` default `mode='accurate'`. `pixeltable/utils/av.py` `ffmpeg_segment_cmd` passes `-break_non_keyframes 1`. `extract_frame` seeks to the nearest keyframe; use `mode='fast'` (splits only at keyframes) when extracting frames from clips. |
| After API keys change, `pxt daemon restart` | Already taught in SKILL.md / `references/cli.md`; repeated in Troubleshooting. |

Document types for the RAG starter-menu phrasing (`pxt.Document`): HTML, MD, PDF, XML, TXT, PPTX, DOCX, XLSX (`type_system.py` `DocumentFormat`).

## What was not re-run

The 2.12.0 isolated `pxt schema update` / `pxt service update` matrix, provider-mock RAG app, and
tool-calling chain were not repeated. Do that before a Pixeltable-API teaching bump.

## Folder vs `name` (canonical skill)

The teaching skill lives at `skills/pixeltable-skill/` with frontmatter `name: pixeltable`. That
violates the Agent Skills rule that the directory name must match `name`. This release does **not**
rename the folder: raw GitHub links, the docs/release stub in `pixeltable/pixeltable`, the
pixeltable.com skills index, and `pxt skills install` still point at `skills/pixeltable-skill`.
New catalog skills do match (`skills/video-search` / `name: video-search`, and the rest). A later
migration can add `skills/pixeltable/` (matching `name`), keep `pixeltable-skill` as a shim until
those three consumers switch, then drop the old path.

## Catalog publishing

This review does not submit, claim, or merge listings on skills.sh, SkillsMP, ClawHub, Tessl,
agentskill.sh, Skillstore, SkillHub, SkillKit, or hf-discover.
