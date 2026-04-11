# Pixeltable Skill

Build multimodal AI applications with [Pixeltable](https://github.com/pixeltable/pixeltable) — declarative tables, computed columns, embedding indexes, similarity search, UDFs, and 25+ AI provider integrations.

Drop it into any AI coding assistant. One skill, every platform.

---

## Why

AI coding assistants write incorrect Pixeltable code because their training data is stale or sparse. This skill gives any assistant deep, current expertise: correct API signatures, idempotent patterns, multimodal workflows, and production-ready templates — so generated code runs on the first try.

- **Correct code** — API signatures, import paths, and parameter names verified against the latest Pixeltable release.
- **Idempotent patterns** — Every example uses `if_exists='ignore'` for safe re-runs.
- **Progressive disclosure** — Concise core instructions with detailed reference files loaded only when needed.
- **25+ AI providers** — OpenAI, Anthropic, Gemini, Hugging Face, Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, Bedrock, Jina, BFL FLUX, RunwayML, fal.ai, Reve, Fabric, llama.cpp, and more.
- **End-to-end recipes** — RAG, video RAG agent, agent with memory and MCP, agentic patterns, ML data pipelines, FastAPI apps.

---

## Quickstart

### Copy-paste (any platform)

1. Find your platform in the table below.
2. Copy the file to the specified location in your project.

### One-liner installer

```bash
# Direct install (specify platform when piping)
curl -fsSL https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main/install.sh | bash -s -- --platform claude-code
```

Or clone and run directly:

```bash
git clone https://github.com/pixeltable/pixeltable-skill.git
cd pixeltable-skill
./install.sh
```

Or non-interactively:

```bash
./install.sh --platform cursor-rule --target ~/my-project
```

### Claude Code Plugin (recommended for Claude Code users)

```bash
/plugin marketplace add pixeltable/pixeltable-skill
/plugin install pixeltable-skill@pixeltable-skill
```

---

## Platform Support

| Platform | File | Copy to | Notes |
|----------|------|---------|-------|
| **Cursor** (rule) | [`pixeltable.mdc`](platforms/cursor-rule/pixeltable.mdc) | `.cursor/rules/` | Compact variant; set `alwaysApply: true` if desired |
| **Cursor** (skill) | [`SKILL.md`](skills/pixeltable-skill/SKILL.md) + [`references/`](skills/pixeltable-skill/references/) | `~/.cursor/skills/pixeltable-skill/` | Full skill with progressive disclosure |
| **Claude Code** | [`SKILL.md`](skills/pixeltable-skill/SKILL.md) + [`references/`](skills/pixeltable-skill/references/) | `.claude/skills/pixeltable-skill/` | Or install as plugin (see above) |
| **GitHub Copilot** | [`copilot-instructions.md`](platforms/github-copilot/copilot-instructions.md) | `.github/` | Auto-loaded in Copilot Chat |
| **Windsurf** | [`.windsurfrules`](platforms/windsurf/.windsurfrules) | Project root | Auto-loaded every session |
| **Cline** | [`.clinerules`](platforms/cline/.clinerules) | Project root | Auto-loaded every session |
| **AGENTS.md** | [`AGENTS.md`](platforms/agents-md/AGENTS.md) | Project root | Emerging multi-agent convention |
| **Any LLM API** | [`system-prompt.md`](platforms/system-prompt/system-prompt.md) | N/A | Paste into system prompt |
| **OpenAI Custom GPT** | [`instructions.md`](platforms/openai-custom-gpt/instructions.md) | N/A | Paste into GPT builder instructions |

---

## Architecture

### Why multiple variants?

The **canonical source of truth** is `skills/pixeltable-skill/SKILL.md` plus its `references/` directory. This is the full skill with progressive disclosure — Claude Code and Cursor load the core instructions first, then pull in reference files on demand.

Most other platforms (Windsurf, Cline, Copilot, etc.) load a **single file** at startup and have no mechanism to reference additional files. For those platforms, we ship **self-contained condensations** of the full skill at different token budgets:

| Variant | Lines | Platforms | Relationship to SKILL.md |
|---------|-------|-----------|--------------------------|
| **Full** | ~2,500 | Claude Code, Cursor skill | `SKILL.md` + 7 reference files — progressive disclosure |
| **Standard** | ~230 | Windsurf, Cline, Copilot, AGENTS.md | Self-contained condensation of SKILL.md core patterns |
| **Compact** | ~110 | Cursor rule | Token-efficient quick reference |
| **Terse** | ~30 | System prompt, Custom GPTs | Minimal footprint for raw LLM API |

**All variants derive from the same source.** When updating content, edit `SKILL.md` and `references/` first (the canonical source), then propagate changes to the platform variants.

### Reference files (loaded on demand)

| File | Coverage |
|------|----------|
| [`core-api.md`](skills/pixeltable-skill/references/core-api.md) | Tables, querying, views, iterators, embeddings, UDFs, B-tree indexes, recompute, data sharing, export SQL, configuration, media destinations, rate limiting |
| [`providers.md`](skills/pixeltable-skill/references/providers.md) | Quick-reference table + full examples for all 25+ AI providers |
| [`workflows.md`](skills/pixeltable-skill/references/workflows.md) | RAG, video analysis, image classification, audio transcription, multi-provider comparison, tool-calling agent, FastAPI app, export |
| [`video-rag-agents.md`](skills/pixeltable-skill/references/video-rag-agents.md) | Combined video processing + transcript/frame retrieval + tool-calling agent |
| [`agents-memory-mcp.md`](skills/pixeltable-skill/references/agents-memory-mcp.md) | Agent with persistent memory (chat history + knowledge bank), MCP integration, multi-provider invoke_tools |
| [`ml-data-pipeline.md`](skills/pixeltable-skill/references/ml-data-pipeline.md) | ML data wrangling: ingest, enrich, curate, version (snapshots), export to PyTorch/Parquet/pandas |
| [`agentic-patterns.md`](skills/pixeltable-skill/references/agentic-patterns.md) | 6 architectural patterns + 2 reasoning strategies (prompt chaining, routing, parallelization, tool use, evaluator-optimizer, orchestrator-worker, ReAct, planning) |

---

## Repository Structure

```
pixeltable-skill/
├── skills/
│   └── pixeltable-skill/          # Canonical full skill (source of truth)
│       ├── SKILL.md               # Core instructions with task router
│       └── references/             # Detailed reference (loaded on demand)
│           ├── core-api.md        # Tables, querying, views, UDFs, config
│           ├── providers.md       # 25+ AI provider examples
│           ├── workflows.md       # End-to-end workflow templates
│           ├── video-rag-agents.md
│           ├── agents-memory-mcp.md
│           ├── ml-data-pipeline.md
│           └── agentic-patterns.md
├── platforms/                     # Self-contained variants for other platforms
│   ├── cursor-rule/               # Compact (~110 lines)
│   ├── github-copilot/            # Standard (~230 lines)
│   ├── windsurf/                  # Standard
│   ├── cline/                     # Standard
│   ├── agents-md/                 # Standard
│   ├── system-prompt/             # Terse (~30 lines)
│   └── openai-custom-gpt/        # Terse
├── .claude-plugin/                # Claude Code plugin metadata
│   ├── plugin.json
│   └── marketplace.json
├── install.sh                     # Multi-platform installer
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Prerequisites

Make sure Pixeltable is installed in your Python environment:

```bash
pip install pixeltable
```

Requires Python >= 3.10. For AI provider integrations, set the appropriate environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
# etc. — see core-api.md Configuration section for all 25+ provider keys
```

---

## What is Pixeltable?

[Pixeltable](https://github.com/pixeltable/pixeltable) is an open-source Python library providing declarative data infrastructure for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration across images, video, audio, and documents.

**Key features:**
- **Tables** with native multimodal column types (Image, Video, Audio, Document)
- **Computed columns** that run AI transformations automatically on new data
- **Views** with iterators for document chunking and video frame extraction
- **Embedding indexes** with automatic maintenance and similarity search
- **25+ AI provider integrations** (OpenAI, Anthropic, Gemini, Hugging Face, etc.)
- **Import/export** from CSV, Parquet, Hugging Face, pandas, SQL databases, PyTorch

---

## What is an Agent Skill?

Agent Skills are instruction sets that AI coding assistants discover and use to work more accurately. When you ask about Pixeltable, the assistant loads the skill and writes correct code based on verified API references — no hallucinated signatures.

This skill implements the open [Agent Skills specification](https://agentskills.io/specification), making it compatible across platforms.

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Key principle**: The canonical source is `skills/pixeltable-skill/SKILL.md` + `references/`. Edit there first, then propagate to platform variants. Platform files are self-contained condensations — they cannot reference external files.

To add a new platform:

1. Create `platforms/<platform-name>/` with the appropriately named config file.
2. Use the standard or compact variant as a starting point.
3. Add any required metadata/frontmatter for the platform.
4. Update the platform matrix in this README.
5. Add the platform to `install.sh`.
6. Open a PR.

---

## Learn More

- [Pixeltable Documentation](https://docs.pixeltable.com/)
- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Pixeltable Starter Kit](https://github.com/pixeltable/pixeltable-starter-kit) — Full-stack FastAPI + React reference with deployment templates
- [Pixeltable MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer)
- [Pixeltable Discord](https://discord.gg/QPyqFYx2UN)

### LLM-Optimized Documentation

For AI coding tools that can fetch URLs directly, Pixeltable provides documentation in the [llms.txt standard](https://llmstxt.org/):

| Resource | URL | Use |
|----------|-----|-----|
| Product overview | [pixeltable.com/llms.txt](https://www.pixeltable.com/llms.txt) | Site map with all links |
| Docs index | [docs.pixeltable.com/llms.txt](https://docs.pixeltable.com/llms.txt) | Documentation structure |
| Full docs | [docs.pixeltable.com/llms-full.txt](https://docs.pixeltable.com/llms-full.txt) | Complete documentation content |
| Any page as markdown | `https://docs.pixeltable.com/<path>.md` | Individual page content |

---

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
