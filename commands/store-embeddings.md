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

2. Declare the table and embedding index as the `vector-database-alternative` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert rows. Search with `similarity(string=query)`, never a positional argument. Needs `OPENAI_API_KEY`. For images or video frames, use CLIP (`embedding=clip`) as in [search-images.md](search-images.md) / [index-videos.md](index-videos.md).

4. Show how to insert a row and retrieve nearest neighbors.
