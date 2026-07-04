#!/usr/bin/env python3
"""Validate the Pixeltable plugin layout. Pure stdlib; no third-party deps.

Checks:
  1. All JSON manifests parse.
  2. Manifest component pointers (skills/agents/commands) resolve on disk.
  3. Every skills/<name>/SKILL.md has `name` and `description` frontmatter.
  4. Listed command/agent files in .claude-plugin/plugin.json exist.

Exit non-zero if any check fails. Intended for CI / pre-commit.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def load_json(rel):
    p = ROOT / rel
    if not p.is_file():
        errors.append(f"missing manifest: {rel}")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"invalid JSON in {rel}: {e}")
        return None


def frontmatter(md_path):
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def main():
    # 1. JSON manifests
    manifests = [
        ".plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".agents/plugins/marketplace.json",
        "package.json",
    ]
    parsed = {m: load_json(m) for m in manifests}

    # 2. Component dir pointers resolve (.plugin / .cursor-plugin)
    for m in (".plugin/plugin.json", ".cursor-plugin/plugin.json"):
        data = parsed.get(m)
        if not data:
            continue
        for key in ("skills", "agents", "commands"):
            if key in data:
                check((ROOT / data[key]).is_dir(), f"{m}: '{key}' dir not found: {data[key]}")

    # 3. SKILL.md frontmatter
    skill_files = list((ROOT / "skills").glob("*/SKILL.md"))
    check(len(skill_files) >= 1, "no skills/*/SKILL.md found")
    for sf in skill_files:
        fm = frontmatter(sf)
        rel = sf.relative_to(ROOT)
        check("name:" in fm, f"{rel}: missing 'name' in frontmatter")
        check("description:" in fm, f"{rel}: missing 'description' in frontmatter")

    # 4a. Any command/agent files listed in .claude-plugin/plugin.json must exist
    claude = parsed.get(".claude-plugin/plugin.json") or {}
    for key in ("commands", "agents"):
        for rel in claude.get(key, []):
            check((ROOT / rel).is_file(), f".claude-plugin/plugin.json: {key} file not found: {rel}")

    # 4b. Auto-discovered commands have a `description`; agents have `name` + `description`
    for cmd in (ROOT / "commands").glob("*.md"):
        check("description:" in frontmatter(cmd), f"commands/{cmd.name}: missing 'description'")
    agent_files = list((ROOT / "agents").glob("*.md"))
    for ag in agent_files:
        fm = frontmatter(ag)
        check("name:" in fm, f"agents/{ag.name}: missing 'name'")
        check("description:" in fm, f"agents/{ag.name}: missing 'description'")
        # tools, if present, must be a comma-separated string (not a YAML/JSON list)
        for line in fm.splitlines():
            if line.strip().startswith("tools:"):
                val = line.split(":", 1)[1].strip()
                check(not val.startswith("["), f"agents/{ag.name}: 'tools' must be comma-separated, not a list")

    # 5. Version sync across all versioned manifests + SKILL.md frontmatter
    versions = {}
    version_getters = {
        ".plugin/plugin.json": lambda d: d.get("version"),
        ".cursor-plugin/plugin.json": lambda d: d.get("version"),
        ".claude-plugin/plugin.json": lambda d: d.get("version"),
        ".claude-plugin/marketplace.json": lambda d: (d.get("metadata") or {}).get("version"),
        ".codex-plugin/plugin.json": lambda d: d.get("version"),
        "package.json": lambda d: d.get("version"),
    }
    for rel, getter in version_getters.items():
        data = parsed.get(rel)
        if data is None:
            continue
        v = getter(data)
        check(v is not None, f"{rel}: missing version field")
        if v is not None:
            versions[rel] = v
    for sf in skill_files:
        m = re.search(r"^\s*version:\s*(.+?)\s*$", frontmatter(sf), re.MULTILINE)
        if m:
            versions[str(sf.relative_to(ROOT))] = m.group(1).strip().strip("\"'")
    check(
        len(set(versions.values())) <= 1,
        "version mismatch (all manifests + SKILL.md must match): "
        + "; ".join(f"{k}={v}" for k, v in sorted(versions.items())),
    )

    if errors:
        print(f"FAIL ({len(errors)} of {checks} checks):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {checks} checks passed ({len(skill_files)} skill(s)).")


if __name__ == "__main__":
    main()
