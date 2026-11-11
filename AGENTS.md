# AGENTS.md

This repo is the Pixeltable Agent Plugin: one skill plus agents, slash commands, and optional hooks. Install via `npx plugins add pixeltable/pixeltable-skill` or `npx skills add pixeltable/pixeltable-skill`.

## Structure

```
skills/pixeltable-skill/
├── SKILL.md
└── references/
    ├── anti-patterns.md
    ├── conventional-design.md
    ├── schema-design.md
    ├── expressions.md
    └── safe-changes.md

commands/                 # /pixeltable:scaffold, add-provider
agents/                   # pipeline-architect, debugger
hooks/
scripts/validate_plugin.py
```

Manifests: root `plugin.json` (portable), `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/`, `.codex-plugin/` (compatibility), and `package.json`. Keep name `pixeltable` and versions in sync (`2.12.0`).

## Architecture: judgment here, release behavior in core

The skill teaches what does not change between Pixeltable releases. How a release behaves is documented in the
pixeltable repository, in `pixeltable/agent_guides/`: one guide per functional area, shipped in the wheel of that
release, updated in the same pull request as the behavior, and tested against the code. Its README states the
rules for the guides.

Belongs in the skill:

- The mental model: what Pixeltable is, and how it differs from a database with application code around it.
- The mapping from a conventional design (workers, queues, status columns, metrics jobs) to tables, computed
  columns, views and routes.
- Schema design, safe changes to a project that has data, and the stacks and habits to avoid.
- The workflow: `pxt init`, the application file, `pxt schema update`, `pxt service update`.
- Where to find the facts: the agent guide of each area, `pxt COMMAND --help`, and the docstrings.

Belongs in the agent guide of its area, not here:

- What an API accepts, returns, defaults to or raises; flags, exit codes, error codes and limits.
- The known issues of a release and their workarounds.
- Anything tied to a version number, such as "0.7.22+".

The test for each sentence: if a Pixeltable release can make it false, it belongs in a guide. The skill mentions
an API only to say which construct does a job, never to describe how that API behaves. A review of a change to the
skill applies this test to every added sentence, and moves a fact to its guide, through a pull request in the
pixeltable repository, instead of accepting it here.

## Rules

- Single skill. Do not split it.
- Hooks are pure Python. No Node/Bun/TypeScript. `hooks.json` finds the interpreter itself (`python`, then `python3`, then `py -3`): a python.org install on Windows has no `python3.exe` (#23).
- SKILL.md teaches the application file. The notebook form is in `pxt guide tables`.
- Start from `pxt init` then `pxt service example --out app.py` (or `pxt schema example --brief`). Then `pxt schema update app.py my_app`. No template zoo. No starter kit.
- `if_exists='ignore'` on notebook `create_*` / `add_*`.
- No LangChain, pandas-as-store, or standalone vector DB patterns.
- Keep SKILL.md under 500 lines (enforced by `validate_plugin.py`).
- Fenced ```python blocks in `skills/`, `agents/` and `commands/` must pass the hook's own `error` checks -- the validator imports `CHECKS` and runs them. Quote a wrong form in prose or a traps table, never in a code block.
- Agent-facing `pxt service update` examples carry `-f`: an agent has no TTY, and without the flag a pending update exits 3.
- Run `python3 scripts/validate_plugin.py`, `python3 tests/test_hooks.py` and `python3 tests/test_integrations.py` after any change.
- Re-verify against the current Pixeltable release before a version bump: the record of the last pass is `docs/review-<skill version>.md`.

## Do not

- Add deprecated APIs (anything under `pixeltable.iterators`, `openai.vision`, `pxt.Required`, positional `.similarity()`)
- Point agents at `--template` names, `pixeltable-new`, the starter kit, or a second apply path
- Let manifest versions drift
