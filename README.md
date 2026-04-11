# Pixeltable Skill

Build multimodal AI applications with [Pixeltable](https://github.com/pixeltable/pixeltable) — declarative tables, computed columns, embedding indexes, similarity search, UDFs, and 25+ AI provider integrations.

---

## Why

AI coding assistants write incorrect Pixeltable code because their training data is stale or sparse. This skill gives any assistant deep, current expertise: correct API signatures, idempotent patterns, multimodal workflows, and production-ready templates — so generated code runs on the first try.

- **Correct code** — API signatures, import paths, and parameter names verified against the latest Pixeltable release.
- **Idempotent patterns** — Every example uses `if_exists='ignore'` for safe re-runs.
- **Progressive disclosure** — Concise core instructions with detailed reference files loaded only when needed.
- **25+ AI providers** — OpenAI, Anthropic, Gemini, Hugging Face, Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, Bedrock, Jina, BFL FLUX, RunwayML, fal.ai, Reve, Fabric, llama.cpp, and more.
- **End-to-end recipes** — RAG, video RAG agent, agent with memory and MCP, agentic patterns, ML data pipelines, FastAPI apps.

---

## Install

### Claude Code (recommended)

```bash
# As a plugin
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable-skill@pixeltable-skill
```

### Cursor (skill mode)

```bash
# Copy the skill directory
git clone https://github.com/pixeltable/pixeltable-skill.git
cp -r pixeltable-skill/skills/pixeltable-skill ~/.cursor/skills/pixeltable-skill
```

### Any project (Claude Code / Cursor / other)

```bash
# Install into current project
git clone https://github.com/pixeltable/pixeltable-skill.git
cp -r pixeltable-skill/skills/pixeltable-skill .claude/skills/pixeltable-skill
```

### One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main/install.sh | bash -s -- --platform claude-code
```

---

## Using with Other Platforms

The canonical skill lives in `skills/pixeltable-skill/` — a `SKILL.md` plus 7 reference files that use progressive disclosure. Platforms that support multi-file skills (Claude Code, Cursor) get the full experience.

For **single-file platforms** (Windsurf, Cline, Copilot, custom GPTs), you have two options:

1. **Copy `SKILL.md` directly** — it's self-contained at 440 lines and covers all core patterns. The `references/` links won't resolve, but the inline content is sufficient for most tasks.

2. **Point agents to the LLM-optimized docs** — add this line to your platform's config file:
   ```
   For detailed Pixeltable API reference, fetch: https://docs.pixeltable.com/llms-full.txt
   ```
   Most modern agents can fetch URLs on demand, giving them the complete documentation without maintaining a separate file.

---

## What's Inside

```
skills/pixeltable-skill/
├── SKILL.md                    # Core instructions (440 lines)
│                                 Task router, core API, agent pipeline,
│                                 25+ providers, common pitfalls
└── references/                  # Loaded on demand
    ├── core-api.md              # Tables, querying, views, UDFs, config, data sharing
    ├── providers.md             # Quick-reference table + examples for 25+ providers
    ├── workflows.md             # RAG, video, image, audio, FastAPI, export
    ├── video-rag-agents.md      # Video + transcript search + agent pipeline
    ├── agents-memory-mcp.md     # Agent with memory, MCP tools, multi-provider
    ├── ml-data-pipeline.md      # Ingest, enrich, version, PyTorch export
    └── agentic-patterns.md      # 6 patterns + 2 reasoning strategies
```

---

## Prerequisites

```bash
pip install pixeltable    # Python >= 3.10

export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
# See core-api.md Configuration section for all 25+ provider keys
```

---

## What is Pixeltable?

[Pixeltable](https://github.com/pixeltable/pixeltable) is an open-source Python library providing declarative data infrastructure for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration across images, video, audio, and documents.

---

## What is an Agent Skill?

Agent Skills are instruction sets that AI coding assistants load to write correct code for specific libraries. This skill implements the open [Agent Skills specification](https://agentskills.io/specification).

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

The canonical source is `skills/pixeltable-skill/SKILL.md` + `references/`. All content lives there — no platform-specific variants to maintain.

---

## Learn More

- [Pixeltable Documentation](https://docs.pixeltable.com/)
- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Pixeltable Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) — FastAPI + React reference with deployment templates
- [Pixeltable MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- [Pixeltable Discord](https://discord.gg/QPyqFYx2UN)

### LLM-Optimized Documentation

| Resource | URL |
|----------|-----|
| Product overview | [pixeltable.com/llms.txt](https://www.pixeltable.com/llms.txt) |
| Docs index | [docs.pixeltable.com/llms.txt](https://docs.pixeltable.com/llms.txt) |
| Full docs | [docs.pixeltable.com/llms-full.txt](https://docs.pixeltable.com/llms-full.txt) |
| Any page as markdown | `https://docs.pixeltable.com/<path>.md` |

---

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
