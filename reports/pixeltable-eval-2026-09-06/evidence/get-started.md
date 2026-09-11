---
name: pixeltable-get-started
area: Getting Started
supported_surfaces:
  - cli
  - skills
  - mcp
description: |-
  Hand your coding agent this playbook to set up Pixeltable: install
  the Python package and pxt CLI, add the Pixeltable Skill, and connect
  MCP once for use across projects.
title: 'Onboard your agent to Pixeltable'
url: https://pixeltable.com/get-started.md
runtimes:
  - Claude Code
  - Cursor
  - Codex CLI
  - VS Code with Copilot
  - Windsurf
  - Gemini CLI
  - OpenCode
---

# Set up Pixeltable for your AI coding agent

Use this playbook to prepare the current agent for Pixeltable. Install the CLI, Skill, and MCP connection once; create a Cloud database only when a hosted deploy requires it.

## How to run

Run section 1 once per machine. Run sections 2 and 3 once per coding agent. Section 5 is Cloud: pause for human sign-in and the API key.

Perform actions yourself when terminal or file access is available. Pause only for user authentication, approval, or UI actions you cannot perform. Do not merely return commands for the user to copy.

After setup, read https://pixeltable.com/llms.txt for the one-file `app.py` Quick Start. This page is setup, not the product overview.

## 1. Install Pixeltable

Check for an existing installation:

```sh
python3 --version
pxt --version
```

Python 3.11+ is required. If `pxt` is missing, install the latest package:

```sh
pip install -U 'pixeltable[serve]'
pxt --version
pxt init
```

`pxt init` marks the project root. Schema and service refuse an application file without one. Catalog-only install is `pip install pixeltable`.

Do not create a Pixeltable Cloud project during global setup. Do not run `pxt service example` yet. Generate a starter app only after the Skill is installed so the file matches current patterns.

## 2. Add Pixeltable guidance

Install the Pixeltable Skill for the current agent. This is the analog of a framework plugin: it teaches table/schema patterns, provider integrations, and anti-patterns.

```sh
npx skills add pixeltable/pixeltable-skill
npx skills list
```

Choose the current agent if prompted and confirm the installation path. Reload only if the newly installed skill is missing.

Skill source: https://github.com/pixeltable/pixeltable-skill
Skills index: https://pixeltable.com/.well-known/agent-skills/index.json

## 3. Connect MCP

Pixeltable has two MCP surfaces. Connect the one the current job needs. Do not invent a hosted authenticated control-plane MCP.

| Server | Transport | What it can do |
| --- | --- | --- |
| pixeltable-web | HTTP | Read-only docs search and integration listing. No table mutations. |
| pixeltable-developer | stdio | Inspect schemas, query tables, run a REPL against a local or Cloud catalog. |

Before changing an MCP configuration file, inspect it and merge the Pixeltable entry without replacing unrelated settings.

### Hosted WebMCP (docs, no auth)

Endpoint (exactly):

```text
https://pixeltable.com/mcp
```

Server card: https://pixeltable.com/.well-known/mcp/server-card.json

After connecting, call `search_docs` with a topic such as "embedding index" to verify.

#### Cursor

Merge this into `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pixeltable-web": {
      "url": "https://pixeltable.com/mcp"
    }
  }
}
```

#### Claude Code

```bash
claude mcp add --transport http pixeltable-web --scope user https://pixeltable.com/mcp
```

Inspect existing MCP entries before adding.

#### Codex CLI

```bash
codex mcp list
codex mcp add pixeltable-web --url https://pixeltable.com/mcp
```

#### VS Code with GitHub Copilot

Run **MCP: Add Server**, choose **HTTP**, enter `https://pixeltable.com/mcp`, name it `pixeltable-web`, and select **Global**.

#### Windsurf

Merge this into `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "pixeltable-web": {
      "serverUrl": "https://pixeltable.com/mcp"
    }
  }
}
```

#### Gemini CLI

Merge this into `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "pixeltable-web": {
      "command": "npx",
      "args": ["mcp-remote", "https://pixeltable.com/mcp"]
    }
  }
}
```

### Developer MCP (stdio: tables and REPL)

Install once per machine, then add the server to the current agent:

```sh
uv tool install --from git+https://github.com/pixeltable/mcp-server-pixeltable-developer.git mcp-server-pixeltable-developer
```

If `uv` is missing:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Claude Code

```bash
claude mcp add pixeltable mcp-server-pixeltable-developer
```

#### Cursor

Merge this into `~/.cursor/mcp.json` (keep any existing `pixeltable-web` entry):

```json
{
  "mcpServers": {
    "pixeltable-developer": {
      "command": "mcp-server-pixeltable-developer"
    }
  }
}
```

Optional: set `PIXELTABLE_HOME` to the data directory the user wants this catalog to use.

Repository: https://github.com/pixeltable/mcp-server-pixeltable-developer

Connect the developer MCP when the user wants to inspect or query a catalog. Skip it for docs-only questions. WebMCP is enough.

Keep human confirmation enabled for every MCP mutation. The developer server can change local catalog state.

## 4. First app (optional, after setup)

Only after sections 1–2 succeed:

```sh
pxt init
pxt service example --out app.py
pxt schema update app.py my_app
pxt service update app.py my_app
pxt schema diff app.py my_app
pxt dashboard
```

Declare (`pxt schema update`), Serve (`pxt service update`), then Experiment (`pxt dashboard`, curl, or `pxt schema diff`). Same file on Cloud: set `PIXELTABLE_API_KEY`, add `[[pixeltable.database]]` with `name = 'pxt://org:db'`, then `pxt db update pxt://org:db`, `pxt schema update app.py pxt://org:db`, `pxt service update app.py pxt://org:db`. `pxt service run` is local only.

## 5. When the user wants Cloud

Pause for the human. Sign-in and key paste are UI actions you cannot perform.

1. Ask the user to click **Sign in** (or Dashboard) on https://pixeltable.com. The CLI cannot create organizations.
2. Ask for the org slug and an org API key (`sk_...`) created at `https://pixeltable.com/dashboard/<org>/api-keys`. Set `PIXELTABLE_API_KEY` in the environment (it wins over `~/.pixeltable/config.toml`). Do not invent `internal-api.pixeltable.com`.
3. `pxt init` writes `pixeltable.toml`, or appends `[[tool.pixeltable.database]]` to an existing `pyproject.toml`. Add `name = 'pxt://org:db'` so it matches the URI.
4. Order is required: `pxt db update pxt://org:db -f`, then `pxt schema update app.py pxt://org:db -f`, then `pxt service update app.py pxt://org:db -f`. Schema first fails with `404: UDF not found`. Omit `cpu` / `memory_mb` / `workers` — use platform defaults.
5. Browse tables and services on the website dashboard (`/dashboard/<org>/<db>`). `pxt dashboard` and `pxt service list` are local only. Call `https://<org>-<db>.svc.pxt.run/<service>/` with a trailing slash and `X-api-key`. `/docs` is the same host and also needs the key.

`pxt.create_table()` at import in `app.py` fails `pxt service check` (`modifies catalog while imported`). Use `TableModel` + `FastAPIRouter`. Scaffold with `pxt service example`, not `pixeltable-new`.

## Completion

Report only verified state:

```text
Pixeltable agent setup is ready
CLI: <version>, pxt available
Guidance: <skill|skipped>
MCP web: <connected|skipped>, https://pixeltable.com/mcp
MCP developer: <connected|skipped>, stdio mcp-server-pixeltable-developer
MCP config: <path|not changed>
Reload: <not needed|completed>
Next: https://pixeltable.com/llms.txt
```

Sources:

- https://pixeltable.com/llms.txt
- https://pixeltable.com/developers/llms.txt
- https://docs.pixeltable.com
- https://github.com/pixeltable/pixeltable-skill
- https://github.com/pixeltable/mcp-server-pixeltable-developer
- https://pixeltable.com/.well-known/agent.json
