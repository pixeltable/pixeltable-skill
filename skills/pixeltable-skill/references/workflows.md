# FastAPIRouter

`from pixeltable.serving import FastAPIRouter`. One application file declares `TableModel` classes and routers. Apply tables with `pxt schema update`. Start HTTP with `pxt service update`.

The default scaffold catalog TARGET is `pipeline` (matches `FastAPIRouter(name='pipeline')`).

```python
# app.py
from __future__ import annotations

import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()
embed_fn = sentence_transformer.using(model_id='intfloat/multilingual-e5-large-instruct')


class Docs(TableModel, name='docs'):
    document: pxt.Document
    timestamp: pxt.Timestamp


class Chunks(
    TableModel,
    name='chunks',
    base=Docs,
    iterator=pxtf.document.document_splitter(
        Docs.document, separators='page, sentence', metadata='title,heading,page'
    ),
):
    __indexes__ = [pxt.EmbeddingIndex(text, embedding=embed_fn, name='chunks_embed')]  # type: ignore[name-defined]


ingest = FastAPIRouter(name='pipeline', prefix='/api', tags=['data'])
ingest.add_insert_route(
    Docs, path='/upload', uploadfile_inputs=[Docs.document], inputs=[Docs.timestamp],
    outputs=[Docs.document], background=True,
)
ingest.add_delete_route(Docs, path='/delete')

@pxt.query
def list_docs():
    return Docs.select(Docs.document, Docs.timestamp).order_by(Docs.timestamp, asc=False)

@pxt.query
def search_docs(query_text: str):
    sim = Chunks.text.similarity(string=query_text)
    return Chunks.where(sim > 0.3).order_by(sim, asc=False).select(
        text=Chunks.text, score=sim).limit(20)

ingest.add_query_route(path='/list', query=list_docs, method='get')
ingest.add_query_route(path='/search', query=search_docs, method='post')
```

```bash
pxt init
pxt schema update app.py pipeline
pxt service update app.py pipeline
```

After apply: `t = pxt.get_table('pipeline.docs')`.

Already have FastAPI: `app.include_router(ingest)` after schema update. Call `pxt.get_table()` inside custom handlers.

- `add_insert_route`: POST from model columns. `uploadfile_inputs` for files, `background=True` for long inserts
- `add_query_route`: wraps `@pxt.query`. Returns `{ "rows": [...] }`
- `add_delete_route`: POST delete by primary key
- Indexes on the model (`__indexes__`)

Batch (no HTTP): `uvx pixeltable-new myapp --batch`, then `pxt schema update app.py pipeline` and `python pipeline.py`. [Starter kit batch/](https://github.com/pixeltable/pixeltable-starter-kit/tree/main/batch).

[cli.md](cli.md) | [core-api.md](core-api.md#serving-fastapirouter)
