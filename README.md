# Pixeltable Skill for Claude Code

**Build multimodal AI applications with Pixeltable — as a Claude Skill**

A Claude Skill that gives Claude deep expertise in [Pixeltable](https://github.com/pixeltable/pixeltable): declarative tables, computed columns, embedding indexes, similarity search, UDFs, views, and 15+ AI provider integrations. Packaged as a Claude Code Plugin for easy installation and distribution.

Claude autonomously discovers this skill when you ask about Pixeltable, loading only the minimal information needed for your specific task.

## Features

- **Full Pixeltable Expertise** — Tables, computed columns, views, embedding indexes, UDFs, queries
- **15+ AI Providers** — OpenAI, Anthropic, Gemini, Hugging Face, Together, Fireworks, Ollama, Mistral, Groq, DeepSeek, Replicate, Voyage AI, Bedrock, OpenRouter, Twelve Labs
- **Multimodal Workflows** — Image, video, audio, and document processing pipelines
- **End-to-End Templates** — RAG, video analysis, image classification, audio transcription, multi-provider comparison
- **Progressive Disclosure** — Concise `SKILL.md` with full `API_REFERENCE.md` loaded only when needed
- **Idempotent Patterns** — All examples use `if_exists='ignore'` for safe re-runs

## Installation

This repository is structured as a Claude Code Plugin containing a skill. Install as a **plugin** (recommended) or extract as a **standalone skill**.

### Understanding the Structure

```
pixeltable-skill/                    # Plugin root
├── .claude-plugin/                  # Plugin metadata
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   └── pixeltable-skill/            # The actual skill
│       ├── SKILL.md                 # Core instructions (Claude reads this)
│       └── API_REFERENCE.md         # Full API reference (loaded on demand)
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

Claude Code expects skills in folders under `.claude/skills/`, so manual installation requires extracting the nested skill folder.

---

### Option 1: Plugin Installation (Recommended)

Install via Claude Code's plugin system for automatic updates:

```bash
# Add this repository as a marketplace
/plugin marketplace add pixeltable/pixeltable-skill

# Install the plugin
/plugin install pixeltable-skill@pixeltable-skill
```

Verify by running `/help` to confirm the skill is available.

---

### Option 2: Standalone Skill Installation

Extract only the skill folder for manual installation.

**Global Installation (Available Everywhere):**

```bash
# Clone to a temporary location
git clone https://github.com/pixeltable/pixeltable-skill.git /tmp/pixeltable-skill-temp

# Copy only the skill folder to your global skills directory
mkdir -p ~/.claude/skills
cp -r /tmp/pixeltable-skill-temp/skills/pixeltable-skill ~/.claude/skills/

# Clean up
rm -rf /tmp/pixeltable-skill-temp
```

**Project-Specific Installation:**

```bash
# Clone to a temporary location
git clone https://github.com/pixeltable/pixeltable-skill.git /tmp/pixeltable-skill-temp

# Copy only the skill folder to your project
mkdir -p .claude/skills
cp -r /tmp/pixeltable-skill-temp/skills/pixeltable-skill .claude/skills/

# Clean up
rm -rf /tmp/pixeltable-skill-temp
```

---

### Option 3: Download Release

1. Download and extract the latest release from [GitHub Releases](https://github.com/pixeltable/pixeltable-skill/releases)
2. Copy the `skills/pixeltable-skill/` folder to:
   - Global: `~/.claude/skills/pixeltable-skill`
   - Project: `/path/to/your/project/.claude/skills/pixeltable-skill`

---

### Verify Installation

Run `/help` to confirm the skill is loaded, then ask Claude:

```
"Create a Pixeltable table for storing images with embeddings"
```

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

## Quick Start

After installation, simply ask Claude to build Pixeltable workflows. Claude will write correct, idempotent Pixeltable code with proper error handling.

### Example Prompts

**Tables and Data:**
```
"Create a Pixeltable table for storing articles with title, content, and category"
"Insert data from a CSV file into my Pixeltable table"
"Import this Hugging Face dataset into Pixeltable"
```

**AI Processing:**
```
"Add a computed column that summarizes each article using GPT-4o-mini"
"Set up embeddings and similarity search on my text column"
"Analyze images in my table using Claude Vision"
```

**Multimodal Pipelines:**
```
"Build a RAG pipeline for my PDF documents"
"Extract video frames and describe each one with GPT-4 Vision"
"Create a multimodal search index using CLIP"
```

**Data Operations:**
```
"Export my Pixeltable query results to Parquet"
"Compare OpenAI and Anthropic responses on the same prompts"
"Set up a local pipeline using Ollama"
```

## How It Works

1. You describe what you want to build with Pixeltable
2. Claude discovers this skill and loads `SKILL.md` (core patterns)
3. If more detail is needed, Claude loads `API_REFERENCE.md` (full API docs)
4. Claude writes production-ready Pixeltable code with idempotent operations
5. Code runs immediately — no guessing about API signatures

## What is a Skill?

Agent Skills are folders of instructions and resources that agents can discover and use to work more accurately and efficiently. When you ask Claude about Pixeltable, Claude discovers this skill, loads the necessary instructions, and writes correct Pixeltable code based on the comprehensive API reference.

This skill implements the open [Agent Skills specification](https://github.com/anthropics/skills), making it compatible across agent platforms.

## What is Pixeltable?

[Pixeltable](https://github.com/pixeltable/pixeltable) is an open-source Python library providing declarative data infrastructure for building multimodal AI applications. It unifies data storage, transformation, indexing, retrieval, and orchestration of data across images, video, audio, and documents.

**Key features:**
- **Tables** with native multimodal column types (Image, Video, Audio, Document)
- **Computed columns** that run AI transformations automatically on new data
- **Views** with iterators for document chunking and video frame extraction
- **Embedding indexes** with automatic maintenance and similarity search
- **15+ AI provider integrations** (OpenAI, Anthropic, Gemini, Hugging Face, etc.)
- **Import/export** from CSV, Parquet, Hugging Face, pandas, LanceDB

## Contributing

Contributions are welcome! Fork the repository, create a feature branch, make your changes, and submit a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Learn More

- [Pixeltable Documentation](https://docs.pixeltable.com/)
- [Pixeltable GitHub](https://github.com/pixeltable/pixeltable)
- [Pixeltable Discord](https://discord.gg/QPyqFYx2UN)
- [Agent Skills Specification](https://github.com/anthropics/skills)
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code Plugins Documentation](https://docs.anthropic.com/en/docs/claude-code/plugins)

## License

MIT License — see [LICENSE](LICENSE) file for details.
