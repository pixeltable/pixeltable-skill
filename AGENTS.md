# AGENTS.md

This repo is the Pixeltable Agent Plugin: one canonical teaching skill, thin task-named catalog skills, agents, slash commands, and optional hooks. Install via `npx plugins add pixeltable/pixeltable-skill` or `npx skills add pixeltable/pixeltable-skill`.

## Structure

```
skills/
├── pixeltable-skill/          # Canonical teaching skill (name: pixeltable)
│   ├── SKILL.md
│   └── references/
└── <job>/SKILL.md             # Thin catalog skills (video-search, agent-memory, ...)

commands/                 # /pixeltable:pixeltable-start, index-videos, rag-over-docs, ...; scaffold and add-provider kept
agents/                   # pipeline-architect, debugger
hooks/
scripts/validate_plugin.py
gemini-extension.json     # Gemini CLI extension + gallery listing
GEMINI.md                 # Gemini CLI context; points at skills/, does not copy them
```

Manifests: root `plugin.json` (portable), `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/`, `.codex-plugin/` (compatibility), `package.json`, and `gemini-extension.json`. Keep plugin name `pixeltable` and versions in sync (`2.13.0`).

## Rules

- One canonical teaching skill: `skills/pixeltable-skill` (frontmatter `name: pixeltable`). Thin task-named catalog skills under `skills/<job>/` are allowed; they route to it and must not duplicate teaching content.
- Hooks are pure Python. No Node/Bun/TypeScript. `hooks.json` finds the interpreter itself (`python`, then `python3`, then `py -3`): a python.org install on Windows has no `python3.exe` (#23).
- SKILL.md teaches the application file first. Notebook SDK is an appendix.
- Start from `pxt init` then `pxt service example --out app.py` (or `pxt schema example --brief`). Then `pxt schema update app.py my_app`. No template zoo. No starter kit.
- `if_exists='ignore'` on notebook `create_*` / `add_*`.
- No LangChain, pandas-as-store, or standalone vector DB patterns.
- Keep SKILL.md under 500 lines (enforced by `validate_plugin.py`).
- Fenced ```python blocks in `skills/`, `agents/`, `commands/`, and `GEMINI.md` must pass the hook's own `error` checks -- the validator imports `CHECKS` and runs them. Quote a wrong form in prose or a traps table, never in a code block.
- `GEMINI.md` is Gemini CLI session context. Point it at `skills/pixeltable-skill/`; do not duplicate `SKILL.md`. Gemini loads `skills/*/SKILL.md` on its own.
- Since Pixeltable 0.7.10, editing a computed column's expression in place is a safe `alter`: `pxt schema update` applies it and keeps the old values until `pxt recompute`. A type change, including `T` to `T | None`, is still `UNSUPPORTED`: rename the column, or drop and re-add it. `--allow-destructive` does not help.
- Agent-facing `pxt service update` examples carry `-f`: an agent has no TTY, and without the flag a pending update exits 3.
- Run `python3 scripts/validate_plugin.py`, `python3 tests/test_hooks.py` and `python3 tests/test_integrations.py` after any change.
- Re-verify against the current Pixeltable release before a version bump: the record of the last pass is `docs/review-<skill version>.md`.

## Do not

- Add deprecated APIs (anything under `pixeltable.iterators`, `openai.vision`, `pxt.Required`, positional `.similarity()`)
- Point agents at `--template` names, `pixeltable-new`, the starter kit, or a second apply path
- Let manifest versions drift
