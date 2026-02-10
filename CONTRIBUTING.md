# Contributing to Pixeltable Skill

Thanks for your interest in improving the Pixeltable Skill! This guide covers how to contribute effectively.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/pixeltable-skill.git`
3. Create a feature branch: `git checkout -b my-feature`
4. Make your changes
5. Push to your fork: `git push origin my-feature`
6. Open a Pull Request

## What to Contribute

### Improving SKILL.md

- Fix incorrect API examples
- Add missing patterns for common use cases
- Improve clarity of existing instructions
- Keep it concise — detailed content goes in `API_REFERENCE.md`

### Improving API_REFERENCE.md

- Add examples for new Pixeltable features or providers
- Fix outdated API signatures
- Add new workflow templates
- Ensure all examples use idempotent flags (`if_exists='ignore'`)

### Plugin Metadata

- Update version numbers in `plugin.json`
- Add relevant tags in `marketplace.json`

## Guidelines

### Keep Instructions Concise

`SKILL.md` should stay under 5,000 words. It's what Claude loads first. Move detailed reference material to `API_REFERENCE.md`.

### All Examples Must Be Idempotent

Every example should use `if_exists='ignore'` or equivalent so it can be safely re-run:

```python
# Good
pxt.create_table('dir.table', schema, if_exists='ignore')

# Bad - will error on re-run
pxt.create_table('dir.table', schema)
```

### Test Your Changes

Before submitting, verify:

1. YAML frontmatter in `SKILL.md` is valid (no XML tags, name in kebab-case)
2. All code examples are syntactically correct
3. Provider examples match the current Pixeltable API

### No XML Tags

The Claude Skills specification forbids XML angle brackets (`<` `>`) in skill files. Use markdown formatting instead.

## Reporting Issues

- Use [GitHub Issues](https://github.com/pixeltable/pixeltable-skill/issues)
- Include: what you expected, what happened, and steps to reproduce
- For Pixeltable library bugs, report to [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable/issues)

## Code of Conduct

Be respectful and constructive. We follow the [Pixeltable Code of Conduct](https://github.com/pixeltable/pixeltable/blob/main/CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
