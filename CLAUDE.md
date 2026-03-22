# LabLens — Scientific Metadata Extractor

NLP-powered tool that extracts structured experimental metadata from scientific publications. Combines spaCy NER with 300+ domain-specific regex patterns to identify entities across 8 categories: instruments, chemicals, conditions, parameters, materials, methods, organisms, and samples. Dual interface (CLI + Streamlit), exports to JSON/CSV/BioSchemas JSON-LD.

## How to Run

```bash
uv sync && uv run python -m spacy download en_core_web_sm && uv run streamlit run src/app.py
```

Opens at http://localhost:8501 with 3 built-in demo papers.

## Key Files

| File | Purpose |
|------|---------|
| `src/app.py` | Streamlit web interface for interactive extraction and entity review |
| `src/cli.py` | CLI interface for batch processing and automation |
| `src/extractor.py` | Main pipeline: parse -> extract -> score -> export |
| `src/ner.py` | spaCy NER + regex pattern matching engine |
| `src/patterns.py` | 300+ regex patterns for scientific entities across 8 categories |
| `src/parsers.py` | PDF (pdfplumber) and text file parsing |
| `src/schemas.py` | Typed dataclasses for extraction results |
| `src/scoring.py` | Multi-signal confidence scoring (specificity, context, frequency, source) + deduplication |
| `src/sample_papers.py` | 3 built-in synthetic demo papers |

## Testing

```bash
uv run python -c "from src.sample_papers import *; print('Imports OK')"
```

## Architecture

Data flow: Document input (PDF/TXT/MD/TEX or pasted text) -> parsing (parsers) -> NER + regex extraction (ner, patterns) -> confidence scoring & deduplication (scoring) -> structured results (schemas) -> export (extractor: JSON/CSV/BioSchemas).

Confidence scoring is a weighted composite: specificity (0.30), context (0.25), frequency (0.25), source agreement (0.20).
