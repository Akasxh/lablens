"""Confidence scoring for extracted entities.

Scores are based on multiple signals:
- Pattern specificity (longer/more specific patterns score higher)
- Context quality (entity near section headers, figure captions, etc.)
- Frequency (entities mentioned multiple times score higher)
- Source (spaCy NER vs regex vs both)
"""

from __future__ import annotations

import math
from collections import Counter

try:
    from .schemas import ExtractedEntity
except ImportError:
    from schemas import ExtractedEntity


# Weights for different scoring components
_W_SPECIFICITY = 0.30
_W_CONTEXT = 0.25
_W_FREQUENCY = 0.25
_W_SOURCE = 0.20

# Context keywords that boost confidence
_STRONG_CONTEXT = {
    "instrument": ["using", "measured", "equipped", "operated", "performed"],
    "chemical": ["dissolved", "solution", "reagent", "prepared", "added", "mixed"],
    "condition": ["maintained", "set", "held", "adjusted", "controlled"],
    "parameter": ["measured", "recorded", "obtained", "set", "applied"],
    "material": ["composed", "made", "fabricated", "synthesized", "consisting"],
    "method": ["performed", "carried", "conducted", "employed", "applied"],
    "organism": ["cultured", "grown", "incubated", "inoculated", "harvested"],
    "sample": ["prepared", "collected", "processed", "analyzed", "characterized"],
}


def _specificity_score(entity: ExtractedEntity) -> float:
    """Score based on entity text length/specificity. Longer = more specific."""
    length = len(entity.text)
    if length <= 2:
        return 0.3
    if length <= 5:
        return 0.5
    if length <= 15:
        return 0.7
    return min(0.95, 0.7 + 0.01 * (length - 15))


def _context_score(entity: ExtractedEntity) -> float:
    """Score based on surrounding context quality."""
    if not entity.context:
        return 0.3
    ctx_lower = entity.context.lower()
    keywords = _STRONG_CONTEXT.get(entity.category, [])
    matches = sum(1 for kw in keywords if kw in ctx_lower)
    if matches >= 2:
        return 0.95
    if matches == 1:
        return 0.75
    # Check for section header patterns
    if any(h in ctx_lower for h in ["methods", "materials", "experimental", "procedure"]):
        return 0.7
    return 0.4


def _frequency_score(entity_text: str, all_texts: list[str]) -> float:
    """Score based on how frequently the entity appears in the document."""
    count = sum(1 for t in all_texts if t.lower() == entity_text.lower())
    if count >= 5:
        return 0.95
    if count >= 3:
        return 0.8
    if count >= 2:
        return 0.65
    return 0.4


def _source_score(entity: ExtractedEntity) -> float:
    """Score based on extraction source.

    Entities found by both spaCy and regex get highest scores.
    The subcategory field encodes the source: 'spacy', 'regex', 'spacy+regex'.
    """
    src = entity.subcategory.lower()
    if "spacy" in src and "regex" in src:
        return 0.95
    if "spacy" in src:
        return 0.7
    if "regex" in src:
        return 0.65
    return 0.5


def score_entity(
    entity: ExtractedEntity,
    all_entity_texts: list[str],
) -> float:
    """Compute composite confidence score for a single entity."""
    s1 = _specificity_score(entity)
    s2 = _context_score(entity)
    s3 = _frequency_score(entity.text, all_entity_texts)
    s4 = _source_score(entity)

    raw = (
        _W_SPECIFICITY * s1
        + _W_CONTEXT * s2
        + _W_FREQUENCY * s3
        + _W_SOURCE * s4
    )
    # Apply sigmoid-like squashing to keep in [0.1, 0.99]
    return round(0.1 + 0.89 / (1 + math.exp(-6 * (raw - 0.5))), 3)


def score_entities(entities: list[ExtractedEntity]) -> list[ExtractedEntity]:
    """Score all entities, mutating their confidence fields in place."""
    all_texts = [e.text for e in entities]
    for entity in entities:
        entity.confidence = score_entity(entity, all_texts)
    return entities


def deduplicate_entities(entities: list[ExtractedEntity]) -> list[ExtractedEntity]:
    """Remove near-duplicate entities, keeping the highest-confidence instance.

    Two entities are considered duplicates if they have the same normalized text
    and the same category.
    """
    seen: dict[tuple[str, str], ExtractedEntity] = {}
    for entity in entities:
        key = (entity.text.lower().strip(), entity.category)
        existing = seen.get(key)
        if existing is None or entity.confidence > existing.confidence:
            # Merge source info
            if existing and existing.subcategory != entity.subcategory:
                sources = set(existing.subcategory.split("+")) | set(entity.subcategory.split("+"))
                entity.subcategory = "+".join(sorted(sources))
            seen[key] = entity
    return list(seen.values())


def rank_entities(entities: list[ExtractedEntity]) -> list[ExtractedEntity]:
    """Return entities sorted by confidence (descending)."""
    return sorted(entities, key=lambda e: e.confidence, reverse=True)
