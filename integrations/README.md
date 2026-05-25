# Pixeltable Agent Framework Integrations

Python toolkits for using Pixeltable with popular agent frameworks.

## Agno

```python
from agno.agent import Agent
from integrations.agno import PixeltableTools

agent = Agent(tools=[PixeltableTools()])
agent.print_response("Create a table for articles with text and image columns")
```

**Tools provided:** `list_tables`, `create_table`, `get_table_schema`, `insert_rows`, `query_table`, `add_computed_column`, `add_embedding_index`, `similarity_search`, `drop_table`

## CrewAI

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

**Tools provided:** `pixeltable_list_tables`, `pixeltable_create_table`, `pixeltable_insert`, `pixeltable_query`, `pixeltable_similarity_search`, `pixeltable_get_schema`

## Requirements

```
pip install pixeltable agno        # for Agno
pip install pixeltable crewai      # for CrewAI
```
