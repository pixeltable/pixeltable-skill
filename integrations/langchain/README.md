# langchain-pixeltable

LangChain VectorStore integration backed by [Pixeltable](https://github.com/pixeltable/pixeltable) -- multimodal data infrastructure with built-in embedding indexes, incremental computation, and 25+ AI provider integrations.

## Installation

```bash
pip install langchain-pixeltable
```

## Quick Start

```python
from langchain_pixeltable import PixeltableVectorStore
from langchain_openai import OpenAIEmbeddings

# Create a vector store and add documents
vs = PixeltableVectorStore.from_texts(
    texts=["Pixeltable handles multimodal data", "LangChain is great for chains"],
    embedding=OpenAIEmbeddings(),
    table_name="mydir.docs",
)

# Similarity search
results = vs.similarity_search("multimodal data management", k=3)
for doc in results:
    print(doc.page_content)
```

## Connect to an Existing Pixeltable Table

```python
vs = PixeltableVectorStore.from_existing_table(
    table_name="mydir.existing_docs",
    embedding=OpenAIEmbeddings(),
    text_column="content",
    embedding_column="content_embedding",
)
results = vs.similarity_search("search query")
```

## Use as a LangChain Retriever

```python
retriever = vs.as_retriever(search_kwargs={"k": 5})
docs = retriever.invoke("What is Pixeltable?")
```

## Why Pixeltable as a Vector Backend?

- **Persistent and versioned**: Data survives restarts; every change is tracked
- **Incremental**: Only new/changed rows get re-embedded
- **Multimodal native**: Images, video, audio, and documents alongside text
- **25+ AI providers**: Built-in functions for OpenAI, Anthropic, Gemini, and more
- **No external services**: Embedded PostgreSQL, no Docker required

## Links

- [Pixeltable Docs](https://docs.pixeltable.com/)
- [GitHub](https://github.com/pixeltable/pixeltable)
- [Discord](https://discord.gg/QPyqFYx2UN)
