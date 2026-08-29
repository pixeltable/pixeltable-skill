---
description: Scaffold a new Pixeltable project, then edit app.py.
argument-hint: "[project-name]"
---

Scaffold a Pixeltable project with `pixeltable-new`. Then write tables in `app.py`.

Arguments: `$ARGUMENTS`

Steps:

1. Pick a fresh directory name (the generator refuses to overwrite).

```bash
uvx pixeltable-new myapp
```

No HTTP: `uvx pixeltable-new myapp --batch`.

2. Apply and serve:

```bash
cd myapp
uv sync
pxt schema update app.py pipeline
pxt service update app.py pipeline
```

`pipeline` is a catalog name, not a folder on disk. Batch: schema update, then run the printed `pipeline.py` command. No `pxt service`.

3. Extra features (RAG, video, agents, a UI) are added in `app.py`. Do not guess `--template` names. Do not invent a second apply path.

4. State the directory you created and the commands you ran.
