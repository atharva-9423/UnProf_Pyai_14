# ✂️ Text Chunking Utility — Day 13 (Phase 2: NLP & Text AI)

Reads a **PDF**, extracts its text, and splits it into **smart, overlapping,
metadata-rich chunks** — the foundation of a **RAG (Retrieval-Augmented Generation)**
pipeline. The web app runs the whole flow end to end.

> 🔗 **Continues Day 12:** this tool reads the exact JSON produced by the Day 12
> PDF Extractor. Pipeline so far: **PDF → extract text (Day 12) → chunk (Day 13)**
> → *embed → vector DB → retrieve (coming next)*.

## 🎯 Why Chunk?

Large documents can't be fed to an LLM whole:
- **Context window** — LLMs accept a limited number of tokens.
- **Embedding quality** — embedding models work best on short, focused passages.
- **Retrieval precision** — one idea per chunk = more relevant search results.

## 🧩 Chunking Strategies

| Strategy | How it splits | Overlap | Best for |
|----------|---------------|---------|----------|
| `sentence` | Packs whole sentences up to `chunk_size` chars | ✅ yes | General RAG (default) |
| `paragraph` | One chunk per paragraph (blank-line separated) | ❌ n/a | Well-structured docs |

### 🔁 Chunk Overlap

Overlap repeats a little text between neighbouring chunks so meaning isn't lost at
the boundary. Example (`--overlap 60`):

```
Chunk 0: "... As a result, RAG systems hallucinate far less than a plain LLM."
Chunk 1: "As a result, RAG systems hallucinate far less than a plain LLM. The first step ..."
          └────────────────── shared overlap ──────────────────┘
```

The sentence strategy always keeps **at least one** trailing sentence, so overlap is
guaranteed even when a single sentence is longer than the overlap size.
A typical overlap is **10–20%** of the chunk size.

## 🏷️ Metadata Structure

Every chunk is stored as a record:

```json
{
  "chunk_id": "quarterly_report_p1_c0",
  "text": "Retrieval-Augmented Generation, or RAG, is a technique ...",
  "metadata": {
    "source_file": "quarterly_report.pdf",
    "page_number": 1,
    "chunk_index": 0,
    "strategy": "sentence",
    "char_count": 274,
    "word_count": 41
  }
}
```

- `chunk_id` — human-readable unique ID: `<file>_p<page>_c<index-on-page>`
- `page_number` — traces the chunk back to its source page (used for citations later)
- `chunk_index` — running position across the whole document

## 🖥️ Web UI — full pipeline in one app

Upload a PDF and the app does everything:

```
PDF  →  extract text (extractor.py)  →  chunk + overlap (chunker.py)  →  JSON
```

```bash
pip install -r requirements.txt      # flask + pdfplumber + pypdf
python make_sample_pdf.py            # optional: creates sample_data/sample.pdf
python app.py                        # open http://127.0.0.1:5000
```

- 📄 **Drop a PDF** (or paste raw text) — text is extracted **server-side**
- 🎛️ Choose strategy, chunk size &amp; overlap
- 🟩 Each chunk shows page number, IDs, counts; the **overlap** shared with the
  previous chunk is highlighted in the accent colour
- ↓ **Download** the chunks as JSON

Dark-studio interface, monospace labels, one electric accent. The app reuses the
**same** `extract_document()` and `chunk_document()` functions the modules expose —
extraction and chunking each live in one place.

## 🚀 How to Run

```bash
# default: sentence strategy, 400-char chunks, 80-char overlap
python chunker.py sample_data/extracted_pdf.json

# custom size / overlap
python chunker.py sample_data/extracted_pdf.json --strategy sentence --chunk-size 300 --overlap 60

# paragraph strategy
python chunker.py sample_data/extracted_pdf.json --strategy paragraph
```

Output is written to `output/<input-name>_chunks.json`.

## 📦 Output Shape

```json
{
  "source_document": "quarterly_report.pdf",
  "chunking_config": { "strategy": "sentence", "chunk_size": 300, "overlap": 60 },
  "total_chunks": 7,
  "chunks": [ /* chunk records (see above) */ ]
}
```

## 📁 Project Structure

```
day13_text_chunker/
├── chunker.py                    # chunking engine (sentence/paragraph, overlap, metadata)
├── extractor.py                  # PDF -> text (pdfplumber + pypdf)
├── app.py                        # Flask app: PDF -> extract -> chunk -> JSON
├── make_sample_pdf.py            # generates a 2-page test PDF
├── templates/
│   └── index.html                # dark-studio UI (PDF upload)
├── sample_data/
│   ├── sample.pdf                # test PDF
│   └── extracted_pdf.json        # sample Day-12 JSON (for the CLI)
├── output/                       # generated chunk files
├── requirements.txt
└── README.md
```

## 🔗 What's Next in RAG

Each chunk's `text` gets converted into an **embedding** (a vector), stored in a
**vector database**, and later **retrieved** by semantic similarity to answer questions.
That's the next phase of the internship. 🚀

## 📝 Note on LangChain

The learning resource is LangChain's `RecursiveCharacterTextSplitter`. This project
implements the same ideas (size limit, overlap, metadata) from scratch with the
**standard library only**, so every line is understandable and there are no
dependencies to install.
