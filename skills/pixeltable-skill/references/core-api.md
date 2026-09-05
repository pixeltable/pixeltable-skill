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
- [Built-in functions](#built-in-functions)
- [Import and export](#import-and-export)
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

`pxt.Column(...)` expresses what a bare annotation cannot:

| Param | Purpose |
|-------|---------|
| `type=` | Explicit type where there is no annotation |
| `value=` | Computed expression (a plain assignment does the same) |
| `primary_key=True` | Part of the primary key |
| `stored=False` | Computed on read, never materialized |
| `media_validation=` | `'on_write'` (default) validates on insert; `'on_read'` defers to first read |
| `destination=` | Object store for computed media: `s3`, `gs`, `az`, `r2`, `b2`, `tigris`, `http`, a local path, or `pxtfs`. Also takes a `ConfigVar[URI]`; `add_computed_column(destination=)` takes only `str \| Path` |

```python
thumbnail = pxt.Column(value=cover.rotate(90), stored=False)
scan = pxt.Column(type=pxt.Image, media_validation='on_read', comment='validated lazily')
```

The model class itself takes `name=`, `base=`, `iterator=`, plus `media_validation=`, `comment=`, `custom_metadata=`, `has_default_idxs=`.

From a file: `pxt.create_table('dir.data', source='data.csv', if_exists='ignore')`.

Insert: `t.insert([{...}])`. `return_rows=True` returns computed columns on the status object. `source=` also takes a path or URL (`source_format='csv'|'excel'|'parquet'|'json'`, `schema_overrides=`), a DataFrame, a list of dicts or Pydantic models, another table or query, or a HF dataset.

**Do not let one bad row abort a batch.** `insert(..., on_error='ignore')` and `add_computed_column(..., on_error='ignore')` keep the row, leave the failed cell `None`, and record the reason in `t.<col>.errortype` / `t.<col>.errormsg` (stored computed or media columns only). `t.<col>.fileurl` / `.localpath` locate a media cell.

```python
t.update({'score': 1.0}, where=t.category == 'important')
t.delete(where=t.is_active == False)
t.recompute_columns('summary', errors_only=True)
```

Changing a computed column's logic:

- **App.** Editing an existing column's expression in place is reported `UNSUPPORTED`. `--allow-destructive` does **not** help, and one unsupported table makes the whole `pxt schema update` apply nothing. **Rename** the column instead: the old name is a destructive drop, the new one an additive add, so it lands in one pass with `--allow-destructive`. Or drop it in one pass and re-add it in a second. Either way the data is destroyed and recomputed. (`pxt.move()` is for a genuine rename, where you keep the values.)
- **Notebook.** `t.add_computed_column(summary=..., if_exists='replace')` replaces it in one call. It raises `AlreadyExistsError` if the column has dependents or is a base-table column; then drop the dependents, or `drop_column` and recreate.
- `if_exists='ignore'` never fixes logic -- it skips the call.

## Querying

```python
t.select(t.title, doubled=t.n * 2).where(t.n > 10).order_by(t.n, asc=False).limit(10).collect()
t.where(t.title.like('%pattern%')).count()
t.sample(n=100, seed=42).collect()
df = t.select(t.title).collect().to_pandas()  # export only
```

One `.where()` per query. Compose extra predicates with `&` / `|` (`t.where((t.n > 10) & t.active)`); do not chain `.where()`.

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

A view is either a **filter** over a base or an **iterator** that expands each base row into many. Rows follow the base; you never insert into a view.

### Filtered views

`base=` takes a query over another model, not just the model:

```python
class Titled(TableModel, name='titled', base=Docs.where(Docs.title != '')):
    headline = Docs.title_upper + '!'      # may reference the base's computed columns
```

Notebook: `pxt.create_view('dir.titled', t.where(t.title != ''), if_exists='ignore')`. Add `is_snapshot=True` to freeze it.

### Iterator views

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

# Output columns: pos, frame, frame_attrs  (timestamp is frame_attrs.time)
# Not frame_idx / pos_msec / pos_frame (legacy_frame_iterator only)
frames = pxt.create_view('dir.frames', t, iterator=frame_iterator(t.video, fps=1.0), if_exists='ignore')
frames.select(frames.pos, frames.frame, time=frames.frame_attrs.time).collect()

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

An unbound model class builds queries (`.where()`, `.select()`, `.order_by()`, `.group_by()`, `.limit()`, `.sample()`, `.join()`) -- that is what makes `base=Docs.where(...)` work. Anything that touches rows (`.collect()`, `.insert()`, `.count()`, `.update()`) needs the table to exist: use `pxt.get_table()`, or let a bound router reach it.

Every iterator view also gets `pos`. The nine that ship:

| Iterator | Module | Output columns |
|----------|--------|----------------|
| `document_splitter` | `functions.document` | subset of `text, image, title, heading, sourceline, page, bounding_box` per `elements=` / `metadata=` |
| `frame_iterator` | `functions.video` | `frame` (unstored), `frame_attrs` (`.time`, `.index`, `.key_frame`, ...) |
| `video_splitter` | `functions.video` | `segment_start`, `segment_start_pts`, `segment_end`, `segment_end_pts`, `video_segment` |
| `audio_splitter` | `functions.audio` | `segment_start`, `segment_end`, `audio_segment` |
| `string_splitter` | `functions.string` | `text` |
| `list_iterator` | `functions.json` | keys of `elements=`, or the kwarg names |
| `tile_iterator` | `functions.image` | `tile` (unstored), `tile_coord`, `tile_box` |

`legacy_frame_iterator` (`frame_idx` / `pos_msec` / `pos_frame`) and `sam3_for_video_segmentation` also exist; prefer `frame_iterator`.

## Indexes

App: `__indexes__ = [pxt.EmbeddingIndex(col, embedding=fn, name='...'), pxt.BtreeIndex(col)]`. Do not call `add_embedding_index()` in `app.py`. Index UDFs use `.using(...)`.

One `embedding=` covers a single modality. For a column searchable by more than one, pass the per-modality functions instead: `string_embed=`, `image_embed=`, `audio_embed=`, `video_embed=`, `document_embed=`. Also `metric=` (`'cosine'` default), `precision=` (`'fp16'` default, `'fp32'` available). **The DSL names an index `name=`; `add_embedding_index()` names it `idx_name=`.**

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

`similarity()` takes exactly one of `string=`, `image=`, `audio=`, `video=`, `document=`, `vector=` (a raw array of the index's dimensionality). A positional argument is deprecated. When a column carries more than one embedding index, `idx='name'` picks one.

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

Built-ins: `make_video`, `concat_videos_agg` (`pixeltable.functions.video`), `make_list` (`json`), `stitch_tiles` (`image`), `mean_ap` (`vision`). Scalar `concat_videos` takes a **list** of videos.

`requires_order_by` UDAs take the ordering expression as their **first positional argument**; passing `order_by=` raises. Two ship built in:

```python
t.select(pxtf.video.make_video(t.pos, t.frame, fps=30))          # not make_video(t.frame, order_by=t.pos)
t.group_by(base).select(pxtf.image.stitch_tiles(t.pos, t.tile, t.tile_box, width, height))
```

## Built-in functions

Before writing a UDF, check whether the operation already ships. `pixeltable.functions` (`pxtf`) carries `string`, `json`, `math`, `date`, `timestamp`, `array`, `uuid`, `image`, `audio`, `document`, `net`, `vision`, and `video` (which splits into `video.editing`, `video.filters`, `video.scene_detect`). Import the module and read its docs rather than guessing a name.

The one path worth spelling out, because nothing else documents it -- video to transcript:

```python
class Clips(TableModel, name='clips'):
    video: pxt.Video
    audio = pxtf.video.extract_audio(video, format='mp3')
    transcript = pxtf.openai.transcriptions(audio=audio, model='whisper-1').text
```

Also on video: `clip`, `segment_video`, `extract_frame`, `concat_videos`, `with_audio`, `get_duration`, `get_metadata`, plus the `filters` (`overlay_text`, `crop`, `resize`, `speed`, ...) and `scene_detect_*` families.

## Import and export

`pxt.io.import_{csv,json,parquet,excel,pandas,rows,sql,huggingface_dataset}` and `pxt.io.export_{csv,json,parquet,sql,iceberg,lancedb,images_as_fo_dataset}`. Do not hand-roll a reader or writer.

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

`background=True` returns `{ "id", "job_url" }`. Poll `job_url`; status is `pending` | `done` | `error` (not `succeeded`). JSON media fields are `{prefix}/_pxt/media/...` URLs. `add_compute_route` computes without inserting. `add_query_route(..., one_row=True, return_fileresponse=True)` returns one media file. Details: [workflows.md](workflows.md). Call `pxt.get_table()` inside custom FastAPI handlers. Do not `python app.py` if the file only declares models and routers. After a schema change, run `pxt service update` again.

## Tools

```python
from pixeltable.functions.openai import chat_completions, invoke_tools

tools = pxt.tools(search_docs, lookup_fn)
# invoke_tools is per provider: openai.invoke_tools vs anthropic.invoke_tools
```

MCP: `pxt.mcp_udfs(url)` returns one UDF per remote tool over streamable HTTP; tools returning images or audio are not supported. Keys: env or [Configuration](https://docs.pixeltable.com/platform/configuration), not `api_key=` in calls.

## Pitfalls

- `openai.vision` is deprecated. Use `chat_completions` with `image_url`.
- `from pixeltable.iterators import FrameIterator` is wrong. Use `frame_iterator` from `pixeltable.functions.video`. Outputs: `pos`, `frame`, `frame_attrs` (`frame_attrs.time` is the timestamp). Not `frame_idx` / `pos_msec` / `pos_frame`.
- `similarity(query)` is wrong. Use `similarity(string=query)`.
- `@pxt.query` compiles at decoration time. Do not `.collect()` or `get_table()` a table that does not exist yet inside it.
- Image in messages: `{'type': 'image_url', 'image_url': {'url': t.image}}`.
- Data lives under `~/.pixeltable`, not in the repo.
- Export (CSV / Parquet / SQL): [docs](https://docs.pixeltable.com/).
