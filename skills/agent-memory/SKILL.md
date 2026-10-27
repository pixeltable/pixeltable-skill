---
name: agent-memory
description: >
  Give an AI agent long-term memory across sessions. Store memories, embed
  them, and recall the ones relevant to the current message. Use when an
  agent must remember user preferences, facts, or prior conversations, or
  when chat history belongs in a table rather than an external key-value
  store. Covers agent memory, semantic recall, and memory banks. Load the
  pixeltable skill for tool-calling agents and the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill when an agent should remember facts across sessions.
Memories are rows. An embedding index on the content column retrieves
related rows for the current message. Insert a new memory to store it;
there is no separate memory service to sync.

This pattern is storage and recall. For tool calling
(`pxt.tools()` + `invoke_tools()`), load the `pixeltable` skill.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.openai import embeddings

pxt.create_dir('agent', if_exists='ignore')
memories = pxt.create_table(
    'agent.memories',
    {'content': pxt.String, 'category': pxt.String},
    if_exists='ignore',
)
memories.add_embedding_index(
    'content',
    embedding=embeddings.using(model='text-embedding-3-small'),
    if_exists='ignore',
)

@pxt.query
def recall_memories(context: str, top_k: int = 5):
    sim = memories.content.similarity(string=context)
    return (
        memories.order_by(sim, asc=False)
        .limit(top_k)
        .select(
            content=memories.content,
            category=memories.category,
            score=sim,
        )
    )
```

Notebook or REPL form (`if_exists='ignore'` so it is re-runnable). For an
HTTP app, load the `pixeltable` skill and declare the same columns on a
`TableModel` with indexes in `__indexes__`, then `pxt schema update`.

## Full guidance

This skill is a thin catalog entry. Load the `pixeltable` skill for the
application file, CLI, providers, serving, and anti-patterns:
`skills/pixeltable-skill/SKILL.md` in this repo.

Install: `npx skills add pixeltable/pixeltable-skill`.
Docs: https://docs.pixeltable.com/
