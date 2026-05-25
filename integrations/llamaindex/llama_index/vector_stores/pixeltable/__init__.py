"""LlamaIndex VectorStore backed by Pixeltable.

Install:
    pip install llama-index-vector-stores-pixeltable

Usage:
    from llama_index.vector_stores.pixeltable import PixeltableVectorStore
    from llama_index.core import VectorStoreIndex, StorageContext

    vector_store = PixeltableVectorStore(table_name="mydir.docs")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
"""

from llama_index.vector_stores.pixeltable.base import PixeltableVectorStore

__all__ = ['PixeltableVectorStore']
