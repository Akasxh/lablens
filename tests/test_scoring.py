"""Tests for confidence scoring in src/scoring.py."""

from __future__ import annotations

from schemas import ExtractedEntity
from scoring import (
    deduplicate_entities,
    rank_entities,
    score_entities,
    score_entity,
)


class TestScoreEntity:
    def test_returns_float_in_range(self, sample_entity: ExtractedEntity) -> None:
        score = score_entity(sample_entity, ["SEM", "TEM", "ethanol"])
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_longer_text_scores_higher(self) -> None:
        short = ExtractedEntity(text="AB", category="instrument", subcategory="regex")
        long = ExtractedEntity(text="scanning electron microscopy", category="instrument", subcategory="regex")
        s_short = score_entity(short, ["AB"])
        s_long = score_entity(long, ["scanning electron microscopy"])
        assert s_long > s_short, "Longer/more specific entity should score higher"

    def test_dual_source_scores_higher(self) -> None:
        regex_only = ExtractedEntity(text="SEM", category="instrument", subcategory="regex")
        both = ExtractedEntity(text="SEM", category="instrument", subcategory="spacy+regex")
        texts = ["SEM"]
        s_regex = score_entity(regex_only, texts)
        s_both = score_entity(both, texts)
        assert s_both > s_regex, "Entity from both sources should score higher"


class TestScoreEntities:
    def test_mutates_confidence(self, sample_entities: list[ExtractedEntity]) -> None:
        # All start at their fixture values; score_entities should update them
        scored = score_entities(sample_entities)
        for e in scored:
            assert 0.0 < e.confidence <= 1.0


class TestDeduplicateEntities:
    def test_removes_exact_duplicates(self, sample_entities: list[ExtractedEntity]) -> None:
        # sample_entities has two TEM entries (regex + spacy)
        deduped = deduplicate_entities(sample_entities)
        tem_entries = [e for e in deduped if e.text == "TEM"]
        assert len(tem_entries) == 1, "Duplicate TEM should be merged"

    def test_merges_sources(self) -> None:
        # Put the lower-confidence entity first so the higher one triggers merge
        entities = [
            ExtractedEntity(text="TEM", category="instrument", subcategory="spacy", confidence=0.65),
            ExtractedEntity(text="TEM", category="instrument", subcategory="regex", confidence=0.80),
        ]
        deduped = deduplicate_entities(entities)
        assert len(deduped) == 1
        tem = deduped[0]
        assert "regex" in tem.subcategory
        assert "spacy" in tem.subcategory

    def test_keeps_distinct_entities(self, sample_entities: list[ExtractedEntity]) -> None:
        deduped = deduplicate_entities(sample_entities)
        texts = {e.text for e in deduped}
        assert "ethanol" in texts
        assert "25 °C" in texts
        assert "532 nm" in texts


class TestRankEntities:
    def test_sorted_descending(self, sample_entities: list[ExtractedEntity]) -> None:
        scored = score_entities(sample_entities)
        ranked = rank_entities(scored)
        for i in range(len(ranked) - 1):
            assert ranked[i].confidence >= ranked[i + 1].confidence

    def test_empty_list(self) -> None:
        assert rank_entities([]) == []
