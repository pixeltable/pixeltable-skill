# Pixeltable Skill

Agent Skill that teaches AI coding assistants to write Pixeltable application files: `TableModel` in `app.py`, then `pxt schema update`, then `pxt service update`.

## Install

Choose the package for your client. This repository packages the skill with
client-specific commands, agents, and optional hooks; each client loads the
components it supports. The standalone skill includes `SKILL.md`, references,
and its ChatGPT/Codex display metadata.

### ChatGPT desktop and Codex

Add this repository as a marketplace, then install the plugin:

```bash
codex plugin marketplace add pixeltable/pixeltable-skill --ref main
codex plugin add pixeltable@pixeltable-skill
```

Restart or start a new conversation after installation. In Codex CLI, `/plugins`
opens the plugin browser. In the ChatGPT desktop app, open **Plugins**, select
the **Pixeltable** marketplace under Personal, and install **Pixeltable**.

The Codex IDE extension does not load plugins. Install the standalone skill for
the IDE:

```bash
npx skills add pixeltable/pixeltable-skill
```

Repository marketplaces are local authoring and team-distribution sources.
They do not publish a plugin to ChatGPT's universal public directory.

### Plugin: Claude Code and Cursor ([npx plugins](https://github.com/vercel-labs/plugins))

```bash
npx plugins add pixeltable/pixeltable-skill
```

### Skill only: Codex IDE, Cursor, Copilot, Windsurf, and other agents ([npx skills](https://github.com/vercel-labs/skills))

```bash
npx skills add pixeltable/pixeltable-skill
```

### Claude Code (manual marketplace)

```
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable@pixeltable-skill
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

The root [`plugin.json`](plugin.json) is the portable Agent Plugins manifest.
`.codex-plugin/plugin.json` remains as a Codex compatibility fallback. The
repository marketplace is `.agents/plugins/marketplace.json`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 scripts/validate_plugin.py` after structural changes.

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) · [GitHub](https://github.com/pixeltable/pixeltable) · [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) · [Discord](https://discord.gg/QPyqFYx2UN)
- Start: `pxt init` then `pxt service example --out app.py` then `pxt schema update app.py my_app` then `pxt service update app.py my_app`.

## License

Apache 2.0
