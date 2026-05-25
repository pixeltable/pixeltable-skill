"""LangChain VectorStore backed by Pixeltable.

Install:
    pip install langchain-pixeltable

Usage:
    from langchain_pixeltable import PixeltableVectorStore
    from langchain_openai import OpenAIEmbeddings

    vs = PixeltableVectorStore.from_texts(
        texts=["hello world", "goodbye world"],
        embedding=OpenAIEmbeddings(),
        table_name="my_dir.docs",
    )
    results = vs.similarity_search("hello", k=3)
"""

from langchain_pixeltable.vectorstore import PixeltableVectorStore

__all__ = ['PixeltableVectorStore']
__version__ = '0.1.0'
