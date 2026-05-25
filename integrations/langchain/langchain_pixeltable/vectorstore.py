"""Pixeltable VectorStore for LangChain.

Bridges LangChain's VectorStore interface with Pixeltable's embedding index
and similarity search, letting LangChain users use Pixeltable as a persistent,
multimodal-ready vector backend.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Iterable, Optional

import numpy as np
import pixeltable as pxt
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

logger = logging.getLogger(__name__)

_DEFAULT_TEXT_COL = 'text'
_DEFAULT_METADATA_COL = 'metadata'
_DEFAULT_ID_COL = 'id'
_DEFAULT_EMBEDDING_COL = 'embedding'


class PixeltableVectorStore(VectorStore):
    """LangChain VectorStore backed by a Pixeltable table with an embedding index.

    There are two usage modes:

    1. **Managed embeddings** (recommended): Pixeltable computes embeddings via
       a computed column and an embedding index. Pass a LangChain ``Embeddings``
       object and the store will create a Pixeltable embedding index that wraps it.

    2. **Bring-your-own table**: Point at an existing Pixeltable table that already
       has an embedding index. The LangChain ``Embeddings`` object is only used for
       ``similarity_search_by_vector`` if the index doesn't cover that query modality.

    Example:
        .. code-block:: python

            from langchain_pixeltable import PixeltableVectorStore
            from langchain_openai import OpenAIEmbeddings

            vs = PixeltableVectorStore(
                table_name="mydir.docs",
                embedding=OpenAIEmbeddings(),
            )
            vs.add_texts(["Hello world", "Goodbye world"])
            results = vs.similarity_search("hello", k=3)
    """

    def __init__(
        self,
        table_name: str,
        embedding: Embeddings,
        *,
        text_column: str = _DEFAULT_TEXT_COL,
        metadata_column: str = _DEFAULT_METADATA_COL,
        id_column: str = _DEFAULT_ID_COL,
        embedding_column: str = _DEFAULT_EMBEDDING_COL,
        metric: str = 'cosine',
    ):
        self._table_name = table_name
        self._embedding = embedding
        self._text_col = text_column
        self._metadata_col = metadata_column
        self._id_col = id_column
        self._embedding_col = embedding_column
        self._metric = metric
        self._table: pxt.Table | None = None

    @property
    def embeddings(self) -> Embeddings:
        return self._embedding

    def _get_or_create_table(self) -> pxt.Table:
        """Lazily initialize the Pixeltable table with schema and embedding index."""
        if self._table is not None:
            return self._table

        try:
            self._table = pxt.get_table(self._table_name)
            return self._table
        except Exception:
            pass

        parts = self._table_name.rsplit('.', 1)
        if len(parts) == 2:
            pxt.create_dir(parts[0], if_exists='ignore')

        probe = self._embedding.embed_query('probe')
        embed_dim = len(probe)

        self._table = pxt.create_table(
            self._table_name,
            {
                self._id_col: pxt.String,
                self._text_col: pxt.String,
                self._metadata_col: pxt.Json,
                self._embedding_col: pxt.Array[(embed_dim,), pxt.Float],
            },
            if_exists='ignore',
        )
        t = self._table
        t.add_embedding_index(
            self._embedding_col,
            metric=self._metric,
            if_exists='ignore',
        )
        return t

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[list[dict]] = None,
        *,
        ids: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> list[str]:
        """Add texts with optional metadata to the vector store.

        Args:
            texts: Texts to add.
            metadatas: Optional metadata dicts, one per text.
            ids: Optional IDs. Generated if not provided.

        Returns:
            List of IDs for the added texts.
        """
        t = self._get_or_create_table()
        text_list = list(texts)
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in text_list]
        if metadatas is None:
            metadatas = [{} for _ in text_list]

        vectors = self._embedding.embed_documents(text_list)

        rows = [
            {
                self._id_col: id_,
                self._text_col: text,
                self._metadata_col: meta,
                self._embedding_col: vec,
            }
            for id_, text, meta, vec in zip(ids, text_list, metadatas, vectors)
        ]
        t.insert(rows)
        return ids

    def delete(self, ids: Optional[list[str]] = None, **kwargs: Any) -> Optional[bool]:
        """Delete documents by ID.

        Args:
            ids: List of document IDs to delete.

        Returns:
            True if successful.
        """
        if ids is None:
            return False
        t = self._get_or_create_table()
        id_col = getattr(t, self._id_col)
        for doc_id in ids:
            t.delete(where=(id_col == doc_id))
        return True

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[Document]:
        """Return documents most similar to the query string.

        Args:
            query: Query text.
            k: Number of results.

        Returns:
            List of LangChain Document objects.
        """
        docs_and_scores = self.similarity_search_with_score(query, k=k, **kwargs)
        return [doc for doc, _ in docs_and_scores]

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[tuple[Document, float]]:
        """Return documents and similarity scores for the query.

        Args:
            query: Query text.
            k: Number of results.

        Returns:
            List of (Document, score) tuples.
        """
        t = self._get_or_create_table()
        text_col = getattr(t, self._text_col)
        meta_col = getattr(t, self._metadata_col)
        id_col = getattr(t, self._id_col)
        embed_col = getattr(t, self._embedding_col)

        query_vec = np.array(self._embedding.embed_query(query), dtype=np.float32)
        sim = embed_col.similarity(vector=query_vec)
        result_set = (
            t.order_by(sim, asc=False)
            .limit(k)
            .select(text_col, meta_col, id_col, sim=sim)
            .collect()
        )

        results = []
        for row in result_set:
            metadata = row[self._metadata_col] if row[self._metadata_col] else {}
            doc = Document(
                page_content=row[self._text_col],
                metadata=metadata,
                id=row[self._id_col],
            )
            results.append((doc, float(row['sim'])))
        return results

    def similarity_search_by_vector(
        self, embedding: list[float], k: int = 4, **kwargs: Any
    ) -> list[Document]:
        """Return documents most similar to the given embedding vector.

        Args:
            embedding: Query embedding vector.
            k: Number of results.

        Returns:
            List of LangChain Document objects.
        """
        t = self._get_or_create_table()
        text_col = getattr(t, self._text_col)
        meta_col = getattr(t, self._metadata_col)
        id_col = getattr(t, self._id_col)
        embed_col = getattr(t, self._embedding_col)

        sim = embed_col.similarity(vector=np.array(embedding, dtype=np.float32))
        result_set = (
            t.order_by(sim, asc=False)
            .limit(k)
            .select(text_col, meta_col, id_col)
            .collect()
        )

        results = []
        for row in result_set:
            metadata = row[self._metadata_col] if row[self._metadata_col] else {}
            doc = Document(
                page_content=row[self._text_col],
                metadata=metadata,
                id=row[self._id_col],
            )
            results.append(doc)
        return results

    @classmethod
    def from_texts(
        cls,
        texts: list[str],
        embedding: Embeddings,
        metadatas: Optional[list[dict]] = None,
        *,
        ids: Optional[list[str]] = None,
        table_name: str = 'langchain.documents',
        **kwargs: Any,
    ) -> PixeltableVectorStore:
        """Create a PixeltableVectorStore from a list of texts.

        Args:
            texts: Texts to add.
            embedding: LangChain Embeddings instance.
            metadatas: Optional metadata dicts.
            ids: Optional document IDs.
            table_name: Pixeltable table path.

        Returns:
            Initialized PixeltableVectorStore.
        """
        store = cls(table_name=table_name, embedding=embedding, **kwargs)
        store.add_texts(texts, metadatas=metadatas, ids=ids)
        return store

    @classmethod
    def from_existing_table(
        cls,
        table_name: str,
        embedding: Embeddings,
        *,
        text_column: str = _DEFAULT_TEXT_COL,
        metadata_column: str = _DEFAULT_METADATA_COL,
        id_column: str = _DEFAULT_ID_COL,
        embedding_column: str = _DEFAULT_EMBEDDING_COL,
    ) -> PixeltableVectorStore:
        """Connect to an existing Pixeltable table as a VectorStore.

        Args:
            table_name: Existing Pixeltable table path.
            embedding: LangChain Embeddings instance (used for query embedding).
            text_column: Name of the text content column.
            metadata_column: Name of the metadata JSON column.
            id_column: Name of the ID column.
            embedding_column: Name of the embedding/indexed column.

        Returns:
            PixeltableVectorStore connected to the existing table.
        """
        store = cls(
            table_name=table_name,
            embedding=embedding,
            text_column=text_column,
            metadata_column=metadata_column,
            id_column=id_column,
            embedding_column=embedding_column,
        )
        store._table = pxt.get_table(table_name)
        return store
