# llama-index-vector-stores-pixeltable

LlamaIndex VectorStore integration backed by [Pixeltable](https://github.com/pixeltable/pixeltable) -- multimodal data infrastructure with built-in embedding indexes, incremental computation, and 25+ AI provider integrations.

## Installation

```bash
pip install llama-index-vector-stores-pixeltable
```

## Quick Start

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.pixeltable import PixeltableVectorStore

# Create the vector store
vector_store = PixeltableVectorStore(
    table_name="mydir.docs",
    embed_dim=1536,
)

# Load documents and build index
storage_context = StorageContext.from_defaults(vector_store=vector_store)
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is Pixeltable?")
print(response)
```

## Connect to an Existing Pixeltable Table

```python
vector_store = PixeltableVectorStore(table_name="mydir.existing_docs")
index = VectorStoreIndex.from_vector_store(vector_store)
query_engine = index.as_query_engine()
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
