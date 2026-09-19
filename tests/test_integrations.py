"""Structural tests for the framework integrations. Run: python3 tests/test_integrations.py

Pure stdlib: the adapters import agno/crewai, which are not installed here, so the checks
read the source with ast. They guard the regression where helper functions inserted into
the class body turned the remaining methods into nested functions.
"""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGNO = ROOT / "integrations" / "agno" / "pixeltable_tools.py"
CREWAI = ROOT / "integrations" / "crewai" / "pixeltable_tool.py"

# Keyword arguments that no longer exist on the Pixeltable 0.7.8 SDK.
RETIRED_KWARGS = {"if_not_exists"}


def class_methods(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def nested_defs(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            found += [n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n is not node]
    return found


def call_kwargs(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {kw.arg for node in ast.walk(tree) if isinstance(node, ast.Call) for kw in node.keywords}


class AgnoToolkit(unittest.TestCase):
    def test_every_tool_is_a_method(self):
        methods = class_methods(AGNO)["PixeltableTools"]
        for name in [
            "list_tables", "create_table", "get_table_schema", "insert_rows", "query_table",
            "add_computed_column", "add_embedding_index", "similarity_search", "drop_table",
        ]:
            self.assertIn(name, methods)

    def test_no_method_is_nested_in_a_helper(self):
        self.assertEqual([], nested_defs(AGNO))

    def test_no_retired_sdk_kwargs(self):
        self.assertFalse(call_kwargs(AGNO) & RETIRED_KWARGS)


class CrewAITools(unittest.TestCase):
    def test_every_tool_has_run(self):
        for name, methods in class_methods(CREWAI).items():
            if name.startswith("Pixeltable"):
                self.assertIn("_run", methods, name)

    def test_no_retired_sdk_kwargs(self):
        self.assertFalse(call_kwargs(CREWAI) & RETIRED_KWARGS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
