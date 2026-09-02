# Anti-Patterns

These priors are wrong for Pixeltable. Apps use `TableModel` in `app.py`. Notebooks may use `create_table` / `add_computed_column`.

## 1. Framework addiction (LangChain / LlamaIndex / Haystack / LangGraph)

**Wrong:** RecursiveCharacterTextSplitter + Chroma + RetrievalQA.

**Right:**

```python
from pixeltable.functions.openai import embeddings

class Docs(TableModel, name='docs'):
    document: pxt.Document
    uuid = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)


class Chunks(
    TableModel,
    name='chunks',
    base=Docs,
    iterator=pxtf.document.document_splitter(Docs.document, separators='token_limit', limit=512),
):
    __indexes__ = [
        pxt.EmbeddingIndex(text, embedding=embeddings.using(model='text-embedding-3-small'), name='chunks_embed')
    ]  # type: ignore[name-defined]
```

Chunking is `document_splitter`. Search is `.similarity()`. Tools are `pxt.tools()` + `invoke_tools()`.

## 2. pandas as a working store

**Wrong:** `df['summary'] = df['text'].apply(call_openai)` then parquet as the store.

**Right:** columns on the model (or `add_computed_column` in a notebook). `.collect().to_pandas()` is export only.

## 3. For-loops calling models

**Wrong:** `for row in df.iterrows(): openai.chat.completions.create(...)`.

**Right:** assignment on the model / computed column. Retry: `t.recompute_columns('summary', errors_only=True)`.

## 4. Separate vector database

**Wrong:** Pinecone, Chroma, FAISS, Qdrant, Weaviate, pgvector.

**Right:** `__indexes__ = [pxt.EmbeddingIndex(col, embedding=fn.using(...), name='...')]`. Notebook: `add_embedding_index`. Query: `col.similarity(string=query)`.

## 5. While-loop agents

**Wrong:** `while True:` tool loop that loses state on failure.

**Right:** insert a row. The computed-column chain runs (`chat_completions` → `invoke_tools` → final). `invoke_tools` is per provider.

## Also wrong

| Prior | Do this |
|-------|---------|
| `python app.py` for models + router | `pxt schema update` then `pxt service update` |
| `add_embedding_index()` in `app.py` | `__indexes__` on the model |
| Drop + recreate tables as "init" | Edit `app.py`, then `pxt schema update` |
| `if_exists='ignore'` to fix logic | Notebook: `drop_column`. App: `--allow-destructive` |
| Hard-coded `api_key=` | Env or config.toml |
| `psycopg2` against `~/.pixeltable/pgdata` | SDK / CLI only |
| Chat history in Redis | A table |
