"""Statistical validation: Zimmer et al. 2026, J. Electrochem. Soc., Fig. 1c.

Compares the v0.5 zero-fit cell model against a filtered, aggregated literature
dataset (Nafion N115 + 80 °C) spanning >127 peer-reviewed publications (2006-2024).
Zimmer et al. report cell voltage as mean ± std dev plus min/max envelope at
five benchmark current densities: 0.2, 0.5, 1.0, 1.5, 2.0 A/cm².

Why this validation is methodologically stronger than single-paper validation:

  Zimmer explicitly document that "cell voltages reported at the same current
  density can vary by as much as 1.5 V, with standard deviations often exceeding
  500 mV" across the unfiltered corpus. Even after filtering to fixed membrane
  and temperature, the min/max band spans ~0.3-0.8 V. A single-paper RMSE
  cannot distinguish "model broken" from "we picked a non-average paper".
  An envelope-based test can.

Three tests:

1. `test_dataset_loads_and_is_sane`      — CSV parses, values physical.
2. `test_model_within_literature_envelope` — model prediction at each of the
   5 benchmark j lands inside [E_min, E_max]. PASS expected — this is a real
   zero-fit validation against the full literature spread.
3. `test_model_within_one_sigma_band`    — strict xfail. Model lands outside
   mean ± 1σ at 4 of 5 benchmark points; RMSE vs mean ~210 mV; mean bias
   +175 mV (model runs hot vs literature mean, consistent with the overshoot
   already documented against Bernt 2020).

The xfail target is the v0.6 scope: add a catalyst-preset system (generic vs
premium-calibrated) and drop defaults closer to literature mean.

@ref: Zimmer, S. et al. (2026). "Data Mining for Enhanced PEM Electrolysis."
      J. Electrochem. Soc. 173, 024503. DOI: 10.1149/1945-7111/ae335e.
      Open Access (CC-BY 4.0).
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from src.electrochemistry import Electrochemistry
from src.units import a_per_cm2_to_a_per_m2

DATA_PATH = Path(__file__).parent / "data" / "zimmer_2026_fig1c.csv"


def _load_dataset() -> dict[str, np.ndarray]:
    j, e_mean, e_std, e_min, e_max = [], [], [], [], []
    with DATA_PATH.open() as f:
        for row in csv.reader(f):
            if not row or row[0].startswith("#") or row[0] == "j_A_cm2":
                continue
            j.append(float(row[0]))
            e_mean.append(float(row[1]))
            e_std.append(float(row[2]))
            e_min.append(float(row[3]))
            e_max.append(float(row[4]))
    return {
        "j": np.asarray(j),
        "E_mean": np.asarray(e_mean),
        "E_std": np.asarray(e_std),
        "E_min": np.asarray(e_min),
        "E_max": np.asarray(e_max),
    }


def _n115_80c_cell() -> Electrochemistry:
    """Zimmer Fig. 1c filter: Nafion N115 (~127 µm) + 80 °C + 1 bar.

    Zero fitted parameters — only documented filter conditions become inputs.
    """
    return Electrochemistry.from_engineering(
        temperature_celsius=80.0,
        pressure_bar=1.0,
        membrane_thickness_um=127.0,
        membrane_conductivity_s_per_m=10.0,
    )


def _predict(cell: Electrochemistry, j_a_cm2: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            cell.cell_voltage(a_per_cm2_to_a_per_m2(jj), include_concentration=False)["u_cell"]
            for jj in j_a_cm2
        ]
    )


# ---------------------------------------------------------------- #


def test_dataset_loads_and_is_sane():
    d = _load_dataset()
    assert len(d["j"]) == 5, "Zimmer Fig. 1c has 5 benchmark points"
    assert np.all(d["j"] > 0)
    assert np.all(d["E_std"] > 0), "std must be positive"
    assert np.all(d["E_min"] < d["E_mean"]), "min must be below mean"
    assert np.all(d["E_mean"] < d["E_max"]), "mean must be below max"
    # Monotonic in j:
    assert np.all(np.diff(d["E_mean"]) > 0)


def test_model_within_literature_envelope():
    """Model prediction at each benchmark j lands inside [E_min, E_max].

    This is the core validation: zero-fit model must stay within the full
    literature envelope. Passing means the v0.5 model is *literature-consistent*
    across the N115 + 80 °C corpus. Failing at any j would indicate the model
    is outside the published range — a structural red flag.
    """
    d = _load_dataset()
    cell = _n115_80c_cell()
    e_pred = _predict(cell, d["j"])

    for ji, ep, emin, emax in zip(d["j"], e_pred, d["E_min"], d["E_max"], strict=True):
        assert emin <= ep <= emax, (
            f"j={ji} A/cm²: E_pred={ep:.3f} V outside literature envelope "
            f"[{emin:.3f}, {emax:.3f}] V"
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "v0.5 defaults (Carmo 2013 generic commercial) run ~175 mV hot vs the "
        "Zimmer 2026 filtered-literature mean at N115 + 80 °C. RMSE vs mean "
        "~210 mV, pushing the model outside mean ± 1σ at 4 of 5 benchmark j. "
        "Model stays inside min/max envelope (see passing test above). "
        "Calibration path is v0.6 scope — catalyst-preset system with "
        "independently-derived kinetic parameters. "
        "See docs/validation/zimmer2026_v0.5.md."
    ),
)
def test_model_within_one_sigma_band():
    """Model lands within mean ± 1σ at every benchmark j — EXPECTED TO FAIL.

    Strict xfail: if v0.6 calibration tightens the fit, pytest will raise XPASS
    and force a re-baseline. That is intentional — we want an explicit bump
    when the improvement lands.
    """
    d = _load_dataset()
    cell = _n115_80c_cell()
    e_pred = _predict(cell, d["j"])

    violations = []
    for ji, ep, mu, sigma in zip(d["j"], e_pred, d["E_mean"], d["E_std"], strict=True):
        if abs(ep - mu) > sigma:
            violations.append(
                f"  j={ji} A/cm²: E_pred={ep:.3f} V, mean={mu:.3f} ± {sigma:.2f} V, "
                f"Δ={(ep - mu) * 1000:+.0f} mV"
            )
    if violations:
        pytest.fail("Model outside ±1σ at:\n" + "\n".join(violations))
