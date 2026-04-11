# Contributing to Pixeltable Skill

Thanks for your interest in improving the Pixeltable Skill! This guide covers how to contribute effectively.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/pixeltable-skill.git`
3. Create a feature branch: `git checkout -b my-feature`
4. Make your changes
5. Push to your fork: `git push origin my-feature`
6. Open a Pull Request

## Repository Structure

```
pixeltable-skill/
├── skills/pixeltable-skill/   # Canonical full skill (SKILL.md + references/)
├── platforms/                 # Platform-specific variants at different densities
│   ├── cursor-rule/           # Compact (~95 lines)
│   ├── github-copilot/        # Standard (~200 lines)
│   ├── windsurf/              # Standard
│   ├── cline/                 # Standard
│   ├── agents-md/             # Standard
│   ├── system-prompt/         # Terse (~25 lines)
│   └── openai-custom-gpt/    # Terse
├── install.sh                 # Multi-platform installer
└── .claude-plugin/            # Claude Code plugin metadata
```

## What to Contribute

### Improving Core Content (skills/pixeltable-skill/)

- Fix incorrect API examples
- Add missing patterns for common use cases
- Update provider examples for new Pixeltable releases
- Keep `SKILL.md` concise — detailed content goes in `references/` (core-api.md, providers.md, workflows.md)
- `SKILL.md` should stay under 500 lines

### Improving Platform Variants (platforms/)

When changing core content, propagate relevant updates to platform variants:
- **Standard** (Windsurf, Cline, Copilot, AGENTS.md): Self-contained, ~200 lines
- **Compact** (Cursor rule): Token-efficient, ~95 lines
- **Terse** (system prompt, Custom GPT): Minimal, ~25 lines

### Adding a New Platform

1. Create `platforms/<platform-name>/` with the appropriately named config file
2. Use the standard or compact variant as a starting point
3. Add any required metadata/frontmatter
4. Update the platform matrix in README.md
5. Add the platform to `install.sh` (the `PLATFORMS`, `platform_src`, `platform_dest`, and `platform_label` functions)

### Plugin Metadata

- Update version numbers in `.claude-plugin/plugin.json`
- Add relevant tags in `.claude-plugin/marketplace.json`

## Guidelines

### All Examples Must Be Idempotent

Every example should use `if_exists='ignore'` so it can be safely re-run:

```python
# Correct
pxt.create_table('dir.table', schema, if_exists='ignore')

# Will error on re-run
pxt.create_table('dir.table', schema)
```

### Keep Consistent Terminology

Choose one term and use it throughout. For example: always "computed column" (not "derived column" or "formula column").

### Test Your Changes

Before submitting, verify:

1. YAML frontmatter in `SKILL.md` is valid (name in kebab-case, no XML tags)
2. All code examples are syntactically correct Python
3. Provider examples match the current Pixeltable API
4. The install script still works: `./install.sh --platform cursor-rule --target /tmp/test`

### No XML Tags

The Agent Skills specification forbids XML angle brackets in skill files. Use markdown formatting instead.

## Reporting Issues

- Use [GitHub Issues](https://github.com/pixeltable/pixeltable-skill/issues)
- Include: what you expected, what happened, and steps to reproduce
- For Pixeltable library bugs, report to [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable/issues)

## Code of Conduct

Be respectful and constructive. We follow the [Pixeltable Code of Conduct](https://github.com/pixeltable/pixeltable/blob/main/CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
