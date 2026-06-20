#!/usr/bin/env python3
"""PostToolUse hook: flag deprecated/incorrect Pixeltable APIs and anti-patterns.

Reads the Claude Code hook payload from stdin, inspects Python content written or
edited, and returns non-blocking guidance via hookSpecificOutput.additionalContext.
Pure stdlib; no third-party dependencies.
"""
import json
import re
import sys

# (compiled regex, severity, message). Severity: "error" = wrong/deprecated API,
# "recommended" = redundant framework Pixeltable already replaces.
CHECKS = [
    (
        re.compile(r"from\s+pixeltable\.iterators\s+import\s+FrameIterator|\bFrameIterator\b"),
        "error",
        "Deprecated `FrameIterator`. Use `from pixeltable.functions.video import frame_iterator` "
        "and pass `frame_iterator(t.video, fps=...)` to `create_view`.",
    ),
    (
        re.compile(r"openai\.vision|functions\.openai\s+import\s+[^\n]*\bvision\b"),
        "error",
        "`openai.vision` does not exist. Use `chat_completions` with `image_url` content blocks "
        "for image understanding.",
    ),
    (
        re.compile(r"\.similarity\(\s*(?!string\s*=)[^)\s]"),
        "error",
        "Positional `.similarity(...)` call. Always use the keyword form: "
        "`column.similarity(string=query)`.",
    ),
    (
        re.compile(r"@pxt\.query[\s\S]*?sim=sim"),
        "error",
        "`sim=sim` in `@pxt.query` breaks `.collect()` and `pxt serve`. Alias similarity as "
        "`score=sim` (any name other than `sim`).",
    ),
    (
        re.compile(
            r"^\s*(?:from|import)\s+(langchain|langgraph|llama_index|llama-index|haystack|"
            r"chromadb|faiss|pinecone|qdrant|weaviate|pgvector)\b",
            re.MULTILINE,
        ),
        "recommended",
        "Detected a framework/vector-DB that Pixeltable replaces (chunking, embedding indexes, "
        "retrieval, and tool-calling are built in). See the `pixeltable` skill "
        "`references/anti-patterns.md`.",
    ),
]


def extract_python_content(payload):
    """Return (file_path, text) for Write/Edit/MultiEdit on a .py file, else (None, None)."""
    tool = payload.get("tool_name") or payload.get("toolName") or ""
    if tool not in {"Write", "Edit", "MultiEdit"}:
        return None, None
    ti = payload.get("tool_input") or payload.get("toolInput") or {}
    file_path = ti.get("file_path") or ti.get("path") or ""
    if not file_path.endswith(".py"):
        return None, None
    parts = []
    if isinstance(ti.get("content"), str):
        parts.append(ti["content"])
    if isinstance(ti.get("new_string"), str):
        parts.append(ti["new_string"])
    edits = ti.get("edits")
    if isinstance(edits, list):
        for e in edits:
            if isinstance(e, dict) and isinstance(e.get("new_string"), str):
                parts.append(e["new_string"])
    return file_path, "\n".join(parts)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path, text = extract_python_content(payload)
    if not text:
        sys.exit(0)

    findings = []
    for pattern, severity, message in CHECKS:
        if pattern.search(text):
            marker = "FIX" if severity == "error" else "CONSIDER"
            findings.append(f"[{marker}] {message}")

    if not findings:
        sys.exit(0)

    context = (
        f"Pixeltable review of {file_path}:\n- " + "\n- ".join(findings)
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
