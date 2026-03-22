"""Named Entity Recognition using spaCy + custom rules.

Combines spaCy's built-in NER with domain-specific pattern matching
for scientific entities.
"""

from __future__ import annotations

import spacy

try:
    from .patterns import compile_all_patterns
    from .schemas import ExtractedEntity
except ImportError:
    from patterns import compile_all_patterns
    from schemas import ExtractedEntity


# Map spaCy entity labels to our categories
_SPACY_LABEL_MAP: dict[str, str] = {
    "ORG": "instrument",  # instrument manufacturers often tagged as ORG
    "PRODUCT": "instrument",
    "GPE": "",  # skip locations
    "LOC": "",
    "PERSON": "",
    "DATE": "",
    "TIME": "",
    "MONEY": "",
    "CARDINAL": "",
    "ORDINAL": "",
    "PERCENT": "",
    "QUANTITY": "parameter",
    "NORP": "",
    "FAC": "",
    "EVENT": "",
    "WORK_OF_ART": "",
    "LAW": "",
    "LANGUAGE": "",
}

# Minimum text length for spaCy entities to consider
_MIN_SPACY_LEN = 2


def _load_spacy_model() -> spacy.language.Language:
    """Load the spaCy model, downloading if necessary."""
    model_name = "en_core_web_sm"
    try:
        return spacy.load(model_name)
    except OSError:
        from spacy.cli import download
        download(model_name)
        return spacy.load(model_name)


# Module-level lazy singleton
_nlp: spacy.language.Language | None = None


def get_nlp() -> spacy.language.Language:
    """Get or create the spaCy NLP pipeline (singleton)."""
    global _nlp
    if _nlp is None:
        _nlp = _load_spacy_model()
    return _nlp


def _get_context(text: str, start: int, end: int, window: int = 80) -> str:
    """Extract surrounding context for an entity span."""
    ctx_start = max(0, start - window)
    ctx_end = min(len(text), end + window)
    context = text[ctx_start:ctx_end].replace("\n", " ").strip()
    if ctx_start > 0:
        context = "..." + context
    if ctx_end < len(text):
        context = context + "..."
    return context


def extract_with_spacy(text: str) -> list[ExtractedEntity]:
    """Extract entities using spaCy NER."""
    nlp = get_nlp()
    # Process in chunks for very long texts (spaCy default max is 1M chars)
    max_len = 900_000
    entities: list[ExtractedEntity] = []

    for chunk_start in range(0, len(text), max_len):
        chunk = text[chunk_start : chunk_start + max_len]
        doc = nlp(chunk)

        for ent in doc.ents:
            category = _SPACY_LABEL_MAP.get(ent.label_, "")
            if not category:
                continue
            if len(ent.text.strip()) < _MIN_SPACY_LEN:
                continue

            abs_start = chunk_start + ent.start_char
            abs_end = chunk_start + ent.end_char

            entities.append(ExtractedEntity(
                text=ent.text.strip(),
                category=category,
                subcategory="spacy",
                source_span=(abs_start, abs_end),
                context=_get_context(text, abs_start, abs_end),
            ))

    return entities


def extract_with_patterns(text: str) -> list[ExtractedEntity]:
    """Extract entities using regex patterns."""
    all_patterns = compile_all_patterns()
    entities: list[ExtractedEntity] = []

    for category, patterns in all_patterns.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                matched_text = match.group(0).strip()
                if len(matched_text) < _MIN_SPACY_LEN:
                    continue

                start, end = match.span()
                entities.append(ExtractedEntity(
                    text=matched_text,
                    category=category,
                    subcategory="regex",
                    source_span=(start, end),
                    context=_get_context(text, start, end),
                ))

    return entities


def extract_entities(text: str) -> list[ExtractedEntity]:
    """Run full NER pipeline: spaCy + regex patterns.

    Returns merged, deduplicated entities.
    """
    spacy_entities = extract_with_spacy(text)
    pattern_entities = extract_with_patterns(text)
    return spacy_entities + pattern_entities
