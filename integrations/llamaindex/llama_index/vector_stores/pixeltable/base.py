"""Pixeltable VectorStore for LlamaIndex.

Bridges LlamaIndex's BasePydanticVectorStore interface with Pixeltable's
embedding index and similarity search.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

import numpy as np
import pixeltable as pxt
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.schema import BaseNode, MetadataMode, TextNode
from llama_index.core.vector_stores.types import (
    BasePydanticVectorStore,
    MetadataFilters,
    VectorStoreQuery,
    VectorStoreQueryResult,
)
from llama_index.core.vector_stores.utils import (
    metadata_dict_to_node,
    node_to_metadata_dict,
)

logger = logging.getLogger(__name__)

_DEFAULT_TABLE = 'llamaindex.documents'
_TEXT_COL = 'text'
_METADATA_COL = 'metadata'
_NODE_ID_COL = 'node_id'
_REF_DOC_ID_COL = 'ref_doc_id'
_EMBEDDING_COL = 'embedding'


class PixeltableVectorStore(BasePydanticVectorStore):
    """LlamaIndex VectorStore backed by a Pixeltable table.

    Pixeltable provides persistent, versioned, multimodal-native storage with
    built-in embedding indexes. This store maps LlamaIndex nodes to Pixeltable
    rows and uses Pixeltable's similarity search for retrieval.

    Args:
        table_name: Dot-separated Pixeltable table path.
        embed_dim: Embedding dimension. Required when creating a new table.
        metric: Distance metric for the embedding index.

    Example:
        .. code-block:: python

            from llama_index.vector_stores.pixeltable import PixeltableVectorStore
            from llama_index.core import VectorStoreIndex, StorageContext

            vector_store = PixeltableVectorStore(
                table_name="mydir.docs",
                embed_dim=1536,
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )
            query_engine = index.as_query_engine()
            response = query_engine.query("What is Pixeltable?")
    """

    stores_text: bool = True
    flat_metadata: bool = True

    table_name: str = Field(default=_DEFAULT_TABLE, description='Pixeltable table path')
    embed_dim: Optional[int] = Field(default=None, description='Embedding dimension')
    metric: str = Field(default='cosine', description='Distance metric')

    _table: Optional[Any] = PrivateAttr(default=None)

    def __init__(
        self,
        table_name: str = _DEFAULT_TABLE,
        embed_dim: Optional[int] = None,
        metric: str = 'cosine',
        **kwargs: Any,
    ):
        super().__init__(
            table_name=table_name,
            embed_dim=embed_dim,
            metric=metric,
            **kwargs,
        )

    def _get_or_create_table(self, embed_dim: Optional[int] = None) -> Any:
        if self._table is not None:
            return self._table

        try:
            self._table = pxt.get_table(self.table_name)
            return self._table
        except Exception:
            pass

        dim = embed_dim or self.embed_dim
        if dim is None:
            raise ValueError(
                'embed_dim is required when creating a new table. '
                'Either pass it to the constructor or ensure the table already exists.'
            )

        parts = self.table_name.rsplit('.', 1)
        if len(parts) == 2:
            pxt.create_dir(parts[0], if_exists='ignore')

        self._table = pxt.create_table(
            self.table_name,
            {
                _NODE_ID_COL: pxt.String,
                _REF_DOC_ID_COL: pxt.String,
                _TEXT_COL: pxt.String,
                _METADATA_COL: pxt.Json,
                _EMBEDDING_COL: pxt.Array[(dim,), pxt.Float],
            },
            if_exists='ignore',
        )
        self._table.add_embedding_index(
            _EMBEDDING_COL,
            metric=self.metric,
            if_exists='ignore',
        )
        return self._table

    @property
    def client(self) -> Any:
        return self._get_or_create_table()

    def add(self, nodes: List[BaseNode], **add_kwargs: Any) -> List[str]:
        """Add nodes with embeddings to the store.

        Args:
            nodes: List of BaseNode objects with embeddings.

        Returns:
            List of node IDs that were added.
        """
        if not nodes:
            return []

        first_embedding = nodes[0].get_embedding()
        dim = len(first_embedding) if first_embedding else self.embed_dim
        t = self._get_or_create_table(embed_dim=dim)

        ids = []
        rows = []
        for node in nodes:
            node_dict = node_to_metadata_dict(node, flat_metadata=self.flat_metadata)
            embedding = node.get_embedding()
            rows.append({
                _NODE_ID_COL: node.node_id,
                _REF_DOC_ID_COL: node.ref_doc_id or '',
                _TEXT_COL: node.get_content(metadata_mode=MetadataMode.NONE),
                _METADATA_COL: node_dict,
                _EMBEDDING_COL: embedding,
            })
            ids.append(node.node_id)

        t.insert(rows)
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """Delete all nodes with the given ref_doc_id.

        Args:
            ref_doc_id: The source document ID whose nodes should be deleted.
        """
        t = self._get_or_create_table()
        ref_col = getattr(t, _REF_DOC_ID_COL)
        t.delete(where=(ref_col == ref_doc_id))

    def delete_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **delete_kwargs: Any,
    ) -> None:
        """Delete nodes by node ID.

        Args:
            node_ids: List of node IDs to delete.
            filters: Not yet supported.
        """
        if node_ids is None:
            return
        t = self._get_or_create_table()
        id_col = getattr(t, _NODE_ID_COL)
        for nid in node_ids:
            t.delete(where=(id_col == nid))

    def clear(self) -> None:
        """Remove all rows from the table."""
        t = self._get_or_create_table()
        t.delete(where=None)

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query the vector store for similar nodes.

        Args:
            query: VectorStoreQuery with query_embedding and similarity_top_k.

        Returns:
            VectorStoreQueryResult with nodes, similarities, and IDs.
        """
        t = self._get_or_create_table()
        embed_col = getattr(t, _EMBEDDING_COL)
        text_col = getattr(t, _TEXT_COL)
        meta_col = getattr(t, _METADATA_COL)
        id_col = getattr(t, _NODE_ID_COL)

        k = query.similarity_top_k

        if query.query_embedding is not None:
            vec = np.array(query.query_embedding, dtype=np.float32)
            sim = embed_col.similarity(vector=vec)
        elif query.query_str is not None:
            sim = embed_col.similarity(string=query.query_str)
        else:
            raise ValueError('Either query_embedding or query_str must be provided.')

        result_set = (
            t.order_by(sim, asc=False)
            .limit(k)
            .select(text_col, meta_col, id_col, sim=sim)
            .collect()
        )

        nodes: List[TextNode] = []
        similarities: List[float] = []
        ids: List[str] = []

        for row in result_set:
            meta_dict = row[_METADATA_COL] if row[_METADATA_COL] else {}

            try:
                node = metadata_dict_to_node(meta_dict)
                node.set_content(row[_TEXT_COL])
            except Exception:
                node = TextNode(
                    text=row[_TEXT_COL],
                    id_=row[_NODE_ID_COL],
                    metadata={
                        key: val for key, val in meta_dict.items()
                        if not key.startswith('_')
                    },
                )

            nodes.append(node)
            similarities.append(float(row['sim']))
            ids.append(row[_NODE_ID_COL])

        return VectorStoreQueryResult(
            nodes=nodes,
            similarities=similarities,
            ids=ids,
        )
