# Pixeltable skill 2.12.0 review

Reviewed 2026-09-28 against Pixeltable 0.7.11 (PyPI wheel, released 2026-09-26), the `pxt` 0.7.11
CLI, upstream `pixeltable/pixeltable` at `v0.7.11`, and the release notes for 0.7.9, 0.7.10 and
0.7.11. The last full pass was [review-2.11.0.md](review-2.11.0.md) against 0.7.8.

## Verdict

Every API and CLI claim in `SKILL.md`, the five references, both agents and both commands was
checked against an installed `pixeltable[serve]==0.7.11`. Every fenced Python block compiles, and
every application-form block was applied with `pxt schema check`, `pxt schema update` and a second
`pxt schema diff`. The application loop, a RAG app, a tool-calling chain, and both framework
integrations ran end to end in an isolated `PIXELTABLE_HOME`, with provider calls answered by a
local mock of the OpenAI API.

One rule the skill and `AGENTS.md` both taught became wrong in 0.7.10, one documented example
raised, and one quick-start command failed for every agent. All three are fixed.

## Reproducible baseline

| Item | Evidence |
|---|---|
| Pixeltable package | `pixeltable[serve]==0.7.11`, Python 3.12, scratch venv; `mistune`, `tiktoken`, `pymupdf`, `openai`, `anthropic` added for document and provider checks |
| CLI | `pxt 0.7.11`; help text captured for all 65 commands and verbs |
| Upstream repo | `v0.7.11` (`407842d`); `main` is three commits ahead, none touching the schema DSL |
| Isolation | `PIXELTABLE_HOME` and `PXT_PORT=22189` in the scratchpad |
| Provider calls | a local HTTP mock of `/v1/chat/completions` and `/v1/embeddings` via `OPENAI_BASE_URL`; no paid call |

## What ran live

`pxt init` (fresh, `pyproject.toml`, nested: exit 3, repeated: no-op), `pxt service example`,
`pxt schema example` and `--brief`, `pxt schema check`, `pxt service check`, `pxt schema diff` and
`--json`, `pxt schema update` (additive, alter, destructive with and without flags, unsupported),
`pxt service update` with and without `-f`, `pxt service list --json`, `curl` on every route,
`/openapi.json`, `pxt service logs` (local), `pxt recompute` (`-n`, no TTY, `-f`), `pxt rows`,
`pxt count`, `pxt errors`, `pxt daemon restart`/`stop`/`start`, `pxt service restart`,
`--json-schema` on `schema diff`, `service diff`, `service list`, `db diff`, `db status`, and
`pxt whoami --offline`.

SDK: `alter_computed_column` (with and without `recompute`, with dependents, type change),
`add_computed_column(if_exists='replace')` with and without dependents, `alter_column`,
`TableModel.bind_all`, `uuid.to_string`, `make_video` ordering, the `pixeltable.iterators` shim,
and one view per shipped iterator. Serving: a background insert route (`done` and `error`), a
decorator route, a failing computed column on a synchronous route, and a stale route after a
schema change.

## Findings and remediation

### P1: editing a computed column's expression is no longer `UNSUPPORTED`

0.7.10 (#1600) made a changed value expression with an unchanged type a safe `alter`.
`pxt schema diff` reports `~ the value expression of computed column 'title_upper' will be updated;
existing values will not be recomputed  safe`, `pxt schema update` applies it with no flag, and it
prints `pxt recompute my_app/docs title_upper` as the follow-up. Existing rows keep their old values
until that runs. `SKILL.md`, `core-api.md`, `cli.md`, the pipeline-architect agent and the rule in
`AGENTS.md` all said the edit was `UNSUPPORTED` and prescribed a rename.

Still `UNSUPPORTED`, confirmed live: a computed column's type change, a stored column going from
`T` to `T | None` (its dependents widen too), a stored/computed swap, and a new `stored=`. One
unsupported table still aborts the whole update, including other models' creates. A rename is
still a destructive drop plus an additive add.

Notebook side: `t.alter_computed_column(col=expr)` recomputes the column and its dependents by
default; `recompute=False` leaves the old values; a type change raises `RequestError`.
`add_computed_column(if_exists='replace')` raises `AlreadyExistsError` on a column with
dependents. `t.alter_column(col, type_=T | None)` refuses a column with dependents.

Remediation: the traps table, `core-api.md` Tables, the `cli.md` diff legend, the architect agent,
the debugger agent and `AGENTS.md` describe the alter, the recompute follow-up, and what remains
unsupported, including that renaming a stored column drops its data.

### P1: `list_iterator(t.records)` over `pxt.Json[list[dict[str, str]]]` raised

`core-api.md` declared `records` as `pxt.Json[list[dict[str, str]]]` and iterated it with the
positional form. On 0.7.11 that raises `list_iterator(): Expected a type for elements matching
list[dict]; got Json[(Json, ...)]`: `dict[str, str]` declares no keys. `functions/json.py` did not
change since 0.7.8, so the example was already broken then. A TypedDict element type
(`pxt.Json[list[Record]]`) yields one column per key; the example and its explanation now use one.

### P1: the quick start's `pxt service update` exits 3 for an agent

Without a TTY, `pxt service update app.py my_app` refuses even a first additive start: `pxt:
refusing to proceed without --force/-f (no TTY for confirmation)`, exit 3. An agent never has a
TTY, and the `SKILL.md` quick start, the `cli.md` project and quick-reference blocks, and the
`workflows.md` block omitted `-f`. They carry it now, and `AGENTS.md` has a rule to keep it there.

### P2: Cloud sign-in changed

0.7.10 added `pxt login` (OAuth device grant), `pxt logout`, `pxt whoami` and `pxt key`; 0.7.11 has
`pxt org create`. The skill said Cloud commands "Require `PIXELTABLE_API_KEY`". The `SKILL.md`
Cloud section is now a command block starting with `pxt login`, and `cli.md` documents precedence
(an API key wins over a sign-in), `pxt whoami`, `pxt key create`, and `pxt org create` for a new
account with no organization. Help-text and source review only; no Cloud account was used.

### P2: the daemon's environment and `config.toml` gate every command

The daemon reads the environment and `config.toml` once. After either changes, every `pxt` command
answers 409 (`the daemon started with a different environment` / `configuration has changed since
the daemon started`) until `pxt daemon restart`. Local services take provider keys from the daemon,
not from the caller: a service restarted from a shell that has `OPENAI_API_KEY` still answered
`MISSING_CREDENTIALS` until the daemon itself was restarted with the key. `pxt daemon restart` was
not in `cli.md`. `SKILL.md`, `cli.md` and the debugger agent now say where keys come from and what
to restart.

### P2: provider call shapes

`anthropic.messages` requires a top-level `max_tokens`. The model argument is `model=` on most
providers but `model_id=` on `bedrock` and `huggingface`, `model_name=` on `twelvelabs`, `app=` on
`fal`, `ref=` on `replicate`, and `repo_id=`/`model_path=` on `llama_cpp`. Extra parameters are
`model_kwargs=` on the OpenAI-style modules, `config=` on Gemini, `inference_config=` on Bedrock,
`options=` on Ollama, `sampling_params=` on vLLM. All read from the installed signatures and added
to `providers.md` and the add-provider command. Every function the providers table lists exists.

### P2: `.astype(pxt.String)` on a Json dict fails at insert

Building the tool-calling chain, `tool_output.astype(pxt.String)` passed `pxt schema check` and
failed at insert with `Expected string, got dict`: `astype` converts only a Json value that is a
string, such as `.choices[0].message.content`. `pxtf.json.dumps()` serializes a dict or list. The
old line "Cast Json with `.astype(pxt.String)`" implied otherwise; the traps table and `core-api.md`
say which is which.

### P2: no complete tool-calling chain; the RAG example contradicted `SKILL.md`

The 2026-09-06 eval flagged both. `core-api.md` Tools now has a chain verified against the mock:
the model call with `tools=`, `invoke_tools`, and a second call over `pxtf.json.dumps(tool_output)`.
`invoke_tools` returns one key per registered tool, a list of results or `None`. The
`workflows.md` RAG example used a `sentence_transformer` index and `'sentence'` separators while
`SKILL.md` says not to add Hugging Face or spaCy unless asked; it now uses `openai.embeddings` and
`separators='page, token_limit'` (tiktoken only), and ran end to end: upload, background job,
list, search.

### P3: serving facts added in 0.7.11

A failed background job carries `error_detail`, shaped like an HTTP error's `detail`:
`{error_code, message, retryable}`. A computed column that raises on a synchronous insert route
returns 400 with that body and stores nothing. The job-polling route is in the OpenAPI schema,
which is what `openapi-typescript` needs. After a schema change a route answers 409 until the
service restarts. Decorator routes (`@router.insert_route`) and `export_sql=SqlExport(...)` were
undocumented in the skill and are the alternative to a hand-written endpoint. All in
`workflows.md` and `cli.md`.

### P3: CLI surface

`--json-schema` (0.7.9) on five commands, `--json` on `init`, `login`, `whoami` and `key`,
`pxt db delete -f` (0.7.11), per-database `db_input_media_dest` / `db_output_media_dest` /
`db_exporter_otlp_*` (0.7.11), and the reserved `PIXELTABLE_` secret prefix (0.7.9) are in
`cli.md`. The README's `npx plugins` link pointed at `github.com/vercel-labs/plugins`, which is
now 404; it links the npm package.

### Optimization

The `## pxt CLI` section of `SKILL.md` repeated the quick-start block; it is gone and its extra
commands moved into one line. The duplicated `pxt db update` paragraph folded into the Cloud block,
and two sentences that restated the bullets above them are deleted. The description names
tool-calling agents, so a tools request triggers the skill. `SKILL.md` went from 227 to 220 lines
but from 12,647 to 13,202 bytes: the Cloud command block, the provider-key paragraph and two traps
rows outweigh the cuts, and each replaces a failure an agent hit on the first try.

## Upstream issue found

A computed column whose expression holds a constant dict whose keys are not in length order never
reaches agreement. The stored expression comes back with its keys in PostgreSQL `jsonb` order,
shorter keys first, and `diff.py` compares rendered strings. Every column with
`tools=pxt.tools(...)` is affected, and so is `model_kwargs={'max_tokens': 5, 'seed': 1}`;
`{'seed': 1, 'max_tokens': 5}` and dicts that hold column references are not. `pxt schema diff`
exits 2 forever, and each `pxt schema update` bumps the table version (0, 1, 2 in three runs), so a
running service answers 409 after every update. `cli.md` and `core-api.md` note it. Not yet reported
upstream.

## Correction to the 2.11.3 record

[review-2.11.3.md](review-2.11.3.md) lists `await fn.aexec(...)` in an `async def` handler as a
verified claim. PR #29 replaced that text before merge: custom handlers are `def`, and a provider
function has no public imperative call. `aexec` exists on 0.7.11 but is not in
`docs/public_api.opml`, so the shipped text stands.

## Confirmed unchanged

The `pxt service example` file matches the `SKILL.md` snippet apart from comments. The nine
iterators and their output columns match `core-api.md`. `pixeltable.functions` has the same 41
modules the validator knows. `openai.vision` is still the only deprecated function there, and
`pxt.Required`, positional `similarity()` and the `pixeltable.iterators` shim are still present, so
the hook checks stand. `pxt.Secret` left `pixeltable/__init__.py`; the skill never used it. Both
integrations ran against 0.7.11 with stub `agno` / `crewai` base classes: create, insert, schema,
query, computed column, embedding index, similarity search, list, drop.

## Verification commands

```bash
python3 scripts/validate_plugin.py
python3 tests/test_hooks.py
python3 tests/test_integrations.py
ruff check hooks/ scripts/ tests/ integrations/
claude plugin validate .
```

## Release boundary

Cloud claims (`pxt login`, keys, per-database media, hosted OpenAPI keys) are help-text- and
source-reviewed only. Provider calls were answered by a mock, so response shapes other than OpenAI
chat completions and embeddings are signature-verified only. Issue #30 (Windows hooks under the
Store build of Claude Desktop) is out of scope for this pass.
