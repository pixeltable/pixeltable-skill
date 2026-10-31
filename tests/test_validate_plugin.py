"""Skill discovery used by scripts/validate_plugin.py. Run: python3 tests/test_validate_plugin.py

Pure stdlib (unittest).
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_plugin", ROOT / "scripts" / "validate_plugin.py"
)
validate_plugin = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_plugin)


def found(skills: Path) -> set[str]:
    return {p.relative_to(skills).as_posix() for p in validate_plugin.skill_markdown_files(skills)}


class SkillDiscovery(unittest.TestCase):
    def test_only_the_canonical_skill_matches(self):
        with tempfile.TemporaryDirectory() as raw:
            skills = Path(raw)
            canonical = skills / "pixeltable-skill"
            canonical.mkdir()
            (canonical / "SKILL.md").write_text("name: pixeltable\n", encoding="utf-8")
            self.assertEqual(found(skills), {"pixeltable-skill/SKILL.md"})

    def test_nested_skill_is_discovered(self):
        with tempfile.TemporaryDirectory() as raw:
            skills = Path(raw)
            canonical = skills / "pixeltable-skill"
            canonical.mkdir()
            (canonical / "SKILL.md").write_text("x", encoding="utf-8")
            nested = skills / "nested" / "video-search"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text("x", encoding="utf-8")
            self.assertEqual(
                found(skills),
                {"pixeltable-skill/SKILL.md", "nested/video-search/SKILL.md"},
            )


if __name__ == "__main__":
    unittest.main()
