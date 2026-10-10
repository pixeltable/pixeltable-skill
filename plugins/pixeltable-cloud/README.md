# Pixeltable Cloud

The backend agents build with, hosted: multimodal database, orchestration, and serving in one file, running on Pixeltable Cloud.

This plugin is the Pixeltable skill plus the Pixeltable Cloud MCP server. The skill teaches AI coding assistants to build Pixeltable applications: tables with computed columns, embedding indexes and vector search, RAG, tool-calling agents, and video, audio, image, and document pipelines across 25+ AI providers. The MCP server lets the assistant inspect and operate the Pixeltable Cloud organization you sign in to.

Pixeltable Cloud is in Limited Beta. Email [contact@pixeltable.com](mailto:contact@pixeltable.com) for an account.

## What it connects to

The plugin declares one remote MCP server, `https://www.pixeltable.com/mcp/cloud`. On first use, your browser opens `signin.pixeltable.com` to sign in, and the server acts on the organization you select there.

The server reads databases, services, catalog entries, schemas, up to 25 table rows per call, and logs. It starts a database at once. Stopping a database, restarting a service, or setting a secret returns a preview first and runs only when called again with `confirm: true`. It deletes nothing and does not deploy; use the `pxt` CLI for that. See the [Cloud MCP docs](https://pixeltable.com/developers/mcp-cloud).

The plugin runs no local code: no hooks, scripts, or package installs.

## Self-hosted Pixeltable

If you run Pixeltable on your own machine, install the `pixeltable` plugin instead. Install one of the two, not both: they carry the same skill.

## License

Apache 2.0
