# Pixeltable Skill

Agent Skill that teaches AI coding assistants to write correct [Pixeltable](https://github.com/pixeltable/pixeltable) code — declarative tables that replace LangChain + pandas + vector databases with one system. Covers 25+ AI providers, multimodal pipelines, tool-calling agents, RAG, and production patterns.

## Install

**Which path?** Use `npx plugins add` for the full plugin (skill + agents + slash commands) on Claude Code and Cursor. Use `npx skills add` to install just the skill content across 40+ agents (Copilot, Windsurf, Gemini, etc.) or in CI. Both work; they're complementary.

### Plugin — Claude Code & Cursor ([npx plugins](https://github.com/vercel-labs/plugins))

```bash
npx plugins add pixeltable/pixeltable-skill
```

### Skill only — Cursor, Copilot, Windsurf, and 40+ agents ([npx skills](https://github.com/vercel-labs/skills))

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
skills/pixeltable-skill/        # The skill (content core)
├── SKILL.md                    # Core: negative prompts, task router, API, agents, pitfalls
└── references/                 # Loaded on demand by Claude Code / Cursor
    ├── core-api.md             # Tables, querying, views, UDFs, config, data sharing
    ├── cli.md                  # pxt CLI — inspect, debug, serve, deploy
    ├── providers.md            # 25+ AI providers with quick-reference table
    ├── workflows.md            # RAG, video, image, audio, FastAPI, export
    ├── video-rag-agents.md     # Video + transcript search + agent
    ├── agents-memory-mcp.md    # Agent with memory, MCP, multi-provider
    ├── ml-data-pipeline.md     # Ingest, enrich, version, PyTorch export
    ├── agentic-patterns.md     # 6 patterns + 2 reasoning strategies
    └── anti-patterns.md        # 15 training-distribution biases with wrong/right code

commands/                       # Slash commands: /pixeltable:scaffold, add-provider
agents/                         # Specialists: pipeline-architect, debugger
hooks/                          # Optional pure-Python hooks (Claude Code): orientation + anti-pattern validation
```

The plugin install (`npx plugins add`) bundles the skill, commands, agents, and hooks. The skill install (`npx skills add`) delivers just the skill content. Hooks run on Claude Code; Cursor honors session-start context only.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The skill content lives in `skills/pixeltable-skill/`; run `python3 scripts/validate_plugin.py` after structural changes.

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) · [GitHub](https://github.com/pixeltable/pixeltable) · [Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) · [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) · [Discord](https://discord.gg/QPyqFYx2UN)
- Scaffold a project: `uvx pixeltable-new myapp` ([pixeltable-new](https://github.com/pixeltable/pixeltable-new))
- Application templates: `uvx pixeltable-new --template <name> my-app` — `knowledge-base`, `chat-agent`, `audio-transcription`, `video-search`, `media-indexing`, `image-dataset`, `full-stack-showcase`
- Video frame search: `--template video-search` → `uv sync` → `python schema.py` → `pxt serve videointel` (see `/pixeltable:scaffold`)

## License

Apache 2.0
