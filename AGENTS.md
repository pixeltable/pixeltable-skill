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

Manifests: `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/`, `.codex-plugin/`, `package.json`. Keep name `pixeltable` and versions in sync (`2.6.0`).

## Rules

- Single skill. Do not split it.
- Hooks are pure Python (`python3`). No Node/Bun/TypeScript.
- SKILL.md teaches the application file first. Notebook SDK is an appendix.
- Scaffold is `uvx pixeltable-new myapp` then `pxt schema update app.py agent`. No template zoo.
- `if_exists='ignore'` on notebook `create_*` / `add_*`.
- No LangChain, pandas-as-store, or standalone vector DB patterns.
- Keep SKILL.md under 500 lines.
- Run `python3 scripts/validate_plugin.py` after structural changes.

## Do not

- Add deprecated APIs (`FrameIterator`, `openai.vision`, positional `.similarity()`)
- Point agents at `--template` names or a second apply path
- Let manifest versions drift
