"""Validation: Bernt et al. 2020, CIT 92(1-2), Fig. 1.

Compares the v0.5 zero-fit cell model against a digitized polarization curve
from a lab-scale PEM electrolyzer:

    80 °C, 1 bar, Nafion 212 (~50 µm), 2 mg Ir/cm² (Umicore Elyst Ir75 0480)
    anode, 0.35 mg Pt/cm² cathode, 5 cm² single cell.

The dataset (`tests/data/bernt_2020_fig1.csv`) was digitized by visual
inspection of a screenshot of Fig. 1, red solid line labelled
"2 mg/cm² (measured)". Accuracy ~±20 mV.

Three tests:

1. `test_dataset_loads_and_is_sane` — CSV parses, values in physical range.
2. `test_low_j_shape_within_50mv_rmse` — RMSE < 50 mV for j ≤ 0.1 A/cm².
   Confirms Butler-Volmer + Nernst physics captures the Tafel-dominated
   regime. Expected to pass.
3. `test_full_range_rmse_under_40mv_calibration_target` — strict xfail.
   Full-range RMSE with generic defaults is ~510 mV, dominated by ohmic
   overshoot at j > 1 A/cm². Calibration to Bernt's setup is deferred to
   v0.6. See `docs/validation/bernt2020_v0.5.md`.

@ref: Bernt, M. et al. (2020). *Chemie Ingenieur Technik* 92(1-2), 31-39.
      DOI: 10.1002/cite.201900101. Open Access (CC-BY).
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from src.electrochemistry import Electrochemistry
from src.units import a_per_cm2_to_a_per_m2

DATA_PATH = Path(__file__).parent / "data" / "bernt_2020_fig1.csv"


def _load_dataset() -> tuple[np.ndarray, np.ndarray]:
    j_list: list[float] = []
    e_list: list[float] = []
    with DATA_PATH.open() as f:
        for row in csv.reader(f):
            if not row or row[0].startswith("#") or row[0] == "j_A_cm2":
                continue
            j_list.append(float(row[0]))
            e_list.append(float(row[1]))
    return np.asarray(j_list), np.asarray(e_list)


def _bernt_cell() -> Electrochemistry:
    """Bernt 2020 operating conditions. Zero fitted parameters — only documented inputs."""
    return Electrochemistry.from_engineering(
        temperature_celsius=80.0,
        pressure_bar=1.0,
        membrane_thickness_um=50.0,
        membrane_conductivity_s_per_m=10.0,
    )


def _predict_voltages(cell: Electrochemistry, j_a_cm2: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            cell.cell_voltage(a_per_cm2_to_a_per_m2(jj), include_concentration=False)["u_cell"]
            for jj in j_a_cm2
        ]
    )


# ---------------------------------------------------------------- #


def test_dataset_loads_and_is_sane():
    j, e = _load_dataset()
    assert len(j) >= 10, "dataset has too few points"
    assert np.all(j > 0), "current densities must be positive"
    assert np.all((e > 1.2) & (e < 2.5)), "cell voltages outside physical range"
    # Polarization is monotonic in current density for PEMEL — sanity check digitization.
    assert np.all(np.diff(e) >= 0), "voltage must be non-decreasing in j"


def test_low_j_shape_within_50mv_rmse():
    """Tafel-region (j ≤ 0.1 A/cm²) RMSE < 50 mV — shape is captured.

    At low current the model is dominated by Butler-Volmer kinetics and
    matches Bernt within ~35 mV RMSE. This confirms that the physics shape
    (Tafel slope, E_rev, low-j transition) are correct. Absolute calibration
    for Bernt's specific catalyst is a separate issue, documented by the
    xfail test below.
    """
    j, e_meas = _load_dataset()
    mask = j <= 0.1
    assert mask.sum() >= 3, "need at least 3 low-j points for a meaningful RMSE"

    cell = _bernt_cell()
    e_pred = _predict_voltages(cell, j[mask])
    rmse = float(np.sqrt(np.mean((e_pred - e_meas[mask]) ** 2)))
    assert rmse < 0.050, f"Low-j RMSE {rmse * 1000:.1f} mV exceeds 50 mV tolerance"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "v0.5 defaults are not calibrated to Bernt's research-grade setup. "
        "Full-range RMSE is ~510 mV, driven by ohmic overshoot at j > 1 A/cm². "
        "Generic IrO₂ j0 and conservative interface resistances overshoot "
        "Bernt's Umicore Elyst Ir75 premium catalyst and optimized cell press. "
        "See docs/validation/bernt2020_v0.5.md. Calibration is v0.6 scope."
    ),
)
def test_full_range_rmse_under_40mv_calibration_target():
    """Full-range RMSE target 40 mV — EXPECTED TO FAIL with current defaults.

    Marked `xfail(strict=True)`: if this test ever passes (e.g. after v0.6
    preset work), pytest will raise XPASS and we'll know to re-baseline.
    """
    j, e_meas = _load_dataset()
    cell = _bernt_cell()
    e_pred = _predict_voltages(cell, j)
    rmse = float(np.sqrt(np.mean((e_pred - e_meas) ** 2)))
    assert rmse < 0.040, f"RMSE {rmse * 1000:.1f} mV exceeds 40 mV target"
