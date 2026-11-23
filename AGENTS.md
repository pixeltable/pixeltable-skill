# AGENTS.md

This repo is the Pixeltable Agent Plugin: one skill plus agents, slash commands, and optional hooks. Install via `npx plugins add pixeltable/pixeltable-skill` or `npx skills add pixeltable/pixeltable-skill`.

## Structure

```
skills/pixeltable-skill/  # The skill (name: pixeltable)
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
gemini-extension.json     # Gemini CLI extension + gallery listing
GEMINI.md                 # Gemini CLI context; points at skills/, does not copy them
```

Manifests: root `plugin.json` (portable), `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/`, `.codex-plugin/` (compatibility), `package.json`, and `gemini-extension.json`. Keep plugin name `pixeltable` and versions in sync (`2.15.0`).

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

- Single skill. Do not split it, and do not add a task-named skill under `skills/`, including in a nested folder: `npx skills` discovers every `SKILL.md` there, so each one ships as its own skill. Put job names in the `description` and manifest keywords instead. `validate_plugin.py` enforces this.
- The folder `skills/pixeltable-skill` does not match `name: pixeltable` (Agent Skills spec). Do not rename it until `pxt skills install`, the pixeltable.com skills index, and the docs/release stub can move together.
- `description` in SKILL.md and `commands/*.md` is a single-line quoted string. SkillKit's parser reads folded YAML (`description: >`) as the literal string `>`.
- Hooks are pure Python. No Node/Bun/TypeScript. `hooks.json` finds the interpreter itself (`python`, then `python3`, then `py -3`): a python.org install on Windows has no `python3.exe` (#23).
- SKILL.md teaches the application file. The notebook form is in `pxt guide tables`.
- Start from `pxt init` then `pxt service example --out app.py` (or `pxt schema example --brief`). Then `pxt schema update app.py my_app`. No template zoo. No starter kit.
- `if_exists='ignore'` on notebook `create_*` / `add_*`.
- No LangChain, pandas-as-store, or standalone vector DB patterns.
- Keep SKILL.md under 500 lines (enforced by `validate_plugin.py`).
- Fenced ```python blocks in `skills/`, `agents/`, `commands/`, and `GEMINI.md` must pass the hook's own `error` checks -- the validator imports `CHECKS` and runs them. Quote a wrong form in prose or a traps table, never in a code block.
- `GEMINI.md` is Gemini CLI session context. Point it at `skills/pixeltable-skill/`; do not duplicate `SKILL.md`. Gemini loads `skills/*/SKILL.md` on its own.
- Agent-facing `pxt service update` examples carry `-f`: an agent has no TTY, and without the flag a pending update exits 3.
- Run `python3 scripts/validate_plugin.py` and `python3 tests/test_hooks.py` after any change.
- Re-verify against the current Pixeltable release before a version bump: the record of the last pass is `docs/review-<skill version>.md`.

## Do not

- Add removed APIs (`pixeltable.iterators` and `pxt.Required`, gone in 0.7.25), deprecated `openai.vision`, or positional `.similarity()`
- Point agents at `--template` names, `pixeltable-new`, the starter kit, or a second apply path
- Let manifest versions drift
