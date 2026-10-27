---
description: >
  Store embeddings next to your data instead of running a separate vector
  database (Qdrant, pgvector, Pinecone, Chroma, Weaviate, FAISS). Use for
  embeddings and vector search in the same tables as PDFs, images, video,
  or audio.
argument-hint: "[what to embed]"
---

Store embeddings with the source rows instead of adding a standalone vector DB. Request: `$ARGUMENTS`

Load the `vector-database-alternative` skill and the `pixeltable` skill. Indexes go on the table. Do not install Qdrant, pgvector, Pinecone, Chroma, Weaviate, or FAISS for this.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare a table with an embedding index:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
embed_fn = pxtf.openai.embeddings.using(model='text-embedding-3-small')


class Items(TableModel, name='items'):
    body: pxt.String
    __indexes__ = [pxt.EmbeddingIndex(body, embedding=embed_fn, name='body_idx')]


@pxt.query
def search_items(query_text: str):
    sim = Items.body.similarity(string=query_text)
    return Items.order_by(sim, asc=False).select(Items.body, score=sim).limit(10)
```

3. Apply with `pxt schema update app.py my_app`. Insert rows. Search with `similarity(string=query)`, never a positional argument. Needs `OPENAI_API_KEY`. For images or video frames, use CLIP (`embedding=clip`) as in [search-images.md](search-images.md) / [index-videos.md](index-videos.md).

4. Show how to insert a row and retrieve nearest neighbors.
