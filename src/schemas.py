"""Output schemas for structured metadata extraction results."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExtractedEntity:
    """A single extracted entity with metadata."""

    text: str
    category: str
    subcategory: str = ""
    confidence: float = 0.0
    source_span: tuple[int, int] = (0, 0)
    context: str = ""
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["source_span"] = list(d["source_span"])
        return d


@dataclass
class ExtractionResult:
    """Complete extraction result for a single document."""

    document_name: str
    entities: list[ExtractedEntity] = field(default_factory=list)
    raw_text_length: int = 0
    extraction_time_ms: float = 0.0

    @property
    def samples(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "sample"]

    @property
    def instruments(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "instrument"]

    @property
    def conditions(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "condition"]

    @property
    def parameters(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "parameter"]

    @property
    def materials(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "material"]

    @property
    def methods(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "method"]

    @property
    def chemicals(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "chemical"]

    @property
    def organisms(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.category == "organism"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_name": self.document_name,
            "raw_text_length": self.raw_text_length,
            "extraction_time_ms": self.extraction_time_ms,
            "entity_count": len(self.entities),
            "entities": [e.to_dict() for e in self.entities],
            "summary": {
                "samples": len(self.samples),
                "instruments": len(self.instruments),
                "conditions": len(self.conditions),
                "parameters": len(self.parameters),
                "materials": len(self.materials),
                "methods": len(self.methods),
                "chemicals": len(self.chemicals),
                "organisms": len(self.organisms),
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_bioschemas(self) -> dict[str, Any]:
        """Export in BioSchemas-compatible JSON-LD format."""
        defined_terms = []
        for entity in self.entities:
            term: dict[str, Any] = {
                "@type": "DefinedTerm",
                "name": entity.text,
                "inDefinedTermSet": entity.category,
            }
            if entity.subcategory:
                term["termCode"] = entity.subcategory
            defined_terms.append(term)

        return {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": self.document_name,
            "description": f"Extracted metadata from {self.document_name}",
            "keywords": defined_terms,
            "variableMeasured": [
                {
                    "@type": "PropertyValue",
                    "name": e.text,
                    "description": e.context,
                }
                for e in self.parameters
            ],
            "measurementTechnique": [e.text for e in self.methods],
        }

    def to_csv_rows(self) -> list[dict[str, Any]]:
        """Convert to flat rows suitable for CSV/DataFrame export."""
        rows = []
        for entity in self.entities:
            rows.append({
                "document": self.document_name,
                "text": entity.text,
                "category": entity.category,
                "subcategory": entity.subcategory,
                "confidence": round(entity.confidence, 3),
                "context": entity.context,
                "verified": entity.verified,
                "span_start": entity.source_span[0],
                "span_end": entity.source_span[1],
            })
        return rows
