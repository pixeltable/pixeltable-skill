#!/usr/bin/env python3
"""Validate the Pixeltable plugin layout. Pure stdlib; no third-party deps.

Checks:
  1. All JSON manifests parse (including gemini-extension.json).
  2. Portable and compatibility manifests agree and component pointers resolve.
  3. Every skills/<name>/SKILL.md has `name` and `description` (spec length, folder match);
     discovery skills stay short and point at the teaching skill.
  4. Listed command/agent files in .claude-plugin/plugin.json exist.
  5-9. Versions agree, doc code blocks parse and pass the hook's error checks, documented modules exist,
     SKILL.md stays under 500 lines, and shell blocks pass -f to `pxt service update`.

Exit non-zero if any check fails. Intended for CI / pre-commit.
"""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
checks = 0

# Catalog-facing task skills. The teaching skill stays in skills/pixeltable-skill
# with frontmatter name `pixeltable` (installers already key on that id).
TEACHING_SKILL_DIR = "pixeltable-skill"
TEACHING_SKILL_NAME = "pixeltable"
DISCOVERY_SKILL_NAMES = (
    "agent-memory",
    "audio-transcription-search",
    "dataset-versioning",
    "image-similarity-search",
    "incremental-ml-pipeline",
    "multimodal-rag",
    "vector-database-alternative",
    "video-search",
)
MAX_DESCRIPTION_LENGTH = 1024
MAX_DISCOVERY_SKILL_LINES = 120


def iter_agent_docs():
    """Markdown agents copy from: skill, agents, commands, and Gemini context."""
    for root_name in ("skills", "agents", "commands"):
        yield from sorted((ROOT / root_name).rglob("*.md"))
    gemini_md = ROOT / "GEMINI.md"
    if gemini_md.is_file():
        yield gemini_md


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


def frontmatter_name(fm):
    for line in fm.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def frontmatter_description(fm):
    """Unfold a `description:` scalar or `>` / `|` block without PyYAML."""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        rest = line.split(":", 1)[1].strip()
        folded = rest.startswith(">")
        literal = rest.startswith("|")
        if folded or literal:
            block = []
            for nxt in lines[i + 1 :]:
                if nxt.startswith("  "):
                    block.append(nxt[2:])
                elif nxt.strip() == "":
                    block.append("")
                else:
                    break
            while block and block[-1] == "":
                block.pop()
            if literal:
                return "\n".join(block)
            paras, para = [], []
            for item in block:
                if item.strip() == "":
                    if para:
                        paras.append(" ".join(para))
                        para = []
                else:
                    para.append(item.strip())
            if para:
                paras.append(" ".join(para))
            return "\n\n".join(paras)
        return rest.strip().strip("\"'")
    return None


def main():
    # 1. JSON manifests
    manifests = [
        "plugin.json",
        ".plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".agents/plugins/marketplace.json",
        "package.json",
        "gemini-extension.json",
    ]
    parsed = {m: load_json(m) for m in manifests}

    portable = parsed.get("plugin.json") or {}
    check(
        portable.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "plugin.json: missing Agent Plugins 1.0 schema",
    )
    check(portable.get("name") == "pixeltable", "plugin.json: name must be 'pixeltable'")
    openai_extension = ((portable.get("extensions") or {}).get("com.openai") or {})
    codex = parsed.get(".codex-plugin/plugin.json") or {}
    check(
        openai_extension.get("interface") == codex.get("interface"),
        "plugin.json OpenAI interface must match .codex-plugin compatibility metadata",
    )
    check(codex.get("skills") == "./skills/", ".codex-plugin/plugin.json: skills must point to ./skills/")

    gemini = parsed.get("gemini-extension.json") or {}
    check(gemini.get("name") == "pixeltable", "gemini-extension.json: name must be 'pixeltable'")
    check(
        gemini.get("contextFileName") == "GEMINI.md",
        "gemini-extension.json: contextFileName must be GEMINI.md",
    )
    check((ROOT / "GEMINI.md").is_file(), "missing GEMINI.md (Gemini CLI context file)")
    mcp = gemini.get("mcpServers") or {}
    cloud = mcp.get("pixeltable-cloud") or {}
    local = mcp.get("pixeltable") or {}
    check(
        cloud.get("httpUrl") == "https://www.pixeltable.com/mcp/cloud",
        "gemini-extension.json: pixeltable-cloud must use the hosted Cloud MCP httpUrl",
    )
    check(
        "Authorization" not in (cloud.get("headers") or {}),
        "gemini-extension.json: Cloud MCP OAuth is handled by Gemini CLI; no auth header",
    )
    check(local.get("command") == "uvx", "gemini-extension.json: pixeltable MCP must run via uvx")
    check(
        "mcp-server-pixeltable-developer" in (local.get("args") or []),
        "gemini-extension.json: pixeltable MCP must invoke mcp-server-pixeltable-developer",
    )
    setting_vars = [s.get("envVar") for s in (gemini.get("settings") or []) if isinstance(s, dict)]
    check(
        "PIXELTABLE_HOME" in setting_vars,
        "gemini-extension.json: settings must declare PIXELTABLE_HOME for the local MCP",
    )
    check(
        not any(isinstance(v, str) and "API_KEY" in v for v in setting_vars),
        "gemini-extension.json: do not declare an API key (Cloud OAuth is handled by Gemini CLI)",
    )

    marketplace = parsed.get(".agents/plugins/marketplace.json") or {}
    entries = marketplace.get("plugins") or []
    entry = next((item for item in entries if item.get("name") == "pixeltable"), None)
    check(entry is not None, ".agents/plugins/marketplace.json: missing pixeltable entry")
    if entry is not None:
        source = entry.get("source") or {}
        path = source.get("path")
        check(source.get("source") == "local", "Codex marketplace source must be local")
        check(
            isinstance(path, str) and (ROOT / path).resolve() == ROOT,
            "Codex marketplace path must resolve to plugin root",
        )

    # 2. Component dir pointers resolve (.plugin / .cursor-plugin)
    for m in (".plugin/plugin.json", ".cursor-plugin/plugin.json"):
        data = parsed.get(m)
        if not data:
            continue
        for key in ("skills", "agents", "commands"):
            if key in data:
                check((ROOT / data[key]).is_dir(), f"{m}: '{key}' dir not found: {data[key]}")

    # 3. SKILL.md frontmatter (Agent Skills spec: name, description <= 1024)
    skill_files = list((ROOT / "skills").glob("*/SKILL.md"))
    check(len(skill_files) >= 1, "no skills/*/SKILL.md found")
    found_dirs = {sf.parent.name for sf in skill_files}
    check(
        TEACHING_SKILL_DIR in found_dirs,
        f"missing teaching skill directory skills/{TEACHING_SKILL_DIR}",
    )
    missing = [n for n in DISCOVERY_SKILL_NAMES if n not in found_dirs]
    check(not missing, f"missing discovery skill directories: {', '.join(missing)}")
    extra = sorted(found_dirs - {TEACHING_SKILL_DIR} - set(DISCOVERY_SKILL_NAMES))
    check(not extra, f"unexpected skills/ directories: {', '.join(extra)}")
    install_sh = (ROOT / "install.sh").read_text(encoding="utf-8", errors="ignore")
    for name in DISCOVERY_SKILL_NAMES:
        check(name in install_sh, f"install.sh: missing discovery skill {name}")
    for sf in skill_files:
        fm = frontmatter(sf)
        rel = sf.relative_to(ROOT)
        folder = sf.parent.name
        check("name:" in fm, f"{rel}: missing 'name' in frontmatter")
        check("description:" in fm, f"{rel}: missing 'description' in frontmatter")
        name = frontmatter_name(fm)
        expected = TEACHING_SKILL_NAME if folder == TEACHING_SKILL_DIR else folder
        check(name == expected, f"{rel}: frontmatter name {name!r} must be {expected!r}")
        desc = frontmatter_description(fm) or ""
        check(bool(desc.strip()), f"{rel}: empty description")
        check(
            len(desc) <= MAX_DESCRIPTION_LENGTH,
            f"{rel}: description is {len(desc)} chars, spec max is {MAX_DESCRIPTION_LENGTH}",
        )
        if folder == TEACHING_SKILL_DIR:
            continue
        body = sf.read_text(encoding="utf-8", errors="ignore")
        n = len(body.splitlines())
        check(
            n < MAX_DISCOVERY_SKILL_LINES,
            f"{rel}: {n} lines, discovery skills must stay under {MAX_DISCOVERY_SKILL_LINES}",
        )
        check(
            "npx skills add pixeltable/pixeltable-skill" in body,
            f"{rel}: must point at `npx skills add pixeltable/pixeltable-skill`",
        )
        check(
            "load the `pixeltable` skill" in body.lower()
            or "Load the `pixeltable` skill" in body,
            f"{rel}: must tell the agent to load the pixeltable skill",
        )

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
        "plugin.json": lambda d: d.get("version"),
        ".plugin/plugin.json": lambda d: d.get("version"),
        ".cursor-plugin/plugin.json": lambda d: d.get("version"),
        ".claude-plugin/plugin.json": lambda d: d.get("version"),
        ".claude-plugin/marketplace.json": lambda d: (d.get("metadata") or {}).get("version"),
        ".codex-plugin/plugin.json": lambda d: d.get("version"),
        "package.json": lambda d: d.get("version"),
        "gemini-extension.json": lambda d: d.get("version"),
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
        openai_yaml = sf.parent / "agents" / "openai.yaml"
        check(openai_yaml.is_file(), f"{sf.parent.relative_to(ROOT)}: missing agents/openai.yaml")
        if openai_yaml.is_file():
            metadata = openai_yaml.read_text(encoding="utf-8", errors="ignore")
            check("display_name:" in metadata, f"{openai_yaml.relative_to(ROOT)}: missing display_name")
            check("short_description:" in metadata, f"{openai_yaml.relative_to(ROOT)}: missing short_description")
    check(
        len(set(versions.values())) <= 1,
        "version mismatch (all manifests + SKILL.md must match): "
        + "; ".join(f"{k}={v}" for k, v in sorted(versions.items())),
    )

    # 6. The docs must not teach what the hook flags.
    #    Only fenced python blocks are linted: an agent copies those. Prose and the
    #    "Wrong" column of the API-traps tables quote bad forms deliberately.
    sys.path.insert(0, str(ROOT / "hooks"))
    try:
        from validate_antipatterns import CHECKS
    except ImportError as e:  # pragma: no cover - the hook is part of the repo
        errors.append(f"cannot import hook checks: {e}")
        CHECKS = []
    fence = re.compile(r"^```(?:python|py)\n(.*?)^```", re.DOTALL | re.MULTILINE)
    for md in iter_agent_docs():
        body = md.read_text(encoding="utf-8", errors="ignore")
        for i, block in enumerate(fence.findall(body), 1):
            try:
                ast.parse(block)
            except SyntaxError as e:
                check(
                    False,
                    f"{md.relative_to(ROOT)}: python block {i} does not parse: {e.msg}",
                )
            for entry in CHECKS:
                pattern, severity, message, gate = entry
                if severity != "error":
                    continue
                if gate is not None and not gate.search(block):
                    continue
                hit = pattern.search(block)
                check(
                    hit is None,
                    f"{md.relative_to(ROOT)}: a python block matches a hook 'error' check "
                    f"({hit.group(0).strip()!r} -- {message.split('.')[0]})"
                    if hit
                    else "",
                )

    # 7. Documented pixeltable modules must be real, and not the deprecated shim.
    KNOWN_MODULES = {
        "anthropic", "array", "audio", "bedrock", "bfl", "date", "deepseek", "document",
        "fabric", "fal", "fireworks", "gemini", "globals", "groq", "huggingface", "image",
        "jina", "json", "llama_cpp", "math", "mistralai", "nebius", "net", "ollama",
        "openai", "openrouter", "replicate", "runwayml", "string", "timestamp", "together",
        "twelvelabs", "util", "uuid", "video", "vision", "vllm", "voyageai", "whisper",
        "whisperx", "yolox",
    }
    mod_ref = re.compile(r"pixeltable\.functions\.(\w+)")
    for md in iter_agent_docs():
        body = md.read_text(encoding="utf-8", errors="ignore")
        for mod in sorted(set(mod_ref.findall(body))):
            check(
                mod in KNOWN_MODULES,
                f"{md.relative_to(ROOT)}: unknown module pixeltable.functions.{mod}",
            )

    # 8. AGENTS.md caps SKILL.md length; nothing enforced it until now.
    for sf in skill_files:
        n = len(sf.read_text(encoding="utf-8", errors="ignore").splitlines())
        check(n < 500, f"{sf.relative_to(ROOT)}: {n} lines, must stay under 500")

    # 9. An agent has no TTY, and a pending `pxt service update` without -f exits 3 there.
    shell_fence = re.compile(r"^```(?:bash|sh|shell)\n(.*?)^```", re.DOTALL | re.MULTILINE)
    for md in iter_agent_docs():
        for block in shell_fence.findall(md.read_text(encoding="utf-8", errors="ignore")):
            for line in block.splitlines():
                command = line.split("#", 1)[0]
                if re.search(r"\bpxt service update\b", command):
                    check(
                        re.search(r"\s-(?:f|n)\b|--force\b|--dry-run\b", command) is not None,
                        f"{md.relative_to(ROOT)}: `pxt service update` without -f: {command.strip()!r}",
                    )

    if errors:
        print(f"FAIL ({len(errors)} of {checks} checks):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {checks} checks passed ({len(skill_files)} skill(s)).")


if __name__ == "__main__":
    main()
