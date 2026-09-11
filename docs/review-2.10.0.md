# Pixeltable skill 2.10.0 review

Reviewed 2026-09-10 against upstream skill commit
`318c1b79034379243f024e12f70b0fdec0df39b0`, Pixeltable 0.7.7, the current
website agent documents, and the current ChatGPT/Codex plugin documentation.

## Verdict

The 2.10.0 candidate is ready for review. It preserves the repository's
single-skill, application-file-first workflow and corrects every reproduced
Pixeltable API error found in 2.9.1. The portable manifest validates against
the Agent Plugins 1.0 schema, Codex installs the full plugin from the local
repository marketplace, and the standalone installer places the skill and its
OpenAI display metadata in the shared `.agents/skills` location.

No live provider call, Pixeltable Cloud deployment, ChatGPT desktop UI install,
or universal-directory publication was performed. Those surfaces are source-
and contract-reviewed only.

## Reproducible baseline

| Item | Evidence |
|---|---|
| Pixeltable skill | `318c1b79034379243f024e12f70b0fdec0df39b0` (2.9.1) |
| Pixeltable package | 0.7.7; Python `>=3.11`; wheel `pixeltable-0.7.7-py3-none-any.whl` |
| Wheel SHA-256 | `0642d78d3f90766cc6cec60c587b9e19682df1241dde8000d8e1856a2838610f` |
| Pixeltable tag | `v0.7.7`, `8d14e6c88d3dcd749d71ef5799447454470f68f9` |
| `get-started.md` | SHA-256 `7d03873526a31940552adbd4ea3b1be79b308d058a6d4b64d437ac97d14e4578` |
| `llms.txt` | SHA-256 `7b326e37ac26468d1553a86fafe03680a61ddd0216e44c46f1931e168e3b72d8` |
| Codex CLI used | 0.153.4 |

The 0.7.7 release adds `pxt service logs`, `pxt db logs`, and a managed Cloud
home bucket as the default media destination. The skill now covers all three.
The remaining API probes from 0.7.6 also pass unchanged on 0.7.7.

## Findings and remediation

### P1: no current portable ChatGPT/Codex manifest

2.9.1 exposed only `.codex-plugin/plugin.json`. Current Agent Plugins use a
root `plugin.json`; the older location is a compatibility fallback. The new
root manifest uses the 1.0 schema and places OpenAI-only UI metadata under
`extensions.com.openai`. The repository validator enforces schema identity,
version parity, and equality with the compatibility metadata.

Verification: JSON Schema validation passed, and an isolated `CODEX_HOME`
installed `pixeltable@pixeltable-skill` as version 2.10.0.

### P1: guidance contained executable API errors

The review reproduced and corrected these issues against the installed 0.7.7
wheel:

- `FastAPIRouter.add_update_route()` does not accept `match_columns`;
  `add_delete_route()` does.
- `list_iterator` requires typed Json. Scalar lists use keyword arguments;
  its positional form accepts a typed list of dictionaries.
- OpenAI Responses, Gemini generation, Ollama generate, and Runway image
  extraction had incorrect or overgeneralized return guidance.
- `pxt.move()` moves a table or directory; `Table.rename_column()` renames a
  column.
- Custom embedding UDFs must return a fixed-length one-dimensional array.
- `concat_videos_agg` is also an ordered aggregate.
- Cloud database secrets belong under `secrets`, and noninteractive database
  updates support `-f`.

Verification: import/signature probes passed for every listed API using
`pixeltable[serve]==0.7.7` on Python 3.11.

### P1: hooks missed Codex edits and produced avoidable false positives

The edit hook understood only Claude-style Write/Edit payloads and matched
deprecated names inside comments, strings, and unrelated source files. It now
accepts Codex's canonical `apply_patch` payload, reads the resulting Python or
notebook file, ignores comments and strings, bounds file reads, and gates broad
checks on actual Pixeltable code. Multiline deprecated imports are covered.

Verification: 23 hook tests pass, including a real temporary-file
`apply_patch` case and false-positive regressions.

### P2: ChatGPT/Codex installation was incomplete

The README now gives marketplace installation for ChatGPT desktop and Codex,
explains the `/plugins` browser, distinguishes the Codex IDE standalone-skill
path, and states that a repository marketplace is not publication to the
universal directory. The skill now includes `agents/openai.yaml`. The direct
installer supports `codex-skill` and copies that metadata.

Verification: local Codex marketplace add/install/list passed in an isolated
home; direct standalone installation produced `SKILL.md`, five references,
and `agents/openai.yaml`; `npx plugins` and `npx skills` discovery both passed.

### P2: release checks did not cover the new contract

CI now uses read-only permissions, a job timeout, commit-pinned GitHub Actions,
and a standalone Codex install smoke test. Repository validation now checks the
portable manifest, marketplace root, UI metadata, and every versioned manifest.

## Website findings kept separate

`get-started.md` is aligned with the application-file workflow and explicitly
directs agents to `pxt service example`, not `pixeltable-new`. `llms.txt` later
advertises `pixeltable-new` and starter-kit recipes despite also giving the
opposite instruction. The skill intentionally follows its repository contract
and does not copy that website contradiction. Neither website document yet
explains the full ChatGPT desktop/Codex plugin marketplace route; the repository
README now does.

## Verification commands

```bash
python3 scripts/validate_plugin.py
python3 tests/test_hooks.py
ruff check hooks/ scripts/ tests/
bash -n install.sh
npx -y plugins@latest discover .
npx -y skills@latest add . --list

temp_codex="$(mktemp -d)"
CODEX_HOME="$temp_codex" codex plugin marketplace add . --json
CODEX_HOME="$temp_codex" codex plugin add pixeltable@pixeltable-skill --json
CODEX_HOME="$temp_codex" codex plugin list --json
```

Observed results: 191 repository checks passed, 23 hook tests passed, Ruff
passed, both `npx` discovery paths passed, the portable manifest passed its
published JSON Schema, and isolated Codex installation reported version 2.10.0.
With Pixeltable 0.7.7, `pxt init` followed by `pxt service example --out app.py`,
`pxt schema check app.py`, and `pxt service check app.py` also passed.

## Release boundary

Before publishing 2.10.0, review the branch diff and run the same checks on
Linux CI. Universal-directory publication and a ChatGPT desktop installation
remain separate release operations. Cloud and provider claims should remain
labeled untested until credentials and a controlled live-test budget are
available.
