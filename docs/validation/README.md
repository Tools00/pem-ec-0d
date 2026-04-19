# Validation

## MVP validation (implemented)

1. **Tafel-slope identity.** The fitted slope of η_act vs log10(j) at high
   current densities must match the analytical b = 2.303·R·T/(α·F) within
   0.5 %. Implemented in `tests/test_electrochemistry.py::test_tafel_slope_matches_analytical`.

2. **Nernst temperature coefficient.** dE_rev/dT at fixed pressure must match
   -0.846 mV/K.

3. **Nernst pressure dependence.** E_rev must increase with operating pressure.

4. **Monotonicity of U_cell.** Cell voltage must strictly increase with current
   density over the operating range.

5. **Plausible operating range.** At 80 °C, 10 bar, 1 A/cm², U_cell ∈ [1.6, 2.2] V
   per Carmo et al. (2013) Fig. 6.

## v0.5 validation (planned)

1. **Digitize** one polarization curve from Carmo et al. (2013) Fig. 6
   (or another suitable peer-reviewed experimental dataset).
2. **Store** as `docs/validation/carmo2013_fig6.csv` with columns
   `j_a_per_cm2, u_cell_v, temperature_c, pressure_bar`.
3. **Compare** simulation output against digitized curve at matched operating
   conditions; compute RMSE and MAPE.
4. **Pass criterion:** RMSE < 50 mV, MAPE < 5 % over the 0.1–2.0 A/cm² range.

## Not validated — known limitations

- No two-phase (liquid water) transport effects
- No thermal gradient across the cell
- No concentration overpotential contribution from variable O2 partial pressure
- No time-dependent (transient) behavior
- Exchange current densities are inputs, not derived from catalyst loading

These limitations are documented in the README; adding them is v1.0 scope.
