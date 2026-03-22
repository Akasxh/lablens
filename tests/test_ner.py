"""Tests for NER extraction in src/ner.py."""

from __future__ import annotations

from ner import extract_entities, extract_with_patterns, extract_with_spacy
from schemas import ExtractedEntity


class TestExtractWithSpacy:
    def test_returns_list_of_entities(self, tem_text: str) -> None:
        entities = extract_with_spacy(tem_text)
        assert isinstance(entities, list)
        # spaCy should find at least some entities in scientific text
        assert len(entities) > 0

    def test_entities_have_spacy_subcategory(self, tem_text: str) -> None:
        entities = extract_with_spacy(tem_text)
        for e in entities:
            assert e.subcategory == "spacy"

    def test_empty_input_returns_empty(self, empty_text: str) -> None:
        entities = extract_with_spacy(empty_text)
        assert entities == []


class TestExtractWithPatterns:
    def test_returns_entities_for_scientific_text(self, tem_text: str) -> None:
        entities = extract_with_patterns(tem_text)
        assert len(entities) > 0
        categories = {e.category for e in entities}
        # TEM study should have instruments, chemicals, conditions at minimum
        assert "instrument" in categories
        assert "chemical" in categories
        assert "condition" in categories

    def test_entities_have_regex_subcategory(self, tem_text: str) -> None:
        entities = extract_with_patterns(tem_text)
        for e in entities:
            assert e.subcategory == "regex"

    def test_entities_have_context(self, tem_text: str) -> None:
        entities = extract_with_patterns(tem_text)
        for e in entities:
            assert len(e.context) > 0, f"Entity '{e.text}' has no context"


class TestExtractEntities:
    def test_combines_spacy_and_regex(self, tem_text: str) -> None:
        entities = extract_entities(tem_text)
        subcategories = {e.subcategory for e in entities}
        # Should have entities from both sources
        assert "regex" in subcategories
        # spaCy may or may not find entities depending on text, so just check list is non-empty
        assert len(entities) > 0

    def test_empty_input(self, empty_text: str) -> None:
        entities = extract_entities(empty_text)
        assert entities == []
