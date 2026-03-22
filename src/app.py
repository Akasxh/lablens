"""Streamlit web interface for LabLens metadata extraction pipeline."""

from __future__ import annotations

import html as html_lib
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from .extractor import extract_from_file, extract_from_text, results_to_dataframe
    from .sample_papers import SAMPLES_BY_NAME
    from .schemas import ExtractionResult
except ImportError:
    from extractor import extract_from_file, extract_from_text, results_to_dataframe
    from sample_papers import SAMPLES_BY_NAME
    from schemas import ExtractionResult

st.set_page_config(
    page_title="LabLens - Scientific Metadata Extraction",
    page_icon="\U0001f52c",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "LabLens extracts structured experimental metadata from scientific "
            "publications using spaCy NER + domain-specific regex patterns. "
            "No API keys required. Runs entirely locally."
        ),
    },
)

# ---------------------------------------------------------------------------
# Professional CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Gradient sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stTextArea label {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(148,163,184,0.2);
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        background-color: rgba(255,255,255,0.1);
    }

    /* Hero section */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #64748b;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    /* Category pills */
    .category-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 3px;
        letter-spacing: 0.02em;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-weight: 700;
    }

    /* Entity card */
    .entity-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .entity-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .entity-name {
        font-weight: 700;
        font-size: 1rem;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .entity-meta {
        font-size: 0.82rem;
        color: #64748b;
    }
    .conf-bar-bg {
        background: #e2e8f0;
        border-radius: 6px;
        height: 8px;
        width: 100%;
        overflow: hidden;
        margin-top: 6px;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.3s;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }

    /* Download buttons */
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        transform: translateY(-1px);
    }

    /* === POLISH LAYER === */

    /* Keyframes */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-16px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseFill {
        from { transform: scaleX(0); transform-origin: left; }
        to   { transform: scaleX(1); transform-origin: left; }
    }
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Entity card micro-interactions + staggered entrance */
    .entity-card {
        transition: box-shadow 0.22s ease, transform 0.22s ease;
        animation: fadeInUp 0.4s ease both;
    }
    .entity-card:hover {
        transform: translateY(-2px) scale(1.008);
        box-shadow: 0 8px 20px rgba(0,0,0,0.10);
    }
    .entity-card:nth-child(2)  { animation-delay: 0.05s; }
    .entity-card:nth-child(3)  { animation-delay: 0.10s; }
    .entity-card:nth-child(4)  { animation-delay: 0.15s; }
    .entity-card:nth-child(5)  { animation-delay: 0.20s; }

    /* Confidence bar pulse on load */
    .conf-bar-fill {
        animation: pulseFill 0.6s ease both;
    }

    /* Category pill hover */
    .category-pill {
        transition: filter 0.2s ease, transform 0.2s ease;
    }
    .category-pill:hover {
        filter: brightness(1.15);
        transform: translateY(-1px);
    }

    /* Tab hover + active gradient border */
    .stTabs [data-baseweb="tab"] {
        transition: background-color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(59,130,246,0.06);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-image: linear-gradient(135deg, #3b82f6, #8b5cf6) 1;
        border-bottom: 2px solid;
    }

    /* Glass-morphism metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg,
            rgba(248,250,252,0.85), rgba(241,245,249,0.75));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(226,232,240,0.6);
        animation: fadeInUp 0.4s ease both;
    }

    /* Hero animation + subtle pattern */
    .hero-title {
        animation: slideIn 0.5s ease both;
    }
    .hero-sub {
        animation: fadeInUp 0.5s ease 0.15s both;
    }

    /* Hero separator */
    .hero-sep {
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
        margin: 0.5rem 0 1.2rem 0;
        border: none;
    }

    /* Sidebar toggle styling */
    button[data-testid="stSidebarCollapsedControl"],
    button[data-testid="collapsedControl"] {
        border-radius: 8px !important;
        transition: background 0.2s ease;
    }

    /* Sidebar smooth transition */
    section[data-testid="stSidebar"] {
        transition: transform 0.3s cubic-bezier(0.4,0,0.2,1),
                    width 0.3s cubic-bezier(0.4,0,0.2,1);
    }

    /* Multiselect + slider theming */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        border-radius: 6px !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        border: 2px solid #fff !important;
        box-shadow: 0 1px 4px rgba(59,130,246,0.3);
    }
    div[data-baseweb="slider"] div[data-testid="stTickBar"] ~ div div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    }
</style>
""", unsafe_allow_html=True)

_CATEGORY_COLORS: dict[str, str] = {
    "instrument": "#10b981",
    "chemical": "#3b82f6",
    "condition": "#f59e0b",
    "parameter": "#8b5cf6",
    "material": "#ef4444",
    "method": "#06b6d4",
    "organism": "#84cc16",
    "sample": "#78716c",
}

_CATEGORY_ICONS: dict[str, str] = {
    "instrument": "Instruments",
    "chemical": "Chemicals",
    "condition": "Conditions",
    "parameter": "Parameters",
    "material": "Materials",
    "method": "Methods",
    "organism": "Organisms",
    "sample": "Samples",
}


def _render_sidebar() -> tuple[str, str | None, list | None]:
    """Render sidebar and return (input_mode, text, uploaded_files)."""
    st.sidebar.markdown("### LabLens")
    st.sidebar.caption("Scientific Metadata Extraction")
    st.sidebar.markdown("---")

    input_mode = st.sidebar.radio(
        "Input Source",
        ["Demo Samples", "Paste Text", "Upload Files"],
        index=0,
        help="Start with Demo Samples to see LabLens in action.",
    )

    text: str | None = None
    uploaded_files: list | None = None

    if input_mode == "Demo Samples":
        sample_name = st.sidebar.selectbox("Select sample", list(SAMPLES_BY_NAME.keys()))
        text = SAMPLES_BY_NAME[sample_name]
        st.sidebar.caption(f"{len(text):,} characters")
        # Store selected name for use as source_name
        st.session_state["demo_sample_name"] = sample_name

    elif input_mode == "Paste Text":
        text = st.sidebar.text_area(
            "Paste text from a scientific paper",
            height=200,
            placeholder="Paste abstract, methods section, or full paper text here...",
        )

    elif input_mode == "Upload Files":
        uploaded_files = st.sidebar.file_uploader(
            "Upload scientific papers",
            type=["pdf", "txt", "md", "tex"],
            accept_multiple_files=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Built with [spaCy](https://spacy.io/) + regex patterns. "
        "No API keys. Runs locally."
    )

    return input_mode, text, uploaded_files


def _render_hero() -> None:
    """Render the hero section with project description."""
    st.markdown('<p class="hero-title">LabLens</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">'
        "Extract structured experimental metadata from scientific publications "
        "using NLP &mdash; no API keys, fully local."
        "</p>",
        unsafe_allow_html=True,
    )

    # Inline SVG favicon override
    st.markdown(
        '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,'
        '%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E'
        '%3Ccircle cx=%2732%27 cy=%2732%27 r=%2730%27 fill=%27%233b82f6%27/%3E'
        '%3Cpath d=%27M32 14c-2 0-3.5 1.5-3.5 3.5v17c0 2 1.5 3.5 3.5 3.5s3.5-1.5 3.5-3.5v-17'
        'C35.5 15.5 34 14 32 14zM24 42h16v3H24z%27 fill=%27white%27/%3E'
        '%3Ccircle cx=%2732%27 cy=%2749%27 r=%273%27 fill=%27white%27/%3E'
        '%3C/svg%3E">',
        unsafe_allow_html=True,
    )

    pills_html = " ".join(
        f'<span class="category-pill" style="background:{color}18;color:{color};'
        f'border:1px solid {color}40;">'
        f"{label}</span>"
        for label, color in zip(
            _CATEGORY_ICONS.values(), _CATEGORY_COLORS.values(), strict=False
        )
    )
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown('<div class="hero-sep"></div>', unsafe_allow_html=True)


def _conf_color(confidence: float) -> str:
    """Return a color for the confidence value (red -> yellow -> green)."""
    if confidence >= 0.75:
        return "#10b981"
    if confidence >= 0.55:
        return "#f59e0b"
    return "#ef4444"


def _render_entity_cards(result: ExtractionResult) -> None:
    """Render top entities as styled cards with color-coded categories."""
    if not result.entities:
        return

    st.markdown("### Top Extracted Entities")

    # Group by category
    by_cat: dict[str, list] = {}
    for e in result.entities:
        by_cat.setdefault(e.category, []).append(e)

    # Render in a grid
    cat_names = sorted(by_cat.keys(), key=lambda c: len(by_cat[c]), reverse=True)
    cols = st.columns(min(len(cat_names), 4))

    for idx, cat in enumerate(cat_names):
        col = cols[idx % len(cols)]
        color = _CATEGORY_COLORS.get(cat, "#64748b")
        entities = by_cat[cat][:5]  # top 5 per category

        with col:
            st.markdown(
                f'<span class="category-pill" style="background:{color}18;color:{color};'
                f'border:1px solid {color}40;font-size:0.9rem;">'
                f'{_CATEGORY_ICONS.get(cat, cat)} ({len(by_cat[cat])})</span>',
                unsafe_allow_html=True,
            )
            for e in entities:
                conf_color = _conf_color(e.confidence)
                conf_pct = int(e.confidence * 100)
                card_html = f"""
                <div class="entity-card">
                    <div class="entity-name">{e.text}</div>
                    <div class="entity-meta">
                        confidence: {e.confidence:.2f} &middot; {e.subcategory}
                    </div>
                    <div class="conf-bar-bg">
                        <div class="conf-bar-fill"
                             style="width:{conf_pct}%;background:{conf_color};">
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
            if len(by_cat[cat]) > 5:
                st.caption(f"+ {len(by_cat[cat]) - 5} more")


def _render_entity_table(result: ExtractionResult) -> pd.DataFrame | None:
    """Render entity table with category filters."""
    if not result.entities:
        st.warning("No entities extracted. Try a longer or more technical text.")
        return None

    df = pd.DataFrame(result.to_csv_rows())

    col_filter, col_conf = st.columns([3, 1])

    with col_filter:
        categories = sorted(df["category"].unique())
        selected_cats = st.multiselect(
            "Filter categories",
            categories,
            default=categories,
            key="cat_filter",
        )

    with col_conf:
        min_conf = st.slider(
            "Min confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            key="conf_slider",
        )

    filtered = df[df["category"].isin(selected_cats) & (df["confidence"] >= min_conf)]

    st.dataframe(
        filtered[["text", "category", "subcategory", "confidence", "context"]].reset_index(
            drop=True
        ),
        width="stretch",
        height=400,
        column_config={
            "confidence": st.column_config.ProgressColumn(
                "confidence", min_value=0.0, max_value=1.0, format="%.2f"
            ),
        },
    )

    return filtered


def _render_summary_metrics(result: ExtractionResult) -> None:
    """Render summary metric cards."""
    cols = st.columns(4)
    cols[0].metric("Total Entities", len(result.entities))
    cols[1].metric("Categories", len({e.category for e in result.entities}))
    avg_conf = (
        sum(e.confidence for e in result.entities) / len(result.entities)
        if result.entities
        else 0
    )
    cols[2].metric("Avg Confidence", f"{avg_conf:.2f}")
    cols[3].metric("Extraction Time", f"{result.extraction_time_ms:.0f} ms")


def _render_category_breakdown(result: ExtractionResult) -> None:
    """Render per-category entity counts as a bar chart."""
    if not result.entities:
        return

    summary = result.to_dict()["summary"]
    chart_data = pd.DataFrame(
        {"category": list(summary.keys()), "count": list(summary.values())}
    )
    chart_data = chart_data[chart_data["count"] > 0].sort_values("count", ascending=False)

    st.bar_chart(chart_data.set_index("category")["count"])


def _render_review_ui(result: ExtractionResult) -> ExtractionResult:
    """Interactive review UI where users can verify/correct extractions."""
    st.subheader("Interactive Review")
    st.markdown("Verify or reject extracted entities. Changes update the export.")

    if not result.entities:
        st.info("No entities to review.")
        return result

    state_key = f"verified_{result.document_name}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {i: None for i in range(len(result.entities))}

    verified_state = st.session_state[state_key]

    page_size = 10
    total_pages = max(1, (len(result.entities) + page_size - 1) // page_size)
    page = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, key="review_page"
    )
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(result.entities))

    for i in range(start_idx, end_idx):
        entity = result.entities[i]
        col1, col2, col3, col4 = st.columns([3, 2, 1, 2])

        with col1:
            color = _CATEGORY_COLORS.get(entity.category, "#64748b")
            st.markdown(f"**{entity.text}**")
            st.markdown(
                f'<span class="category-pill" style="background:{color}18;color:{color};'
                f'border:1px solid {color}40;font-size:0.75rem;">'
                f"{entity.category}</span>"
                f" &middot; confidence: {entity.confidence:.2f}",
                unsafe_allow_html=True,
            )

        with col2:
            st.caption(
                entity.context[:100] + "..." if len(entity.context) > 100 else entity.context
            )

        with col3:
            status = verified_state.get(i)
            if status is True:
                st.success("Verified")
            elif status is False:
                st.error("Rejected")

        with col4:
            c1, c2 = st.columns(2)
            if c1.button("Accept", key=f"accept_{i}"):
                verified_state[i] = True
                entity.verified = True
            if c2.button("Reject", key=f"reject_{i}"):
                verified_state[i] = False
                entity.verified = False

        st.markdown("---")

    accepted = [
        e for i, e in enumerate(result.entities) if verified_state.get(i) is not False
    ]

    verified_count = sum(1 for v in verified_state.values() if v is True)
    rejected_count = sum(1 for v in verified_state.values() if v is False)
    remaining = len(result.entities) - verified_count - rejected_count
    st.info(f"Verified: {verified_count} | Rejected: {rejected_count} | Remaining: {remaining}")

    return ExtractionResult(
        document_name=result.document_name,
        entities=accepted,
        raw_text_length=result.raw_text_length,
        extraction_time_ms=result.extraction_time_ms,
    )


def _render_exports(result: ExtractionResult, fmt: str) -> None:
    """Render download buttons for a single export format."""
    if fmt == "JSON":
        data = result.to_json(indent=2)
        st.download_button(
            "Download JSON",
            data=data,
            file_name=f"{result.document_name}_metadata.json",
            mime="application/json",
        )
        with st.expander("Preview JSON"):
            st.json(json.loads(data))

    elif fmt == "CSV":
        df = pd.DataFrame(result.to_csv_rows())
        csv_data = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"{result.document_name}_metadata.csv",
            mime="text/csv",
        )
        with st.expander("Preview CSV"):
            st.dataframe(df, width="stretch")

    elif fmt == "BioSchemas JSON-LD":
        data = json.dumps(result.to_bioschemas(), indent=2, ensure_ascii=False)
        st.download_button(
            "Download BioSchemas JSON-LD",
            data=data,
            file_name=f"{result.document_name}_bioschemas.jsonld",
            mime="application/ld+json",
        )
        with st.expander("Preview BioSchemas"):
            st.json(json.loads(data))


def _render_knowledge_graph(result: ExtractionResult) -> None:
    """Render an interactive force-directed entity co-occurrence graph using vis.js."""
    if not result.entities:
        st.info("No entities to visualize.")
        return

    st.subheader("Entity Co-occurrence Graph")
    st.caption(
        "Nodes represent extracted entities (sized by confidence, colored by category). "
        "Edges connect entities that co-occur within ~200 characters of each other in the source text."
    )

    # Build nodes and edges from entity data
    nodes_js: list[str] = []
    seen_texts: dict[str, int] = {}
    entity_list = result.entities[:80]  # cap for performance

    for idx, e in enumerate(entity_list):
        if e.text in seen_texts:
            continue
        seen_texts[e.text] = idx
        color = _CATEGORY_COLORS.get(e.category, "#64748b")
        size = max(12, int(e.confidence * 40))
        label = e.text[:25] + ("..." if len(e.text) > 25 else "")
        escaped_text = html_lib.escape(e.text)
        escaped_sub = html_lib.escape(e.subcategory)
        nodes_js.append(
            f'{{id:{idx},label:"{html_lib.escape(label)}",'
            f'color:"{color}",size:{size},'
            f'title:"{escaped_text}\\n{e.category} / {escaped_sub}\\nconf: {e.confidence:.2f}",'
            f'font:{{color:"#1e293b",size:11}}}}'
        )

    # Build edges: entities co-occurring within 200 chars of each other
    edges_js: list[str] = []
    edge_set: set[tuple[int, int]] = set()
    for i, e1 in enumerate(entity_list):
        if e1.text not in seen_texts:
            continue
        n1 = seen_texts[e1.text]
        for j, e2 in enumerate(entity_list):
            if j <= i or e2.text not in seen_texts:
                continue
            n2 = seen_texts[e2.text]
            if n1 == n2:
                continue
            pair = (min(n1, n2), max(n1, n2))
            if pair in edge_set:
                continue
            # Check proximity via source_span
            s1_mid = (e1.source_span[0] + e1.source_span[1]) / 2
            s2_mid = (e2.source_span[0] + e2.source_span[1]) / 2
            if abs(s1_mid - s2_mid) < 200:
                edge_set.add(pair)
                edges_js.append(
                    f'{{from:{n1},to:{n2},color:{{color:"#cbd5e1",opacity:0.5}},'
                    f'width:1}}'
                )

    graph_html = f"""
    <!DOCTYPE html>
    <html><head>
    <script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
    <style>
      #graph-container {{
        width: 100%; height: 520px; border: 1px solid #e2e8f0;
        border-radius: 12px; background: #fafbfc;
      }}
    </style>
    </head><body>
    <div id="graph-container"></div>
    <script>
      var nodes = new vis.DataSet([{",".join(nodes_js)}]);
      var edges = new vis.DataSet([{",".join(edges_js)}]);
      var container = document.getElementById("graph-container");
      var data = {{nodes: nodes, edges: edges}};
      var options = {{
        physics: {{
          forceAtlas2Based: {{gravitationalConstant: -30, centralGravity: 0.005,
            springLength: 120, springConstant: 0.04}},
          solver: "forceAtlas2Based", stabilization: {{iterations: 150}}
        }},
        interaction: {{hover: true, tooltipDelay: 100, zoomView: true, dragView: true}},
        nodes: {{shape: "dot", borderWidth: 2, borderWidthSelected: 3,
          shadow: {{enabled: true, size: 4, x: 2, y: 2}}}},
        edges: {{smooth: {{type: "continuous"}}}}
      }};
      new vis.Network(container, data, options);
    </script>
    </body></html>
    """
    components.html(graph_html, height=550, scrolling=False)

    # Legend
    legend_cols = st.columns(len(_CATEGORY_COLORS))
    for col, (cat, color) in zip(legend_cols, _CATEGORY_COLORS.items()):
        col.markdown(
            f'<span style="display:inline-block;width:12px;height:12px;'
            f'border-radius:50%;background:{color};margin-right:4px;'
            f'vertical-align:middle;"></span>'
            f'<span style="font-size:0.78rem;color:#475569;">'
            f'{_CATEGORY_ICONS.get(cat, cat)}</span>',
            unsafe_allow_html=True,
        )


def _render_annotated_text(result: ExtractionResult, source_text: str) -> None:
    """Render source text with inline entity highlights and hover tooltips."""
    if not result.entities or not source_text:
        st.info("No source text or entities available for annotation.")
        return

    st.subheader("Annotated Source Text")
    st.caption("Entity mentions are highlighted inline. Hover for details.")

    # Collect valid spans, resolve overlaps by keeping highest confidence
    spans: list[tuple[int, int, str, str, str, float]] = []
    for e in result.entities:
        s, end = e.source_span
        if s == 0 and end == 0:
            continue
        if end > len(source_text):
            continue
        spans.append((s, end, e.category, e.subcategory, e.text, e.confidence))

    # Sort by start, then by confidence desc for overlap resolution
    spans.sort(key=lambda x: (x[0], -x[5]))

    # Remove overlapping spans — keep highest confidence
    filtered: list[tuple[int, int, str, str, str, float]] = []
    last_end = -1
    for span in spans:
        if span[0] >= last_end:
            filtered.append(span)
            last_end = span[1]

    # Build HTML with highlights
    display_text = source_text[:8000]  # cap for rendering performance
    parts: list[str] = []
    cursor = 0

    for s, end, cat, subcat, ent_text, conf in filtered:
        if s > len(display_text) or end > len(display_text):
            continue
        if s > cursor:
            parts.append(html_lib.escape(display_text[cursor:s]))
        color = _CATEGORY_COLORS.get(cat, "#64748b")
        conf_pct = int(conf * 100)
        tooltip = f"{cat} / {subcat} | confidence: {conf:.2f}"
        parts.append(
            f'<span style="background:{color}22;border-bottom:2px solid {color};'
            f'padding:1px 3px;border-radius:3px;cursor:help;" '
            f'title="{html_lib.escape(tooltip)}">'
            f'{html_lib.escape(display_text[s:end])}'
            f'<sup style="font-size:0.65rem;color:{color};font-weight:700;">'
            f' {conf_pct}%</sup></span>'
        )
        cursor = end

    if cursor < len(display_text):
        parts.append(html_lib.escape(display_text[cursor:]))
    if len(source_text) > 8000:
        parts.append('<span style="color:#94a3b8;">... [truncated]</span>')

    annotated_html = (
        '<div style="font-family:\'Georgia\',serif;font-size:0.95rem;'
        'line-height:1.85;color:#1e293b;background:#fff;padding:24px 28px;'
        'border-radius:12px;border:1px solid #e2e8f0;'
        'max-height:600px;overflow-y:auto;white-space:pre-wrap;">'
        + "".join(parts)
        + "</div>"
    )
    st.markdown(annotated_html, unsafe_allow_html=True)

    # Stats bar
    st.caption(
        f"Showing {len(filtered)} entity annotations across {len(display_text):,} characters."
    )


def _render_protocol_card(result: ExtractionResult) -> None:
    """Render a structured protocol card organizing entities into experiment steps."""
    if not result.entities:
        return

    st.markdown("### Reconstructed Protocol")
    st.caption(
        "Entities organized into a logical experiment workflow. "
        "Each section lists extracted entities with confidence badges."
    )

    # Define protocol sections in logical order
    _PROTOCOL_SECTIONS: list[tuple[str, str, str, str]] = [
        ("material", "Materials Used", "Substrates, reagents, and starting materials", "🧱"),
        ("chemical", "Chemicals & Reagents", "Chemical compounds and solutions", "🧪"),
        ("method", "Methods Applied", "Experimental techniques and procedures", "🔬"),
        ("condition", "Conditions Set", "Temperature, pressure, atmosphere, and environment", "🌡️"),
        ("instrument", "Instruments Used", "Equipment and measurement devices", "⚙️"),
        ("parameter", "Parameters Measured", "Quantitative measurements and results", "📊"),
        ("organism", "Biological Systems", "Organisms, cell lines, and biological models", "🧬"),
        ("sample", "Samples & Specimens", "Sample types and preparations", "🏷️"),
    ]

    # Group entities by category
    by_cat: dict[str, list] = {}
    for e in result.entities:
        by_cat.setdefault(e.category, []).append(e)

    # Render protocol sections as a two-column grid
    active_sections = [(cat, title, desc, icon) for cat, title, desc, icon in _PROTOCOL_SECTIONS if cat in by_cat]
    if not active_sections:
        return

    for i in range(0, len(active_sections), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(active_sections):
                break
            cat, title, desc, icon = active_sections[i + j]
            entities = by_cat[cat]
            color = _CATEGORY_COLORS.get(cat, "#64748b")

            # Build entity list HTML
            entity_items = ""
            for e in entities[:8]:  # cap at 8 per section
                conf_color = _conf_color(e.confidence)
                conf_pct = int(e.confidence * 100)
                entity_items += (
                    f'<div style="display:flex;align-items:center;justify-content:space-between;'
                    f'padding:6px 0;border-bottom:1px solid #f1f5f9;">'
                    f'<span style="font-size:0.88rem;color:#1e293b;font-weight:500;">'
                    f'{html_lib.escape(e.text)}</span>'
                    f'<span style="font-size:0.72rem;background:{conf_color}18;color:{conf_color};'
                    f'padding:2px 8px;border-radius:10px;font-weight:600;white-space:nowrap;">'
                    f'{conf_pct}%</span></div>'
                )
            overflow = ""
            if len(entities) > 8:
                overflow = (
                    f'<div style="text-align:center;padding:4px;color:#94a3b8;font-size:0.78rem;">'
                    f'+ {len(entities) - 8} more</div>'
                )

            card_html = (
                f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;'
                f'padding:20px;margin-bottom:12px;border-top:3px solid {color};">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
                f'<span style="font-size:1.3rem;">{icon}</span>'
                f'<span style="font-weight:700;font-size:1rem;color:#1e293b;">{title}</span>'
                f'<span style="font-size:0.72rem;background:{color}18;color:{color};'
                f'padding:2px 10px;border-radius:12px;font-weight:600;">'
                f'{len(entities)}</span></div>'
                f'<div style="font-size:0.78rem;color:#94a3b8;margin-bottom:10px;">{desc}</div>'
                f'{entity_items}{overflow}</div>'
            )
            col.markdown(card_html, unsafe_allow_html=True)


def _render_demo_landing() -> None:
    """Show a prominent demo CTA when no results are loaded."""
    st.markdown("---")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("### Try the demo")
        st.markdown(
            "LabLens ships with **5 built-in sample papers** covering TEM nanoparticle "
            "characterization, polymer scaffold electrospinning, photocatalysis, "
            "CRISPR genome editing, and environmental microplastics research. "
            "Select **Demo Samples** in the sidebar to see extraction results instantly."
        )
        st.markdown(
            "You can also **paste text** from any scientific paper or **upload PDFs** "
            "for batch processing."
        )
    with col_r:
        st.markdown("#### Supported entity types")
        for label, color in zip(
            _CATEGORY_ICONS.values(), _CATEGORY_COLORS.values(), strict=False
        ):
            st.markdown(
                f'<span style="color:{color};font-weight:600;">{label}</span>',
                unsafe_allow_html=True,
            )


def main() -> None:
    input_mode, text, uploaded_files = _render_sidebar()

    _render_hero()

    result: ExtractionResult | None = None

    if input_mode in ("Demo Samples", "Paste Text") and text and text.strip():
        if input_mode == "Demo Samples":
            source = st.session_state.get("demo_sample_name", "demo_sample")
        else:
            source = "pasted_text"
        auto_run = input_mode == "Demo Samples"
        if auto_run or st.button("Extract Metadata", type="primary"):
            with st.spinner("Extracting metadata..."):
                result = extract_from_text(text, source_name=source)
            st.session_state["last_result"] = result

        if "last_result" in st.session_state and result is None:
            result = st.session_state["last_result"]

    elif input_mode == "Upload Files" and uploaded_files:
        if st.button("Extract Metadata", type="primary"):
            results = []
            for uf in uploaded_files:
                with tempfile.NamedTemporaryFile(
                    suffix=Path(uf.name).suffix, delete=False
                ) as tmp:
                    tmp.write(uf.read())
                    tmp_path = Path(tmp.name)
                with st.spinner(f"Processing {uf.name}..."):
                    r = extract_from_file(tmp_path)
                    r.document_name = uf.name
                    results.append(r)
            if len(results) == 1:
                result = results[0]
            else:
                all_entities = []
                for r in results:
                    for e in r.entities:
                        e.context = f"[{r.document_name}] {e.context}"
                        all_entities.append(e)
                result = ExtractionResult(
                    document_name="batch_results",
                    entities=all_entities,
                    raw_text_length=sum(r.raw_text_length for r in results),
                    extraction_time_ms=sum(r.extraction_time_ms for r in results),
                )
            st.session_state["last_result"] = result

        if "last_result" in st.session_state and result is None:
            result = st.session_state["last_result"]

    if result is None:
        _render_demo_landing()
        return

    # Display results in tabs
    tab_overview, tab_entities, tab_graph, tab_annotated, tab_review, tab_export = st.tabs(
        ["Overview", "Entities", "Knowledge Graph", "Annotated Text", "Review", "Export"]
    )

    with tab_overview:
        _render_summary_metrics(result)
        st.markdown("")
        _render_entity_cards(result)
        _render_protocol_card(result)
        st.markdown("### Entity Distribution")
        _render_category_breakdown(result)

        if text:
            with st.expander("Source Text", expanded=False):
                st.text(text[:5000] + ("..." if len(text) > 5000 else ""))

    with tab_entities:
        _render_entity_table(result)

    with tab_graph:
        _render_knowledge_graph(result)

    with tab_annotated:
        source_text = text or ""
        _render_annotated_text(result, source_text)

    with tab_review:
        reviewed_result = _render_review_ui(result)

    with tab_export:
        st.subheader("Export Results")
        st.markdown("Download extraction results in your preferred format.")
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            _render_exports(reviewed_result, fmt="JSON")
        with exp_col2:
            _render_exports(reviewed_result, fmt="CSV")
        with exp_col3:
            _render_exports(reviewed_result, fmt="BioSchemas JSON-LD")


if __name__ == "__main__":
    main()
