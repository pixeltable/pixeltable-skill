# Pixeltable Core API Reference

Apps use `app.py` plus `pxt schema update`. This file is notebook form (`pxt.create_table()`) unless noted. CLI: [cli.md](cli.md). Routes: [workflows.md](workflows.md).

Types are non-nullable by default. Optional is `T | None`. Do not use `pxt.Required`.

## Contents

- [Tables](#tables)
- [Querying](#querying)
- [Computed columns](#computed-columns)
- [Views](#views)
- [Indexes](#indexes)
- [UDFs](#udfs)
- [UDAs](#udas)
- [Serving](#serving)
- [Tools](#tools)
- [Pitfalls](#pitfalls)

## Tables

App:

```python
class Docs(TableModel, name='docs'):
    title: pxt.String
    body: pxt.String | None
    title_upper = pxtf.string.upper(title)
    uuid = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
```

Notebook:

```python
import pixeltable as pxt
from pixeltable.functions.uuid import uuid7

t = pxt.create_table('dir.docs', {
    'title': pxt.String,
    'body': pxt.String | None,
    'image': pxt.Image,
    'video': pxt.Video,
    'audio': pxt.Audio,
    'doc': pxt.Document,
    'uuid': uuid7(),
}, primary_key=['uuid'], if_exists='ignore')
```

Types: `String`, `Int`, `Float`, `Bool`, `Image`, `Video`, `Audio`, `Document`, `Json`, `Timestamp`, `Date`, `UUID`, `Binary`, `Array[(3, 4), pxt.Float]`.

From a file: `pxt.create_table('dir.data', source='data.csv', if_exists='ignore')`.

Insert: `t.insert([{...}])`. `return_rows=True` returns computed columns on the status object.

```python
t.update({'score': 1.0}, where=t.category == 'important')
t.delete(where=t.is_active == False)
t.recompute_columns('summary', errors_only=True)
```

App: change a computed column in `app.py`, then `pxt schema update --allow-destructive`. Notebook: `drop_column` then recreate. `if_exists='ignore'` does not fix logic.

## Querying

```python
t.select(t.title, doubled=t.n * 2).where(t.n > 10).order_by(t.n, asc=False).limit(10).collect()
t.where(t.title.like('%pattern%')).count()
t.sample(n=100, seed=42).collect()
df = t.select(t.title).collect().to_pandas()  # export only
```

Aggregates run in queries, not computed columns:

```python
t.select(t.amount.sum()).collect()
t.group_by(t.region).select(t.region, total=t.amount.sum()).collect()
```

Local handle: `pxt.get_table('my_app.docs')`. Cloud: `pxt.get_table('pxt://org:db/docs')`.

## Computed columns

Notebook: `t.add_computed_column(...)`. App: assignment on the model.

```python
from pixeltable.functions.openai import chat_completions

t.add_computed_column(
    summary=chat_completions(
        messages=[{'role': 'user', 'content': t.body}],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore',
)
```

Extract the field (`.text`, `.choices[0].message.content`). Cast Json with `.astype(pxt.String)` only before embedding or concatenating.

## Views

Iterator output columns are reserved. Do not redeclare them. `string_splitter` / `document_splitter(..., separators='sentence')` need spaCy. `token_limit` needs `tiktoken`.

```python
from pixeltable.functions.document import document_splitter
from pixeltable.functions.video import frame_iterator
from pixeltable.functions.string import string_splitter
from pixeltable.functions.audio import audio_splitter
from pixeltable.functions.json import list_iterator

chunks = pxt.create_view(
    'dir.chunks', t,
    iterator=document_splitter(t.doc, separators='token_limit', limit=300),
    if_exists='ignore',
)
# Image elements only with separators='page' on PDFs
pages = pxt.create_view(
    'dir.pages', t,
    iterator=document_splitter(t.doc, separators='page', elements=['text', 'image']),
    if_exists='ignore',
)

# frame, frame_attrs (index, pts, dts, time, ...)
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video, fps=1.0), if_exists='ignore')

# text
sentences = pxt.create_view(
    'dir.sentences', t, iterator=string_splitter(text=t.body, separators='sentence'), if_exists='ignore',
)

# segment_start, segment_end, audio_segment
audio = pxt.create_view(
    'dir.audio', t, iterator=audio_splitter(audio=t.audio, duration=30.0), if_exists='ignore',
)

items = pxt.create_view('dir.items', t, iterator=list_iterator(t.tags), if_exists='ignore')
```

App: `base=` plus `iterator=` on the model. See [workflows.md](workflows.md).

## Indexes

App: `__indexes__ = [pxt.EmbeddingIndex(col, embedding=fn, name='...'), pxt.BtreeIndex(col)]`. Do not call `add_embedding_index()` in `app.py`. Index UDFs use `.using(...)`.

```python
from pixeltable.functions.openai import embeddings
from pixeltable.functions.huggingface import sentence_transformer

embed_fn = embeddings.using(model='text-embedding-3-small')
# or: sentence_transformer.using(model_id='sentence-transformers/all-MiniLM-L6-v2')

class Docs(TableModel, name='docs'):
    body: pxt.String
    __indexes__ = [pxt.EmbeddingIndex(body, embedding=embed_fn, name='body_idx')]

t.add_embedding_index('body', embedding=embed_fn, if_exists='ignore')

sim = t.body.similarity(string=query)
t.where(sim > 0.3).order_by(sim, asc=False).limit(10).select(t.body, score=sim).collect()
```

CLIP: `clip.using(model_id='openai/clip-vit-base-patch32')` then `similarity(string=...)` or `similarity(image=...)`. Metrics: `cosine` (default), `ip`, `l2`.

## UDFs

A UDF is recorded as a module path from the project root (`app.excerpt`). Type hints are required.

```python
@pxt.udf
def excerpt(text: str, n: int = 12) -> str:
    return text if len(text) <= n else f'{text[:n]}...'

from pixeltable.func import Batch

@pxt.udf(batch_size=32)
def batch_process(texts: Batch[str]) -> Batch[list[float]]:
    return model.encode(texts).tolist()

lookup_fn = pxt.retrieval_udf(t, name='lookup_items', description='Look up items by name',
    parameters=['name'], limit=5)
```

## UDAs

`@pxt.uda` is many rows → one value. Use in `select()` / `group_by()`, not `add_computed_column`. Subclass `pxt.Aggregator`: `__init__`, `update`, `value`. `__init__` args must be constants.

```python
@pxt.uda
class avg_int(pxt.Aggregator):
    def __init__(self):
        self.sum = 0
        self.count = 0

    def update(self, val: int) -> None:
        if val is not None:
            self.sum += val
            self.count += 1

    def value(self) -> float:
        return self.sum / self.count if self.count > 0 else 0.0

t.select(avg_int(t.value)).collect()
t.group_by(t.category).select(t.category, avg_val=avg_int(t.value)).collect()
```

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `requires_order_by` | `False` | First positional arg is the order key |
| `allows_std_agg` | `True` | Plain `SELECT agg(col)` |
| `allows_window` | `False` | `order_by=` / `group_by=` window calls |

Built-ins: `make_video`, `concat_videos_agg` (`pixeltable.functions.video`), `make_list` (`json`), `mean_ap` (`vision`). Scalar `concat_videos` takes a **list** of videos.

## Serving

`from pixeltable.serving import FastAPIRouter`. Start from `pxt service example --out app.py`. `add_update_route` / `add_delete_route` need a primary key (or `match_columns=`).

```python
from pixeltable.serving import FastAPIRouter

ingest = FastAPIRouter(name='ingest')
ingest.add_insert_route(Docs, path='/docs', inputs=[Docs.title, Docs.body], outputs=[Docs.title_upper])
ingest.add_compute_route(Docs, path='/titles', inputs=[Docs.title], outputs=[Docs.title_upper])
ingest.add_update_route(Docs, path='/update', inputs=[Docs.title], outputs=[Docs.title])
ingest.add_delete_route(Docs, path='/delete')

@pxt.query
def search_docs(query_text: str):
    sim = Docs.body.similarity(string=query_text)
    return Docs.where(sim > 0.3).order_by(sim, asc=False).select(text=Docs.body, score=sim).limit(20)

ingest.add_query_route(path='/search', query=search_docs, method='post')
```

`background=True` on insert returns `{ "id", "job_url" }`. Call `pxt.get_table()` inside custom FastAPI handlers. Do not `python app.py` if the file only declares models and routers. After a schema change, run `pxt service update` again.

## Tools

```python
from pixeltable.functions.openai import chat_completions, invoke_tools

tools = pxt.tools(search_docs, lookup_fn)
# invoke_tools is per provider: openai.invoke_tools vs anthropic.invoke_tools
```

MCP: `pxt.mcp_udfs(...)`. Keys: env or [Configuration](https://docs.pixeltable.com/platform/configuration), not `api_key=` in calls.

## Pitfalls

- `openai.vision` is deprecated. Use `chat_completions` with `image_url`.
- `from pixeltable.iterators import FrameIterator` is wrong. Use `frame_iterator` from `pixeltable.functions.video`.
- `similarity(query)` is wrong. Use `similarity(string=query)`.
- `@pxt.query` compiles at decoration time. Do not `.collect()` or `get_table()` a table that does not exist yet inside it.
- Image in messages: `{'type': 'image_url', 'image_url': {'url': t.image}}`.
- Data lives under `~/.pixeltable`, not in the repo.
- Export (CSV / Parquet / SQL): [docs](https://docs.pixeltable.com/).
