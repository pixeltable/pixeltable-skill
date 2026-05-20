# AGENTS.md — For AI agents working in this repo

This repo contains the **Pixeltable Agent Skill** — documentation that teaches AI coding assistants to write correct Pixeltable code.

## Structure

```
skills/pixeltable-skill/
├── SKILL.md              ← Main skill file (frontmatter + task router + core patterns)
└── references/           ← Deep-dive files loaded on demand
    ├── core-api.md
    ├── providers.md
    ├── workflows.md
    ├── anti-patterns.md
    ├── agents-memory-mcp.md
    ├── video-rag-agents.md
    ├── ml-data-pipeline.md
    └── agentic-patterns.md
```

## Rules

- **SKILL.md is the entry point.** It must be self-contained for the common case; reference files are for deep dives.
- **Negative prompts go at the top** of SKILL.md (the "STOP" section). These deflect LLM training-distribution biases.
- **All code examples must be tested** against the current Pixeltable release before committing.
- **`if_exists='ignore'`** on every `create_*` and `add_*` call in examples — agents re-run code.
- **No LangChain, pandas-as-store, or standalone vector DB patterns** anywhere in this repo.
- **Keep SKILL.md under 500 lines.** Move detail to reference files.

## When editing

1. Read `SKILL.md` first to understand current structure
2. Check `references/` for existing coverage before adding new content
3. Maintain the Task Router table if adding new capabilities
4. Update the Reference Files table at the bottom of SKILL.md if adding/removing reference files
5. Bump `metadata.version` in SKILL.md frontmatter on meaningful changes

## Do NOT

- Add examples using deprecated APIs (`FrameIterator`, `openai.vision`, positional `.similarity()`)
- Create new top-level files — all skill content lives under `skills/pixeltable-skill/`
- Modify `install.sh` or `.claude-plugin/` without understanding the plugin distribution system
