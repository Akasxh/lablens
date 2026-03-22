"""LabLens - Scientific Metadata Extraction Pipeline."""

from .extractor import (
    export_results,
    extract_batch,
    extract_from_file,
    extract_from_text,
    results_to_dataframe,
)
from .ner import extract_entities, extract_with_patterns, extract_with_spacy
from .parsers import parse_document, parse_pdf_file, parse_text_file
from .patterns import compile_all_patterns
from .sample_papers import ALL_SAMPLES, SAMPLES_BY_NAME, SAMPLE_NAMES
from .schemas import ExtractedEntity, ExtractionResult
from .scoring import deduplicate_entities, rank_entities, score_entities

__all__ = [
    "ALL_SAMPLES",
    "SAMPLES_BY_NAME",
    "SAMPLE_NAMES",
    "ExtractedEntity",
    "ExtractionResult",
    "compile_all_patterns",
    "deduplicate_entities",
    "export_results",
    "extract_batch",
    "extract_entities",
    "extract_from_file",
    "extract_from_text",
    "extract_with_patterns",
    "extract_with_spacy",
    "parse_document",
    "parse_pdf_file",
    "parse_text_file",
    "rank_entities",
    "results_to_dataframe",
    "score_entities",
]
