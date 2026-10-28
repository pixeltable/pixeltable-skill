---
name: video-search
description: >
  Index and semantically search a video library by what is actually in the
  videos: extract frames, embed them, and find matching scenes with
  similarity search. Use when searching videos by a text description,
  extracting frames for a vision model, running video analysis, or storing
  detections from video files. Covers video search, video frame extraction,
  CLIP embeddings, and semantic video search. A CLIP index on an image
  (frame) column can answer similarity(string=...). Load the pixeltable
  skill for the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.13.0
---

## When to use

Use this skill to search a video library by visual content, not only
by filename or transcript. Pixeltable turns each video into frame rows,
then an embedding index on those frames supports text-to-video and
image-to-frame search.

`frame_iterator` takes at most one of `fps`, `num_frames`, or
`keyframes_only`. Frame timestamp is `frame_attrs.time`, not a legacy
`pos_msec` column. CLIP needs `torch` and `transformers`.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.huggingface import clip
from pixeltable.functions.video import frame_iterator

pxt.create_dir('video_lib', if_exists='ignore')
videos = pxt.create_table(
    'video_lib.videos', {'video': pxt.Video}, if_exists='ignore',
)
frames = pxt.create_view(
    'video_lib.frames',
    videos,
    iterator=frame_iterator(videos.video, fps=1.0),
    if_exists='ignore',
)
frames.add_embedding_index(
    'frame',
    embedding=clip.using(model_id='openai/clip-vit-base-patch32'),
    if_exists='ignore',
)
sim = frames.frame.similarity(string='a red bicycle')
frames.order_by(sim, asc=False).limit(5).select(
    frames.frame, time=frames.frame_attrs.time, score=sim,
).collect()
```

Notebook or REPL form (`if_exists='ignore'` so it is re-runnable). For an
HTTP app, load the `pixeltable` skill and declare the same columns on a
`TableModel` with indexes in `__indexes__`, then `pxt schema update`.

## Full guidance

This skill is a thin catalog entry. Load the `pixeltable` skill for the
application file, CLI, providers, serving, and anti-patterns:
`skills/pixeltable-skill/SKILL.md` in this repo.

Install: `npx skills add pixeltable/pixeltable-skill`.
Docs: https://docs.pixeltable.com/
