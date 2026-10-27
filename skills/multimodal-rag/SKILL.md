---
name: multimodal-rag
description: >
  Build multimodal RAG over PDFs, slide decks, images, and documents: chunk
  files, embed the chunks, and run semantic search for a RAG chatbot. Use
  when setting up RAG over a folder of PDFs, indexing documents that include
  images, chunking documents then embedding them, or building
  retrieval-augmented generation. Covers PDF RAG, document chunking,
  embeddings, and multimodal retrieval. Pixeltable stores chunks as rows
  with an embedding index on the table. Load the pixeltable skill for the
  full app.py backend, HTTP search routes, and provider setup.
license: Apache-2.0
metadata:
  author: Pixeltable
  version: 2.12.1
---

## When to use

Use this skill to build RAG over PDFs, slide decks, and other documents,
including files that mix text and images. Chunking is a view over the
document table. Embeddings live on that view. New documents are chunked
and indexed on insert.

For PDF pages that include images, `document_splitter` can emit `text`
and `image` rows with `separators='page'` and `elements=['text', 'image']`.
Sentence splitting needs spaCy. `token_limit` needs tiktoken.

## Minimal pattern

```python
import pixeltable as pxt
from pixeltable.functions.document import document_splitter
from pixeltable.functions.openai import embeddings

pxt.create_dir('rag', if_exists='ignore')
docs = pxt.create_table(
    'rag.docs', {'document': pxt.Document}, if_exists='ignore',
)
chunks = pxt.create_view(
    'rag.chunks',
    docs,
    iterator=document_splitter(
        docs.document, separators='token_limit', limit=300,
        metadata='title,heading,page',
    ),
    if_exists='ignore',
)
chunks.add_embedding_index(
    'text',
    embedding=embeddings.using(model='text-embedding-3-small'),
    if_exists='ignore',
)
sim = chunks.text.similarity(string='your question')
chunks.order_by(sim, asc=False).limit(5).select(
    chunks.text, score=sim,
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
