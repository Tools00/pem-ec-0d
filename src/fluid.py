"""
Fluid-Modell — Druckabfall im BPP-Flow-Field + Pumpenleistung (v0.5).

Laminare Strömung in rechteckigen Kanälen. PEM-EC-Betrieb sitzt durchgehend
im laminaren Bereich (Re ≈ 10…100 für typ. Flow-Rates 1 mL/min/Kanal), daher
Darcy-Friction-Factor als Funktion des Aspect-Ratios α = d/w nach Shah & London
(1978). Flow-Pattern bestimmt Pfadlänge L: Serpentine läuft durch alle N
Kanäle seriell → lange Schlange, Parallel verteilt auf N Kanäle gleichzeitig.

Alle Einheiten intern SI. Referenzen:
  - Shah, R. K., & London, A. L. (1978). Laminar Flow Forced Convection in
    Ducts. Advances in Heat Transfer, Suppl. 1. Table 42 (f·Re vs α).
  - Kakac, Shah & Aung (1987). Handbook of Single-Phase Convective Heat
    Transfer, Ch. 3. — Bestätigung der f·Re-Korrelation.
  - Barbir (2012) PEM Fuel Cells, Ch. 4.3 — Serpentine-Pfadlängen-Heuristik.

Constants lokal gehalten (keine globalen); physikalische Konstanten aus
src/constants.py werden hier nicht benötigt (Wasser-Dichte/Viskosität als
temperaturabhängige Approximation).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.constants import M_H2O, F

# Shah & London (1978), Table 42 — f·Re für laminare Strömung in rechteckigen
# Kanälen mit Aspect-Ratio α = min(d,w) / max(d,w), d=depth, w=width.
# Stützstellen + lineare Interpolation zwischen ihnen. Quadratischer Kanal
# (α=1.0) ergibt 56.91, kreisrund (α→0 als Limit) 96.
_SHAH_LONDON_F_RE: list[tuple[float, float]] = [
    (1.0, 56.91),
    (0.9, 57.30),
    (0.8, 58.00),
    (0.7, 59.14),
    (0.5, 62.20),
    (0.4, 65.47),
    (0.3, 68.36),
    (0.25, 72.93),
    (0.125, 82.34),
    (0.1, 84.68),
    (0.05, 89.91),
    (0.01, 95.00),
]


def darcy_friction_factor(aspect_ratio: float, reynolds: float) -> float:
    """
    Darcy-Friction-Factor f für laminare Strömung in rechteckigem Kanal.

    Args:
        aspect_ratio: α = min(d, w) / max(d, w), dimensionslos, (0, 1].
        reynolds:     Re = ρ · V · D_h / μ, dimensionslos, > 0.

    Returns:
        Darcy f [–]. Für laminare Strömung gilt f · Re = C(α), also
        f = C(α) / Re.

    @ref: Shah & London (1978) Adv. Heat Transfer Suppl. 1, Table 42.
    @valid-range: α ∈ (0.01, 1.0], Re ∈ (0, ~2000] (laminar).
    """
    if not 0.01 <= aspect_ratio <= 1.0:
        raise ValueError(f"aspect_ratio={aspect_ratio} outside [0.01, 1.0]")
    if reynolds <= 0:
        raise ValueError(f"reynolds={reynolds} must be positive")
    c = _interp_f_re(aspect_ratio)
    return c / reynolds


def _interp_f_re(alpha: float) -> float:
    """Lineare Interpolation zwischen Shah-London-Stützstellen. α-Tabelle ist
    absteigend sortiert; wir clampen an die Extreme."""
    table = _SHAH_LONDON_F_RE
    if alpha >= table[0][0]:
        return table[0][1]
    if alpha <= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        a1, v1 = table[i]
        a2, v2 = table[i + 1]
        if a2 <= alpha <= a1:
            t = (a1 - alpha) / (a1 - a2)
            return v1 + t * (v2 - v1)
    raise AssertionError("unreachable")  # pragma: no cover


# ---------------- Wasser-Eigenschaften (Temperatur-Approximation) ---------------- #


def water_density_kg_m3(temperature_k: float) -> float:
    """
    Dichte von reinem Wasser [kg/m³], lineare Näherung 20–100 °C.

    Fit zweier Stützstellen aus NIST Webbook:
      293.15 K → 998.2 kg/m³, 373.15 K → 958.4 kg/m³
    → ρ(T) ≈ 1144.1 − 0.4975 · T[K]. Abweichung < 0.5 kg/m³ im Fit-Bereich.

    @ref: NIST Webbook (https://webbook.nist.gov), Saturated Water Properties.
    @valid-range: T ∈ [283, 383] K. Für PEM-EC-Betrieb (50–90 °C) hinreichend.
    """
    if not 283.0 <= temperature_k <= 383.0:
        raise ValueError(f"temperature_k={temperature_k} outside [283, 383] K")
    return 1144.1 - 0.4975 * temperature_k


def water_viscosity_pa_s(temperature_k: float) -> float:
    """
    Dynamische Viskosität von Wasser [Pa·s].

    Vogel-Fulcher-Tammann-Fit (vereinfacht): μ = A · exp(B/(T-C)).
    A=2.414e-5, B=247.8, C=140.0 (Seeton 2006, Int. J. Thermophys. 27, 1327).

    @valid-range: T ∈ [273, 373] K.
    """
    if not 273.0 <= temperature_k <= 383.0:
        raise ValueError(f"temperature_k={temperature_k} outside [273, 383] K")
    return 2.414e-5 * 10 ** (247.8 / (temperature_k - 140.0))


# ---------------- Geometrie-Hilfen ---------------- #


def hydraulic_diameter_m(channel_width_m: float, channel_depth_m: float) -> float:
    """D_h = 4·A / P_wetted für rechteckigen Kanal [m]."""
    w, d = channel_width_m, channel_depth_m
    if w <= 0 or d <= 0:
        raise ValueError(f"channel dims must be positive: w={w}, d={d}")
    return 2.0 * w * d / (w + d)


def n_channels_parallel(active_edge_m: float, channel_pitch_m: float) -> int:
    """Anzahl parallel geschalteter Kanäle im Flow-Field (entlang der Edge)."""
    return max(1, int(active_edge_m / channel_pitch_m))


def flow_path_length_m(
    flow_pattern: str, active_width_m: float, active_height_m: float, channel_pitch_m: float
) -> float:
    """
    Kanal-Pfadlänge L [m] abhängig vom Flow-Pattern.

    - serpentine: L ≈ active_height · (active_width / pitch)
                  (eine Schlange, alle N Passes seriell)
    - parallel:   L ≈ active_height
                  (Flow verteilt auf N parallele gerade Kanäle)
    - interdigitated: wird in v0.5 **wie parallel** approximiert;
                  echtes Modell (Land-Crossing dominiert) → v0.6.

    @ref: Barbir (2012) Ch. 4.3.
    """
    if active_width_m <= 0 or active_height_m <= 0 or channel_pitch_m <= 0:
        raise ValueError("active/channel dims must be positive")
    if flow_pattern == "serpentine":
        n = max(1, int(active_width_m / channel_pitch_m))
        return active_height_m * n
    if flow_pattern in ("parallel", "interdigitated"):
        return active_height_m
    raise ValueError(f"unknown flow_pattern {flow_pattern!r}")


# ---------------- Hauptfunktion: ΔP ---------------- #


@dataclass(frozen=True)
class PressureDropResult:
    """Ergebnis-Bundle eines ΔP-Laufs. Alle SI-Einheiten."""

    dp_pa: float  # Druckabfall [Pa]
    reynolds: float  # Re im Kanal [–]
    velocity_m_s: float  # Mittelgeschwindigkeit [m/s]
    hydraulic_diameter_m: float  # D_h [m]
    n_channels: int  # parallel Kanäle
    path_length_m: float  # Einzelkanal-Pfadlänge L [m]
    friction_factor: float  # Darcy f [–]


def pressure_drop(
    *,
    flow_pattern: str,
    channel_width_m: float,
    channel_depth_m: float,
    channel_pitch_m: float,
    active_width_m: float,
    active_height_m: float,
    volumetric_flow_per_cell_m3_s: float,
    temperature_k: float,
) -> PressureDropResult:
    """
    Druckabfall im Flow-Field einer Zelle.

    Formel: ΔP = f · (L / D_h) · (ρ · V² / 2)         (Darcy-Weisbach)

    Water-Flow wird gleichmäßig auf alle parallelen Kanäle verteilt (parallel,
    interdigitated) bzw. durchläuft alle Kanäle seriell (serpentine).

    @ref: Darcy-Weisbach; f via Shah & London (1978).
    @valid-range: Re < 2000 (laminar). Bei Re > 2000 wird ValueError geworfen;
                  turbulente Strömung ist für PEM-EC untypisch und braucht ein
                  anderes Korrelationsmodell.
    """
    rho = water_density_kg_m3(temperature_k)
    mu = water_viscosity_pa_s(temperature_k)
    dh = hydraulic_diameter_m(channel_width_m, channel_depth_m)

    if flow_pattern == "serpentine":
        # Alle Kanäle seriell durchflossen → Q_channel = Q_cell
        q_channel = volumetric_flow_per_cell_m3_s
        n = 1
    else:
        # parallel / interdigitated: Flow auf N Kanäle aufgeteilt
        n = n_channels_parallel(active_width_m, channel_pitch_m)
        q_channel = volumetric_flow_per_cell_m3_s / n

    a_channel = channel_width_m * channel_depth_m
    velocity = q_channel / a_channel
    re = rho * velocity * dh / mu

    if re > 2000.0:
        raise ValueError(
            f"Re={re:.0f} exceeds laminar regime (2000). "
            f"Turbulent correlation not implemented in v0.5."
        )

    alpha = min(channel_width_m, channel_depth_m) / max(channel_width_m, channel_depth_m)
    f = darcy_friction_factor(alpha, max(re, 1e-6))
    l_path = flow_path_length_m(flow_pattern, active_width_m, active_height_m, channel_pitch_m)
    dp = f * (l_path / dh) * (rho * velocity**2 / 2.0)

    return PressureDropResult(
        dp_pa=dp,
        reynolds=re,
        velocity_m_s=velocity,
        hydraulic_diameter_m=dh,
        n_channels=n,
        path_length_m=l_path,
        friction_factor=f,
    )


# ---------------- Pumpenleistung ---------------- #


def pump_power_w(dp_pa: float, volumetric_flow_m3_s: float, eta_pump: float) -> float:
    """
    Hydraulische Pumpenleistung [W].

    P_pump = ΔP · Q / η_pump

    η_pump deckt mechanische + hydraulische Verluste ab (typ. 0.3–0.7 für
    kommerzielle Membran- oder Zentrifugalpumpen im EC-Bereich).
    """
    if dp_pa < 0 or volumetric_flow_m3_s < 0:
        raise ValueError("dp_pa and flow must be non-negative")
    if not 0.0 < eta_pump <= 1.0:
        raise ValueError(f"eta_pump={eta_pump} must be in (0, 1]")
    return dp_pa * volumetric_flow_m3_s / eta_pump


# ---------------- Stoichiometrische Wasserzufuhr ---------------- #


def stoichiometric_water_flow_m3_s(
    current_a: float,
    stoich_ratio: float,
    temperature_k: float,
) -> float:
    """
    Wasserzufuhr pro Zelle [m³/s] bei gegebener Stöchiometrie.

    ṁ_stoich = I / (2 · F) · M_H2O        [kg/s]    (2 e⁻ pro H2O-Molekül)
    Q         = λ · ṁ_stoich / ρ(T)        [m³/s]

    λ (stoich_ratio) typisch 10–200 im EC-Betrieb, oft 50–100 für adequate
    Zwei-Phasen-Strömung und Wärmeabfuhr.

    @ref: Carmo et al. (2013) IJHE 38(12), §3.2 — λ-Bereich Literatur.
    """
    if current_a < 0 or stoich_ratio <= 0:
        raise ValueError("current and stoich_ratio must be positive")
    m_dot_stoich = current_a / (2.0 * F) * M_H2O
    rho = water_density_kg_m3(temperature_k)
    return stoich_ratio * m_dot_stoich / rho
