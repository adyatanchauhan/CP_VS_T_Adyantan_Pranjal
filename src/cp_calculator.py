"""Specific heat capacity (Cp) calculation engines for engineering materials."""

from __future__ import annotations

import numpy as np
from typing import Any


def shomate_cp(temperature_k: np.ndarray, coeffs: list[float]) -> np.ndarray:
    """
    NIST Shomate equation for molar Cp in J/(mol·K).

    Cp = A + B*t + C*t² + D*t³ + E/t²
    where t = T / 1000 and T is in Kelvin.
    """
    t = temperature_k / 1000.0
    a, b, c, d, e = coeffs
    return a + b * t + c * t**2 + d * t**3 + e / t**2


def polynomial_cp_kg(temperature_k: np.ndarray, coeffs: list[float]) -> np.ndarray:
    """
    Engineering polynomial for mass-specific Cp in J/(kg·K).

    Cp = A + B*T + C*T² + D*T³
    """
    a, b, c, d = coeffs
    return a + b * temperature_k + c * temperature_k**2 + d * temperature_k**3


def nasa_cp_molar(temperature_k: np.ndarray, coeffs: list[float]) -> np.ndarray:
    """
    NASA Glenn polynomial (7 coefficients) for molar Cp in J/(mol·K).

    Cp/R = a1 + a2*T + a3*T² + a4*T³ + a5*T⁴
    """
    r_gas = 8.314462618  # J/(mol·K)
    a1, a2, a3, a4, a5 = coeffs
    t = temperature_k
    cp_over_r = a1 + a2 * t + a3 * t**2 + a4 * t**3 + a5 * t**4
    return cp_over_r * r_gas


def calculate_cp(
    temperature_k: np.ndarray,
    material: dict[str, Any],
) -> np.ndarray:
    """Calculate mass-specific Cp in J/(kg·K) for a material."""
    eq_type = material["equation_type"]
    coeffs = material["coefficients"]
    molar_mass = material.get("molar_mass_g_mol")

    if eq_type == "shomate":
        cp_molar = shomate_cp(temperature_k, coeffs)
        if molar_mass is None or molar_mass <= 0:
            raise ValueError(f"Molar mass required for Shomate: {material['name']}")
        return cp_molar * 1000.0 / molar_mass

    if eq_type == "polynomial_kg":
        return polynomial_cp_kg(temperature_k, coeffs)

    if eq_type == "nasa":
        cp_molar = nasa_cp_molar(temperature_k, coeffs)
        if molar_mass is None or molar_mass <= 0:
            raise ValueError(f"Molar mass required for NASA: {material['name']}")
        return cp_molar * 1000.0 / molar_mass

    raise ValueError(f"Unknown equation type: {eq_type}")


def validate_temperature_range(
    t_min: float,
    t_max: float,
    valid_min: float,
    valid_max: float,
) -> list[str]:
    """Return warning messages when user range exceeds valid data range."""
    warnings: list[str] = []
    if t_min < valid_min:
        warnings.append(
            f"Minimum temperature {t_min:.1f} K is below valid range "
            f"({valid_min:.1f} K). Extrapolation may be inaccurate."
        )
    if t_max > valid_max:
        warnings.append(
            f"Maximum temperature {t_max:.1f} K exceeds valid range "
            f"({valid_max:.1f} K). Extrapolation may be inaccurate."
        )
    return warnings


def cp_at_temperature(material: dict[str, Any], temperature_k: float) -> float:
    """Single-point Cp evaluation in J/(kg·K), clamped to valid range."""
    t = float(np.clip(temperature_k, material["t_min_k"], material["t_max_k"]))
    val = float(calculate_cp(np.array([t]), material)[0])
    return max(val, 0.0)
