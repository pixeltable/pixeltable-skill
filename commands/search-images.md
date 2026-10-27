---
description: >
  Semantic search over an image collection: CLIP embeddings, similar images,
  and text-to-image search. Use for image similarity search, image semantic
  search, visual search, or multimodal embeddings of text and images.
argument-hint: "[image-dir-or-urls]"
---

Build image similarity search (similar photos, or search images by a text description). Request: `$ARGUMENTS`

Load the `image-similarity-search` skill and the `pixeltable` skill. Put the index on the table. Do not install a separate vector DB.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare an image table with a CLIP embedding index:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
clip = pxtf.huggingface.clip.using(model_id='openai/clip-vit-base-patch32')


class Images(TableModel, name='images'):
    image: pxt.Image
    __indexes__ = [pxt.EmbeddingIndex(image, embedding=clip, name='images_clip')]


@pxt.query
def search_images(query_text: str):
    sim = Images.image.similarity(string=query_text)
    return Images.order_by(sim, asc=False).select(Images.image, score=sim).limit(10)
```

3. Apply with `pxt schema update app.py my_app`. Insert images. Query with `similarity(string=...)` or `similarity(image=...)`. Do not pass only `image_embed=` if you will query with text. Needs `torch` and `transformers`.

4. Show how to insert sample images and collect top matches.
