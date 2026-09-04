"""Load and query the materials database."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "materials.json"


def load_materials() -> list[dict[str, Any]]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def materials_to_dataframe(materials: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": m["id"],
                "name": m["name"],
                "formula": m["formula"],
                "category": m["category"],
                "source": m["source"],
                "t_min_k": m["t_min_k"],
                "t_max_k": m["t_max_k"],
                "molar_mass_g_mol": m.get("molar_mass_g_mol"),
                "phase_transition_k": m.get("phase_transition_k"),
                "phase_transition_label": m.get("phase_transition_label"),
            }
            for m in materials
        ]
    )


def get_categories(materials: list[dict[str, Any]]) -> list[str]:
    return sorted({m["category"] for m in materials})


def get_material_by_id(materials: list[dict[str, Any]], material_id: str) -> dict[str, Any]:
    for m in materials:
        if m["id"] == material_id:
            return m
    raise KeyError(f"Material not found: {material_id}")


def filter_materials(
    materials: list[dict[str, Any]],
    category: str | None = None,
    search: str = "",
) -> list[dict[str, Any]]:
    result = materials
    if category and category != "All":
        result = [m for m in result if m["category"] == category]
    if search.strip():
        q = search.strip().lower()
        result = [
            m
            for m in result
            if q in m["name"].lower()
            or q in m["formula"].lower()
            or q in m["category"].lower()
            or q in m["source"].lower()
        ]
    return result
