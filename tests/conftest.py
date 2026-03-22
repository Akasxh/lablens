"""Shared fixtures for LabLens test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from sample_papers import SAMPLE_CATALYSIS_STUDY, SAMPLE_TEM_STUDY, SAMPLE_POLYMER_STUDY
from schemas import ExtractedEntity, ExtractionResult


# ---------------------------------------------------------------------------
# Text fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tem_text() -> str:
    return SAMPLE_TEM_STUDY


@pytest.fixture
def polymer_text() -> str:
    return SAMPLE_POLYMER_STUDY


@pytest.fixture
def catalysis_text() -> str:
    return SAMPLE_CATALYSIS_STUDY


@pytest.fixture
def non_scientific_text() -> str:
    return (
        "The weather today is sunny with a high of 75 degrees. "
        "John went to the grocery store and bought apples and bread. "
        "The stock market rose by 2% on Tuesday. "
        "She drove her car to the park and played with the dog."
    )


@pytest.fixture
def empty_text() -> str:
    return ""


# ---------------------------------------------------------------------------
# Entity fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_entity() -> ExtractedEntity:
    return ExtractedEntity(
        text="SEM",
        category="instrument",
        subcategory="regex",
        confidence=0.75,
        source_span=(10, 13),
        context="...performed using SEM at 15 kV...",
    )


@pytest.fixture
def sample_entity_spacy() -> ExtractedEntity:
    return ExtractedEntity(
        text="SEM",
        category="instrument",
        subcategory="spacy",
        confidence=0.70,
        source_span=(10, 13),
        context="...performed using SEM at 15 kV...",
    )


@pytest.fixture
def sample_entities() -> list[ExtractedEntity]:
    return [
        ExtractedEntity(text="TEM", category="instrument", subcategory="regex", confidence=0.8),
        ExtractedEntity(text="ethanol", category="chemical", subcategory="regex", confidence=0.7),
        ExtractedEntity(text="25 °C", category="condition", subcategory="regex", confidence=0.6),
        ExtractedEntity(text="TEM", category="instrument", subcategory="spacy", confidence=0.65),
        ExtractedEntity(text="532 nm", category="parameter", subcategory="regex", confidence=0.75),
    ]


@pytest.fixture
def sample_result(sample_entities: list[ExtractedEntity]) -> ExtractionResult:
    return ExtractionResult(
        document_name="test_doc.txt",
        entities=sample_entities,
        raw_text_length=5000,
        extraction_time_ms=42.5,
    )


@pytest.fixture
def tmp_text_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.txt"
    p.write_text("Scanning electron microscopy (SEM) was used at 25 °C with ethanol.")
    return p
