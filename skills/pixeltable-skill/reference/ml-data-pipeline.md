# ML Data Wrangling Pipeline

A complete recipe for processing multimodal data (video, audio, images, documents) into training-ready datasets. Covers ingestion, enrichment with AI models, dataset versioning, and export to PyTorch, Parquet, and pandas.

## Full Pipeline

```python
import pixeltable as pxt
from pixeltable.functions.video import frame_iterator
from pixeltable.functions.openai import chat_completions
from pixeltable.functions.huggingface import clip, detr_for_object_detection
from pixeltable.functions import image as pxt_image

pxt.create_dir('ml_data', if_exists='ignore')

# ── 1. Ingest raw data ──────────────────────────────────────────────

# From local files, URLs, or cloud storage (S3, GCS, Azure)
images = pxt.create_table('ml_data.images', {
    'image': pxt.Image,
    'filename': pxt.String,
    'split': pxt.String,        # 'train', 'val', 'test'
}, if_exists='ignore')

images.insert([
    {'image': 'path/to/cat_01.jpg', 'filename': 'cat_01.jpg', 'split': 'train'},
    {'image': 'path/to/dog_01.jpg', 'filename': 'dog_01.jpg', 'split': 'train'},
    {'image': 's3://bucket/images/bird.jpg', 'filename': 'bird.jpg', 'split': 'val'},
])

# From CSV with schema overrides for media columns
labeled_data = pxt.create_table('ml_data.labeled',
    source='annotations.csv',
    schema_overrides={'image_path': pxt.Image},
    if_exists='ignore')

# From Hugging Face datasets
from pixeltable.io import import_huggingface_dataset
import datasets
ds = datasets.load_dataset('cifar10', split='train[:500]')
cifar = import_huggingface_dataset('ml_data.cifar', ds, if_exists='ignore')

# ── 2. Explore and sample ───────────────────────────────────────────

# Quick look at the data
first_5 = images.head(5)
total = images.count()
train_count = images.where(images.split == 'train').count()

# ── 3. Enrich with AI models ────────────────────────────────────────

# Resize images for consistent training input
images.add_computed_column(
    resized=pxt_image.resize(images.image, width=224, height=224),
    if_exists='ignore')

# Auto-classify with a vision LLM
images.add_computed_column(
    label=chat_completions(
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Classify this image into exactly one word: cat, dog, bird, or other.'},
                {'type': 'image_url', 'image_url': {'url': images.image}}
            ]
        }],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore')

# Object detection for bounding boxes
detect = detr_for_object_detection.using(model_id='facebook/detr-resnet-50')
images.add_computed_column(
    detections=detect(images.image, threshold=0.8),
    if_exists='ignore')

# Generate captions
images.add_computed_column(
    caption=chat_completions(
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Describe this image in one sentence.'},
                {'type': 'image_url', 'image_url': {'url': images.image}}
            ]
        }],
        model='gpt-4o-mini',
    ).choices[0].message.content,
    if_exists='ignore')

# Add CLIP embeddings for similarity search and deduplication
embed_fn = clip.using(model_id='openai/clip-vit-base-patch32')
images.add_embedding_index('image', embedding=embed_fn, if_exists='ignore')

# ── 4. Curate: filter, deduplicate, quality check ───────────────────

# Test on a small sample first (recommended workflow)
sample = images.limit(5).select(images.image, images.label, images.caption).collect()

# Filter by label
cats = images.where(images.label == 'cat').select(images.image, images.caption).collect()

# Find near-duplicates via similarity
sim = images.image.similarity(image='path/to/reference.jpg')
near_dupes = images.where(sim > 0.95).select(images.filename, sim).collect()

# Review errors from computed columns
errors = images.where(images.label.errortype != None).select(
    images.filename, images.label.errormsg).collect()

# ── 5. Video → frame extraction → labeled dataset ───────────────────

videos = pxt.create_table('ml_data.videos', {
    'video': pxt.Video,
    'category': pxt.String,
}, if_exists='ignore')

frames = pxt.create_view('ml_data.frames', videos,
    iterator=frame_iterator(videos.video, fps=1.0),
    if_exists='ignore')

frames.add_computed_column(
    resized=pxt_image.resize(frames.frame, width=224, height=224),
    if_exists='ignore')

# ── 6. Retrieval UDFs for structured data lookup ────────────────────

# Create a lookup function for enrichment across tables
products = pxt.create_table('ml_data.products', {
    'sku': pxt.String,
    'name': pxt.String,
    'category': pxt.String,
}, if_exists='ignore')

get_product = pxt.retrieval_udf(
    products,
    name='get_product',
    description='Look up a product by SKU',
    parameters=['sku'],
    limit=1,
)

# Use as a computed column for cross-table enrichment
# orders.add_computed_column(product_info=get_product(sku=orders.product_sku), if_exists='ignore')

# ── 7. Version with snapshots ───────────────────────────────────────

# Take a point-in-time snapshot before exporting
snap_v1 = pxt.create_snapshot('ml_data.images_v1', images, if_exists='ignore')

# Later, take another snapshot after adding more data
# snap_v2 = pxt.create_snapshot('ml_data.images_v2', images, if_exists='ignore')

# Query any snapshot like a regular table
snap_v1.select(snap_v1.filename, snap_v1.label).limit(5).collect()

# ── 8. Export for training ───────────────────────────────────────────

# To PyTorch Dataset (recommended for training loops)
train_query = images.where(images.split == 'train').select(
    images.resized, images.label)

pytorch_ds = train_query.to_pytorch_dataset(image_format='pt')

from torch.utils.data import DataLoader
dataloader = DataLoader(pytorch_ds, batch_size=32, num_workers=4)

# Iterate in a training loop
for batch in dataloader:
    imgs, labels = batch  # imgs: (32, 3, 224, 224) tensor
    # ... training step ...
    break

# To Parquet (for Spark, DuckDB, or cross-platform sharing)
from pixeltable.io import export_parquet

export_parquet(
    images.where(images.split == 'train').select(
        images.filename, images.label, images.caption),
    'output/train/')

export_parquet(
    images.where(images.split == 'val').select(
        images.filename, images.label, images.caption),
    'output/val/')

# To pandas (for quick analysis or CSV export)
df = images.select(
    images.filename, images.label, images.caption
).collect().to_pandas()
df.to_csv('output/annotations.csv', index=False)
```

## Key Patterns

### Test Before Deploying

Always test transformations on a small sample before committing:

```python
# 1. Test the expression inline
result = images.limit(5).select(
    images.image, label=chat_completions(...).choices[0].message.content
).collect()

# 2. Review results, then deploy as a computed column
images.add_computed_column(label=chat_completions(...).choices[0].message.content, if_exists='ignore')
```

### Error Handling for Batch Processing

```python
# Insert with error tolerance
status = images.insert(rows, on_error='ignore')
print(f'Inserted: {status.num_rows}, Errors: {status.num_excs}')

# Find and inspect failed rows
errors = images.where(images.label.errortype != None).select(
    images.filename, images.label.errormsg).collect()
```

### PyTorch Dataset Options

| Parameter | Values | Description |
|-----------|--------|-------------|
| `image_format` | `'pt'` | CxHxW float tensors in [0, 1] |
| `image_format` | `'np'` | HxWxC uint8 arrays in [0, 255] |

Data is cached to disk for efficient repeated loading. Use `num_workers > 0` in DataLoader for parallel loading.

## Building Blocks

| Step | Function | Purpose |
|------|----------|---------|
| Ingest | `create_table(source='file.csv')` | Load from CSV, Parquet, URLs, S3 |
| Ingest | `import_huggingface_dataset()` | Load from Hugging Face Hub |
| Explore | `t.head(5)`, `t.count()` | Quick data inspection |
| Enrich | `add_computed_column(label=...)` | Auto-label with AI models |
| Enrich | `detr_for_object_detection()` | Bounding box detection |
| Search | `add_embedding_index()` + `.similarity()` | Find similar / deduplicate |
| Curate | `.where(col.errortype != None)` | Review failed transformations |
| Version | `create_snapshot('name', table)` | Point-in-time dataset copy |
| Export | `to_pytorch_dataset(image_format='pt')` | PyTorch DataLoader-ready |
| Export | `export_parquet(query, 'path/')` | Parquet files for sharing |
| Export | `.collect().to_pandas()` | pandas DataFrame |
| Lookup | `pxt.retrieval_udf(table, ...)` | Structured data enrichment |

## Adapting This Recipe

- **Audio data**: Use `audio_splitter` and `transcriptions` to create labeled audio datasets — see [workflows.md → Audio Transcription](workflows.md#audio-transcription-and-analysis)
- **Document data**: Use `document_splitter` to chunk PDFs into training examples — see [workflows.md → RAG Pipeline](workflows.md#rag-pipeline)
- **Add human labels**: Export to Label Studio, annotate, then re-import
- **Multi-GPU training**: The PyTorch dataset supports `DistributedSampler` with standard PyTorch patterns
