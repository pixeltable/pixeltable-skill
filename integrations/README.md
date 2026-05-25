# Pixeltable Agent Framework Integrations

Python packages for using Pixeltable with popular AI frameworks.

## LangChain (`langchain-pixeltable`)

Drop-in VectorStore that lets any LangChain chain or retriever use Pixeltable as its vector backend.

```python
from langchain_pixeltable import PixeltableVectorStore
from langchain_openai import OpenAIEmbeddings

vs = PixeltableVectorStore.from_texts(
    texts=["hello", "world"],
    embedding=OpenAIEmbeddings(),
    table_name="mydir.docs",
)
retriever = vs.as_retriever(search_kwargs={"k": 5})
```

```bash
pip install langchain-pixeltable
```

## LlamaIndex (`llama-index-vector-stores-pixeltable`)

VectorStore integration that plugs into LlamaIndex's `VectorStoreIndex` and query engine pipeline.

```python
from llama_index.vector_stores.pixeltable import PixeltableVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

vector_store = PixeltableVectorStore(table_name="mydir.docs", embed_dim=1536)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
query_engine = index.as_query_engine()
```

```bash
pip install llama-index-vector-stores-pixeltable
```

## Agno (`integrations/agno/`)

Toolkit class that gives Agno agents full access to Pixeltable operations.

```python
from agno.agent import Agent
from integrations.agno import PixeltableTools

agent = Agent(tools=[PixeltableTools()])
agent.print_response("Create a table for articles with text and image columns")
```

**Tools:** `list_tables`, `create_table`, `get_table_schema`, `insert_rows`, `query_table`, `add_computed_column`, `add_embedding_index`, `similarity_search`, `drop_table`

## CrewAI (`integrations/crewai/`)

Individual `BaseTool` subclasses for CrewAI agents.

```python
from crewai import Agent
from integrations.crewai import (
    PixeltableListTablesTool,
    PixeltableCreateTableTool,
    PixeltableInsertTool,
    PixeltableQueryTool,
    PixeltableSimilaritySearchTool,
)

researcher = Agent(
    role="Data Analyst",
    goal="Manage multimodal data",
    tools=[
        PixeltableListTablesTool(),
        PixeltableCreateTableTool(),
        PixeltableInsertTool(),
        PixeltableQueryTool(),
        PixeltableSimilaritySearchTool(),
    ],
)
```

**Tools:** `pixeltable_list_tables`, `pixeltable_create_table`, `pixeltable_insert`, `pixeltable_query`, `pixeltable_similarity_search`, `pixeltable_get_schema`
