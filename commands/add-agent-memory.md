---
description: >
  Give an AI agent long-term memory across sessions: store facts and
  preferences, embed them, recall by similarity. Use for agent memory,
  long-term memory, chat memory, or recalling user context in later turns.
argument-hint: "[what to remember]"
---

Add long-term agent memory (facts and preferences recalled in later sessions). Request: `$ARGUMENTS`

Load the `agent-memory` skill and the `pixeltable` skill. Memory is a table with an embedding index, not Redis or a separate vector DB.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare a memory table and a recall query:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
embed_fn = pxtf.openai.embeddings.using(model='text-embedding-3-small')


class Memories(TableModel, name='memories'):
    content: pxt.String
    category: pxt.String
    __indexes__ = [pxt.EmbeddingIndex(content, embedding=embed_fn, name='memory_idx')]


@pxt.query
def recall_memories(context: str, top_k: int = 5):
    sim = Memories.content.similarity(string=context)
    return Memories.order_by(sim, asc=False).limit(top_k).select(
        Memories.content, Memories.category, score=sim
    )
```

3. Apply with `pxt schema update app.py my_app`. Insert memories as rows. Call `recall_memories` from a computed column or a route to ground the next reply. Needs `OPENAI_API_KEY`. Tool-calling agents: `pxt.tools()` + `invoke_tools()` in the `pixeltable` skill.

4. Show how to insert one memory and recall it with a related query.
