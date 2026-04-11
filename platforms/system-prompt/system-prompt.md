Pixeltable: open-source Python (>= 3.10) for declarative multimodal AI data infrastructure. `pip install pixeltable`

TABLES: pxt.create_table('dir.name', {'col': pxt.String, 'img': pxt.Image}, if_exists='ignore')
Types: String, Int, Float, Bool, Image, Video, Audio, Document, Json, Array, Timestamp, Date, UUID, Binary.

COMPUTED COLUMNS: t.add_computed_column(result=fn(t.col), if_exists='ignore')
Auto-run on insert. Use AI provider functions from pixeltable.functions.*.

QUERYING: t.where(t.col > val).order_by(t.col).limit(n).select(t.col).collect()
Pagination: .limit(n, offset=m). To pandas: .collect().to_pandas(). To Pydantic: .collect().to_pydantic(Model).

VIEWS: pxt.create_view('dir.v', t, iterator=splitter(t.col), if_exists='ignore')
Document chunking (document_splitter), video frames (frame_iterator), audio splitting (audio_splitter).

EMBEDDINGS: t.add_embedding_index('col', embedding=fn, if_exists='ignore')
SEARCH: sim = t.col.similarity(string='query'); t.order_by(sim, asc=False).limit(k).collect()

UDFs: @pxt.udf for transforms, @pxt.query for reusable queries (also usable as agent tools).

AGENTS: tools = pxt.tools(udf, query); use with messages() + invoke_tools() as computed columns.
invoke_tools available for: openai, anthropic, groq, gemini, bedrock.

PROVIDERS (pixeltable.functions.*): openai, anthropic, gemini, huggingface, together, fireworks, ollama, mistralai, groq, deepseek, openrouter, replicate, voyageai, bedrock, twelvelabs, jina, bfl, runwayml, fal, reve, fabric, llama_cpp, whisper, whisperx, yolox.
Output: OpenAI-compatible → .choices[0].message.content. Anthropic → .content[0].text.

EXPORT: export_parquet(t, 'path/'), export_sql(t, 'table', db_connect_str='...'), .to_pytorch_dataset(image_format='pt').

RULES: Always if_exists='ignore'. Use on_error='ignore' for fault-tolerant inserts. Retry: t.recompute_columns(columns=['col'], where=t.col.errortype != None). FastAPI: def not async def. Anthropic messages: [{'type': 'text', 'text': val}] content blocks.

Docs: https://docs.pixeltable.com/ | GitHub: https://github.com/pixeltable/pixeltable
LLM docs: https://www.pixeltable.com/llms.txt | https://docs.pixeltable.com/llms.txt | https://docs.pixeltable.com/llms-full.txt
