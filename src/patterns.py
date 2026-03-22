"""Regex patterns for scientific entity extraction.

Organized by category: instruments, chemicals, conditions, parameters,
materials, methods, organisms, and sample types.
"""

from __future__ import annotations

import regex

# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------
INSTRUMENT_NAMES: list[str] = [
    # Microscopy
    r"(?:scanning|transmission)\s+electron\s+microscop(?:e|y)",
    r"SEM", r"TEM", r"STEM", r"AFM", r"STM",
    r"atomic\s+force\s+microscop(?:e|y)",
    r"scanning\s+tunneling\s+microscop(?:e|y)",
    r"(?:confocal|fluorescence|optical|light)\s+microscop(?:e|y)",
    r"cryo[\-\s]?(?:EM|TEM)",
    r"HRTEM",
    r"HAADF[\-\s]?STEM",
    # Spectroscopy
    r"(?:X[\-\s]?ray|XRD|XANES|EXAFS|XPS|XRF)",
    r"(?:UV[\-\s]?Vis|UV[\-\s]?visible)\s+spectro(?:meter|scopy|photometer)?",
    r"(?:FTIR|IR|infrared)\s*(?:spectro(?:meter|scopy))?",
    r"Raman\s*(?:spectro(?:meter|scopy))?",
    r"NMR\s*(?:spectro(?:meter|scopy))?",
    r"nuclear\s+magnetic\s+resonance",
    r"mass\s+spectromet(?:er|ry)",
    r"(?:ICP[\-\s]?(?:MS|OES|AES))",
    r"(?:GC[\-\s]?MS|LC[\-\s]?MS|MALDI[\-\s]?TOF)",
    r"(?:EDS|EDX|EELS|WDS)",
    r"(?:AES|Auger)\s*(?:spectro(?:meter|scopy))?",
    # Diffraction / scattering
    r"(?:SAXS|WAXS|DLS|GISAXS)",
    r"(?:neutron|electron|powder)\s+diffraction",
    # Thermal analysis
    r"(?:DSC|TGA|DTA|TMA)",
    r"differential\s+scanning\s+calorimetr(?:y|er)",
    r"thermogravimetric\s+analysis",
    # Chromatography
    r"(?:HPLC|GC|SEC|FPLC)",
    r"gel\s+(?:permeation|filtration)\s+chromatography",
    r"size[\-\s]?exclusion\s+chromatography",
    # Other
    r"(?:BET|BJH)\s*(?:analysis|surface\s+area)?",
    r"(?:rheometer|viscometer|tensiometer|ellipsometer)",
    r"(?:potentiostat|galvanostat)",
    r"(?:SQUID|VSM)\s*(?:magneto(?:meter|metry))?",
    r"profilometer",
    r"contact\s+angle\s+(?:goniometer|measurement)",
    r"zeta\s+potential\s+(?:analyzer|measurement)",
]

INSTRUMENT_PATTERN = regex.compile(
    r"\b(?:" + "|".join(INSTRUMENT_NAMES) + r")\b",
    regex.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Chemical compounds
# ---------------------------------------------------------------------------
CHEMICAL_PATTERNS: list[regex.Pattern[str]] = [
    # Molecular formulas: H2O, NaCl, C60, TiO2, Fe3O4, CH3CH2OH
    regex.compile(
        r"\b(?:[A-Z][a-z]?\d*){2,}\b"
        r"(?<![A-Z]{3})"  # avoid matching acronyms like SEM
    ),
    # IUPAC-ish names: prefix MUST be followed by a hyphen or a chemical-looking suffix
    regex.compile(
        r"\b(?:(?:mono|di|tri|tetra|penta|hexa|poly|iso|neo|cyclo|methyl|ethyl|propyl|butyl|"
        r"phenyl|amino|chloro|fluoro|bromo|nitro|hydroxy|carboxy|sulfo)"
        r"[\-]"  # require hyphen between prefix and rest
        r"[a-z]{3,})\b",
        regex.IGNORECASE,
    ),
    # Multi-prefix IUPAC without hyphen (e.g., dichloromethane, polyethylene)
    regex.compile(
        r"\b(?:(?:mono|di|tri|tetra|penta|hexa|poly|iso|neo|cyclo)"
        r"(?:methyl|ethyl|propyl|butyl|phenyl|amino|chloro|fluoro|bromo|nitro|hydroxy|"
        r"vinyl|styrene|acryl|ester|ether|amine|amide|imide|carbonate|urethane|ethylene|"
        r"propylene|lactide|glycol|saccharide|peptide|nucleotide|"
        r"mer(?:ize|ization|ase|ic)?)[a-z]*)\b",
        regex.IGNORECASE,
    ),
    # Common chemicals by name
    regex.compile(
        r"\b(?:acetone|methanol|ethanol|isopropanol|toluene|benzene|chloroform|"
        r"dichloromethane|hexane|acetonitrile|dimethyl\s*sulfoxide|DMSO|DMF|THF|"
        r"dimethylformamide|tetrahydrofuran|"
        r"hydrochloric\s+acid|sulfuric\s+acid|nitric\s+acid|phosphoric\s+acid|"
        r"acetic\s+acid|citric\s+acid|formic\s+acid|"
        r"sodium\s+hydroxide|potassium\s+hydroxide|ammonium\s+hydroxide|"
        r"sodium\s+chloride|calcium\s+carbonate|silicon\s+dioxide|"
        r"glutaraldehyde|formaldehyde|paraformaldehyde|"
        r"phosphate[\-\s]?buffered\s+saline|PBS|"
        r"(?:Tris|HEPES|EDTA|SDS|CTAB|PEG|PVA|PLGA|PCL|PLA|PDMS))\b",
        regex.IGNORECASE,
    ),
]

# ---------------------------------------------------------------------------
# Experimental conditions (temperature, pressure, pH, etc.)
# ---------------------------------------------------------------------------
CONDITION_PATTERNS: list[regex.Pattern[str]] = [
    # Temperature: 25 °C, 300 K, room temperature, 100°C
    regex.compile(
        r"\b\d+(?:\.\d+)?\s*(?:\u00b0\s*[CFK]|[°]\s*[CFK]|deg(?:rees?)?\s*[CFK]"
        r"|K(?:elvin)?|[CF](?:elsius|ahrenheit)?)\b",
        regex.IGNORECASE,
    ),
    regex.compile(r"\b(?:room\s+temperature|ambient\s+temperature|RT)\b", regex.IGNORECASE),
    # Pressure: 1 atm, 760 mmHg, 101.3 kPa, 1 bar, 10 mbar
    regex.compile(
        r"\b\d+(?:\.\d+)?\s*(?:atm|Pa|kPa|MPa|GPa|bar|mbar|torr|mmHg|psi)\b",
        regex.IGNORECASE,
    ),
    regex.compile(r"\b(?:atmospheric\s+pressure|vacuum|UHV|ultra[\-\s]?high\s+vacuum)\b", regex.IGNORECASE),
    # pH
    regex.compile(r"\bpH\s*(?:=|of|~)?\s*\d+(?:\.\d+)?\b"),
    # Time durations: 30 min, 2 h, 24 hours, overnight
    regex.compile(
        r"\b\d+(?:\.\d+)?\s*(?:s(?:ec(?:onds?)?)?|min(?:utes?)?|h(?:(?:ou)?rs?)?|"
        r"days?|weeks?|months?)\b",
        regex.IGNORECASE,
    ),
    regex.compile(r"\b(?:overnight|(?:for|over)\s+\d+\s+(?:hours?|days?))\b", regex.IGNORECASE),
    # Concentration: 0.1 M, 10 mM, 5 mg/mL, 1 wt%, 10 vol%
    regex.compile(
        r"\b\d+(?:\.\d+)?\s*(?:[munpf]?[Mm](?:ol(?:/[Ll])?)?|"
        r"(?:m|u|n)?g\s*/\s*(?:m?[Ll]|d[Ll])|"
        r"(?:wt|vol|w/v|v/v)\s*%|ppm|ppb|mg/kg)\b",
    ),
    # Voltage / current
    regex.compile(
        r"\b[\-\+]?\d+(?:\.\d+)?\s*(?:m?[VA]|kV|mV|[mu]A)\b",
    ),
    # Speed: rpm
    regex.compile(r"\b\d+(?:,\d{3})*\s*(?:rpm|RPM|rcf|RCF|[xg])\b"),
    # Humidity
    regex.compile(r"\b\d+(?:\.\d+)?\s*%\s*(?:RH|relative\s+humidity)\b", regex.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Measurement parameters
# ---------------------------------------------------------------------------
PARAMETER_PATTERNS: list[regex.Pattern[str]] = [
    # Wavelength: 532 nm, 1064 nm
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:nm|um|\u00b5m|mm|cm|m|km)\b"),
    # Energy: eV, keV, MeV, J, kJ
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:[kMG]?eV|[kMm]?J(?:/mol)?|cal(?:/mol)?|kcal)\b"),
    # Frequency: Hz, kHz, MHz, GHz, THz
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:[kMGT]?Hz)\b"),
    # Power/intensity: W, mW, W/cm2
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:m?W(?:/cm\^?2)?|mW)\b"),
    # Flow rate
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:m?L/min|mL/h|sccm|slm)\b", regex.IGNORECASE),
    # Angle: degrees, 2theta
    regex.compile(r"\b\d+(?:\.\d+)?\s*(?:deg(?:rees?)?|[°]|mrad)\b"),
    regex.compile(r"\b2\s*[\u03b8\u0398]?\s*(?:theta)?\b", regex.IGNORECASE),
    # Magnification
    regex.compile(r"\b\d+(?:,\d{3})*\s*[xX]\s+(?:magnification)\b"),
    # Acceleration voltage (for electron microscopy)
    regex.compile(
        r"\b(?:accelerat(?:ing|ion)\s+voltage|beam\s+energy)\s*(?:of|=|:)?\s*\d+(?:\.\d+)?\s*(?:k?eV|kV)\b",
        regex.IGNORECASE,
    ),
]

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
MATERIAL_NAMES: list[str] = [
    # Metals & alloys
    r"(?:gold|silver|copper|iron|aluminum|titanium|zinc|nickel|cobalt|platinum|palladium)",
    r"(?:stainless\s+steel|carbon\s+steel|brass|bronze)",
    # Polymers
    r"(?:polyethylene|polypropylene|polystyrene|polyester|polyamide|nylon|Kevlar)",
    r"(?:polyurethane|polycarbonate|polyimide|epoxy|silicone|rubber|latex)",
    r"(?:PMMA|PEEK|PTFE|Teflon|PET|PVC|PP|PE|PS|PA|PI|PU)",
    # Ceramics & glasses
    r"(?:alumina|zirconia|silica|titania|quartz|glass|sapphire|mica)",
    r"(?:silicon\s+(?:carbide|nitride)|boron\s+nitride|tungsten\s+carbide)",
    # Carbon materials
    r"(?:graphene|graphite|carbon\s+(?:nanotube|fiber|black|dot)s?|fullerene|diamond)",
    r"(?:CNT|SWCNT|MWCNT|rGO|GO)",
    # Nanomaterials
    r"(?:nano(?:particle|wire|rod|tube|sheet|fiber|crystal|composite|cluster)s?)",
    r"(?:quantum\s+dots?|QDs?)",
    # Biological
    r"(?:collagen|gelatin|chitosan|cellulose|starch|silk|alginate|hyaluronic\s+acid|fibrin)",
    # Semiconductors
    r"(?:silicon|germanium|gallium\s+arsenide|GaAs|InP|GaN|ZnO|CdSe|CdS)",
    # Substrates
    r"(?:glass\s+slide|silicon\s+wafer|ITO|FTO|gold\s+film|copper\s+grid|TEM\s+grid)",
]

MATERIAL_PATTERN = regex.compile(
    r"\b(?:" + "|".join(MATERIAL_NAMES) + r")s?\b",
    regex.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Methods / Techniques
# ---------------------------------------------------------------------------
METHOD_NAMES: list[str] = [
    # Deposition
    r"(?:chemical|physical)\s+vapor\s+deposition",
    r"(?:CVD|PVD|ALD|MBE|PLD|MOCVD|PECVD)",
    r"(?:sputter(?:ing)?|evaporation|electrodeposition|electroplating)",
    r"(?:spin[\-\s]?coat(?:ing)?|dip[\-\s]?coat(?:ing)?|spray[\-\s]?coat(?:ing)?|drop[\-\s]?cast(?:ing)?)",
    # Lithography
    r"(?:photo|e[\-\s]?beam|nano[\-\s]?imprint|soft)\s*lithography",
    r"(?:EBL|NIL|FIB)",
    r"(?:focused\s+ion\s+beam)",
    # Etching
    r"(?:wet|dry|plasma|reactive\s+ion)\s+etch(?:ing)?",
    r"RIE",
    # Synthesis
    r"(?:sol[\-\s]?gel|hydrothermal|solvothermal|co[\-\s]?precipitation|sonication)",
    r"(?:ball\s+milling|mechanical\s+alloying|freeze[\-\s]?dry(?:ing)?|lyophilization)",
    r"(?:emulsion|microemulsion|miniemulsion)\s+polymerization",
    # Bio-methods
    r"(?:PCR|qPCR|RT[\-\s]?PCR|Western\s+blot|ELISA|flow\s+cytometry)",
    r"(?:cell\s+culture|incubation|centrifugation|filtration|dialysis)",
    r"(?:gel\s+electrophoresis|SDS[\-\s]?PAGE|immunostaining|transfection)",
    # Characterization methods
    r"(?:tensile\s+test(?:ing)?|hardness\s+test(?:ing)?|nanoindentation)",
    r"(?:contact\s+angle\s+measurement|surface\s+roughness\s+measurement)",
    r"(?:cyclic\s+voltammetry|impedance\s+spectroscopy|chronoamperometry)",
    # Processing
    r"(?:anneal(?:ing)?|sinter(?:ing)?|calcin(?:ation|ing)|quench(?:ing)?)",
    r"(?:ion\s+implantation|plasma\s+treatment|surface\s+functionalization)",
]

METHOD_PATTERN = regex.compile(
    r"\b(?:" + "|".join(METHOD_NAMES) + r")\b",
    regex.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Biological organisms / specimens
# ---------------------------------------------------------------------------
ORGANISM_PATTERNS: list[regex.Pattern[str]] = [
    # Genus species italicized or not (common model organisms)
    regex.compile(
        r"\b(?:Escherichia\s+coli|E\.\s*coli|"
        r"Staphylococcus\s+aureus|S\.\s*aureus|"
        r"Pseudomonas\s+aeruginosa|Bacillus\s+subtilis|"
        r"Saccharomyces\s+cerevisiae|Candida\s+albicans|"
        r"Aspergillus\s+niger|Aspergillus\s+fumigatus|"
        r"Drosophila\s+melanogaster|Caenorhabditis\s+elegans|C\.\s*elegans|"
        r"Mus\s+musculus|Rattus\s+norvegicus|"
        r"Arabidopsis\s+thaliana|"
        r"Homo\s+sapiens|"
        r"HeLa|HEK[\-\s]?293[T]?|CHO|Jurkat|MCF[\-\s]?7|A549|NIH[\-\s]?3T3)\b",
    ),
    # General organism types
    regex.compile(
        r"\b(?:bacteria|bacterium|fungus|fungi|yeast|virus|vir(?:us|ion)|phage|"
        r"(?:meso|thermo|cryo)phil(?:e|ic)|"
        r"(?:gram[\-\s]?(?:positive|negative))\s+(?:bacteria|cocci|bacilli|organism))\b",
        regex.IGNORECASE,
    ),
    # Cell types
    regex.compile(
        r"\b(?:fibroblast|osteoblast|osteocyte|epithelial\s+cell|endothelial\s+cell|"
        r"stem\s+cell|progenitor\s+cell|macrophage|neutrophil|lymphocyte|"
        r"mesenchymal\s+(?:stem|stromal)\s+cell|iPSC|MSC|ESC)s?\b",
        regex.IGNORECASE,
    ),
]

# ---------------------------------------------------------------------------
# Sample types
# ---------------------------------------------------------------------------
SAMPLE_PATTERNS: list[regex.Pattern[str]] = [
    regex.compile(
        r"\b(?:thin\s+film|bulk\s+sample|powder|pellet|coupon|specimen|"
        r"single\s+crystal|polycrystal(?:line)?|amorphous|"
        r"(?:nano|micro|meso)(?:porous|structured|crystalline)|"
        r"(?:cross[\-\s]?section|longitudinal\s+section|"
        r"(?:tissue|biopsy|blood|serum|plasma|urine|saliva)\s+sample)|"
        r"substrate|coating|membrane|scaffold|hydrogel|aerogel|"
        r"(?:core[\-\s]?shell|hollow|solid|porous)\s+(?:particle|sphere|structure)s?|"
        r"monolayer|bilayer|multilayer|heterostructure|superlattice)\b",
        regex.IGNORECASE,
    ),
]


def compile_all_patterns() -> dict[str, list[regex.Pattern[str]]]:
    """Return all pattern groups keyed by category."""
    return {
        "instrument": [INSTRUMENT_PATTERN],
        "chemical": CHEMICAL_PATTERNS,
        "condition": CONDITION_PATTERNS,
        "parameter": PARAMETER_PATTERNS,
        "material": [MATERIAL_PATTERN],
        "method": [METHOD_PATTERN],
        "organism": ORGANISM_PATTERNS,
        "sample": SAMPLE_PATTERNS,
    }
