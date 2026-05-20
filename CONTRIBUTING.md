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
├── SKILL.md               # Core instructions (<500 lines)
├── references/            # Detailed reference (loaded on demand)
├── install.sh             # Installer for Claude Code and Cursor
└── .claude-plugin/        # Claude Code plugin metadata
```

## What to Contribute

- Fix incorrect API examples
- Add missing patterns for common use cases
- Update provider examples for new Pixeltable releases
- Keep `SKILL.md` concise — detailed content goes in `references/`
- `SKILL.md` should stay under 500 lines

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

Always "computed column" (not "derived column"), always `string=` keyword in `similarity()`.

### Test Your Changes

Before submitting, verify:

1. YAML frontmatter in `SKILL.md` is valid (name in kebab-case, no XML tags)
2. All code examples are syntactically correct Python
3. Provider examples match the current Pixeltable API
4. The install script works: `./install.sh --platform claude-code --target /tmp/test`

### No XML Tags

The Agent Skills specification forbids XML angle brackets in skill files.

## Reporting Issues

- Use [GitHub Issues](https://github.com/pixeltable/pixeltable-skill/issues)
- For Pixeltable library bugs: [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable/issues)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
