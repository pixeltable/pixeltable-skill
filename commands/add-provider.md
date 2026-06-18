---
description: Add an AI provider call as a Pixeltable computed column (correct import + output shape).
argument-hint: "[provider] [task, e.g. summarize/classify/embed/transcribe]"
---

Wire an AI provider into a Pixeltable table as a computed column. The model runs automatically on insert — never write a `for row in ...:` loop calling the model.

Request: `$ARGUMENTS`

Steps:

1. Identify the provider module under `pixeltable.functions.<provider>` (e.g. `openai`, `anthropic`, `gemini`, `groq`, `bedrock`, `together`, `fireworks`, `ollama`, `whisper`). Confirm the exact import and output shape in the `pixeltable` skill (`references/providers.md` → Quick Reference) before writing code.

2. Add the call as a computed column, extracting the right field from the response. For chat completions:

```python
from pixeltable.functions.openai import chat_completions

t.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': t.content}],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore',
)
```

3. Critical correctness rules:
   - `openai.vision` does NOT exist — for image input use `chat_completions` with `image_url` content blocks.
   - Set API keys via config/env, not hard-coded.
   - To change a column's logic, `drop_column()` then recreate — re-running with `if_exists='ignore'` is a silent no-op.

4. After adding, show how to insert a row and `collect()` the result so the user can verify output shape.
