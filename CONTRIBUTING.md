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

This repo is an agent **plugin**: one skill (the content core) wrapped with commands, agents, and optional hooks.

```
pixeltable-skill/
├── skills/pixeltable-skill/   # THE skill — do not split
│   ├── SKILL.md               # Core instructions (<500 lines)
│   └── references/            # Detailed reference (loaded on demand)
├── commands/                  # Slash commands (Markdown): /pixeltable:scaffold, add-provider
├── agents/                    # Specialist subagents (Markdown): pipeline-architect, debugger
├── hooks/                     # Optional pure-Python hooks + hooks.json (Claude Code)
├── scripts/validate_plugin.py # Manifest + frontmatter validator
├── install.sh                 # Installer for Claude Code and Cursor
├── .plugin/ .cursor-plugin/   # Vendor-neutral + Cursor manifests (npx plugins)
├── .claude-plugin/            # Claude Code plugin + marketplace metadata
├── .codex-plugin/ .agents/    # Codex + universal-agents metadata
└── package.json               # pi.skills (npx skills)
```

Install paths: `npx plugins add pixeltable/pixeltable-skill` (full plugin, Claude Code + Cursor) or `npx skills add pixeltable/pixeltable-skill` (skill only, 40+ agents). Keep both working.

### Conventions
- Plugin identity is `pixeltable` (commands render as `/pixeltable:<name>`); keep all manifest `name`/`version` fields in sync.
- Hooks are **pure Python** (`python3 "${CLAUDE_PLUGIN_ROOT}/hooks/*.py"`) — no Node/Bun/TypeScript.
- Run `python3 scripts/validate_plugin.py` before submitting structural changes.

## What to Contribute

- Fix incorrect API examples
- Add missing patterns for common use cases
- Update provider examples for new Pixeltable releases
- Keep `SKILL.md` concise — detailed content goes in `references/`
- `SKILL.md` should stay under 500 lines

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

Always "computed column" (not "derived column"), always `string=` keyword in `similarity()`.

### Test Your Changes

Before submitting, verify:

1. YAML frontmatter in `SKILL.md` is valid (name in kebab-case, no XML tags)
2. All code examples are syntactically correct Python
3. Provider examples match the current Pixeltable API
4. Scaffold/template names match the starter-kit repos (`pixeltable-new` `TEMPLATES` and `pixeltable-app-template/templates/`), not a possibly-stale published `uvx pixeltable-new --list`
5. The install script works: `./install.sh --platform claude-code --target /tmp/test` and `./install.sh --platform cursor-skill`
6. Plugin layout validates: `python3 scripts/validate_plugin.py`
7. Discovery resolves: `npx plugins discover .` and `npx skills add . --list`
8. Cursor install (from repo): `npx plugins add . -y --target cursor` then restart Agent; verify `/pixeltable:scaffold` and 9 files under `~/.cursor/skills/pixeltable-skill/references/` (or plugin cache)

### No XML Tags

The Agent Skills specification forbids XML angle brackets in skill files.

## Reporting Issues

- Use [GitHub Issues](https://github.com/pixeltable/pixeltable-skill/issues)
- For Pixeltable library bugs: [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable/issues)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
