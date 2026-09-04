"""Interactive Cp vs T Database — main entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_materials
from src.ui import (
    render_browse_tab,
    render_header,
    render_material_panel,
    render_plot_tab,
    render_ranking_tab,
    render_sidebar,
    render_sources_tab,
    setup_page,
)


@st.cache_data
def get_materials():
    return load_materials()


def main() -> None:
    setup_page()
    materials = get_materials()
    render_header(materials)
    settings = render_sidebar()

    col_left, col_right = st.columns([0.9, 3.1])

    with col_left:
        filtered, selected_ids = render_material_panel(materials)

    with col_right:
        render_plot_tab(materials, selected_ids, settings)

        tab_rank, tab_browse, tab_sources = st.tabs(["Ranking", "Browse", "Data Sources"])
        with tab_rank:
            render_ranking_tab(filtered, settings["rank_temp_k"])
        with tab_browse:
            render_browse_tab(filtered)
        with tab_sources:
            render_sources_tab(materials)


if __name__ == "__main__":
    main()
