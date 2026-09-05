# AGENTS.md

This repo is the Pixeltable Agent Plugin: one skill plus agents, slash commands, and optional hooks. Install via `npx plugins add pixeltable/pixeltable-skill` or `npx skills add pixeltable/pixeltable-skill`.

## Structure

```
skills/pixeltable-skill/
├── SKILL.md
└── references/
    ├── core-api.md
    ├── cli.md
    ├── providers.md
    ├── workflows.md
    └── anti-patterns.md

commands/                 # /pixeltable:scaffold, add-provider
agents/                   # pipeline-architect, debugger
hooks/
scripts/validate_plugin.py
```

Manifests: `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/`, `.codex-plugin/`, `package.json`. Keep name `pixeltable` and versions in sync (`2.8.0`).

## Rules

- Single skill. Do not split it.
- Hooks are pure Python (`python3`). No Node/Bun/TypeScript.
- SKILL.md teaches the application file first. Notebook SDK is an appendix.
- Start from `pxt init` then `pxt service example --out app.py` (or `pxt schema example --brief`). Then `pxt schema update app.py my_app`. No template zoo. No starter kit.
- `if_exists='ignore'` on notebook `create_*` / `add_*`.
- No LangChain, pandas-as-store, or standalone vector DB patterns.
- Keep SKILL.md under 500 lines (enforced by `validate_plugin.py`).
- Fenced ```python blocks in `skills/`, `agents/` and `commands/` must pass the hook's own `error` checks -- the validator imports `CHECKS` and runs them. Quote a wrong form in prose or a traps table, never in a code block.
- Changing a computed column's expression in place is `UNSUPPORTED`. Rename the column, or drop and re-add it. `--allow-destructive` does not help.
- Run `python3 scripts/validate_plugin.py` and `python3 tests/test_hooks.py` after any change.

## Do not

- Add deprecated APIs (anything under `pixeltable.iterators`, `openai.vision`, `pxt.Required`, positional `.similarity()`)
- Point agents at `--template` names, `pixeltable-new`, the starter kit, or a second apply path
- Let manifest versions drift
