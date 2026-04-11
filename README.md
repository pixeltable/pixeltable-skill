# Pixeltable Skill

Build multimodal AI applications with [Pixeltable](https://github.com/pixeltable/pixeltable) — declarative tables, computed columns, embedding indexes, similarity search, UDFs, and 15+ AI provider integrations.

Drop it into any AI coding assistant. One skill, every platform.

---

## Why

AI coding assistants write incorrect Pixeltable code because their training data is stale or sparse. This skill gives any assistant deep, current expertise: correct API signatures, idempotent patterns, multimodal workflows, and production-ready templates — so generated code runs on the first try.

- **Correct code** — API signatures, import paths, and parameter names verified against the latest Pixeltable release.
- **Idempotent patterns** — Every example uses `if_exists='ignore'` for safe re-runs.
- **Progressive disclosure** — Concise core instructions with a full API reference loaded only when needed.
- **15+ AI providers** — OpenAI, Anthropic, Gemini, Hugging Face, Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, Replicate, Voyage AI, Bedrock, OpenRouter, Twelve Labs.
- **End-to-end templates** — RAG, video analysis, image classification, audio transcription, tool-calling agents, FastAPI apps.

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
| **Cursor** (skill) | [`SKILL.md`](skills/pixeltable-skill/SKILL.md) + [`reference/`](skills/pixeltable-skill/reference/) | `~/.cursor/skills/pixeltable-skill/` | Full skill with progressive disclosure |
| **Claude Code** | [`SKILL.md`](skills/pixeltable-skill/SKILL.md) + [`reference/`](skills/pixeltable-skill/reference/) | `.claude/skills/pixeltable-skill/` | Or install as plugin (see above) |
| **GitHub Copilot** | [`copilot-instructions.md`](platforms/github-copilot/copilot-instructions.md) | `.github/` | Auto-loaded in Copilot Chat |
| **Windsurf** | [`.windsurfrules`](platforms/windsurf/.windsurfrules) | Project root | Auto-loaded every session |
| **Cline** | [`.clinerules`](platforms/cline/.clinerules) | Project root | Auto-loaded every session |
| **AGENTS.md** | [`AGENTS.md`](platforms/agents-md/AGENTS.md) | Project root | Emerging multi-agent convention |
| **Any LLM API** | [`system-prompt.md`](platforms/system-prompt/system-prompt.md) | N/A | Paste into system prompt |
| **OpenAI Custom GPT** | [`instructions.md`](platforms/openai-custom-gpt/instructions.md) | N/A | Paste into GPT builder instructions |

---

## Variants

The repo ships four densities of Pixeltable expertise:

| Variant | Lines | Best for |
|---------|-------|----------|
| **Full** ([SKILL.md](skills/pixeltable-skill/SKILL.md) + [reference/](skills/pixeltable-skill/reference/)) | ~1,800 | Claude Code, Cursor skill — progressive disclosure |
| **Standard** ([platform files](platforms/windsurf/.windsurfrules)) | ~200 | Windsurf, Cline, Copilot, AGENTS.md — self-contained |
| **Compact** ([Cursor rule](platforms/cursor-rule/pixeltable.mdc)) | ~95 | Cursor rule — token-efficient context |
| **Terse** ([system-prompt](platforms/system-prompt/system-prompt.md)) | ~25 | Raw LLM API, Custom GPTs — minimal footprint |

All encode the same core patterns. Choose based on your platform and token budget.

---

## Repository Structure

```
pixeltable-skill/
├── skills/
│   └── pixeltable-skill/          # Canonical full skill
│       ├── SKILL.md               # Core instructions (loaded first)
│       └── reference/             # Detailed reference (loaded on demand)
│           ├── core-api.md        # Tables, querying, views, UDFs, tools
│           ├── providers.md       # All AI provider examples
│           └── workflows.md       # End-to-end workflow templates
├── platforms/
│   ├── cursor-rule/               # Compact .mdc rule
│   ├── github-copilot/            # Standard variant
│   ├── windsurf/                  # Standard variant
│   ├── cline/                     # Standard variant
│   ├── agents-md/                 # Standard variant
│   ├── system-prompt/             # Terse variant
│   └── openai-custom-gpt/        # Terse variant
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

For AI provider integrations, set the appropriate environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
# etc.
```

---

## What is Pixeltable?

[Pixeltable](https://github.com/pixeltable/pixeltable) is an open-source Python library providing declarative data infrastructure for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration across images, video, audio, and documents.

**Key features:**
- **Tables** with native multimodal column types (Image, Video, Audio, Document)
- **Computed columns** that run AI transformations automatically on new data
- **Views** with iterators for document chunking and video frame extraction
- **Embedding indexes** with automatic maintenance and similarity search
- **15+ AI provider integrations** (OpenAI, Anthropic, Gemini, Hugging Face, etc.)
- **Import/export** from CSV, Parquet, Hugging Face, pandas, LanceDB

---

## What is an Agent Skill?

Agent Skills are instruction sets that AI coding assistants discover and use to work more accurately. When you ask about Pixeltable, the assistant loads the skill and writes correct code based on verified API references — no hallucinated signatures.

This skill implements the open [Agent Skills specification](https://github.com/anthropics/skills), making it compatible across platforms.

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on improving the skill content, adding platform support, or fixing API examples.

To add a new platform:

1. Create `platforms/<platform-name>/` with the appropriately named config file.
2. Use the standard or compact variant as a starting point.
3. Add any required metadata/frontmatter for the platform.
4. Update the platform matrix in this README.
5. Add the platform to `install.sh` (the `PLATFORMS`, `platform_src`, `platform_dest`, and `platform_label` functions).
6. Open a PR.

---

## Learn More

- [Pixeltable Documentation](https://docs.pixeltable.com/)
- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Pixeltable App Template](https://github.com/pixeltable/pixeltable-app-template) — Full-stack FastAPI + React reference
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
