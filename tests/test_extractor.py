"""Tests for the main extraction pipeline in src/extractor.py."""

from __future__ import annotations

import pandas as pd

from extractor import extract_from_text, results_to_dataframe
from schemas import ExtractionResult


class TestExtractFromText:
    def test_returns_extraction_result(self, tem_text: str) -> None:
        result = extract_from_text(tem_text, source_name="test_tem")
        assert isinstance(result, ExtractionResult)
        assert result.document_name == "test_tem"
        assert result.raw_text_length == len(tem_text)
        assert result.extraction_time_ms > 0

    def test_finds_entities_in_tem_study(self, tem_text: str) -> None:
        result = extract_from_text(tem_text, source_name="tem")
        assert len(result.entities) > 10, "TEM study should yield many entities"
        categories = {e.category for e in result.entities}
        assert "instrument" in categories
        assert "chemical" in categories
        assert "condition" in categories

    def test_entities_are_ranked_by_confidence(self, tem_text: str) -> None:
        result = extract_from_text(tem_text)
        for i in range(len(result.entities) - 1):
            assert result.entities[i].confidence >= result.entities[i + 1].confidence

    def test_polymer_study_finds_materials(self, polymer_text: str) -> None:
        result = extract_from_text(polymer_text, source_name="polymer")
        categories = {e.category for e in result.entities}
        assert "material" in categories or "chemical" in categories
        assert "method" in categories


class TestResultsToDataframe:
    def test_returns_dataframe(self, tem_text: str) -> None:
        result = extract_from_text(tem_text)
        df = results_to_dataframe([result])
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        expected_cols = {"document", "text", "category", "subcategory", "confidence"}
        assert expected_cols.issubset(set(df.columns))

    def test_empty_results(self) -> None:
        df = results_to_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
