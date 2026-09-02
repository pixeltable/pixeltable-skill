---
description: Scaffold a new Pixeltable project, then edit app.py.
argument-hint: "[project-name]"
---

Scaffold a Pixeltable project with `pixeltable-new`. Then write tables in `app.py`.
The loop is Declare, Experiment, Serve.

Arguments: `$ARGUMENTS`

Steps:

1. Pick a fresh directory name (the generator refuses to overwrite).

```bash
uvx pixeltable-new myapp
```

Video: `uvx pixeltable-new myapp --video`.

2. Apply and serve (Declare, then Serve):

```bash
cd myapp
uv sync
pxt schema update app.py agent
pxt service update app.py agent
```

`agent` is a catalog name, not a folder on disk. Video TARGET is `videointel`. Experiment: insert, `/ask`, or `pxt dashboard`.

3. Extra features (RAG, video, agents, a UI) are added in `app.py`. Copy from starter-kit `chat-agent/` or `video-search/` if you need a starting file. Do not guess `--template` names. Do not invent a second apply path.

4. State the directory you created and the commands you ran.
