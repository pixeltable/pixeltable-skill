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

2. Declare the video table, frame view, CLIP embedding index, and search query as the `video-search` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert video paths or URLs into `videos`. Search with `similarity(string=query)` (or `image=`). Needs `torch` and `transformers`.

4. Show how to insert one video and collect top matches so the user can verify search.
