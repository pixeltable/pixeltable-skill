# Interoperability: Bridging LangChain, LlamaIndex, and Agent Frameworks

Pixeltable replaces LangChain + pandas + vector DB for **greenfield** applications.
However, many users already have working LangChain or LlamaIndex pipelines.
For those users, Pixeltable provides bridge packages that let them use Pixeltable
as a vector backend **without rebuilding their existing chain logic**.

## Decision Tree

```
User building a new app?
  → Pure Pixeltable (see anti-patterns.md)
  → Do NOT stack LangChain/LlamaIndex on top

User has an existing LangChain chain they want to keep?
  → pip install langchain-pixeltable
  → Use PixeltableVectorStore as a drop-in replacement for Chroma/Pinecone/etc.

User has an existing LlamaIndex pipeline?
  → pip install llama-index-vector-stores-pixeltable
  → Use PixeltableVectorStore with StorageContext

User wants agent tool access to Pixeltable?
  → Agno: pixeltable-skill/integrations/agno/
  → CrewAI: pixeltable-skill/integrations/crewai/
```

## LangChain Bridge

```bash
pip install langchain-pixeltable
```

```python
from langchain_pixeltable import PixeltableVectorStore
from langchain_openai import OpenAIEmbeddings

vs = PixeltableVectorStore(
    table_name='mydir.docs',
    embedding=OpenAIEmbeddings(),
)
vs.add_texts(['hello world', 'goodbye world'])
results = vs.similarity_search('hello', k=3)
retriever = vs.as_retriever(search_kwargs={'k': 5})
```

Source: [github.com/pixeltable/langchain-pixeltable](https://github.com/pixeltable/langchain-pixeltable)

## LlamaIndex Bridge

```bash
pip install llama-index-vector-stores-pixeltable
```

```python
from llama_index.vector_stores.pixeltable import PixeltableVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

vector_store = PixeltableVectorStore(table_name='mydir.docs', embed_dim=1536)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
query_engine = index.as_query_engine()
```

Source: [github.com/pixeltable/llama-index-vector-stores-pixeltable](https://github.com/pixeltable/llama-index-vector-stores-pixeltable)

## Why Bridge Instead of Replace?

The bridge packages give users Pixeltable's advantages (persistent versioned storage,
incremental embedding, multimodal columns) without requiring a full rewrite.
Over time, users can migrate toward pure Pixeltable as they see the benefits
of computed columns, views, and the declarative model.

## What NOT to Do

Do not stack Pixeltable's chunking, embedding, and retrieval **on top of** LangChain's
equivalents. If using the bridge, let LangChain handle the chain logic and use
Pixeltable only as the storage backend. For new functionality, add it as Pixeltable
computed columns rather than LangChain chains.

See `anti-patterns.md` for the full list of structural anti-patterns.
