---
description: >
  Index a video library and search by what is in the videos: extract frames,
  embed them with CLIP, search by text or image. Use for video search, video
  frame extraction, video analysis, or a searchable recording archive.
argument-hint: "[video-dir-or-urls]"
---

Index videos so they are searchable by content. Request: `$ARGUMENTS`

Load the `video-search` skill and the `pixeltable` skill. Put models in `app.py`. Do not install a separate vector DB or pull frames in a Python loop.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare a video table, a frame view, and a CLIP embedding index:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
clip = pxtf.huggingface.clip.using(model_id='openai/clip-vit-base-patch32')


class Videos(TableModel, name='videos'):
    video: pxt.Video


class Frames(
    TableModel,
    name='frames',
    base=Videos,
    iterator=pxtf.video.frame_iterator(Videos.video, fps=1.0),
):
    __indexes__ = [pxt.EmbeddingIndex(frame, embedding=clip, name='frames_clip')]  # type: ignore[name-defined]


@pxt.query
def search_videos(query_text: str):
    sim = Frames.frame.similarity(string=query_text)
    return Frames.order_by(sim, asc=False).select(Frames.frame, score=sim).limit(10)
```

3. Apply with `pxt schema update app.py my_app`. Insert video paths or URLs into `videos`. Search with `similarity(string=query)` (or `image=`). Needs `torch` and `transformers`.

4. Show how to insert one video and collect top matches so the user can verify search.
