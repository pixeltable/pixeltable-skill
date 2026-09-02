---
description: Start a Pixeltable project with pxt init and a CLI example file.
argument-hint: "[project-name]"
---

Start a Pixeltable project with the CLI. Then edit `app.py`.

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
