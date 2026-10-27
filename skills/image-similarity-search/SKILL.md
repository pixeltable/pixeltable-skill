---
name: image-similarity-search
description: >
  Semantic search over an image collection: find similar images and search
  images by a text description. Use when you want CLIP embeddings, visual
  similarity search, image-to-image retrieval, or multimodal embeddings for
  text and images. Covers image semantic search, cross-modal retrieval, and
  duplicate detection. Embeddings stay on the image table. A CLIP index on
  an image column answers similarity(string=...) and similarity(image=...).
  Load the pixeltable skill for the full app.py backend.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill for visual similarity search, searching photos by a
text query, or generating multimodal embeddings for text and images.
CLIP understands images and text in one space, so one index on the
image column serves both query types.

Do not pass only `image_embed=` if you will query with
`similarity(string=...)`. Prefer `embedding=clip.using(...)` so both
modalities register. CLIP needs `torch` and `transformers`.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.huggingface import clip

pxt.create_dir('image_lib', if_exists='ignore')
images = pxt.create_table(
    'image_lib.images', {'image': pxt.Image}, if_exists='ignore',
)
images.add_embedding_index(
    'image',
    embedding=clip.using(model_id='openai/clip-vit-base-patch32'),
    if_exists='ignore',
)
sim = images.image.similarity(string='people eating food')
images.order_by(sim, asc=False).limit(5).select(
    images.image, score=sim,
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
