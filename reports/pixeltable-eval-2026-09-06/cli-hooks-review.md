# CLI, commands, agents, hooks, and metadata review

Reviewed the repository checkout's CLI reference, both commands, both agents, hooks, and all plugin/package manifests against the published 0.7.5 wheel. Source paths below are relative to `/private/tmp/pxt-skill-eval-20260906/source/`; repository paths are relative to the checkout. This is source review plus deterministic local probes, not live Cloud validation or a controlled agent trial.

## Verdict

The CLI material closely tracks the released application's declarative workflow, including several subtle migration restrictions. Two actionable Cloud issues remain: an invalid secret declaration and missing noninteractive database-update guidance. Hook coverage is useful but is neither a syntax checker nor safe to attribute to skill-only performance: raw-text matching creates reproducible false positives and fragmented edits evade application-file checks. Packaging versions are internally consistent at 2.8.1; installation across external clients was not executed.

## Prioritized findings

### C1 — P1: documented project secret declaration fails configuration validation

`skills/pixeltable-skill/references/cli.md:237` says to put `openai_api_key = 'env:OPENAI_API_KEY'` on `[[pixeltable.database]]`. The released `pixeltable/config.py:33-43` sets `extra='forbid'` and declares a **secrets mapping**, not an `openai_api_key` field. Direct `DatabaseConfig.model_validate()` under the isolated 0.7.5 environment rejects the documented entry with `extra_forbidden`; replacing the key with `secrets.openai_api_key` succeeds. The `env:` value form itself is supported (`pixeltable/service/db.py:54-55,390-400`).

Correction: explicitly teach `secrets.openai_api_key = 'env:OPENAI_API_KEY'` inside the database entry. Verify both standalone and `pyproject.toml` representations using the real parser/model without contacting Cloud. Neither website baseline supplies this erroneous secret assignment; this defect belongs to the skill reference.

### C2 — P2: database updates are omitted from the noninteractive flags reference

`references/cli.md:55-56,209-225,252-259` lists force/dry-run behavior without `db update`; its Cloud examples omit `-f`. Released `pixeltable_cli/client/commands/db.py:42-54` supports `-f`, `-n`, and `--allow-destructive`. Lines 157-176 show pending updates and initial creation call `confirm_or_exit` before applying. An agent following the Cloud section without consulting help can be refused in a noninteractive session. Add `db update` to the flags table and teach `pxt db update pxt://org:db -f` for the initial hosted loop. Distinguish destructive capacity/secret changes that also need `--allow-destructive`. Website `get-started.md:220` explicitly includes the missing `-f`; `llms.txt:295` states agents need it. This is a demonstrated guidance gap against the website baseline; Cloud API execution was not attempted.

### C3 — P2: hook false positives ask for fixes to comments, strings, and unrelated code

`hooks/validate_antipatterns.py:23-26,48-60,121-132,160-168` runs regular expressions on raw text without verifying imports or stripping comments/string literals. Deterministic probes produce `[FIX]` for `# Do not use t.text.similarity(query)`, the same text in an ordinary string, `class FrameIterator: pass`, and `response["request_errormsg"]`. An ordinary LangChain-only file gets a Pixeltable recommendation even though the orientation hook deliberately remains quiet in unrelated projects. This is nonblocking guidance but can provoke unnecessary rewrites; it contradicts the hook's stated preference to avoid false positives.

Correction: tokenize Python before matching executable constructs; bind Pixeltable aliases/import provenance before high-confidence API warnings; leave ambiguous unrelated symbols unflagged. Tests must assert silence for the four demonstrated cases and retain detection for actual deprecated calls. Do not promote these recommendations into hard blockers.

### C4 — P2: application-context hook gates miss incremental edits

`hooks/validate_antipatterns.py:98-118,139-157` requires `TableModel`/`model_base` in the inspected text, but an Edit supplies only its replacement fragment. The full file text `TableModel = pxt.model_base()` followed by `t.add_embedding_index(...)` warns; editing only the latter statement produces no finding. A multiline import of deprecated `vision` also escapes the import expression at line 39. Correction: where the tool exposes a saved file path, inspect the resulting local file under a bounded size limit, or explicitly document fragment-only detection; support parenthesized imports in the parser. Add full-write and fragment-edit regression cases. These are coverage gaps, not evidence that the skill itself generates incorrect code.

### C5 — P3: confirmation rules are overgeneralized

`references/cli.md:56,252` claims schema updates refuse without `-f` in noninteractive contexts. Released `schema.py:458-481` returns immediately for additive-only changes, and no-op updates exit successfully. The scaffold command's initial schema update without `-f` is therefore valid. Similarly `references/cli.md:23,190,258` says service update “always prompts,” but `service.py:334-343` exits without prompting on an in-sync plan or dry run. Correction: distinguish pending service/database updates and destructive schema updates from additive/no-op schemas. Verify using stubbed plans without launching services.

## Claim matrix

| Claim and repository location | Assessment | Released evidence / test |
| --- | --- | --- |
| `pxt init` writes standalone config or appends to pyproject; refuses nested roots (`references/cli.md:18`) | Supported | `pixeltable_cli/client/commands/init.py:62-122` |
| Schema and service are separate operations (`references/cli.md:22-24,134-139,174-185`) | Supported | `schema.py:435-455` posts schema update; `service.py:323-359` posts service update |
| CLI scaffold starts from generated example (`commands/scaffold.md:12-29`) | Supported | `service.py:303-308`; `schema.py:348-354` |
| Schema destructive changes need allow-destructive (`references/cli.md:158`) | Supported | `schema.py:469-481` refuses entire client request before apply |
| Changed computed expression cannot be migrated in place (`agents/pixeltable-pipeline-architect.md:22`) | Supported | `pixeltable/catalog/model/diff.py:344-365` compares column properties and marks alterations unsupported |
| Schema-only application can run without `-f` (`commands/scaffold.md:26`) | Supported | `schema.py:469-472` skips prompt when destructive count is zero |
| All schema updates require force in CI (`references/cli.md:56,252`) | Incorrect | Same source as previous row |
| Every service update prompts (`references/cli.md:190,258`) | Incorrect, minor overstatement | `service.py:334-343` exits on agreement or dry run |
| db update requires named database entry (`references/cli.md:220`) | Supported | `db.py:25-32`; `pixeltable/config.py` database configuration selection |
| Cloud project secret is bare `openai_api_key` (`references/cli.md:237`) | Incorrect | Real 0.7.5 `DatabaseConfig` validation rejects it |
| Cloud agent workflow needs database force flag | Incomplete | `db.py:42-54,157-176`; website get-started explicitly adds `-f` |
| Deprecated iterator/OpenAI vision guidance (`hooks/validate_antipatterns.py:23-44`) | Supported in API intent; imprecise matching | `pixeltable/functions/openai.py:782-787` deprecation; raw-text probe false positives/negative |
| Positional similarity is deprecated | Supported | `pixeltable/exprs/column_ref.py:194-204,234` retains deprecated `item`; do not describe every such call as runtime-invalid |
| Hook sees whole application context after edits | Incomplete | `extract_python_content` collects only replacement strings; recorded probes |
| Plugin/package versions agree | Supported | `.plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.claude-plugin/{plugin,marketplace}.json`, `.codex-plugin/plugin.json`, `package.json`: 2.8.1 |
| Hooks run in every install/client | Unverified; do not infer | Claude hook JSON matches Claude Write/Edit tool names and CLAUDE_PLUGIN_ROOT; Codex manifest only declares skills; no external client installation tested |

## Reproduction artifacts and limitations

Run `python3 reports/pixeltable-eval-2026-09-06/evidence/hook-probes.py`. Its checked-in output is `evidence/hook-probes.json`; it includes inputs and actual finding strings. “invalid_positional_similarity” is a probe identifier for a policy violation, not an assertion that 0.7.5 always rejects deprecated positional syntax.

Secret validation reproduction:

```python
import tomllib
from pixeltable.config import DatabaseConfig
for key in ['openai_api_key', 'secrets.openai_api_key']:
    entry = tomllib.loads("[[pixeltable.database]]\nname='pxt://org:db'\n" + key + "='env:OPENAI_API_KEY'\n")['pixeltable']['database'][0]
    try:
        print(key, 'ACCEPTED', DatabaseConfig.model_validate(entry))
    except Exception as error:
        print(key, type(error).__name__, str(error))
```

Actual output: bare field fails `ValidationError: Extra inputs are not permitted`; dotted `secrets.openai_api_key` succeeds. No secret value or account was used. Commands/agent guidance was reviewed as text; no paid provider calls, hosted resources, installation side effects, or skill changes were made. Website shell snippets frequently omit `-f`, but their explicit agent-specific Cloud guidance mitigates that omission; interactive examples alone are not a website runtime defect.
