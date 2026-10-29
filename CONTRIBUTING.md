# Contributing to Pixeltable Skill

Thanks for your interest in improving the Pixeltable Skill! This guide covers how to contribute effectively.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/pixeltable-skill.git`
3. Create a feature branch: `git checkout -b my-feature`
4. Make your changes
5. Push to your fork: `git push origin my-feature`
6. Open a Pull Request

## Repository Structure

This repo is an agent **plugin**: one canonical teaching skill, plus thin task-named catalog skills, wrapped with commands, agents, and optional hooks.

```
pixeltable-skill/
├── skills/pixeltable-skill/   # Canonical teaching skill (name: pixeltable)
│   ├── SKILL.md               # Core instructions (<500 lines)
│   └── references/            # Detailed reference (loaded on demand)
├── skills/<job>/SKILL.md      # Thin catalog skills that route to pixeltable
├── commands/                  # Slash commands: /pixeltable:pixeltable-start, index-videos, ...; scaffold and add-provider kept
├── agents/                    # Specialist subagents (Markdown): pipeline-architect, debugger
├── hooks/                     # Optional pure-Python hooks + hooks.json (Claude Code)
├── scripts/validate_plugin.py # Manifest + frontmatter validator
├── install.sh                 # Standalone skill installer
├── plugin.json                # Portable Agent Plugins manifest
├── gemini-extension.json      # Gemini CLI extension + gallery listing
├── GEMINI.md                  # Gemini CLI context (points at skills/)
├── .plugin/ .cursor-plugin/   # Vendor-neutral + Cursor manifests (npx plugins)
├── .claude-plugin/            # Claude Code plugin + marketplace metadata
├── .codex-plugin/             # Codex compatibility manifest
├── .agents/plugins/           # Repo marketplace metadata
└── package.json               # pi.skills (npx skills)
```

Install paths: `npx plugins add pixeltable/pixeltable-skill` (full plugin, Claude Code + Cursor) or `npx skills add pixeltable/pixeltable-skill` (skill only, 40+ agents). Keep both working.

### Conventions
- Plugin identity is `pixeltable` (commands render as `/pixeltable:<name>`); keep root `plugin.json`, `gemini-extension.json`, and all compatibility manifest versions in sync.
- Hooks are **pure Python** (`hooks/*.py`, 3.9+), no Node/Bun/TypeScript. The `hooks.json` command tries `python`, `python3`, then `py -3`, because a python.org install on Windows ships no `python3.exe`.
- Run `python3 scripts/validate_plugin.py` before submitting structural changes.

## What to Contribute

- Fix incorrect API examples
- Add missing patterns for common use cases
- Update provider examples for new Pixeltable releases
- Keep `SKILL.md` concise: detailed content goes in `references/`
- `skills/pixeltable-skill/SKILL.md` should stay under 500 lines
- Catalog skills under `skills/<job>/` stay under 100 lines, use searcher-language descriptions
  (Agent Skills spec: name matches the folder, description <= 1024 chars as a **single-line
  quoted string**; SkillKit treats `description: >` as the literal `>`), include a correct
  Pixeltable snippet, and point at the canonical `pixeltable` skill. Do not duplicate teaching
  content. Do not rename `skills/pixeltable-skill` to match `name: pixeltable` without a
  coordinated move of `pxt skills install`, the public skills index, and the docs/release stub.

## Guidelines

### All Examples Must Be Idempotent

Every example should use `if_exists='ignore'` so it can be safely re-run:

```python
# Correct
pxt.create_table('dir.table', schema, if_exists='ignore')

# Will error on re-run
pxt.create_table('dir.table', schema)
```

### Keep Consistent Terminology

Always "computed column" (not "derived column"), always `string=` keyword in `similarity()`. No em dashes (U+2014): use a period, a colon, or a comma.

### Test Your Changes

Before submitting, verify:

1. YAML frontmatter in `SKILL.md` is valid (name in kebab-case, no XML tags)
2. All code examples are syntactically correct Python
3. Provider examples match the current Pixeltable API
4. Start from `pxt service example --out app.py` (or `pxt schema example --brief`). No `--template` zoo. No starter kit.
5. The install script works for `claude-code`, `cursor-skill`, `codex-skill`, and `antigravity`
6. Plugin layout validates: `python3 scripts/validate_plugin.py`
7. Discovery resolves: `npx plugins discover .` and `npx skills add . --list`
8. Cursor install (from repo): `npx plugins add . -y --target cursor` then restart Agent; verify `/pixeltable:pixeltable-start` (and `/pixeltable:scaffold`) and 5 files under `~/.cursor/skills/pixeltable-skill/references/` (or plugin cache)
9. Codex marketplace install resolves in an isolated `CODEX_HOME`; start a new conversation after installing

### No XML Tags

The Agent Skills specification forbids XML angle brackets in skill files.

## Reporting Issues

- Use [GitHub Issues](https://github.com/pixeltable/pixeltable-skill/issues)
- For Pixeltable library bugs: [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable/issues)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
