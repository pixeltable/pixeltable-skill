# API and provider source review

Reviewed repository `skills/pixeltable-skill/SKILL.md`, `references/core-api.md`, `references/workflows.md`, and `references/providers.md` against the extracted published Pixeltable 0.7.5 wheel. Package paths below are relative to `/private/tmp/pxt-skill-eval-20260906/source/pixeltable/`; skill reference paths are relative to `skills/pixeltable-skill/references/`. This is a source audit plus the explicitly recorded import-time checks, not provider or Cloud execution.

The main application pattern is aligned with the published API. The reference material nevertheless contains actionable output-shape and signature errors, plus omissions likely to cause first-attempt failures. These findings do not independently establish agent parity.

## Findings

### P2 — Split provider extraction guidance by function/output type

`providers.md:11-33` assigns a single extraction form to each provider while grouping functions with incompatible outputs. The sharpest case is Gemini: the row says “Json -- extract a field,” but the installed function signatures are Image (`generate_images`), Video (`generate_videos`), Audio (`generate_speech`), and String (`transcribe`). `functions/gemini.py:259`, `365-367`, `496`, and `644` establish the return types. The `generate_content` response is a dictionary; its shape cannot stand in for all Gemini functions.

OpenAI's row similarly groups `responses` with Chat Completions and suggests `.choices[0].message.content` for both. `functions/openai.py:663-698` specifies the Responses shape, and `1369-1405` explicitly distinguishes `output` from `choices`. Ollama's row groups `generate` and `chat`; consult their separate implementations (`functions/ollama.py:37-76`, `79` onward), rather than using `.message.content` universally. Runway's row recommends a Video cast even for `text_to_image`, whose own example extracts `response['output'][0].astype(pxt.Image)` (`functions/runwayml.py:56-98`). The video docstrings themselves use the unindexed `output` extraction, so whether those video docstrings are also defective requires SDK fixture/live evidence; do not declare a verified video fix from these docstrings alone.

Correction: keep provider inventory compact, but describe extraction by function family and include exact shape/type entries for OpenAI Responses, Gemini generation/transcription, Ollama generate, and Runway image generation. Add fixture-based extraction checks; do not make paid calls.

Executed import-time verification against installed wheel:

```text
generate_images: [Image]
generate_videos: [Video, Video]
generate_speech: [Audio, Audio]
transcribe: [String]
```

Reproduce:

```bash
/private/tmp/pxt-skill-eval-20260906/venv/bin/python -c 'import pixeltable.functions.gemini as g; print([(n,[str(s.return_type) for s in getattr(g,n).signatures]) for n in ["generate_images","generate_videos","generate_speech","transcribe"]])'
```

### P2 — `match_columns` is a delete-route option, not an update-route option

`core-api.md:315` says both update/delete routes need a primary key “or `match_columns=`.” `serving/_fastapi.py:1381-1391` has no `match_columns` parameter in `add_update_route`; `1696-1747` does have it on `add_delete_route`. Update matching requires the target's primary key (`1394-1400`, `2338`). Following the stated alternative for an update raises an unexpected-keyword error.

Correction: distinguish update (primary key required) from delete (primary key default, explicit nonempty match columns allowed). Verify by inspecting signatures and declaring routers for models with and without primary keys.

Executed import-time signature check:

```text
add_update_route(self, t, *, path, inputs=None, outputs=None,
                 return_fileresponse=False, export_sql=None, background=False)
```

### P2 — Teach typed JSON and the two list-iterator call patterns

`core-api.md:180` shows `list_iterator(t.tags)` without declaring the tags type; the output table at `196` describes only output names. `functions/json.py:494-518` requires typed Json and distinguishes positional lists of dictionaries from keyword lists of scalar values. `560-610` actively rejects untyped Json and incompatible positional elements before a usable view can be created.

Correction: declare the element schema in the example. For scalar tags demonstrate `list_iterator(tag=t.tags)` with a typed list column; for structured elements demonstrate a typed list of dictionaries. Include a short note that arbitrary `pxt.Json` is insufficient. Verify view construction/insertion for both supported forms and rejection of untyped Json. This is an omission, not proof that every possible `t.tags` supplied by a user would fail.

### P2 — Do not recommend `pxt.move` for a column rename

In the computed-column migration paragraph, `core-api.md:85` adds “`pxt.move()` is for a genuine rename, where you keep the values.” In context this implies a column rename. `globals.py:591-625` moves schema objects and demonstrates tables. The column operation is `Table.rename_column(old_name, new_name)` at `catalog/table.py:423-437`.

Correction: remove the ambiguous aside or explicitly identify table/directory moves and column renames separately. Preserve the existing valid advice that replacing an expression requires a different column or two updates. A renamed existing column preserves its existing computation; renaming alone does not install a new expression. Verify with a local table and a schema diff after renaming.

### P3 — Ordered aggregates count omits `concat_videos_agg`

`core-api.md:285-287` lists `concat_videos_agg`, then says only two built-in UDAs require a positional ordering expression. There are three: `make_video` (`functions/video/editing.py:24`), `stitch_tiles` (`functions/image.py:575`), and `concat_videos_agg` (`functions/video/editing.py:660-680`).

Correction: avoid the brittle count and add `concat_videos_agg(order_key, video)` to the examples. Verify expression construction for all three, with order-by keyword rejection where claimed.

### P3 — Correct the replacement exception for inherited columns

`core-api.md:86` says a base-table column replacement raises `AlreadyExistsError`. The view-inherited column branch raises `RequestError(UNSUPPORTED_OPERATION)` at `catalog/local_table.py:465-473`; dependent-column replacement does raise `AlreadyExistsError` at `479-485`.

Correction: describe the replacement constraints without promising one exception class, or distinguish them explicitly. “Base-table column” here means an inherited column being addressed through a view, not every stored base-table column.

### P3 — RAG reference contradicts the main skill's dependency default

Main `SKILL.md:128` says not to add Hugging Face or spaCy unless requested, but the only full RAG application (`workflows.md:9-30`) imports sentence-transformers and uses sentence splitting. It acknowledges dependencies in a comment but provides no installation command. This is an internal policy inconsistency rather than an invalid Pixeltable API. The reference makes a heavy model/dependency choice for an agent merely following “RAG, views, and search.”

Correction: select one explicit default consistent with the main skill; keep provider-dependent examples labeled and provide exact required installation/setup instructions adjacent to them. Validate the documented path from a clean environment, including sentence splitting's language-model requirements. Do not change the model silently during parity trials.

## Claim matrix

| Skill claim/location | Classification | Published source evidence / verification |
|---|---|---|
| One application file, `TableModel`, `FastAPIRouter` (main application section) | Supported at API surface; CLI/runtime reviewed separately | `catalog/model/declaration.py`, `serving/_fastapi.py`; router signatures exist |
| DSL index `name`, SDK index `idx_name` (`core-api.md:202-240`) | Supported | `catalog/model/declaration.py:130-150`; `catalog/table.py:463-475` |
| General embedding resolves each compatible modality (`core-api.md:204-215`) | Supported | `index/embedding_index.py:97-127` |
| Invalid explicit modality raises (`core-api.md:215`) | Supported | `index/embedding_index.py:110-121` |
| `embedding=` skips unmatched modalities | Supported with qualification | It skips individual modalities, but raises if none match: `index/embedding_index.py:128-136` |
| fp16 default, fp32 allowed (`core-api.md:215`) | Supported | `catalog/table.py:475`; `catalog/model/declaration.py:150` |
| Every custom embedding needs `.using(...)` (main appendix; `core-api.md:202`) | Incomplete/overgeneralized | A directly usable unary module-level UDF is valid; binding is needed for extra model parameters, not inherently every function. `index/embedding_index.py:308-333` |
| Custom embedding return requirements | Incomplete | Reference batch UDF demonstrates `Batch[list[float]]`, but does not state index functions need a fixed-length 1D Array. `index/embedding_index.py:335-375` rejects Json/list or unspecified dimensions |
| One `.where()` per query (`core-api.md:98`) | Supported | `_query_base.py:489-490` explicitly rejects a second where clause |
| Frozen views via `is_snapshot=True` (`core-api.md:140`) | Supported | `globals.py:302-328` |
| New frame iterator returns frame plus frame_attrs (`core-api.md:166-169`) | Supported | `functions/video/iterators.py:37-59`, `233` onward |
| Document page image extraction (`core-api.md:159-164`) | Supported | `functions/document.py:164-200`, `267-278`, `474-488` |
| `list_iterator(t.tags)` general recipe (`core-api.md:180`) | Incomplete | Typed list/dictionary requirements absent; `functions/json.py:494-610` |
| `add_computed_column(if_exists='replace')` with dependents rejected (`core-api.md:86`) | Supported, exception details partly incorrect | `catalog/local_table.py:465-485` |
| Computed column rename via `pxt.move` aside (`core-api.md:85`) | Incorrect in column context | `globals.py:591-625`; correct column API `catalog/table.py:423-437` |
| Ordered UDA positional key (`core-api.md:287-292`) | Supported, inventory incomplete | `functions/video/editing.py:24`, `660-680`; `functions/image.py:575` |
| `background=True` jobs use pending/done/error (`core-api.md:334`, `workflows.md:79`) | Supported | `serving/_fastapi.py:95-113` response model |
| Update route can use `match_columns` (`core-api.md:315`) | Incorrect | Absent from signature `serving/_fastapi.py:1381-1391`; import-time verified |
| Per-provider invoke_tools (`providers.md:53`, `core-api.md:338-346`) | Supported | OpenAI `functions/openai.py:1364-1405`; Gemini `functions/gemini.py:233`; Anthropic `functions/anthropic.py:267`; Bedrock `functions/bedrock.py:742`; Groq `functions/groq.py:102` |
| Complete tool execution recipe | Incomplete | Main text describes concepts and imports but does not include a full tools → provider response → provider invoke_tools → result chain; agent tests must establish whether external retrieval compensates |
| MCP discovery via streamable HTTP (`core-api.md:345`) | Supported | `func/mcp.py:14-38` |
| Gemini functions all return Json (`providers.md:13`) | Incorrect | `functions/gemini.py:259`, `365`, `496`, `644`; imported function return types verified |
| OpenAI functions all use choices extraction (`providers.md:11`) | Incorrect as general guidance | `functions/openai.py:663-698`, `1369-1405`; no live provider calls |
| Runway image extraction as Video (`providers.md:33`) | Incorrect for text_to_image | `functions/runwayml.py:56-98` |
| Runway video extraction matches runtime payload | Unverified | Wrapper forwards SDK result, source video example also uses unindexed output; requires SDK fixture verification |

## Minimum remediation acceptance

1. Correct signature/output facts before adding more provider inventory.
2. Add deterministic schema construction probes for route matching, typed list iterators, and custom Array embeddings.
3. Add fixture-based output extraction tests for the differing provider families; mark these as wiring checks.
4. Add one compact complete tool chain and a reproducible RAG dependency path inside existing references, preserving the single skill and line cap.
5. Rerun plugin validation/hook tests, then rerun the same failing parity scenarios with identical model/tools/settings. Do not infer parity from source correctness alone.

No reviewed skill files were edited.
