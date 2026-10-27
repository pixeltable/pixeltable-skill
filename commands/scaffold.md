---
description: >
  Original /pixeltable:scaffold name. Start a Pixeltable project for
  multimodal RAG, video search, image similarity search, agent memory, or
  embeddings stored with your data. Alias of /pixeltable-start.
argument-hint: "[project-name]"
---

This is the original `/pixeltable:scaffold` command, kept so existing users are not broken. Same onboarding as [pixeltable-start.md](pixeltable-start.md) (pxt init, example `app.py`, schema update, HTTP).

Arguments: `$ARGUMENTS`

Steps:

1. Pick a fresh directory. Install, mark the project root, and write a working file:

```bash
mkdir myapp && cd myapp
pip install 'pixeltable[serve]'
pxt init
pxt service example --out app.py
```

Schema only (no HTTP): `pxt schema example --brief --out app.py`.

2. Create tables, then start HTTP:

```bash
pxt schema update app.py my_app
pxt service update app.py my_app -f
pxt service list
```

The last argument (`my_app`) is a catalog name, not a folder on disk. Try the app: insert, curl a route, or `pxt dashboard`. Pass `-f` when there is no TTY.

3. Extra features (RAG, video, agents, a UI) are added in `app.py`. Start from the example file. Do not invent a second `pxt schema update` path.

4. State the directory you created and the commands you ran.
