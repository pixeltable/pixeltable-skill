# Pixeltable skill 2.11.3 review

Reviewed 2026-09-24 against Pixeltable 0.7.10
(`/opt/homebrew/lib/python3.11/site-packages/pixeltable`, Python 3.11). Scope is
the three doc corrections in `cab3567` on `fix-image-url-direct-column`
(PR #28): the `image_url` message shape, `model_kwargs`, and `aexec`.

## Verdict

All three claims in `providers.md` and `workflows.md` were re-verified live
against the installed 0.7.10 package and hold.

## Reproducible baseline

| Item | Evidence |
|---|---|
| Pixeltable package | `pixeltable 0.7.10`, site-packages install |
| Commit under test | `cab3567`, `fix-image-url-direct-column` |

## What ran live

- `openai.chat_completions` image blocks take
  `{'type': 'image_url', 'image_url': t.image}` with the image column itself;
  Pixeltable serializes the PIL/media payload. The OpenAI HTTP envelope
  `{'url': ...}` nested under `image_url` raises `TypeError`.
- `chat_completions` binds `(messages, model, model_kwargs, tools,
  tool_choice)`. Extra OpenAI parameters (`max_tokens`, `temperature`,
  `response_format`) go in `model_kwargs={...}`; an unknown top-level kwarg
  fails signature binding.
- Imperative invocation is `await fn.aexec(*args, **kwargs)` inside an
  `async def` FastAPI handler. `fn.exec()` is internal and takes a single
  `(args, kwargs)` pair: `exec(self, args: Sequence[Any], kwargs:
  dict[str, Any])`.

## Findings and remediation

- `providers.md`: image message shape corrected to pass the column directly;
  `model_kwargs` note added for signature-external OpenAI parameters.
- `workflows.md`: FastAPI handler guidance now names `aexec`; recommending
  `exec` was wrong for direct use because of its tuple signature.

## Verification commands

```bash
python3 scripts/validate_plugin.py
python3 tests/test_hooks.py
python3 tests/test_integrations.py
```

## Release boundary

No live provider call was performed; `model_kwargs` forwarding to OpenAI is
signature-verified only.
