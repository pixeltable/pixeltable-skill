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

2. Declare the memory table and recall query as the `agent-memory` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert memories as rows. Call the recall query from a computed column or a route to ground the next reply. Needs `OPENAI_API_KEY`. Tool-calling agents: `pxt.tools()` + `invoke_tools()` in the `pixeltable` skill.

4. Show how to insert one memory and recall it with a related query.
