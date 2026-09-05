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
        check=False,
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

    def test_similarity_every_valid_modality_is_silent(self):
        """Regression guard: the whitelist once covered only string=, so every other
        modality was flagged FIX -- contradicting core-api.md, which documents them."""
        self.assertEqual("", self.write(
            "a = t.body.similarity(string=q)\n"
            "b = t.img.similarity(image=q)\n"
            "c = t.clip.similarity(video=v)\n"
            "d = t.narration.similarity(audio=a)\n"
            "e = t.doc.similarity(document=d)\n"
            "f = t.emb.similarity(vector=arr)\n"
            "g = t.body.similarity(string=q, idx='body_idx')\n"
            "h = t.body.similarity(\n    string=q,\n)\n"))

    def test_flags_named_deprecated_similarity_item(self):
        self.assertIn("similarity", context(self.write("r = t.txt.similarity(item=q)\n")))

    def test_flags_underscore_error_property(self):
        self.assertIn("errortype", context(self.write("t.select(t.summary_errortype).collect()\n")))

    def test_flags_order_by_on_requires_order_by_uda(self):
        self.assertIn("POSITIONAL", context(self.write("make_video(t.frame, order_by=t.pos)\n")))

    def test_flags_pxt_required(self):
        self.assertIn("Required", context(self.write("x: pxt.Required[pxt.String]\n")))

    def test_flags_any_deprecated_iterators_import(self):
        self.assertIn("deprecated shim", context(self.write(
            "from pixeltable.iterators import DocumentSplitter\n")))

    def test_app_file_checks_are_gated_off_in_notebook_style_code(self):
        """No TableModel in the payload: create_table and add_embedding_index are correct."""
        self.assertEqual("", self.write(
            "t = pxt.create_table('dir.docs', {'body': pxt.String})\n"
            "t.add_embedding_index('body', embedding=fn)\n"))

    def test_app_file_checks_fire_when_a_model_is_declared(self):
        out = context(self.write(
            "TableModel = pxt.model_base()\n"
            "t = pxt.create_table('dir.docs', {'body': pxt.String})\n"
            "t.add_embedding_index('body', embedding=fn)\n"))
        self.assertIn("__indexes__", out)
        self.assertIn("must not mutate the catalog", out)

    def test_reads_notebook_edits(self):
        out = run(VALIDATE, {"tool_name": "NotebookEdit", "tool_input": {
            "notebook_path": "explore.ipynb", "new_source": "x = t.txt.similarity(query)\n"}})
        self.assertIn("similarity", context(out))

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

    def test_detects_via_pixeltable_toml(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "pixeltable.toml").write_text("[pixeltable]\n")
            self.assertIn("Pixeltable", context(run(ORIENT, {"cwd": d})))

    def test_silent_on_unrelated_project(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "requirements.txt").write_text("flask\nrequests\n")
            self.assertEqual("", run(ORIENT, {"cwd": d}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
