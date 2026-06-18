---
description: Build a document RAG pipeline in Pixeltable (chunk, embed, retrieve, answer).
argument-hint: "[source docs or table name]"
---

Build a retrieval-augmented-generation pipeline using Pixeltable natively. Do NOT use LangChain, LlamaIndex, or a standalone vector DB — Pixeltable handles chunking, embedding, indexing, and retrieval.

Context: `$ARGUMENTS`

Produce idiomatic code following this shape:

```python
import pixeltable as pxt
from pixeltable.functions.document import document_splitter
from pixeltable.functions.openai import chat_completions, embeddings

pxt.create_dir('rag', if_exists='ignore')

docs = pxt.create_table('rag.docs', {'doc': pxt.Document}, if_exists='ignore')

chunks = pxt.create_view(
    'rag.chunks', docs,
    iterator=document_splitter(docs.doc, separators='token_limit', limit=300),
    if_exists='ignore',
)

chunks.add_embedding_index(
    'text',
    embedding=embeddings(model='text-embedding-3-small'),
    if_exists='ignore',
)

@pxt.query
def top_k(query_text: str, k: int = 5):
    sim = chunks.text.similarity(string=query_text)
    return chunks.order_by(sim, asc=False).select(chunks.text, sim=sim).limit(k)
```

Requirements:
- Chunk with a view + `document_splitter` (install `tiktoken` for `token_limit`).
- Search with `column.similarity(string=query)` — keyword arg, never positional.
- Cast AI-generated text to `pxt.String` before indexing if needed (`.astype(pxt.String)`).
- Build the answer step as a computed column over retrieved context, not a Python loop.
- Use `if_exists='ignore'` on every create/add call.

For deeper patterns, consult the `pixeltable` skill (`references/workflows.md` → RAG Pipeline).
