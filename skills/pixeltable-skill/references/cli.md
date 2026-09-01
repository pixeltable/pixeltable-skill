# Pixeltable CLI Reference (`pxt`)

Agent-focused map of the `pxt` CLI. Official source: [platform/cli.md](https://docs.pixeltable.com/platform/cli.md). Always run `pxt <command> --help` for version-specific flags -- never guess.

Python 3.11+. There is no `pxt serve`, no `pxt deploy`, no `pxt app`, and no `[tool.pixeltable.service]` TOML.

## Two surfaces

| Surface | Purpose | Requires |
|---------|---------|----------|
| **Catalog** | Inspect, query, mutate tables/views/dirs | `pip install pixeltable` |
| **Schema / service** | Apply a `TableModel` file; run `FastAPIRouter` services | `pip install 'pixeltable[serve]'` for `pxt service` |

Verify: `pxt --help` and `pxt health`.

## Project root

`pxt init` writes `pixeltable.toml` in the current directory (no-op if present). That file is the project root. Schema and service refuse an application file with no project root. `uvx pixeltable-new` already writes it.

```bash
pxt init                          # pixeltable.toml project root; no-op if present
pxt schema update app.py my_app   # creates catalog dir + tables; does NOT start HTTP
pxt service update app.py my_app  # starts local HTTP; does NOT create tables
```

`my_app` is a catalog directory, not a folder on disk. After apply: `t = pxt.get_table('my_app.docs')`.

## Daemon

On the first catalog command, `pxt` auto-spawns a daemon at `127.0.0.1:22089` (~40 ms per command after warm-up). Override with `PXT_PORT`. Lifecycle: `pxt daemon status`, `pxt daemon stop`, `pxt daemon start`.

## Command categories

| Category | Commands |
|----------|----------|
| **Project** | `init` |
| **Inspection** | `ls`, `describe`, `columns`, `computed`, `idxs`, `history`, `status`, `config` |
| **Query** | `rows`, `get`, `count`, `errors` |
| **Mutation** | `drop`, `drop-dir`, `rename`, `mv`, `revert` |
| **Schema** | `schema diff`, `schema update`, `schema prune`, `schema example` |
| **Serving** | `service diff`, `service update`, `service run`, `service prune`, `service stop`, `service list`, `service example` |
| **Cloud** | `db`, `org`, `secret` |
| **Interactive** | `shell` |
| **Lifecycle** | `daemon`, `dashboard`, `health` |

## Universal flags

| Flag | Description |
|------|-------------|
| `-h`, `--help` | Every command |
| `--json` | Machine-readable output on catalog commands, `schema` / `service` verbs, `db`, `org`, `secret`, `daemon status`. Not on `shell`, `dashboard`, or `daemon start`/`stop`. `health` is always JSON. |
| `-n`, `--dry-run` | Catalog mutations (`drop`, `drop-dir`, `rename`, `mv`, `revert`) plus `schema update`, `schema prune`, `service update`, `service prune` |
| `-f`, `--force` | Skip `[y/N]` on `drop`, `drop-dir`, `revert`, `schema update`, `schema prune`, `service update`, `service prune`. Required in non-interactive/CI contexts. Not on `rename`/`mv`. |

## Agent workflows

| Task | Prefer CLI | Example |
|------|-----------|---------|
| Mark a project root | `pxt init` | no-op if `pixeltable.toml` exists |
| Apply tables | `pxt schema update` | `pxt schema update app.py my_app` |
| Review schema drift | `pxt schema diff` | exit `0` in sync, `2` pending |
| Start HTTP | `pxt service update` | `pxt service update app.py my_app` |
| Foreground HTTP | `pxt service run` | container entrypoint / dev loop |
| Inspect catalog | `pxt ls -l`, `pxt describe`, `pxt columns --computed` | `pxt ls --json \| jq '.entries[] \| select(.kind == "table")'` |
| Debug failed columns | `pxt errors`, `pxt rows --cols` | `pxt errors my_app/docs --col embedding` |
| Check runtime/config | `pxt status`, `pxt config` | `pxt config --section openai` |
| Many commands in sequence | `pxt shell` | amortizes startup; errors don't kill session |
| Visual inspection | `pxt dashboard` | read-only UI at daemon port |
| Pack hosted project | `pxt db update` | secrets, image, and archive. Then schema, then `pxt service update` on `pxt://` |

**SDK vs CLI:** Notebooks and one-off REPL use the Python SDK (`create_table`, `add_computed_column`). Apps use a `TableModel` file plus `pxt schema` / `pxt service`. Use CLI for inspect, debug, and CI drift checks.

## Quick reference

```bash
# project + apply + serve
pxt init
pxt schema update app.py my_app
pxt service update app.py my_app

# inspect
pxt ls -l
pxt describe my_app/docs
pxt rows my_app/docs -n 5

# query / debug
pxt get my_app/docs 42
pxt count my_app/docs
pxt errors my_app/docs

# mutations (use -f in CI)
pxt drop my_app/docs -f
pxt revert my_app/docs --steps 3 -f

# interactive
pxt shell
pxt dashboard
```

## Inspection highlights

- **`pxt ls`**: `-l` (metadata), `--counts` (row counts), `--tree`
- **`pxt describe`**: schema; `--json` returns full `get_metadata()` dict
- **`pxt computed`**: shorthand for `pxt columns --computed`
- **`pxt idxs`**: `--embedding` for embedding indexes only
- **`pxt history`**: `-n N` for last N versions (run before `revert`)
- **`pxt status`**: daemon PID, version, total errors; `--sizes` for disk usage

## Query highlights

- **`pxt rows`**: `-n N` (default 10), `--cols a,b,c`. Unstored computed columns skipped unless listed in `--cols` (forces eval).
- **`pxt get`**: PK lookup; composite PKs in declared order. Table must have a primary key.
- **`pxt errors`**: rows where stored computed columns failed; `--col NAME` to filter. Table must have a primary key.

## Mutation highlights

- **`pxt drop`**: tables/views; `--cascade` drops dependent views; use `pxt drop-dir` for directories
- **`pxt drop-dir`**: `-r` for recursive directory removal
- **`pxt revert`**: irreversible -- run `pxt history` first

Table paths accept `my_app/docs` or `my_app.docs`.

## Schema (`pxt schema`)

Reconcile a catalog directory with the `TableModel` classes in a Python file. Provisioning an empty target and evolving an existing one are the same command.

| Command | Description |
|---------|-------------|
| `pxt schema diff APP TARGET` | What `update` would change. Read-only. Exit `2` if pending |
| `pxt schema update APP TARGET` | Create the catalog dir + tables; migrate existing ones. Does **not** start HTTP |
| `pxt schema prune APP TARGET` | Drop tables under `TARGET` that the file does not declare |
| `pxt schema example` | Write a working file (`--brief` for the minimal one) |

```bash
pxt schema example --out app.py
pxt schema diff   app.py my_app
pxt schema update app.py my_app
pxt schema update app.py my_app -n                       # plan only; exit 2 if pending
pxt schema update app.py my_app --allow-destructive -f   # including column/index drops
pxt schema prune  app.py my_app -n
```

`TARGET` is a catalog directory or a `pxt://org:db/...` URI. Destructive ops (drop column/index) need `--allow-destructive`. Exit `3` if the plan is destructive and that flag is missing. `UNSUPPORTED` diffs apply nothing (exit `1`).

A CI drift check:

```bash
pxt schema diff app.py pxt://acme:main/prod    # 0 = in sync, 2 = drift, 1 = error
```

## Serving (`pxt service`)

Runs the `FastAPIRouter` instances an application file declares. Requires `pip install 'pixeltable[serve]'`. Same file as the models: apply tables first, then start HTTP.

| Command | Description |
|---------|-------------|
| `pxt service diff APP TARGET` | What `update` would change. Exit `2` if pending |
| `pxt service update APP TARGET` | Start declared services in the background; restart those that changed. Does **not** create tables |
| `pxt service run APP TARGET [SERVICE]` | Serve one service from this process until interrupted |
| `pxt service prune APP TARGET` | Stop and forget services at `TARGET` that the file does not declare |
| `pxt service stop NAME...` | Stop named services (`ingest` or `my_app/ingest`) |
| `pxt service list [TARGET]` | What is running, and where |
| `pxt service example` | Write a working application file |

```bash
pxt service example --out app.py
pxt schema update app.py my_app
pxt service update app.py my_app
pxt service list
pxt service run app.py my_app --port 9000    # foreground; name the service if the file declares several
pxt service stop ingest
```

`update` starts one background process per service, each on its own port. Adding a route is additive; changing or removing one needs `--allow-destructive`. OpenAPI docs are at `/docs`.

Do **not** write `[tool.pixeltable.service]` TOML or call `pxt serve`.

## Cloud (`pxt db`, `pxt org`, `pxt secret`)

Require `PIXELTABLE_API_KEY`. URIs are `pxt://org` or `pxt://org:db`.

```bash
pxt db create pxt://myorg:mydb
pxt db list pxt://myorg
pxt db status pxt://myorg:mydb
pxt db start pxt://myorg:mydb
pxt db stop pxt://myorg:mydb
pxt db diff pxt://myorg:mydb
pxt db update pxt://myorg:mydb
pxt db build-image pxt://myorg:mydb
pxt db delete pxt://myorg:mydb
pxt org list
pxt org status pxt://myorg
```

Hosted apply order: `pxt db update pxt://org:db` packs image and workers (not Experiment), then `pxt schema update app.py pxt://org:db`. `pxt service` stays local. If `pxt db diff` says the database project is behind the working copy, run `pxt db update` first.

A UDF is recorded as a module path relative to the project root (`app.excerpt`), not a raw file path. `pxt db update` packs the project so Cloud can import it.

### Secrets

```bash
pxt secret list pxt://myorg
pxt secret list pxt://myorg:mydb
pxt secret set  pxt://myorg OPENAI_API_KEY=sk-...
pxt secret delete pxt://myorg:mydb OLD_KEY
```

An org secret applies to every database in the org; a database secret wins on a key collision. A project can declare secrets on `[[pixeltable.database]]` as `openai_api_key = 'env:OPENAI_API_KEY'`; `pxt db update` sets them. A running database keeps the values it started with. Run `pxt db stop` then `pxt db start` to pick up a change.

## Scripting with `--json`

```bash
pxt ls --json | jq '.entries[] | select(.kind == "table")'
pxt get my_app/docs 42 --json | jq '.row'
pxt count my_app/docs --json | jq '.count'
pxt schema diff app.py my_app --json
pxt service diff app.py my_app --json
```

## Known gotchas

1. **Never invent flags** -- `pxt <cmd> --help` is authoritative
2. **CI mutations need `-f`** -- `drop`, `drop-dir`, `revert`, schema/service update/prune refuse without a TTY
3. **Unstored computed columns** -- skipped in `rows`/`get` unless `--cols` forces evaluation (may invoke LLMs)
4. **Revert is irreversible** -- check `pxt history` first
5. **Serve extra** -- `pip install 'pixeltable[serve]'` before `pxt service`
6. **Schema first** -- `pxt schema update` does not start HTTP; `pxt service update` does not create tables
7. **No `pxt serve` / TOML service / `pxt app`** -- routes live on `FastAPIRouter` in the application file

## Related references

- [core-api.md → Serving](core-api.md#serving-fastapirouter) -- `FastAPIRouter` Python API
- [workflows.md](workflows.md) -- application-file example
- [Configuration](https://docs.pixeltable.com/platform/configuration) -- API keys, paths, env vars
