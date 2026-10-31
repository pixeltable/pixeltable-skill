# Pixeltable skill 2.14.0 review

Reviewed 2026-10-30. This bump is a **structure** release: it returns the repo to one skill and
removes the framework integrations. It changes no teaching claim. Core claims still rest on
[review-2.12.0.md](review-2.12.0.md) (Pixeltable 0.7.11); #51 added the 0.7.22 query shapes.

## Verdict

Ship one skill, `skills/pixeltable-skill` (`name: pixeltable`), with the commands `scaffold` and
`add-provider`.

## What this version removes

- The eight catalog skills from 2.13.0: `multimodal-rag`, `video-search`,
  `image-similarity-search`, `audio-transcription-search`, `agent-memory`,
  `vector-database-alternative`, `incremental-ml-pipeline`, `dataset-versioning`.
  Installers copy every `skills/*/SKILL.md`, so each one shipped as a separate skill that repeated
  a snippet from the main skill. Nothing measured whether they improved discovery. The job names
  stay in the main skill's `description` and in the manifest keywords.
- The job-named commands that loaded those skills: `pixeltable-start`, `index-videos`,
  `search-images`, `rag-over-docs`, `add-agent-memory`, `transcribe-and-search-audio`,
  `store-embeddings`, `incremental-pipeline`, `version-dataset`.
- `integrations/` (Agno and CrewAI toolkits) and `tests/test_integrations.py`. No skill, command,
  agent, manifest, or README pointed at them.

## What this version changes

- `scripts/validate_plugin.py` fails if `skills/` holds anything but `pixeltable-skill/SKILL.md`,
  and requires single-line quoted `description` in `commands/*.md` as well as SKILL.md.
- `scaffold` and `add-provider` use single-line quoted descriptions; `scaffold` no longer points at
  `pixeltable-start`.
- `install.sh` installs only the skill. CI asserts the Codex install leaves one skill folder and no
  longer runs or lints the integrations.

## Verification

```bash
python3 scripts/validate_plugin.py       # OK: 264 checks passed (1 skill(s))
python3 tests/test_hooks.py              # 30 tests OK
ruff check hooks/ scripts/ tests/        # ruff 0.16.8, all checks passed
bash -n install.sh
./install.sh --platform <p>              # claude-code, cursor-skill, codex-skill, antigravity: one folder each
npx skills add . --list                  # Found 1 skill: pixeltable
npx plugins discover .                   # pixeltable: 1 skill, 2 cmds, 2 agents, hooks
claude plugin validate .                 # marketplace and plugin manifests pass
```

A scratch copy with an added `skills/video-search/SKILL.md` and a folded `scaffold` description
fails the validator on both.

## What was not re-run

The 2.12.0 isolated `pxt schema update` / `pxt service update` matrix. No teaching text changed.

## Existing installs

`npx skills` and `install.sh` do not delete skills they installed earlier. A user who installed
2.13.0 keeps the eight catalog folders until they remove them. Each one routes to `pixeltable`,
so they still work.
