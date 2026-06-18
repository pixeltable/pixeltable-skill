---
description: Diagnose a failing or stale Pixeltable pipeline (errored columns, wrong logic, retrieval issues).
argument-hint: "[table/view name or error message]"
---

Diagnose and fix a Pixeltable issue. Reason from how Pixeltable actually behaves, not from generic Python/pandas intuition.

Symptom: `$ARGUMENTS`

Checklist:

1. Inspect state — `t.describe()`, `t.select(...).collect()`, and check for error columns: a computed column stores `<col>_errortype` / `<col>_errormsg` for rows that failed.
2. Failed computed columns: retry with `t.recompute_columns('<col>')` after fixing the cause (e.g. rate limits, bad input). Re-inserting does NOT recompute existing rows.
3. Wrong column logic: `if_exists='ignore'` will silently skip an existing column. To change logic you must `t.drop_column('<col>')` then re-add it.
4. Common deprecated/incorrect APIs to flag and fix:
   - `from pixeltable.iterators import FrameIterator` → `from pixeltable.functions.video import frame_iterator`
   - `openai.vision(...)` → `chat_completions(...)` with `image_url` content blocks
   - positional `t.col.similarity(query)` → `t.col.similarity(string=query)`
   - embedding a non-string AI output → cast with `.astype(pxt.String)` first
5. Rate limits / throughput: configure limits via Pixeltable config (`references/core-api.md` → Configuration) rather than adding sleeps in a loop.
6. If LangChain/pandas-as-store/manual loops appear, replace them with the native Pixeltable equivalent (see the `pixeltable` skill `references/anti-patterns.md`).

Report the root cause, the exact fix, and the verification command.
