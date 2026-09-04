"""Streamlit UI components."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.config import CUSTOM_CSS, DATA_SOURCES, SOURCE_URLS
from src.cp_calculator import cp_at_temperature
from src.data_loader import filter_materials, get_categories, get_material_by_id, materials_to_dataframe
from src.plotting import (
    build_category_pie,
    build_cp_plot,
    build_inspector_table,
    build_ranking_chart,
    build_sample_temperature_table,
    build_source_bar,
)


def setup_page() -> None:
    st.set_page_config(
        page_title="Cp vs T Materials Database",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(materials: list[dict]) -> None:
    categories = get_categories(materials)
    
    st.markdown(
        f'''
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div class="brand-wrapper">
                <div class="logo-box">🔥</div>
                <div>
                    <h1 class="main-header">Interactive C<sub>p</sub> vs T Database</h1>
                    <p class="sub-header">Engineering Materials Thermodynamic Property Explorer</p>
                </div>
            </div>
            <div class="stat-card-row">
                <div class="stat-card">
                    <div class="stat-num">{len(materials)}</div>
                    <div class="stat-lbl">Materials</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">{len(categories)}</div>
                    <div class="stat-lbl">Categories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">3</div>
                    <div class="stat-lbl">Cp Models</div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict:
    with st.sidebar:
        st.header("Plot Settings")
        unit = st.radio("Temperature unit", ["Kelvin (K)", "Celsius (°C)"], horizontal=True)
        use_celsius = unit.startswith("Celsius")

        if use_celsius:
            t_min = st.number_input("T minimum (°C)", value=25.0, step=10.0)
            t_max = st.number_input("T maximum (°C)", value=500.0, step=10.0)
            t_min_k, t_max_k = t_min + 273.15, t_max + 273.15
        else:
            t_min = st.number_input("T minimum (K)", value=298.0, step=10.0)
            t_max = st.number_input("T maximum (K)", value=773.0, step=10.0)
            t_min_k, t_max_k = t_min, t_max

        n_points = st.slider("Plot points", 50, 500, 200, 10)
        show_phase = st.checkbox("Show phase transitions", value=True)
        show_molar = st.checkbox("Plot molar Cp (J/mol·K)", value=False)

        st.markdown("#### Curve display")
        display_mode = st.radio(
            "Y-axis mode",
            [
                "Absolute Cp",
                "Normalized (Cp / Cp@300K)",
                "ΔCp from T min",
            ],
            index=1,
            help="Use Normalized when comparing many materials — shows how Cp changes with temperature instead of one flat band.",
        )
        display_key = {
            "Absolute Cp": "absolute",
            "Normalized (Cp / Cp@300K)": "normalized",
            "ΔCp from T min": "delta",
        }[display_mode]
        log_y = st.checkbox("Log Y-axis (absolute mode only)", value=False)
        color_by_category = st.checkbox(
            "Color by category",
            value=False,
            help="Off = each material gets its own bright color (recommended).",
        )

        st.divider()
        rank_temp = st.number_input("Rank at T =", value=300.0 if not use_celsius else 27.0, step=10.0)
        rank_temp_k = rank_temp if not use_celsius else rank_temp + 273.15

        st.divider()
        st.markdown("#### Data Sources")
        for src in DATA_SOURCES[:4]:
            st.markdown(f"• [{src['name']}]({src['url']})")
        st.caption("See **Data Sources** tab for full list.")

    return {
        "use_celsius": use_celsius,
        "t_min_k": t_min_k,
        "t_max_k": t_max_k,
        "n_points": n_points,
        "show_phase": show_phase,
        "show_molar": show_molar,
        "display_mode": display_key,
        "log_y": log_y,
        "color_by_category": color_by_category,
        "rank_temp_k": rank_temp_k,
    }


def _init_selection(materials: list[dict]) -> None:
    if "selected_ids" not in st.session_state:
        st.session_state.selected_ids = [m["id"] for m in materials[:3]]


def render_material_panel(materials: list[dict]) -> tuple[list[dict], list[str]]:
    """Left panel: material list with reliable multi-selection."""
    _init_selection(materials)
    categories = ["All"] + get_categories(materials)

    st.markdown("### All Materials")
    category = st.selectbox("Category", categories, key="cat_filter")
    search = st.text_input("Search", placeholder="Name, formula, category…", key="search_filter")

    filtered = filter_materials(materials, category, search)
    label_to_id = {f"{m['name']} ({m['formula']})": m["id"] for m in filtered}
    id_to_label = {v: k for k, v in label_to_id.items()}
    filtered_id_set = set(label_to_id.values())

    # Keep only selections that are still visible
    st.session_state.selected_ids = [
        mid for mid in st.session_state.selected_ids if mid in filtered_id_set
    ]
    if not st.session_state.selected_ids and filtered:
        st.session_state.selected_ids = [filtered[0]["id"]]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select all", use_container_width=True, key="btn_all"):
            st.session_state.selected_ids = list(label_to_id.values())
            st.session_state._sync_multiselect = True
            st.rerun()
    with c2:
        if st.button("Clear", use_container_width=True, key="btn_clear"):
            st.session_state.selected_ids = []
            st.session_state._sync_multiselect = True
            st.rerun()

    current_labels = [
        id_to_label[mid] for mid in st.session_state.selected_ids if mid in id_to_label
    ]

    if "mat_multiselect" not in st.session_state:
        st.session_state.mat_multiselect = current_labels

    # Sync multiselect when select-all / clear buttons change selected_ids
    if st.session_state.get("_sync_multiselect"):
        st.session_state.mat_multiselect = current_labels
        st.session_state._sync_multiselect = False

    picked = st.multiselect(
        "Materials to plot",
        options=list(label_to_id.keys()),
        key="mat_multiselect",
    )
    st.session_state.selected_ids = [label_to_id[lbl] for lbl in picked if lbl in label_to_id]

    st.caption(f"**{len(picked)}** selected · **{len(filtered)}** shown · **{len(materials)}** total")

    list_df = pd.DataFrame(
        {
            "#": range(1, len(filtered) + 1),
            "Material": [m["name"] for m in filtered],
            "Formula": [m["formula"] for m in filtered],
            "Category": [m["category"] for m in filtered],
            "Source": [m["source"] for m in filtered],
            "Valid T (K)": [f"{m['t_min_k']:.0f}–{m['t_max_k']:.0f}" for m in filtered],
        }
    )
    st.dataframe(list_df, use_container_width=True, hide_index=True, height=360)

    return filtered, st.session_state.selected_ids


def render_plot_tab(materials: list[dict], selected_ids: list[str], settings: dict) -> None:
    st.markdown("### Cp – T Plot")

    if not selected_ids:
        st.warning("Select at least one material from the list on the left.")
        return
    if settings["t_min_k"] >= settings["t_max_k"]:
        st.error("T minimum must be less than T maximum.")
        return

    if len(selected_ids) > 20 and settings["display_mode"] == "absolute":
        st.info(
            f"**{len(selected_ids)} materials selected.** Absolute Cp values span a huge range "
            f"(gases ≈ 10,000+ J/kg·K vs metals ≈ 400 J/kg·K), so most curves look flat. "
            f"Switch sidebar **Y-axis mode** to **Normalized** to see temperature trends clearly."
        )

    try:
        fig, warnings, summary, plot_df = build_cp_plot(
            materials,
            selected_ids,
            settings["t_min_k"],
            settings["t_max_k"],
            settings["n_points"],
            settings["use_celsius"],
            settings["show_molar"],
            settings["show_phase"],
            settings["display_mode"],
            settings["log_y"],
            settings["color_by_category"],
        )
    except Exception as exc:
        st.error(f"Could not generate plot: {exc}")
        return

    st.markdown(
        f'<div class="plot-hero"><div class="plot-hero-title">'
        f'{len(selected_ids)} materials · {settings["n_points"]} temperature points each · '
        f'hover a line to read values · use the tables below to export data'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="main_cp_plot",
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "responsive": True,
            "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        },
    )

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "Download plot (HTML)",
            data=fig.to_html(include_plotlyjs="cdn"),
            file_name="cp_vs_t_plot.html",
            mime="text/html",
        )
    with dl_col2:
        if not plot_df.empty:
            st.download_button(
                f"Download plot data (CSV, {len(plot_df):,} rows)",
                data=plot_df.to_csv(index=False),
                file_name="cp_vs_t_data.csv",
                mime="text/csv",
            )

    st.markdown("#### Read values from the plot")
    inspect_default = 300.0 if not settings["use_celsius"] else 27.0
    inspect_t = st.slider(
        "Inspect Cp at temperature",
        min_value=float(settings["t_min_k"] if not settings["use_celsius"] else settings["t_min_k"] - 273.15),
        max_value=float(settings["t_max_k"] if not settings["use_celsius"] else settings["t_max_k"] - 273.15),
        value=float(inspect_default),
        step=5.0,
        format="%.0f °C" if settings["use_celsius"] else "%.0f K",
    )
    inspect_t_k = inspect_t if not settings["use_celsius"] else inspect_t + 273.15
    inspector_df = build_inspector_table(materials, selected_ids, inspect_t_k, settings["use_celsius"])
    st.dataframe(inspector_df, use_container_width=True, hide_index=True, height=min(400, 38 + 35 * len(inspector_df)))

    sample_temps = [298.0, 400.0, 500.0, 600.0, 773.0]
    sample_df = build_sample_temperature_table(plot_df, sample_temps)
    if not sample_df.empty:
        with st.expander("Cp at key temperatures (298, 400, 500, 600, 773 K)", expanded=len(selected_ids) <= 15):
            st.dataframe(sample_df, use_container_width=True, hide_index=True)

    if warnings:
        with st.expander(f"Warnings ({len(warnings)})", expanded=False):
            for w in warnings:
                st.markdown(f"- {w}")

    if summary:
        with st.expander("Comparison Summary", expanded=False):
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    with st.expander("Material Details", expanded=False):
        for mat_id in selected_ids:
            try:
                mat = get_material_by_id(materials, mat_id)
            except KeyError:
                continue
            st.markdown(f"**{mat['name']}** — `{mat['formula']}`")
            c1, c2, c3 = st.columns(3)
            c1.metric("Category", mat["category"])
            c2.metric("Valid T", f"{mat['t_min_k']:.0f}–{mat['t_max_k']:.0f} K")
            c3.metric("Cp @ 300 K", f"{cp_at_temperature(mat, 300):.1f} J/(kg·K)")
            st.caption(f"Source: {mat['source']}  |  Equation: {mat['equation_type']}")
            st.divider()


def render_ranking_tab(filtered: list[dict], rank_temp_k: float) -> None:
    st.subheader(f"Ranking by Cp at T = {rank_temp_k:.1f} K")
    rows = []
    for mat in filtered:
        try:
            rows.append(
                {
                    "Material": mat["name"],
                    "Formula": mat["formula"],
                    "Category": mat["category"],
                    "Cp (J/kg·K)": round(cp_at_temperature(mat, rank_temp_k), 2),
                    "Source": mat["source"],
                }
            )
        except (ValueError, KeyError):
            continue

    if not rows:
        st.info("No materials to rank.")
        return

    df_rank = pd.DataFrame(rows).sort_values("Cp (J/kg·K)", ascending=False).reset_index(drop=True)
    df_rank.index += 1
    df_rank.index.name = "Rank"
    st.dataframe(df_rank, use_container_width=True)
    st.plotly_chart(build_ranking_chart(df_rank, rank_temp_k), use_container_width=True)


def render_browse_tab(filtered: list[dict]) -> None:
    st.subheader("Full Database")
    df = materials_to_dataframe(filtered)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.plotly_chart(build_category_pie(df), use_container_width=True)


def render_sources_tab(materials: list[dict]) -> None:
    st.subheader("Data Sources & Citations")
    st.markdown(
        f"All **{len(materials)}** materials use thermodynamic coefficients from "
        "the peer-reviewed and engineering sources below."
    )

    st.markdown("### Primary References")
    for src in DATA_SOURCES:
        st.markdown(
            f'<div class="source-card">'
            f'<strong><a href="{src["url"]}" target="_blank">{src["name"]}</a></strong><br>'
            f'<span style="color:#555">{src["description"]}</span></div>',
            unsafe_allow_html=True,
        )

    df_stats = materials_to_dataframe(materials)
    source_counts = (
        df_stats.groupby("source")
        .size()
        .reset_index(name="Material Count")
        .sort_values("Material Count", ascending=False)
    )
    source_counts["Link"] = source_counts["source"].map(
        lambda s: SOURCE_URLS.get(s, "https://webbook.nist.gov/chemistry/")
    )

    st.markdown("### Materials per Source")
    st.dataframe(
        source_counts,
        use_container_width=True,
        hide_index=True,
        column_config={"Link": st.column_config.LinkColumn("Reference URL")},
    )

    st.markdown("### Complete Material–Source Mapping")
    mapping = df_stats[["name", "formula", "category", "source"]].rename(
        columns={"name": "Material", "formula": "Formula", "category": "Category", "source": "Source"}
    )
    st.dataframe(mapping, use_container_width=True, hide_index=True, height=400)
    st.plotly_chart(build_source_bar(source_counts), use_container_width=True)

    st.markdown("### Equations Used")
    st.markdown(
        """
| Equation | Formula | Used For |
|---|---|---|
| **NIST Shomate** | Cp = A + Bt + Ct² + Dt³ + E/t², t = T/1000 | Elements, gases, compounds |
| **Polynomial** | Cp = A + BT + CT² + DT³ (J/kg·K) | Alloys, polymers, ceramics |
        """
    )
