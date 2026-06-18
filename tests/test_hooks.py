#!/usr/bin/env python3
"""Tests for the pure-Python plugin hooks. Run: python3 tests/test_hooks.py

Pure stdlib (unittest); no third-party deps, mirroring the repo's no-Node policy.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "hooks" / "validate_antipatterns.py"
ORIENT = ROOT / "hooks" / "session_orientation.py"


def run(script, payload):
    p = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert p.returncode == 0, f"{script} exited {p.returncode}: {p.stderr}"
    return p.stdout.strip()


def context(out):
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""


class ValidateAntiPatterns(unittest.TestCase):
    def write(self, content, path="app.py", tool="Write", key="content"):
        return run(VALIDATE, {"tool_name": tool, "tool_input": {"file_path": path, key: content}})

    def test_flags_frame_iterator(self):
        self.assertIn("frame_iterator", context(self.write(
            "from pixeltable.iterators import FrameIterator\n")))

    def test_flags_positional_similarity(self):
        self.assertIn("similarity", context(self.write("r = t.txt.similarity(query)\n")))

    def test_flags_openai_vision(self):
        self.assertIn("chat_completions", context(self.write("x = openai.vision(img)\n")))

    def test_flags_framework_import(self):
        out = self.write("from langchain.text_splitter import X\n", key="new_string", tool="Edit")
        self.assertIn("replaces", context(out))

    def test_silent_on_correct_code(self):
        self.assertEqual("", self.write(
            "from pixeltable.functions.video import frame_iterator\n"
            "r = t.txt.similarity(string=query)\n"))

    def test_silent_on_non_python(self):
        self.assertEqual("", self.write("FrameIterator", path="notes.md"))

    def test_silent_on_non_edit_tool(self):
        self.assertEqual("", run(VALIDATE, {"tool_name": "Read", "tool_input": {"file_path": "a.py"}}))


class SessionOrientation(unittest.TestCase):
    def test_detects_pixeltable_project(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "requirements.txt").write_text("pixeltable>=0.2\n")
            self.assertIn("Pixeltable", context(run(ORIENT, {"cwd": d})))

    def test_detects_via_import(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "main.py").write_text("import pixeltable as pxt\n")
            self.assertNotEqual("", run(ORIENT, {"cwd": d}))

    def test_silent_on_unrelated_project(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "requirements.txt").write_text("flask\nrequests\n")
            self.assertEqual("", run(ORIENT, {"cwd": d}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
