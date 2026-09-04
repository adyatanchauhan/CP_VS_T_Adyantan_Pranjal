"""Plotly chart builders for Cp vs T visualisation."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.cp_calculator import calculate_cp, cp_at_temperature, validate_temperature_range

# Vibrant palette tuned for dark backgrounds — each material gets its own color.
VIVID_PALETTE = (
    px.colors.qualitative.Alphabet
    + px.colors.qualitative.Dark24
    + px.colors.qualitative.Light24
    + px.colors.qualitative.Vivid
    + px.colors.qualitative.Set3
    + px.colors.qualitative.Plotly
    + px.colors.qualitative.G10
    + px.colors.qualitative.T10
    + px.colors.qualitative.Alphabet_r
)

DARK_THEME = {
    "paper_bgcolor": "#12151c",
    "plot_bgcolor": "#0d1117",
    "gridcolor": "#2a3140",
    "linecolor": "#8b9cb3",
    "title_color": "#e8edf5",
    "legend_color": "#c5d0de",
    "spikecolor": "#4ecdc4",
    "annotation_color": "#9aa8bc",
}

CATEGORY_COLORS = {
    "Gases": "#ff6b6b",
    "Metals and alloys": "#54a0ff",
    "Ceramics": "#c56cf0",
    "Semiconductors": "#2ed573",
    "Polymers": "#ffa502",
    "Glasses": "#1dd1a1",
    "Refractories": "#ff6348",
    "Composites": "#70a1ff",
    "Other": "#a4b0be",
}


def _material_line_color(index: int) -> str:
    """Return a distinct bright color for each material trace."""
    return VIVID_PALETTE[index % len(VIVID_PALETTE)]

DisplayMode = Literal["absolute", "normalized", "delta"]


def _safe_cp_curve(temperatures_k: np.ndarray, mat: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Return temperatures and Cp values only within the material's valid range."""
    valid_min = float(mat["t_min_k"])
    valid_max = float(mat["t_max_k"])
    mask = (temperatures_k >= valid_min) & (temperatures_k <= valid_max)
    t_valid = temperatures_k[mask]
    if len(t_valid) == 0:
        return np.array([]), np.array([])
    cp_valid = calculate_cp(t_valid, mat)
    cp_valid = np.clip(cp_valid, 0, None)
    return t_valid, cp_valid


def _transform_y(
    cp_plot: np.ndarray,
    display_mode: DisplayMode,
    t_valid: np.ndarray,
    mat: dict[str, Any],
    show_molar: bool,
) -> np.ndarray:
    """Transform Cp values for clearer multi-material comparison."""
    if display_mode == "absolute" or len(cp_plot) == 0:
        return cp_plot

    ref_t = float(np.clip(300.0, mat["t_min_k"], mat["t_max_k"]))
    if show_molar and mat.get("molar_mass_g_mol"):
        ref_cp = float(calculate_cp(np.array([ref_t]), mat)[0] * mat["molar_mass_g_mol"] / 1000.0)
    else:
        ref_cp = float(calculate_cp(np.array([ref_t]), mat)[0])

    if display_mode == "normalized":
        return cp_plot / ref_cp if ref_cp > 0 else cp_plot
    # delta from first plotted point
    return cp_plot - cp_plot[0]


def _y_label(show_molar: bool, display_mode: DisplayMode) -> str:
    if display_mode == "normalized":
        return "Cp / Cp(300 K)"
    if display_mode == "delta":
        return "ΔCp from T<sub>min</sub> (J kg⁻¹ K⁻¹)" if not show_molar else "ΔCp from T<sub>min</sub> (J mol⁻¹ K⁻¹)"
    return "Cp (J mol⁻¹ K⁻¹)" if show_molar else "Cp (J kg⁻¹ K⁻¹)"


def build_cp_plot(
    materials: list[dict[str, Any]],
    selected_ids: list[str],
    t_min_k: float,
    t_max_k: float,
    n_points: int,
    use_celsius: bool,
    show_molar: bool,
    show_phase_transitions: bool,
    display_mode: DisplayMode = "absolute",
    log_y: bool = False,
    color_by_category: bool = False,
) -> tuple[go.Figure, list[str], list[dict], pd.DataFrame]:
    """Build the main Cp-T comparison figure and return warnings, summary, and plot data."""
    temperatures_k = np.linspace(t_min_k, t_max_k, n_points)
    x_label = "Temperature (°C)" if use_celsius else "Temperature (K)"
    y_label = _y_label(show_molar, display_mode)

    fig = go.Figure()
    warnings: list[str] = []
    summary: list[dict] = []
    plot_rows: list[dict] = []
    mat_map = {m["id"]: m for m in materials}
    has_data = False
    n_selected = len(selected_ids)
    line_width = 2.5 if n_selected <= 10 else (1.8 if n_selected <= 40 else 1.0)
    many_traces = n_selected > 15

    for i, mat_id in enumerate(selected_ids):
        if mat_id not in mat_map:
            warnings.append(f"**{mat_id}**: material not found in database.")
            continue

        mat = mat_map[mat_id]
        color = (
            CATEGORY_COLORS.get(mat["category"], "#a4b0be")
            if color_by_category
            else _material_line_color(i)
        )

        for msg in validate_temperature_range(t_min_k, t_max_k, mat["t_min_k"], mat["t_max_k"]):
            warnings.append(f"**{mat['name']}**: {msg}")

        t_valid, cp_valid = _safe_cp_curve(temperatures_k, mat)
        if len(t_valid) == 0:
            warnings.append(
                f"**{mat['name']}**: no overlap between your T range "
                f"({t_min_k:.0f}–{t_max_k:.0f} K) and valid range "
                f"({mat['t_min_k']:.0f}–{mat['t_max_k']:.0f} K)."
            )
            continue

        if show_molar and mat.get("molar_mass_g_mol"):
            cp_plot = cp_valid * mat["molar_mass_g_mol"] / 1000.0
        else:
            cp_plot = cp_valid

        cp_plot = _transform_y(cp_plot, display_mode, t_valid, mat, show_molar)
        x_plot = t_valid - 273.15 if use_celsius else t_valid
        has_data = True

        temp_unit = "°C" if use_celsius else "K"
        if display_mode == "absolute":
            cp_fmt = "%{y:.2f} J/mol·K" if show_molar else "%{y:.1f} J/kg·K"
        elif display_mode == "normalized":
            cp_fmt = "%{y:.4f} (ratio)"
        else:
            cp_fmt = "%{y:.2f} ΔCp"

        fig.add_trace(
            go.Scatter(
                x=x_plot,
                y=cp_plot,
                mode="lines",
                name=mat["name"],
                legendgroup=mat["category"] if color_by_category else None,
                line=dict(width=line_width, color=color),
                connectgaps=False,
                hovertemplate=(
                    f"<b>{mat['name']}</b> ({mat['formula']})<br>"
                    f"Category: {mat['category']}<br>"
                    f"T: %{{x:.1f}} {temp_unit}<br>"
                    f"Cp: {cp_fmt}<br>"
                    f"Source: {mat['source']}<extra></extra>"
                ),
            )
        )

        for y_val, t_k, cp_raw in zip(cp_plot, t_valid, cp_valid):
            plot_rows.append(
                {
                    "Material": mat["name"],
                    "Formula": mat["formula"],
                    "Category": mat["category"],
                    "Temperature_K": round(float(t_k), 2),
                    "Temperature_C": round(float(t_k) - 273.15, 2),
                    "Cp_J_kg_K": round(float(cp_raw), 4),
                    "Plotted_Y": round(float(y_val), 6),
                    "Display_Mode": display_mode,
                    "Source": mat["source"],
                }
            )

        if show_phase_transitions and mat.get("phase_transition_k"):
            pt = float(mat["phase_transition_k"])
            if t_min_k <= pt <= t_max_k:
                pt_x = pt - 273.15 if use_celsius else pt
                fig.add_vline(
                    x=pt_x,
                    line_dash="dot",
                    line_color=color,
                    line_width=1.5,
                    annotation_text=mat.get("phase_transition_label", "Phase change"),
                    annotation_position="top right",
                    annotation_font_size=10,
                )

        try:
            cp_300 = cp_at_temperature(mat, 300.0)
        except (ValueError, FloatingPointError):
            cp_300 = float("nan")

        summary.append(
            {
                "Material": mat["name"],
                "Formula": mat["formula"],
                "Category": mat["category"],
                "Cp @ 300 K (J/kg·K)": round(cp_300, 1) if cp_300 == cp_300 else "N/A",
                "Valid T (K)": f"{mat['t_min_k']:.0f}–{mat['t_max_k']:.0f}",
                "Source": mat["source"],
            }
        )

    if not has_data:
        fig.add_annotation(
            text="No data in selected temperature range — adjust T min/max in sidebar",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=DARK_THEME["annotation_color"]),
        )

    hover_mode = "closest" if many_traces else "x unified"
    axis_font = dict(color=DARK_THEME["linecolor"])
    yaxis_cfg: dict[str, Any] = dict(
        title=dict(text=y_label, font=axis_font),
        tickfont=axis_font,
        showgrid=True,
        gridcolor=DARK_THEME["gridcolor"],
        zeroline=display_mode == "delta",
        zerolinecolor="#3d4a5c",
        showline=True,
        linewidth=1.5,
        linecolor=DARK_THEME["linecolor"],
        type="log" if log_y and display_mode == "absolute" else "linear",
    )
    if display_mode == "absolute" and not log_y:
        yaxis_cfg["rangemode"] = "normal"

    fig.update_layout(
        title=dict(
            text=f"Cp vs Temperature — {n_selected} material{'s' if n_selected != 1 else ''}, {n_points} points each",
            font=dict(size=18, color=DARK_THEME["title_color"]),
            x=0.5,
        ),
        xaxis=dict(
            title=dict(text=x_label, font=axis_font),
            tickfont=axis_font,
            showgrid=True,
            gridcolor=DARK_THEME["gridcolor"],
            zeroline=False,
            showline=True,
            linewidth=1.5,
            linecolor=DARK_THEME["linecolor"],
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikecolor=DARK_THEME["spikecolor"],
            spikethickness=1,
        ),
        yaxis=yaxis_cfg,
        template="plotly_dark",
        hovermode=hover_mode,
        hoverlabel=dict(bgcolor="#1e2530", font_color="#e8edf5", bordercolor="#4ecdc4"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10 if many_traces else 12, color=DARK_THEME["legend_color"]),
            bgcolor="rgba(18, 21, 28, 0.85)",
        ),
        height=580 if many_traces else 550,
        margin=dict(t=90, b=60, l=70, r=20),
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
    )

    plot_df = pd.DataFrame(plot_rows)
    return fig, warnings, summary, plot_df


def build_inspector_table(
    materials: list[dict[str, Any]],
    selected_ids: list[str],
    inspect_t_k: float,
    use_celsius: bool,
) -> pd.DataFrame:
    """Return Cp for each selected material at a single inspection temperature."""
    mat_map = {m["id"]: m for m in materials}
    rows = []
    for mat_id in selected_ids:
        mat = mat_map.get(mat_id)
        if not mat:
            continue
        t_clamped = float(np.clip(inspect_t_k, mat["t_min_k"], mat["t_max_k"]))
        in_range = mat["t_min_k"] <= inspect_t_k <= mat["t_max_k"]
        try:
            cp = cp_at_temperature(mat, inspect_t_k)
        except (ValueError, FloatingPointError):
            cp = float("nan")
        rows.append(
            {
                "Material": mat["name"],
                "Formula": mat["formula"],
                "Category": mat["category"],
                "T (K)": round(inspect_t_k, 1),
                "T (°C)": round(inspect_t_k - 273.15, 1),
                "Cp (J/kg·K)": round(cp, 2) if cp == cp else None,
                "In valid range": "Yes" if in_range else f"No (clamped to {t_clamped:.0f} K)",
                "Source": mat["source"],
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Cp (J/kg·K)", ascending=False, na_position="last")
    return df


def build_sample_temperature_table(
    plot_df: pd.DataFrame,
    sample_temps_k: list[float],
) -> pd.DataFrame:
    """Pivot Cp values at a few key temperatures for easy reading."""
    if plot_df.empty:
        return pd.DataFrame()

    rows = []
    for mat, grp in plot_df.groupby("Material"):
        row: dict[str, Any] = {"Material": mat, "Formula": grp["Formula"].iloc[0], "Category": grp["Category"].iloc[0]}
        for t_k in sample_temps_k:
            nearest = grp.iloc[(grp["Temperature_K"] - t_k).abs().argsort()[:1]]
            if not nearest.empty:
                label = f"Cp @ {t_k:.0f} K"
                row[label] = nearest["Cp_J_kg_K"].iloc[0]
        rows.append(row)
    return pd.DataFrame(rows)


def build_ranking_chart(df_rank: pd.DataFrame, rank_temp_k: float) -> go.Figure:
    fig = px.bar(
        df_rank.head(20),
        x="Material",
        y="Cp (J/kg·K)",
        color="Category",
        title=f"Top 20 Materials by Cp at {rank_temp_k:.0f} K",
        template="plotly_white",
    )
    fig.update_layout(xaxis_tickangle=-45, height=400)
    return fig


def build_category_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    return px.pie(counts, names="Category", values="Count", title="Materials by Category", hole=0.35)


def build_source_bar(source_counts: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        source_counts,
        x="source",
        y="Material Count",
        title="Number of Materials from Each Source",
        template="plotly_white",
        color_discrete_sequence=["#2e86ab"],
    )
    fig.update_layout(xaxis_tickangle=-30, height=350)
    return fig
