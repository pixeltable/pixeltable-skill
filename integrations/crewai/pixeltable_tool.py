"""CrewAI Tools for Pixeltable multimodal data operations.

Install:
    pip install pixeltable crewai crewai-tools

Usage:
    from crewai import Agent
    from pixeltable_tool import (
        PixeltableListTablesTool,
        PixeltableCreateTableTool,
        PixeltableInsertTool,
        PixeltableQueryTool,
        PixeltableSimilaritySearchTool,
    )

    researcher = Agent(
        role="Data Analyst",
        goal="Manage multimodal data pipelines",
        tools=[
            PixeltableListTablesTool(),
            PixeltableCreateTableTool(),
            PixeltableInsertTool(),
            PixeltableQueryTool(),
            PixeltableSimilaritySearchTool(),
        ],
    )
"""

from __future__ import annotations

import json
from typing import Optional, Type

import pixeltable as pxt
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class _ListTablesInput(BaseModel):
    """No input required."""


class PixeltableListTablesTool(BaseTool):
    name: str = 'pixeltable_list_tables'
    description: str = (
        'List all Pixeltable tables and directories. '
        'Always call this before creating tables to avoid duplicates.'
    )
    args_schema: Type[BaseModel] = _ListTablesInput

    def _run(self) -> str:
        tables = pxt.list_tables()
        return json.dumps(tables, default=str)


class _CreateTableInput(BaseModel):
    path: str = Field(..., description='Dot-separated table path (e.g., "mydir.articles").')
    schema_json: str = Field(
        ...,
        description=(
            'JSON object mapping column names to type strings. '
            'Types: String, Int, Float, Bool, Timestamp, Json, Image, Video, Audio, Document, Array.'
        ),
    )
    if_exists: str = Field('ignore', description='What to do if table exists: "ignore" or "error".')


class PixeltableCreateTableTool(BaseTool):
    name: str = 'pixeltable_create_table'
    description: str = 'Create a Pixeltable table with multimodal column types.'
    args_schema: Type[BaseModel] = _CreateTableInput

    def _run(self, path: str, schema_json: str, if_exists: str = 'ignore') -> str:
        type_map = {
            'String': pxt.String, 'Int': pxt.Int, 'Float': pxt.Float,
            'Bool': pxt.Bool, 'Timestamp': pxt.Timestamp, 'Json': pxt.Json,
            'Image': pxt.Image, 'Video': pxt.Video, 'Audio': pxt.Audio,
            'Document': pxt.Document, 'Array': pxt.Array,
        }
        raw_schema = json.loads(schema_json)
        schema = {}
        for col_name, col_type in raw_schema.items():
            if col_type not in type_map:
                return f'Error: unknown type "{col_type}". Supported: {list(type_map.keys())}'
            schema[col_name] = type_map[col_type]

        parts = path.rsplit('.', 1)
        if len(parts) == 2:
            pxt.create_dir(parts[0], if_exists='ignore')

        t = pxt.create_table(path, schema, if_exists='ignore' if if_exists == 'ignore' else 'error')
        cols = {c.name: str(c.col_type) for c in t.columns()}
        return json.dumps({'table': path, 'columns': cols, 'rows': t.count()})


class _InsertInput(BaseModel):
    path: str = Field(..., description='Dot-separated table path.')
    rows_json: str = Field(
        ...,
        description='JSON array of row objects mapping column names to values. Use file paths or URLs for media.',
    )


class PixeltableInsertTool(BaseTool):
    name: str = 'pixeltable_insert'
    description: str = 'Insert rows into a Pixeltable table. Supports text, numbers, and media (images, video, audio, documents) via paths or URLs.'
    args_schema: Type[BaseModel] = _InsertInput

    def _run(self, path: str, rows_json: str) -> str:
        t = pxt.get_table(path)
        rows = json.loads(rows_json)
        result = t.insert(rows)
        return json.dumps({
            'inserted': result.num_rows,
            'errors': result.num_excs,
            'total_rows': t.count(),
        })


class _QueryInput(BaseModel):
    path: str = Field(..., description='Dot-separated table path.')
    limit: int = Field(20, description='Maximum rows to return.')
    columns: Optional[str] = Field(None, description='Comma-separated column names. Returns all if omitted.')


class PixeltableQueryTool(BaseTool):
    name: str = 'pixeltable_query'
    description: str = 'Query and collect rows from a Pixeltable table.'
    args_schema: Type[BaseModel] = _QueryInput

    def _run(self, path: str, limit: int = 20, columns: Optional[str] = None) -> str:
        t = pxt.get_table(path)
        if columns:
            col_names = [c.strip() for c in columns.split(',')]
            col_refs = [getattr(t, name) for name in col_names]
            df = t.select(*col_refs).limit(limit).collect()
        else:
            df = t.limit(limit).collect()
        return df.to_json(orient='records', default_handler=str)


class _SimilaritySearchInput(BaseModel):
    path: str = Field(..., description='Dot-separated table path.')
    column: str = Field(..., description='Column name with an embedding index.')
    query: str = Field(..., description='Search query text.')
    limit: int = Field(10, description='Maximum number of results.')


class PixeltableSimilaritySearchTool(BaseTool):
    name: str = 'pixeltable_similarity_search'
    description: str = (
        'Run similarity search on a Pixeltable column that has an embedding index. '
        'Returns results ranked by relevance with similarity scores.'
    )
    args_schema: Type[BaseModel] = _SimilaritySearchInput

    def _run(self, path: str, column: str, query: str, limit: int = 10) -> str:
        t = pxt.get_table(path)
        col_ref = getattr(t, column)
        sim = col_ref.similarity(string=query)
        df = t.order_by(sim, asc=False).limit(limit).select(col_ref, sim=sim).collect()
        return df.to_json(orient='records', default_handler=str)


class _SchemaInput(BaseModel):
    path: str = Field(..., description='Dot-separated table path.')


class PixeltableGetSchemaTool(BaseTool):
    name: str = 'pixeltable_get_schema'
    description: str = 'Get the schema and row count of an existing Pixeltable table.'
    args_schema: Type[BaseModel] = _SchemaInput

    def _run(self, path: str) -> str:
        t = pxt.get_table(path)
        cols = {c.name: str(c.col_type) for c in t.columns()}
        return json.dumps({'table': path, 'columns': cols, 'rows': t.count()})
