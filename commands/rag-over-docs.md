---
description: >
  Set up RAG over PDFs, slide decks, and documents that include images:
  chunk, embed, retrieve. Use for multimodal RAG, PDF RAG, document
  chunking and embeddings, or a RAG chatbot over a folder of PDFs.
argument-hint: "[pdf-dir-or-files]"
---

Build RAG over PDFs and documents (including decks that contain images). Request: `$ARGUMENTS`

Load the `multimodal-rag` skill and the `pixeltable` skill. Chunking is `document_splitter`. Search is `.similarity()`. Do not add LangChain, LlamaIndex, or a separate vector DB.

Steps:

1. If there is no project yet, follow [pixeltable-start.md](pixeltable-start.md).

2. Declare a document table, a chunk view, and an embedding index:

```python
import pixeltable as pxt
import pixeltable.functions as pxtf

TableModel = pxt.model_base()
embed_fn = pxtf.openai.embeddings.using(model='text-embedding-3-small')


class Docs(TableModel, name='docs'):
    document: pxt.Document


class Chunks(
    TableModel,
    name='chunks',
    base=Docs,
    iterator=pxtf.document.document_splitter(
        Docs.document, separators='page, token_limit', limit=300, metadata='title,heading,page'
    ),
):
    __indexes__ = [pxt.EmbeddingIndex(text, embedding=embed_fn, name='chunks_embed')]  # type: ignore[name-defined]


@pxt.query
def search_docs(query_text: str):
    sim = Chunks.text.similarity(string=query_text)
    return Chunks.order_by(sim, asc=False).select(
        text=Chunks.text, page=Chunks.page, score=sim
    ).limit(10)
```

3. Apply with `pxt schema update app.py my_app`. Insert PDFs into `docs`. `token_limit` needs `tiktoken`. The index needs `OPENAI_API_KEY`. For image elements on PDF pages, use `separators='page'` and `elements=['text', 'image']`. Serving pattern: [workflows.md](../skills/pixeltable-skill/references/workflows.md).

4. Show how to insert one PDF and run `search_docs` so the user can verify retrieval.
