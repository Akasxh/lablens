"""CLI interface for LabLens metadata extraction pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .extractor import export_results, extract_batch, extract_from_file, extract_from_text
    from .schemas import ExtractionResult
except ImportError:
    from extractor import export_results, extract_batch, extract_from_file, extract_from_text
    from schemas import ExtractionResult


def _print_summary(result: ExtractionResult) -> None:
    """Print a formatted summary of extraction results to stdout."""
    print(f"\n{'='*70}")
    print(f"Document: {result.document_name}")
    print(f"Text length: {result.raw_text_length:,} chars")
    print(f"Extraction time: {result.extraction_time_ms:.0f} ms")
    print(f"Total entities: {len(result.entities)}")
    print(f"{'='*70}")

    categories = {
        "Samples": result.samples,
        "Instruments": result.instruments,
        "Conditions": result.conditions,
        "Parameters": result.parameters,
        "Materials": result.materials,
        "Methods": result.methods,
        "Chemicals": result.chemicals,
        "Organisms": result.organisms,
    }

    for cat_name, entities in categories.items():
        if not entities:
            continue
        print(f"\n  {cat_name} ({len(entities)}):")
        for e in entities[:10]:  # Show top 10 per category
            conf_bar = "█" * int(e.confidence * 10) + "░" * (10 - int(e.confidence * 10))
            print(f"    [{conf_bar}] {e.confidence:.2f}  {e.text}")
        if len(entities) > 10:
            print(f"    ... and {len(entities) - 10} more")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="lablens",
        description="LabLens - Scientific Metadata Extraction Pipeline",
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        nargs="+",
        help="Input file(s) to process (PDF, TXT, MD, TEX)",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Direct text input (alternative to --input)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file path (default: stdout JSON)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv", "bioschemas"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress summary output, only emit structured data",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run on built-in demo samples",
    )

    args = parser.parse_args()

    results: list[ExtractionResult] = []

    if args.demo:
        try:
            from .sample_papers import SAMPLES_BY_NAME
        except ImportError:
            from sample_papers import SAMPLES_BY_NAME
        for name, text in SAMPLES_BY_NAME.items():
            result = extract_from_text(text, source_name=name)
            results.append(result)
    elif args.text:
        result = extract_from_text(args.text, source_name="stdin")
        results.append(result)
    elif args.input:
        for p in args.input:
            if not p.exists():
                print(f"Error: File not found: {p}", file=sys.stderr)
                sys.exit(1)
        results = extract_batch(args.input)
    else:
        # Read from stdin if no arguments
        text = sys.stdin.read()
        if text.strip():
            result = extract_from_text(text, source_name="stdin")
            results.append(result)
        else:
            parser.print_help()
            sys.exit(1)

    if not args.quiet:
        for result in results:
            _print_summary(result)
        print()

    if args.output:
        out_path = export_results(results, args.output, fmt=args.format)
        if not args.quiet:
            print(f"Results exported to: {out_path}")
    elif args.quiet:
        # Quiet mode with no output file: dump JSON to stdout
        data = [r.to_dict() for r in results]
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
