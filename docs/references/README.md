# References

Primary literature for the electrochemistry model.
BibTeX extraction from the 2.5 GB PDF library is a v0.5 task.

## Core references (MVP)

- **Larminie, J., & Dicks, A. (2003).** *Fuel Cell Systems Explained.* 2nd ed. Wiley.
  — Equations 2.22 (Nernst), 3.36 (concentration loss).

- **Barbir, F. (2012).** *PEM Fuel Cells: Theory and Practice.* 2nd ed. Academic Press.
  — Overview of overpotential decomposition for PEM cells.

- **Carmo, M., Fritz, D. L., Mergel, J., & Stolten, D. (2013).**
  A comprehensive review on PEM water electrolysis.
  *International Journal of Hydrogen Energy*, 38(12), 4901–4934.
  DOI: 10.1016/j.ijhydene.2013.01.151
  — Tafel parameters, efficiency definitions, literature Section 3.

- **Springer, T. E., Zawodzinski, T. A., & Gottesfeld, S. (1991).**
  Polymer electrolyte fuel cell model.
  *Journal of The Electrochemical Society*, 138(8), 2334–2342.
  — Membrane conductivity correlation (used in extended models).

- **Tiesinga, E., Mohr, P. J., Newell, D. B., & Taylor, B. N. (2021).**
  CODATA recommended values of the fundamental physical constants: 2018.
  *Reviews of Modern Physics*, 93(2), 025010.
  — Source for R, F, N_A in `src/constants.py`.

## Local PDF library

The `~/Downloads/PEMFC Claude AVL others/` folder contains ~2.5 GB of
peer-reviewed papers tagged R.81 through R.90. These are
copyright-protected and **must never be committed to this repository**.

See `_archive/pointers/research-pdfs.md` in the parent Simulation-tools
folder for the index.

## Validation data (v0.5 target)

- Carmo et al. (2013) Fig. 6 — polarization curves for several commercial
  electrolyzers. To be digitized for the second validation test in v0.5.
