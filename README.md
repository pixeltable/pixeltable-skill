# Pixeltable Skill

Agent Skill that teaches AI coding assistants to write correct [Pixeltable](https://github.com/pixeltable/pixeltable) code — declarative tables that replace LangChain + pandas + vector databases with one system. Covers 25+ AI providers, multimodal pipelines, tool-calling agents, RAG, and production patterns.

## Install

### Claude Code

```
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable-skill@pixeltable-skill
```

### Cursor, Copilot, Windsurf, and 40+ agents ([npx skills](https://github.com/vercel-labs/skills))

```bash
npx skills add pixeltable/pixeltable-skill
```

### Any LLM (paste URL into context)

- [llms.txt](https://www.pixeltable.com/llms.txt)
- [llms-full.txt](https://docs.pixeltable.com/llms-full.txt)

## What's Inside

```
pixeltable-skill/               # Repo root IS the skill
├── SKILL.md                    # Core: negative prompts, task router, API, agents, pitfalls
├── references/                 # Loaded on demand by Claude Code / Cursor
│   ├── core-api.md             # Tables, querying, views, UDFs, config, data sharing
│   ├── providers.md            # 25+ AI providers with quick-reference table
│   ├── workflows.md            # RAG, video, image, audio, FastAPI, export
│   ├── video-rag-agents.md     # Video + transcript search + agent
│   ├── agents-memory-mcp.md    # Agent with memory, MCP, multi-provider
│   ├── ml-data-pipeline.md     # Ingest, enrich, version, PyTorch export
│   ├── agentic-patterns.md     # 6 patterns + 2 reasoning strategies
│   └── anti-patterns.md        # 15 training-distribution biases with wrong/right code
├── install.sh                  # Installer for Claude Code and Cursor
└── .claude-plugin/             # Claude Code plugin metadata
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All skill content lives at the repo root (`SKILL.md` + `references/`).

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) · [GitHub](https://github.com/pixeltable/pixeltable) · [Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) · [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) · [Discord](https://discord.gg/QPyqFYx2UN)
- Scaffold a project: `uvx pixeltable-new myapp` ([pixeltable-new](https://github.com/pixeltable/pixeltable-new))
- Application templates: `uvx pixeltable-new --template <name> my-app` — `multimodal-rag`, `video-intel`, `agent`, `audio-intel`, `content-pipeline`, `data-lab`

## License

Apache 2.0
