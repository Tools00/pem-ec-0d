"""
Unit conversions between SI (internal) and engineering units (UI display).

Rule: all physics modules use SI. Only the UI layer or user-facing helpers
call these functions. Round-trip through a converter MUST be identity
(tested in tests/test_units.py).
"""

from .constants import P_BAR, T_ZERO_CELSIUS

# -------------------- Pressure -------------------- #


def bar_to_pa(p_bar: float) -> float:
    """Convert pressure from bar to Pascal (SI)."""
    return p_bar * P_BAR


def pa_to_bar(p_pa: float) -> float:
    """Convert pressure from Pascal (SI) to bar."""
    return p_pa / P_BAR


# -------------------- Temperature -------------------- #


def celsius_to_kelvin(t_celsius: float) -> float:
    """Convert temperature from Celsius to Kelvin (SI)."""
    return t_celsius + T_ZERO_CELSIUS


def kelvin_to_celsius(t_kelvin: float) -> float:
    """Convert temperature from Kelvin (SI) to Celsius."""
    return t_kelvin - T_ZERO_CELSIUS


# -------------------- Current density -------------------- #


def a_per_cm2_to_a_per_m2(j_a_cm2: float) -> float:
    """Convert current density from A/cm² to A/m² (SI). 1 A/cm² = 10,000 A/m²."""
    return j_a_cm2 * 1e4


def a_per_m2_to_a_per_cm2(j_a_m2: float) -> float:
    """Convert current density from A/m² (SI) to A/cm²."""
    return j_a_m2 / 1e4


# -------------------- Area-specific resistance -------------------- #


def ohm_cm2_to_ohm_m2(r_ohm_cm2: float) -> float:
    """Convert area-specific resistance from Ω·cm² to Ω·m² (SI). 1 Ω·cm² = 1e-4 Ω·m²."""
    return r_ohm_cm2 * 1e-4


def ohm_m2_to_ohm_cm2(r_ohm_m2: float) -> float:
    """Convert area-specific resistance from Ω·m² (SI) to Ω·cm²."""
    return r_ohm_m2 / 1e-4


# -------------------- Length -------------------- #


def um_to_m(l_um: float) -> float:
    """Convert length from micrometers to meters (SI)."""
    return l_um * 1e-6


def m_to_um(l_m: float) -> float:
    """Convert length from meters (SI) to micrometers."""
    return l_m * 1e6


def cm_to_m(l_cm: float) -> float:
    """Convert length from centimeters to meters (SI)."""
    return l_cm * 1e-2


def m_to_cm(l_m: float) -> float:
    """Convert length from meters (SI) to centimeters."""
    return l_m * 1e2


# -------------------- Area -------------------- #


def cm2_to_m2(a_cm2: float) -> float:
    """Convert area from cm² to m² (SI). 1 cm² = 1e-4 m²."""
    return a_cm2 * 1e-4


def m2_to_cm2(a_m2: float) -> float:
    """Convert area from m² (SI) to cm²."""
    return a_m2 / 1e-4


# -------------------- Specific energy -------------------- #


def j_per_kg_to_kwh_per_kg(e_j_kg: float) -> float:
    """Convert specific energy from J/kg (SI) to kWh/kg. 1 kWh = 3.6e6 J."""
    return e_j_kg / 3.6e6


def kwh_per_kg_to_j_per_kg(e_kwh_kg: float) -> float:
    """Convert specific energy from kWh/kg to J/kg (SI)."""
    return e_kwh_kg * 3.6e6
