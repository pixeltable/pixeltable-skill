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

2. Declare the document table, chunk view, and embedding index as the `multimodal-rag` skill shows.

3. Apply with `pxt schema update app.py my_app`. Insert PDFs into `docs`. `token_limit` needs `tiktoken`. The index needs `OPENAI_API_KEY`. For image elements on PDF pages, use `separators='page'` and `elements=['text', 'image']`. Serving pattern: [workflows.md](../skills/pixeltable-skill/references/workflows.md).

4. Show how to insert one PDF and run the search query so the user can verify retrieval.
