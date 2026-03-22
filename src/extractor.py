"""Main extraction pipeline orchestrating parsing, NER, scoring, and output."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

try:
    from .ner import extract_entities
    from .parsers import parse_document, parse_text_content
    from .schemas import ExtractionResult, ExtractedEntity
    from .scoring import deduplicate_entities, rank_entities, score_entities
except ImportError:
    from ner import extract_entities
    from parsers import parse_document, parse_text_content
    from schemas import ExtractionResult, ExtractedEntity
    from scoring import deduplicate_entities, rank_entities, score_entities


def extract_from_text(
    text: str,
    source_name: str = "pasted_text",
) -> ExtractionResult:
    """Run the full extraction pipeline on raw text."""
    t0 = time.perf_counter()

    # Extract entities
    raw_entities = extract_entities(text)

    # Score, deduplicate, rank
    scored = score_entities(raw_entities)
    deduped = deduplicate_entities(scored)
    # Re-score after deduplication (merged sources may change scores)
    scored_final = score_entities(deduped)
    ranked = rank_entities(scored_final)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    return ExtractionResult(
        document_name=source_name,
        entities=ranked,
        raw_text_length=len(text),
        extraction_time_ms=round(elapsed_ms, 1),
    )


def extract_from_file(path: Path) -> ExtractionResult:
    """Run the full extraction pipeline on a file."""
    text = parse_document(path)
    return extract_from_text(text, source_name=path.name)


def extract_batch(paths: list[Path]) -> list[ExtractionResult]:
    """Process multiple documents and return all results."""
    results: list[ExtractionResult] = []
    for path in paths:
        try:
            result = extract_from_file(path)
            results.append(result)
        except Exception as exc:
            # Create a minimal result with error info
            results.append(ExtractionResult(
                document_name=path.name,
                entities=[
                    ExtractedEntity(
                        text=f"ERROR: {exc}",
                        category="error",
                        subcategory="parse_error",
                        confidence=0.0,
                    )
                ],
            ))
    return results


def results_to_dataframe(results: list[ExtractionResult]) -> pd.DataFrame:
    """Convert a list of ExtractionResults to a single DataFrame."""
    all_rows: list[dict] = []
    for result in results:
        all_rows.extend(result.to_csv_rows())
    if not all_rows:
        return pd.DataFrame(columns=[
            "document", "text", "category", "subcategory",
            "confidence", "context", "verified", "span_start", "span_end",
        ])
    return pd.DataFrame(all_rows)


def export_results(
    results: list[ExtractionResult],
    output_path: Path,
    fmt: str = "json",
) -> Path:
    """Export extraction results to a file.

    Supported formats: json, csv, bioschemas
    """
    fmt = fmt.lower().strip()

    if fmt == "json":
        import json
        data = [r.to_dict() for r in results]
        output_path = output_path.with_suffix(".json")
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    elif fmt == "csv":
        df = results_to_dataframe(results)
        output_path = output_path.with_suffix(".csv")
        df.to_csv(output_path, index=False)

    elif fmt == "bioschemas":
        import json
        data = [r.to_bioschemas() for r in results]
        output_path = output_path.with_suffix(".jsonld")
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        raise ValueError(f"Unsupported format: {fmt}. Use 'json', 'csv', or 'bioschemas'.")

    return output_path
