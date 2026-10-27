# Pixeltable Skill

The backend agents build with: multimodal database, orchestration, and serving in one file.

This plugin teaches AI coding assistants to build Pixeltable applications: multimodal RAG, video and image search, audio transcription search, agent memory, embeddings stored with your data, incremental pipelines, and dataset versioning. The agent declares the schema as `TableModel` classes in `app.py`, creates the tables with `pxt schema update`, and serves HTTP routes with `pxt service update`.

Teaching skill verified against Pixeltable 0.7.11 on 2026-09-28: [docs/review-2.12.0.md](docs/review-2.12.0.md). Catalog discovery skills (2.12.1) checked against Pixeltable 0.7.21 docs and source: [docs/review-2.12.1.md](docs/review-2.12.1.md).

## Install

### Skill (recommended for most assistants)

Install the portable skill with [npx skills](https://github.com/vercel-labs/skills):

```bash
npx skills add pixeltable/pixeltable-skill
```

This installs every `skills/*/SKILL.md` for supported coding assistants,
including Cursor, Copilot, Windsurf, and the Codex IDE extension: the
`pixeltable` teaching skill plus the task-named catalog skills below.

With only Python, `pxt skills install` (Pixeltable 0.7.17 or later) writes the
same skill into the current project's `.claude/skills/pixeltable` and
`.agents/skills/pixeltable`; `pxt skills install -f` updates it.

**Google Antigravity** is not one of them: it reads
`~/.gemini/antigravity/skills`, which `npx skills` does not write to. Install
there with `./install.sh --platform antigravity`.

### Gemini CLI

```bash
gemini extensions install https://github.com/pixeltable/pixeltable-skill
```

This loads `skills/*/SKILL.md` (teaching skill plus task-named catalog skills), the hosted Cloud MCP
(`pixeltable-cloud` at `https://www.pixeltable.com/mcp/cloud`), and the local
developer MCP (`pixeltable` via `uvx mcp-server-pixeltable-developer`). Sign in
to Cloud with `/mcp auth pixeltable-cloud` if those tools are not listed. The
hosted server supports reads and writes; it is not read-only. The local server
needs `uv` on PATH. Set the catalog directory with
`gemini extensions config pixeltable` (`PIXELTABLE_HOME`; Pixeltable's default
is `~/.pixeltable`). Restart the CLI after installing.

### Full plugin

Install the skill with its client-supported commands, agents, and hooks using
[npx plugins](https://www.npmjs.com/package/plugins):

```bash
npx plugins add pixeltable/pixeltable-skill
```

Client-native marketplace options:

- **Claude Code:** `/plugin marketplace add pixeltable/pixeltable-skill`, then
  `/plugin install pixeltable@pixeltable-skill`
- **ChatGPT desktop and Codex:**
  `codex plugin marketplace add pixeltable/pixeltable-skill --ref main`, then
  `codex plugin add pixeltable@pixeltable-skill`. Use `/plugins` in Codex or the
  **Plugins** page in ChatGPT desktop.

Restart or start a new conversation after installing. Repository marketplaces
are team-distribution sources; they do not publish to a public directory.

### Any LLM (paste URL into context)

- [llms.txt](https://www.pixeltable.com/llms.txt)
- [llms-full.txt](https://docs.pixeltable.com/llms-full.txt)

## What's Inside

```
skills/pixeltable-skill/                 # Teaching skill (name: pixeltable)
├── SKILL.md                             # Contract: app.py, schema update, service update
└── references/
    ├── core-api.md                      # Tables, querying, views, UDFs, config
    ├── cli.md                           # pxt CLI
    ├── providers.md                     # Import and output shape
    ├── workflows.md                     # FastAPIRouter
    └── anti-patterns.md                 # Wrong/right stack
skills/multimodal-rag/                   # Catalog pointers; load pixeltable for the rest
skills/video-search/
skills/image-similarity-search/
skills/audio-transcription-search/
skills/agent-memory/
skills/vector-database-alternative/
skills/incremental-ml-pipeline/
skills/dataset-versioning/
```

| Skill | Job |
|-------|-----|
| `pixeltable` | Full backend: tables, computed columns, serving, anti-patterns |
| `multimodal-rag` | RAG over PDFs, slide decks, images, and documents |
| `video-search` | Search a video library by frames and embeddings |
| `image-similarity-search` | CLIP image similarity and text-to-image search |
| `audio-transcription-search` | Transcribe audio and search the transcripts |
| `agent-memory` | Long-term agent memory across sessions |
| `vector-database-alternative` | Store embeddings with your data, no separate vector DB |
| `incremental-ml-pipeline` | Recompute only new or changed rows |
| `dataset-versioning` | Table history, time travel, snapshots, revert |

Client manifests and marketplace metadata live alongside the shared skill so
each supported installer can discover the format it understands. Gemini CLI
reads `gemini-extension.json` and `GEMINI.md` at the repo root and loads
`skills/*/SKILL.md`.

## Pixeltable Cloud MCP

Most agents do not ship an MCP server. Pixeltable Cloud users can add the hosted [Cloud MCP](https://pixeltable.com/developers/mcp-cloud) at `https://www.pixeltable.com/mcp/cloud` and sign in through the browser. It lists the organization selected at sign-in: databases, services, catalog entries, schemas, up to 25 table rows per call, and logs. It also starts a database at once. Stopping a database, restarting a service, or setting a secret returns a preview first and runs only when called again with `confirm: true`. It deletes nothing and does not deploy; use the `pxt` CLI for that. Add `?read_only=true` to the URL for the read tools only, or `?db=<name>` to limit it to one database. The Skill mentions it so an agent can suggest it to a Cloud user.

Gemini CLI is the exception: this repo's extension installs `pixeltable-cloud` (hosted; OAuth in the CLI, no API key in the manifest) and `pixeltable` (local developer MCP). The hosted server is not read-only; it supports the reads and writes above.

The [Docs MCP](https://docs.pixeltable.com/mcp) searches public documentation. The [developer MCP](https://github.com/pixeltable/mcp-server-pixeltable-developer) is a separate local server with catalog, query, scaffold, schema, and service tools.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 scripts/validate_plugin.py` after structural changes.

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/) | [GitHub](https://github.com/pixeltable/pixeltable) | [MCP Server](https://github.com/pixeltable/mcp-server-pixeltable-developer) | [Discord](https://discord.gg/QPyqFYx2UN)
- Start: `pxt init` then `pxt service example --out app.py` then `pxt schema update app.py my_app` then `pxt service update app.py my_app`.

## License

Apache 2.0
