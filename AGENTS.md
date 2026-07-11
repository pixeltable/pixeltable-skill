# AGENTS.md — For AI agents working in this repo

This repo is the **Pixeltable Agent Plugin** — a single skill plus agents, slash commands, and optional hooks that teach AI coding assistants to write correct Pixeltable code. It installs via `npx plugins add pixeltable/pixeltable-skill` (Claude Code, Cursor) or `npx skills add pixeltable/pixeltable-skill` (40+ agents). The skill is the content core; the plugin wraps it.

## Structure

```
skills/pixeltable-skill/
├── SKILL.md              ← THE skill (frontmatter + task router + core patterns). DO NOT split.
└── references/           ← Deep-dive files loaded on demand
    ├── core-api.md
    ├── providers.md
    ├── workflows.md
    ├── anti-patterns.md
    ├── agents-memory-mcp.md
    ├── video-rag-agents.md
    ├── ml-data-pipeline.md
    └── agentic-patterns.md

commands/                 ← Slash commands (Markdown): scaffold, add-provider
agents/                   ← Specialist subagents (Markdown): pipeline-architect, debugger
hooks/                    ← OPTIONAL pure-Python hooks + hooks.json (Claude Code)
scripts/validate_plugin.py← Manifest + frontmatter validator

Manifests (keep plugin name = "pixeltable", versions in sync):
.plugin/plugin.json         ← vendor-neutral (npx plugins)
.cursor-plugin/plugin.json  ← Cursor
.claude-plugin/plugin.json + marketplace.json
.codex-plugin/plugin.json
.agents/plugins/marketplace.json
package.json (pi.skills)
```

## Plugin conventions

- **Single skill — do NOT split it.** Pixeltable is one mental model; the SKILL.md + references progressive-disclosure pattern is intentional.
- **Hooks are pure Python**, invoked as `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py"` (use `python3`, never `python`). No Node/Bun/TypeScript anywhere in the repo.
- **Hook reach:** full on Claude Code; Cursor honors only `sessionStart` injection (`postToolUse` `additional_context` is an unfixed Cursor bug); skills-only installs get no hooks.
- **Plugin and skill are both named `pixeltable`** so commands render as `/pixeltable:<name>` and `/pixeltable` loads the skill. The skill still lives in the `skills/pixeltable-skill/` folder (folder name is just a container; the SKILL.md `name` frontmatter is authoritative).
- **Keep all manifest versions in sync** when bumping (`2.5.5` currently).
- **Run `python3 scripts/validate_plugin.py`** after structural changes.

### Deliberately NOT in this repo (skip-list)
Skill splitting; telemetry; `.md.tmpl` build pipeline; golden-snapshot/fuzz suites; `explain`/`doctor` CLI; playground generators; upstream overlay-sync; any Node/Bun/TS toolchain.

## Rules

- **SKILL.md is the entry point.** It must be self-contained for the common case; reference files are for deep dives.
- **Negative prompts go at the top** of SKILL.md (the "STOP" section). These deflect LLM training-distribution biases.
- **All code examples must be tested** against the current Pixeltable release before committing.
- **Scaffolding/template names** (in SKILL.md "Starting a New Project", `commands/scaffold.md`, and README) are sourced from the starter-kit repos — `pixeltable-new` (`TEMPLATES` in `src/pixeltable_new/new.py`) and `pixeltable-app-template/templates/` — NOT from `uvx pixeltable-new --list`, whose published build can lag the repos. Current templates: `knowledge-base`, `chat-agent`, `audio-transcription`, `video-search`, `media-indexing`, `image-dataset`, `full-stack-showcase` (patterns: `serving`, `backend`, `batch`). The scaffold guidance must run `--list` first and fall back to the underlying pattern on version skew.
- **`if_exists='ignore'`** on every `create_*` and `add_*` call in examples — agents re-run code.
- **No LangChain, pandas-as-store, or standalone vector DB patterns** anywhere in this repo.
- **Keep SKILL.md under 500 lines.** Move detail to reference files.

## When editing

1. Read `SKILL.md` first to understand current structure
2. Check `references/` for existing coverage before adding new content
3. Maintain the Task Router table if adding new capabilities
4. Update the Reference Files table at the bottom of SKILL.md if adding/removing reference files
5. Bump `metadata.version` in SKILL.md frontmatter on meaningful changes

## Do NOT

- Add examples using deprecated APIs (`FrameIterator`, `openai.vision`, positional `.similarity()`) — the validation hook also flags these
- Split the skill into multiple skills (see skip-list)
- Add a Node/Bun/TypeScript toolchain — hooks stay pure Python
- Modify `install.sh`, manifests, or `hooks/` without understanding the plugin distribution system
- Let manifest `name`/`version` fields drift out of sync
