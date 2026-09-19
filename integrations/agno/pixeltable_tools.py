"""Agno Toolkit for Pixeltable multimodal data operations.

Install:
    pip install pixeltable agno

Usage:
    from agno.agent import Agent
    from integrations.agno import PixeltableTools

    agent = Agent(tools=[PixeltableTools()])
    agent.print_response("Create a table for storing articles with text and images")
"""

from __future__ import annotations

import ast
import inspect
import json
import operator
import types
from typing import Any

import pixeltable as pxt
import pixeltable.functions as pxtf

from agno.tools import Toolkit


def _schema(t: pxt.Table) -> dict[str, str]:
    """Column name to type, from Table.get_metadata(); Table.columns() returns names only."""
    return {name: col['type_'] for name, col in t.get_metadata()['columns'].items()}


def _rows_json(rows: Any) -> str:
    """Serialize a collect() ResultSet, which has no to_json()."""
    return json.dumps(rows.to_pandas().to_dict(orient='records'), default=str)


_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


_TYPES = {
    'String': pxt.String, 'Int': pxt.Int, 'Float': pxt.Float,
    'Bool': pxt.Bool, 'Timestamp': pxt.Timestamp, 'Json': pxt.Json,
    'Image': pxt.Image, 'Video': pxt.Video, 'Audio': pxt.Audio,
    'Document': pxt.Document, 'Array': pxt.Array,
}


def _is_pxt_module(value: Any) -> bool:
    return isinstance(value, types.ModuleType) and value.__name__.startswith('pixeltable.functions')


def _is_expr_method(value: Any) -> bool:
    """A bound method of an Expr, such as `t.col.astype`; MethodRefs like `t.col.upper` are Exprs."""
    return inspect.ismethod(value) and isinstance(value.__self__, pxt.exprs.Expr)


def _eval_ast_node(node: ast.AST, scope: dict[str, Any]) -> Any:
    """Evaluate an agent-supplied expression into a Pixeltable Expr.

    The expression comes from a model, so every step is allowlisted: no name that starts
    with an underscore, attributes only on the table, an Expr, `pxt` (types only) or a
    `pixeltable.functions` module, and calls only to Pixeltable functions and Expr
    methods. Anything else raises ValueError or TypeError before it is evaluated.
    """
    if isinstance(node, ast.Expression):
        return _eval_ast_node(node.body, scope)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in scope:
            return scope[node.id]
        raise ValueError(f'Unknown identifier: {node.id}')
    if isinstance(node, ast.Attribute):
        if node.attr.startswith('_'):
            raise ValueError(f'Attribute not allowed: {node.attr}')
        value = _eval_ast_node(node.value, scope)
        if value is pxt:
            if node.attr not in _TYPES:
                raise ValueError(f'pxt.{node.attr} is not a column type')
            return _TYPES[node.attr]
        if isinstance(value, (pxt.Table, pxt.exprs.Expr)):
            result = getattr(value, node.attr)
            if isinstance(result, pxt.exprs.Expr) or _is_expr_method(result):
                return result
            raise TypeError(f'{node.attr} is not a column or an expression method')
        if _is_pxt_module(value):
            result = getattr(value, node.attr)
            if not (_is_pxt_module(result) or isinstance(result, pxt.func.Function)):
                raise ValueError(f'{node.attr} is not a Pixeltable function')
            return result
        raise ValueError(f'Attribute access not allowed on {type(value).__name__}')
    if isinstance(node, ast.Call):
        func = _eval_ast_node(node.func, scope)
        if not (isinstance(func, (pxt.func.Function, pxt.exprs.Expr)) or _is_expr_method(func)):
            raise TypeError('Only Pixeltable functions and expression methods can be called')
        args = [_eval_ast_node(arg, scope) for arg in node.args]
        keywords = {kw.arg: _eval_ast_node(kw.value, scope) for kw in node.keywords if kw.arg is not None}
        return func(*args, **keywords)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _SAFE_OPS:
            return _SAFE_OPS[op_type](_eval_ast_node(node.left, scope), _eval_ast_node(node.right, scope))
        raise ValueError(f'Unsupported binary operator: {op_type.__name__}')
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _SAFE_OPS:
            return _SAFE_OPS[op_type](_eval_ast_node(node.operand, scope))
        raise ValueError(f'Unsupported unary operator: {op_type.__name__}')
    if isinstance(node, ast.Subscript):
        val = _eval_ast_node(node.value, scope)
        if not isinstance(val, pxt.exprs.Expr):
            raise TypeError('Subscripts are only allowed on column expressions')
        return val[_eval_ast_node(node.slice, scope)]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_ast_node(elt, scope) for elt in node.elts]
    raise ValueError(f'Unsupported AST node: {type(node).__name__}')


def _safe_eval_expr(expression: str, scope: dict[str, Any]) -> pxt.exprs.Expr:
    tree = ast.parse(expression.strip(), mode='eval')
    result = _eval_ast_node(tree, scope)
    if not isinstance(result, pxt.exprs.Expr):
        raise TypeError('The expression must produce a column expression')
    return result


class PixeltableTools(Toolkit):
    """Toolkit that gives Agno agents full access to Pixeltable operations.

    Supports table management, data insertion, querying, computed columns,
    embedding indexes, and similarity search across multimodal data.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            name='pixeltable_tools',
            tools=[
                self.list_tables,
                self.create_table,
                self.get_table_schema,
                self.insert_rows,
                self.query_table,
                self.add_computed_column,
                self.add_embedding_index,
                self.similarity_search,
                self.drop_table,
            ],
            instructions=(
                'Use these tools to manage multimodal data with Pixeltable. '
                'Always check list_tables before creating new tables. '
                'Use if_exists="ignore" for idempotent operations.'
            ),
            **kwargs,
        )

    def list_tables(self) -> str:
        """List all Pixeltable tables and directories.

        Returns:
            JSON list of table paths.
        """
        tables = pxt.list_tables()
        return json.dumps(tables, default=str)

    def create_table(self, path: str, schema_json: str, if_exists: str = 'ignore') -> str:
        """Create a Pixeltable table with the given schema.

        Args:
            path: Dot-separated table path (e.g., "mydir.articles").
            schema_json: JSON object mapping column names to type strings.
                Supported types: String, Int, Float, Bool, Timestamp, Json,
                Image, Video, Audio, Document, Array.
            if_exists: What to do if the table exists ("ignore" or "error").

        Returns:
            Confirmation message with table info.
        """
        type_map = _TYPES
        raw_schema = json.loads(schema_json)
        schema = {}
        for col_name, col_type in raw_schema.items():
            if col_type not in type_map:
                return f'Error: unknown type "{col_type}". Supported: {list(type_map.keys())}'
            schema[col_name] = type_map[col_type]

        parts = path.rsplit('.', 1)
        if len(parts) == 2:
            pxt.create_dir(parts[0], if_exists='ignore')

        if_exists_val = 'ignore' if if_exists == 'ignore' else 'error'
        t = pxt.create_table(path, schema, if_exists=if_exists_val)
        cols = _schema(t)
        return json.dumps({'table': path, 'columns': cols, 'rows': t.count()})

    def get_table_schema(self, path: str) -> str:
        """Get schema and row count for an existing table.

        Args:
            path: Dot-separated table path.

        Returns:
            JSON with column names/types and row count.
        """
        t = pxt.get_table(path)
        cols = _schema(t)
        return json.dumps({'table': path, 'columns': cols, 'rows': t.count()})

    def insert_rows(self, path: str, rows_json: str) -> str:
        """Insert rows into a Pixeltable table.

        Args:
            path: Dot-separated table path.
            rows_json: JSON array of objects, each mapping column names to values.
                For media columns, provide file paths or URLs.

        Returns:
            Confirmation with number of rows inserted.
        """
        t = pxt.get_table(path)
        rows = json.loads(rows_json)
        result = t.insert(rows)
        return json.dumps({
            'inserted': result.num_rows,
            'errors': result.num_excs,
            'total_rows': t.count(),
        })

    def query_table(self, path: str, limit: int = 20, columns: str | None = None) -> str:
        """Query rows from a Pixeltable table.

        Args:
            path: Dot-separated table path.
            limit: Maximum number of rows to return.
            columns: Optional comma-separated column names. Returns all if omitted.

        Returns:
            JSON array of row objects.
        """
        t = pxt.get_table(path)
        if columns:
            col_names = [c.strip() for c in columns.split(',')]
            col_refs = [getattr(t, name) for name in col_names]
            rows = t.select(*col_refs).limit(limit).collect()
        else:
            rows = t.limit(limit).collect()
        return _rows_json(rows)

    def add_computed_column(self, path: str, column_name: str, expression: str) -> str:
        """Add a computed column using a Pixeltable expression.

        Args:
            path: Dot-separated table path.
            column_name: Name for the new computed column.
            expression: Pixeltable expression over `t` (the table), `pxtf`
                (`pixeltable.functions`) and `pxt` column types, e.g. "t.text.upper()",
                "t.price * 1.1", "pxtf.string.len(t.text)". Only Pixeltable functions and
                column methods can be called.

        Returns:
            Confirmation message.
        """
        t = pxt.get_table(path)
        expr = _safe_eval_expr(expression, {'t': t, 'pxt': pxt, 'pxtf': pxtf})
        t.add_computed_column(**{column_name: expr}, if_exists='ignore')
        return json.dumps({'status': 'ok', 'column': column_name, 'table': path})

    def add_embedding_index(
        self, path: str, column: str, embedding_function: str, metric: str = 'cosine'
    ) -> str:
        """Add an embedding index to a text or image column.

        Args:
            path: Dot-separated table path.
            column: Column name to index.
            embedding_function: Fully qualified function reference
                (e.g., "pixeltable.functions.openai.embeddings.using(model='text-embedding-3-small')" or
                "pixeltable.functions.huggingface.sentence_transformer.using(model_id='sentence-transformers/all-MiniLM-L6-v2')").
            metric: Distance metric ("cosine", "ip", or "l2").

        Returns:
            Confirmation message.
        """
        import importlib

        t = pxt.get_table(path)

        if '.using(' in embedding_function:
            base, call = embedding_function.rsplit('.using(', 1)
            module_path, attr = base.rsplit('.', 1)
            mod = importlib.import_module(module_path)
            func = getattr(mod, attr)
            tree = ast.parse(f'call({call}', mode='eval')
            call_node = tree.body
            if not isinstance(call_node, ast.Call):
                raise ValueError(f'Invalid .using call expression: {call}')
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call_node.keywords if kw.arg is not None}
            embed_fn = func.using(**kwargs)
        else:
            module_path, attr = embedding_function.rsplit('.', 1)
            mod = importlib.import_module(module_path)
            embed_fn = getattr(mod, attr)

        t.add_embedding_index(column, embedding=embed_fn, metric=metric, if_exists='ignore')
        return json.dumps({'status': 'ok', 'column': column, 'metric': metric, 'table': path})

    def similarity_search(self, path: str, column: str, query: str, limit: int = 10) -> str:
        """Run similarity search on an indexed column.

        Args:
            path: Dot-separated table path.
            column: Column with an embedding index.
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            JSON array of results with similarity scores.
        """
        t = pxt.get_table(path)
        col_ref = getattr(t, column)
        sim = col_ref.similarity(string=query)
        rows = t.order_by(sim, asc=False).limit(limit).select(col_ref, score=sim).collect()
        return _rows_json(rows)

    def drop_table(self, path: str, force: bool = False) -> str:
        """Drop a Pixeltable table.

        Args:
            path: Dot-separated table path.
            force: If True, drop even if the table has dependents.

        Returns:
            Confirmation message.
        """
        pxt.drop_table(path, force=force)
        return json.dumps({'status': 'dropped', 'table': path})
