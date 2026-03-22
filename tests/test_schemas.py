"""Tests for data schemas in src/schemas.py."""

from __future__ import annotations

from schemas import ExtractedEntity, ExtractionResult


class TestExtractionResultToDict:
    def test_to_dict_format(self, sample_result: ExtractionResult) -> None:
        d = sample_result.to_dict()
        assert d["document_name"] == "test_doc.txt"
        assert d["raw_text_length"] == 5000
        assert d["extraction_time_ms"] == 42.5
        assert "entity_count" in d
        assert d["entity_count"] == len(sample_result.entities)
        assert "entities" in d
        assert isinstance(d["entities"], list)
        assert "summary" in d
        summary = d["summary"]
        assert "instruments" in summary
        assert "chemicals" in summary
        assert "conditions" in summary

    def test_entity_to_dict_has_list_span(self, sample_entity) -> None:
        d = sample_entity.to_dict()
        assert isinstance(d["source_span"], list)
        assert d["text"] == "SEM"
        assert d["category"] == "instrument"


class TestExtractionResultToBioschemas:
    def test_bioschemas_format(self, sample_result: ExtractionResult) -> None:
        bio = sample_result.to_bioschemas()
        assert bio["@context"] == "https://schema.org"
        assert bio["@type"] == "Dataset"
        assert bio["name"] == "test_doc.txt"
        assert "keywords" in bio
        assert isinstance(bio["keywords"], list)
        assert len(bio["keywords"]) == len(sample_result.entities)

    def test_bioschemas_defined_terms(self, sample_result: ExtractionResult) -> None:
        bio = sample_result.to_bioschemas()
        for term in bio["keywords"]:
            assert term["@type"] == "DefinedTerm"
            assert "name" in term
            assert "inDefinedTermSet" in term


class TestExtractionResultProperties:
    def test_category_properties(self, sample_result: ExtractionResult) -> None:
        assert len(sample_result.instruments) == 2  # two TEM entries
        assert len(sample_result.chemicals) == 1    # ethanol
        assert len(sample_result.conditions) == 1   # 25 °C
        assert len(sample_result.parameters) == 1   # 532 nm
