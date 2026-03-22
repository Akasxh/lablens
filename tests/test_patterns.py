"""Tests for regex pattern matching in src/patterns.py."""

from __future__ import annotations

import pytest

from patterns import (
    CHEMICAL_PATTERNS,
    CONDITION_PATTERNS,
    INSTRUMENT_PATTERN,
    MATERIAL_PATTERN,
    METHOD_PATTERN,
    PARAMETER_PATTERNS,
    compile_all_patterns,
)


class TestInstrumentPatterns:
    @pytest.mark.parametrize("term", ["SEM", "TEM", "XRD", "AFM", "STEM", "HRTEM"])
    def test_instrument_acronyms_match(self, term: str) -> None:
        assert INSTRUMENT_PATTERN.search(term), f"{term} should match instrument pattern"

    @pytest.mark.parametrize("phrase", [
        "scanning electron microscopy",
        "transmission electron microscope",
        "atomic force microscopy",
    ])
    def test_instrument_full_names_match(self, phrase: str) -> None:
        assert INSTRUMENT_PATTERN.search(phrase), f"'{phrase}' should match"

    def test_non_instrument_no_match(self) -> None:
        assert INSTRUMENT_PATTERN.search("banana") is None


class TestChemicalPatterns:
    @pytest.mark.parametrize("chem", ["ethanol", "methanol", "acetone", "DMSO", "chloroform"])
    def test_common_chemicals_match(self, chem: str) -> None:
        matches = any(p.search(chem) for p in CHEMICAL_PATTERNS)
        assert matches, f"'{chem}' should match a chemical pattern"

    @pytest.mark.parametrize("formula", ["H2O", "NaCl", "TiO2", "Fe3O4"])
    def test_molecular_formulas_match(self, formula: str) -> None:
        matches = any(p.search(formula) for p in CHEMICAL_PATTERNS)
        assert matches, f"'{formula}' should match a chemical pattern"


class TestConditionPatterns:
    @pytest.mark.parametrize("cond", ["25 °C", "300 K", "80 °C"])
    def test_temperature_match(self, cond: str) -> None:
        matches = any(p.search(cond) for p in CONDITION_PATTERNS)
        assert matches, f"'{cond}' should match a condition pattern"

    def test_ph_match(self) -> None:
        matches = any(p.search("pH 7.4") for p in CONDITION_PATTERNS)
        assert matches, "pH 7.4 should match"

    def test_pressure_match(self) -> None:
        matches = any(p.search("1 atm") for p in CONDITION_PATTERNS)
        assert matches, "1 atm should match"

    def test_room_temperature_match(self) -> None:
        matches = any(p.search("room temperature") for p in CONDITION_PATTERNS)
        assert matches, "room temperature should match"


class TestParameterPatterns:
    @pytest.mark.parametrize("param", ["532 nm", "1064 nm", "10 keV", "100 MHz"])
    def test_parameters_match(self, param: str) -> None:
        matches = any(p.search(param) for p in PARAMETER_PATTERNS)
        assert matches, f"'{param}' should match a parameter pattern"


class TestFalsePositives:
    def test_non_scientific_text_produces_few_matches(self, non_scientific_text: str) -> None:
        all_patterns = compile_all_patterns()
        total_matches = 0
        for patterns in all_patterns.values():
            for p in patterns:
                total_matches += len(p.findall(non_scientific_text))
        # Non-scientific text should produce very few matches (allow some due to numbers)
        assert total_matches < 10, f"Expected <10 matches on non-scientific text, got {total_matches}"


class TestCompileAllPatterns:
    def test_returns_all_categories(self) -> None:
        patterns = compile_all_patterns()
        expected = {"instrument", "chemical", "condition", "parameter", "material", "method", "organism", "sample"}
        assert set(patterns.keys()) == expected

    def test_each_category_has_patterns(self) -> None:
        patterns = compile_all_patterns()
        for cat, pat_list in patterns.items():
            assert len(pat_list) > 0, f"Category '{cat}' has no patterns"
