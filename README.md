# Pixeltable Skill

Agent Skill that teaches AI coding assistants to write Pixeltable application files: `TableModel` in `app.py`, then `pxt schema update`, then `pxt service update`.

## Install

**Which path?** Use `npx plugins add` for the full plugin (skill + agents + slash commands) on Claude Code and Cursor. Use `npx skills add` to install just the skill content across 40+ agents (Copilot, Windsurf, Gemini, etc.) or in CI. Both work; they're complementary.

### Plugin: Claude Code and Cursor ([npx plugins](https://github.com/vercel-labs/plugins))

```bash
npx plugins add pixeltable/pixeltable-skill
```

### Skill only: Cursor, Copilot, Windsurf, and 40+ agents ([npx skills](https://github.com/vercel-labs/skills))

```bash
npx skills add pixeltable/pixeltable-skill
```

### Claude Code (manual marketplace)

```
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable@pixeltable-skill
```

### Codex

```bash
codex plugin marketplace add pixeltable/pixeltable-skill --ref main
codex plugin add pixeltable@pixeltable-skill
```

### Any LLM (paste URL into context)

- [llms.txt](https://www.pixeltable.com/llms.txt)
- [llms-full.txt](https://docs.pixeltable.com/llms-full.txt)

## What's Inside

```
skills/pixeltable-skill/
├── SKILL.md                    # Contract: app.py, schema update, service update
└── references/
    ├── core-api.md             # Tables, querying, views, UDFs, config
    ├── cli.md                  # pxt CLI
    ├── providers.md            # Import and output shape
    ├── workflows.md            # FastAPIRouter
    └── anti-patterns.md        # Wrong/right stack
```

The plugin install (`npx plugins add`) bundles the skill, commands, agents, and hooks. The skill install (`npx skills add`) delivers just the skill content.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 scripts/validate_plugin.py` after structural changes.

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) · [GitHub](https://github.com/pixeltable/pixeltable) · [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) · [Discord](https://discord.gg/QPyqFYx2UN)
- Start: `pxt init` then `pxt service example --out app.py` then `pxt schema update app.py my_app` then `pxt service update app.py my_app`. Loop: Declare, Experiment, Serve.

## License

Apache 2.0
