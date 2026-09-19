# Pixeltable skill 2.11.0 review

Reviewed 2026-09-19 against Pixeltable 0.7.8 (PyPI wheel, released 2026-09-16), the
`pxt` 0.7.8 CLI, upstream `AGENTS.md` and `docs/release/skill.md` at `v0.7.8-5`, and the
live docs pages the skill links to.

## Verdict

Every API and CLI claim in `SKILL.md` and the five references was checked against an
installed `pixeltable[serve]==0.7.8`. The application-file loop ran end to end in an
isolated `PIXELTABLE_HOME`. Two files were broken and are fixed: both framework
integrations under `integrations/` called SDK methods that do not exist on 0.7.8, and the
Agno toolkit was structurally broken (four of its nine tools were nested inside a helper
function, so `PixeltableTools()` raised `AttributeError` on construction).

No live provider call, Pixeltable Cloud deployment, or ChatGPT desktop install was
performed. Those surfaces are source- and help-text-reviewed only.

## Reproducible baseline

| Item | Evidence |
|---|---|
| Pixeltable package | `pixeltable[serve]==0.7.8`, Python 3.12, extras `serve` and `otel` only |
| CLI | `pxt 0.7.8`; verb list from `pxt --help` and every `pxt <group> <verb> -h` |
| Upstream repo | `pixeltable/pixeltable` at `v0.7.8-5-g0d733d47` |
| Community catalog | `anthropics/claude-plugins-community` at 2,282 entries; `pixeltable` not yet listed |

## What ran live

`pxt init`, `pxt service example --out app.py`, `pxt schema example --brief`,
`pxt schema check`, `pxt service check`, `pxt schema update` (with and without `-f`),
`pxt schema diff`, `pxt ls -l`, `pxt describe`, `pxt status`, `pxt service update -f`,
`pxt service list --json`, `curl POST /docs`, `/titles`, `GET /docs`, `pxt service logs`,
`pxt errors`, `pxt recompute -n`, `pxt count`, `pxt rows`, `pxt service stop`,
`pxt daemon stop`.

SDK: `get_table`, `insert`, `select/collect`, `.errortype` / `.errormsg`,
`TableModel.bind_all`, `uuid.to_string`, `add_computed_column(if_exists='replace')`, and
one view per shipped iterator to read back its output columns. Every signature in
`core-api.md`, `providers.md` and `workflows.md` was read from the installed package.

## Findings and remediation

### P1: both framework integrations failed on 0.7.8

- `Table.columns()` returns `list[str]`; the adapters read `.name` / `.col_type` off each
  entry. Schema now comes from `Table.get_metadata()['columns']`.
- `collect()` returns a `ResultSet` with `to_pandas()` and `to_pydantic()` only; the
  adapters called `.to_json()`. Rows now serialize through `to_pandas().to_dict()`.
- `add_embedding_index(if_not_exists=True)` is a `TypeError`; the keyword is
  `if_exists='ignore'`.
- Agno: `_SAFE_OPS`, `_eval_ast_node` and `_safe_eval_expr` had been pasted into the
  class body, which made the four methods after them nested functions of
  `_safe_eval_expr`. They are module-level helpers again and the methods are back on
  the class.
- The Agno docstring pointed at `pixeltable.functions.sentence_transformers.SentenceTransformer`,
  which does not exist; it now names `huggingface.sentence_transformer.using(model_id=...)`.

Verification: `tests/test_integrations.py` (stdlib, ast-based) guards the class
structure and the retired keyword, and runs in CI. Both adapters were also exercised
against a live catalog with stub `agno` / `crewai` base classes: create, insert, schema,
query, computed column, list, drop all returned JSON.

### P2: CLI reference lagged 0.7.6 to 0.7.8

- `pxt recompute` (0.7.6) was absent. Added to the command map, flags, quick reference,
  and the debugger agent as the CLI form of `recompute_columns()`.
- `pxt service restart` and `pxt db restart` were absent; the secrets note told readers
  to `db stop` then `db start`. The help text says `restart`.
- `pxt service logs` on a local service exits 1 and prints the log file's path; the
  reference read as if it streamed. The agent-workflow row now says hosted only.
- `pxt service update --port` and `pxt service run --host/--port` were undocumented.
- The `pxt db create` aside quoted a help string that 0.7.8 no longer prints.

### P2: two facts from upstream `skill.md` were missing

- `TableModel.bind_all('my_app')` binds every model for plain-Python access. Added to
  `SKILL.md` and `core-api.md`.
- `add_update_route` matches by primary key, so the request body carries `id` even though
  `inputs` does not list it (confirmed in `pxt service list --json`). Added to
  `SKILL.md`, `core-api.md` and `workflows.md`.
- A file that defines its own `fastapi.FastAPI` and `include_router()`s its routers is
  served as one service by `pxt service update` (from `pxt service update -h`). Added to
  `SKILL.md` and `workflows.md`.

### P3: typography

Two em dashes in `workflows.md` and six arrows across the skill violated the repo's
ASCII rule; manifest descriptions used ` : `. All replaced.

## Confirmed unchanged

`pxt schema update` on an additive plan does not prompt without `-f` (exit 0). The
`pxt service example` file matches the `SKILL.md` snippet apart from comments. Iterator
output columns match the `core-api.md` table exactly. `pxt.Required`, positional
`similarity()`, `openai.vision` and `pixeltable.iterators` are still present and still
deprecated, so the hook checks stand. Every docs URL the skill links returns 200.

## Verification commands

```bash
python3 scripts/validate_plugin.py
python3 tests/test_hooks.py
python3 tests/test_integrations.py
ruff check hooks/ scripts/ tests/ integrations/
bash -n install.sh
claude plugin validate .
```

## Release boundary

Cloud and provider claims remain labeled untested until credentials and a controlled
live-test budget are available. The community-marketplace submission is a separate
operation; the catalog pin will track `main` once approved.
