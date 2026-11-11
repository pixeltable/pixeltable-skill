# Pixeltable skill 2.14.0 review

Reviewed 2026-10-30. This bump is a **structure** release: it returns the repo to one skill and
removes the framework integrations. The skill body is unchanged. Versioning that lived only in
the deleted `dataset-versioning` skill is now a section of `references/core-api.md`, checked
against `create_snapshot`, `get_table('table:N')`, and `revert` in the Pixeltable source.
Core claims still rest on [review-2.12.0.md](review-2.12.0.md) (Pixeltable 0.7.11); #51 added
the 0.7.22 query shapes.

## Verdict

Ship one skill, `skills/pixeltable-skill` (`name: pixeltable`), with the commands `scaffold` and
`add-provider`.

## What this version removes

- The eight catalog skills from 2.13.0: `multimodal-rag`, `video-search`,
  `image-similarity-search`, `audio-transcription-search`, `agent-memory`,
  `vector-database-alternative`, `incremental-ml-pipeline`, `dataset-versioning`.
  `npx skills` discovers every `SKILL.md` under `skills/`, so each one shipped as a separate skill
  that repeated a snippet from the main skill. Nothing measured whether they improved discovery. The job names
  stay in the main skill's `description` and in the manifest keywords.
- The job-named commands that loaded those skills: `pixeltable-start`, `index-videos`,
  `search-images`, `rag-over-docs`, `add-agent-memory`, `transcribe-and-search-audio`,
  `store-embeddings`, `incremental-pipeline`, `version-dataset`.
- `integrations/` (Agno and CrewAI toolkits) and `tests/test_integrations.py`. No skill, command,
  agent, manifest, or README pointed at them.

## What this version changes

- `scripts/validate_plugin.py` fails if `skills/` holds any `SKILL.md` other than
  `pixeltable-skill/SKILL.md`, including one in a nested folder, and requires single-line quoted
  `description` in `commands/*.md` as well as SKILL.md.
- `references/core-api.md` keeps the versioning facts from the deleted `dataset-versioning`
  skill: a `table:N` handle, `pxt.create_snapshot`, and revert's refusal at version 0 or while a
  snapshot still references the current version. SKILL.md points at that section.
- `scaffold` and `add-provider` use single-line quoted descriptions; `scaffold` no longer points at
  `pixeltable-start`.
- `install.sh` installs only the skill. When a sibling folder's SKILL.md still says it is a thin
  catalog skill, it prints that name and leaves the directory in place. CI asserts the Codex
  install leaves one skill folder and no longer runs or lints the integrations.

## Verification

```bash
python3 scripts/validate_plugin.py       # OK: 264 checks passed (1 skill(s))
python3 tests/test_validate_plugin.py    # 2 tests OK
python3 tests/test_hooks.py              # 30 tests OK
ruff check hooks/ scripts/ tests/        # ruff 0.16.8, all checks passed
bash -n install.sh
./install.sh --platform <p>              # claude-code, cursor-skill, codex-skill, antigravity: one folder each
npx skills add . --list                  # Found 1 skill: pixeltable
npx plugins discover .                   # pixeltable: 1 skill, 2 cmds, 2 agents, hooks
claude plugin validate .                 # marketplace and plugin manifests pass
```

A scratch copy with an added `skills/video-search/SKILL.md`, a nested
`skills/nested/video-search/SKILL.md`, and a folded `scaffold` description fails the validator
on each.

## What was not re-run

The 2.12.0 isolated `pxt schema update` / `pxt service update` matrix. The versioning sentences
were checked against the Pixeltable source, not by running them.

## Existing installs

`npx skills` and `install.sh` do not delete skills they installed earlier. A user who installed
2.13.0 keeps the eight catalog folders until they remove them. Each one routes to `pixeltable`,
so they still work.
