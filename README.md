# Pixeltable Skill

Agent Skill that teaches AI coding assistants to write correct [Pixeltable](https://github.com/pixeltable/pixeltable) code — 25+ AI providers, multimodal pipelines, tool-calling agents, RAG, and production patterns.

Implements the [Agent Skills specification](https://agentskills.io/specification).

## Install

### Claude Code

```bash
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable-skill@pixeltable-skill
```

### Cursor

```bash
git clone https://github.com/pixeltable/pixeltable-skill.git
cp -r pixeltable-skill/skills/pixeltable-skill ~/.cursor/skills/pixeltable-skill
```

### Any project

```bash
curl -fsSL https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main/install.sh | bash -s -- --platform claude-code
```

### Other platforms (Windsurf, Cline, Copilot, etc.)

Copy `skills/pixeltable-skill/SKILL.md` into your platform's config location. It's self-contained at 440 lines. For full reference, point agents to `https://docs.pixeltable.com/llms-full.txt`.

## What's Inside

```
skills/pixeltable-skill/
├── SKILL.md                    # Core: task router, API, agents, pitfalls (440 lines)
└── references/                 # Loaded on demand by Claude Code / Cursor
    ├── core-api.md             # Tables, querying, views, UDFs, config, data sharing
    ├── providers.md            # 25+ AI providers with quick-reference table
    ├── workflows.md            # RAG, video, image, audio, FastAPI, export
    ├── video-rag-agents.md     # Video + transcript search + agent
    ├── agents-memory-mcp.md    # Agent with memory, MCP, multi-provider
    ├── ml-data-pipeline.md     # Ingest, enrich, version, PyTorch export
    └── agentic-patterns.md     # 6 patterns + 2 reasoning strategies
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All content lives in `skills/pixeltable-skill/`.

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) · [GitHub](https://github.com/pixeltable/pixeltable) · [Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) · [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) · [Discord](https://discord.gg/QPyqFYx2UN)
- LLM docs: [llms.txt](https://www.pixeltable.com/llms.txt) · [llms-full.txt](https://docs.pixeltable.com/llms-full.txt)

## License

Apache 2.0
