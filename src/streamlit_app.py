"""
Streamlit UI for pem-ec-designer.

UI-Schicht: display in engineering units (°C, bar, A/cm², …). Intern
läuft alles in SI über src/electrochemistry.py + src/units.py.

Run:
    streamlit run src/streamlit_app.py
"""

import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import units as U
from src.electrochemistry import Electrochemistry

# ---- Page config ---- #
st.set_page_config(
    page_title="PEM-EC Designer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("PEM Electrolysis Cell Designer")
st.caption(
    "Physics-based simulation of proton-exchange-membrane water electrolysis. "
    "All calculations in strict SI; displayed values in engineering units."
)

# ---------------- Sidebar: Parameters ---------------- #
st.sidebar.header("Operating conditions")
t_c = st.sidebar.slider("Temperature [°C]", 25.0, 120.0, 80.0, 1.0)
p_bar = st.sidebar.slider("Pressure [bar]", 1.0, 50.0, 10.0, 0.5)
j_op_a_cm2 = st.sidebar.slider(
    "Operating current density [A/cm²]", 0.05, 3.0, 1.0, 0.05
)
active_area_cm2 = st.sidebar.number_input(
    "Active area [cm²]", min_value=1.0, max_value=10_000.0, value=100.0, step=1.0
)

st.sidebar.header("Membrane")
membrane_thickness_um = st.sidebar.slider(
    "Membrane thickness [μm]", 25.0, 250.0, 50.0, 5.0,
    help="Nafion 212 = 50 μm, Nafion 115 = 127 μm",
)
membrane_conductivity = st.sidebar.slider(
    "Membrane conductivity [S/m]", 1.0, 20.0, 10.0, 0.5
)

st.sidebar.header("Catalyst kinetics")
j0_anode_a_cm2 = st.sidebar.select_slider(
    "Anode exchange current density [A/cm²] (OER, IrO₂)",
    options=[1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2],
    value=1e-3,  # Carmo et al. (2013) Tab. 4 — typical commercial IrO₂
    format_func=lambda x: f"{x:.0e}",
)
j0_cathode_a_cm2 = st.sidebar.select_slider(
    "Cathode exchange current density [A/cm²] (HER, Pt)",
    options=[1e-3, 1e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1.0],
    value=1e-1,  # Carmo et al. (2013) Tab. 4 — typical commercial Pt/C
    format_func=lambda x: f"{x:.0e}",
)
alpha_a = st.sidebar.slider("Charge-transfer coefficient anode", 0.1, 1.0, 0.5, 0.05)
alpha_c = st.sidebar.slider("Charge-transfer coefficient cathode", 0.1, 1.0, 0.5, 0.05)

st.sidebar.header("Resistances [Ω·cm²]")
r_contact_ohm_cm2 = st.sidebar.number_input("Contact", 0.0, 1.0, 0.05, 0.01)
r_gdl_a_ohm_cm2 = st.sidebar.number_input("GDL anode (Ti felt)", 0.0, 1.0, 0.02, 0.005)
r_gdl_c_ohm_cm2 = st.sidebar.number_input("GDL cathode (C paper)", 0.0, 1.0, 0.01, 0.005)

# ---------------- Build cell model ---------------- #
cell = Electrochemistry.from_engineering(
    temperature_celsius=t_c,
    pressure_bar=p_bar,
    membrane_conductivity_s_per_m=membrane_conductivity,
    membrane_thickness_um=membrane_thickness_um,
    j0_anode_a_per_cm2=j0_anode_a_cm2,
    j0_cathode_a_per_cm2=j0_cathode_a_cm2,
    alpha_anode=alpha_a,
    alpha_cathode=alpha_c,
    r_contact_ohm_cm2=r_contact_ohm_cm2,
    r_gdl_anode_ohm_cm2=r_gdl_a_ohm_cm2,
    r_gdl_cathode_ohm_cm2=r_gdl_c_ohm_cm2,
)

# ---------------- Operating-point calculation ---------------- #
j_op_si = U.a_per_cm2_to_a_per_m2(j_op_a_cm2)
area_si = U.cm2_to_m2(active_area_cm2)

v = cell.cell_voltage(j_op_si)
eff = cell.efficiency(j_op_si)
h2 = cell.h2_production(j_op_si, area_si)

# ---------------- Top KPIs ---------------- #
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cell voltage", f"{v['u_cell']:.3f} V")
col2.metric("Energy efficiency", f"{eff['eta_energy'] * 100:.1f} %")
col3.metric("Specific energy", f"{eff['specific_energy_kwh_kg']:.1f} kWh/kg H₂")
col4.metric("H₂ production", f"{h2['m_dot_g_per_h']:.1f} g/h")

# ---------------- Polarization curve ---------------- #
st.subheader("Polarization curve")

j_range_a_cm2 = np.linspace(0.05, 3.0, 60)
j_range_si = U.a_per_cm2_to_a_per_m2(j_range_a_cm2)

try:
    pol = cell.polarization_curve(j_range_si)
except Exception as exc:  # noqa: BLE001
    st.error(f"Polarization curve failed: {exc}")
    st.stop()

u_arr = pol["u_cell"]
eta_act_arr = pol["eta_act_total"]
eta_ohm_arr = pol["eta_ohm"]
eta_conc_arr = pol["eta_conc"]
e_rev = cell.e_rev

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=j_range_a_cm2, y=u_arr, name="U_cell",
        line=dict(color="#7dd3fc", width=3),
    )
)
fig.add_trace(
    go.Scatter(
        x=j_range_a_cm2, y=np.full_like(j_range_a_cm2, e_rev),
        name="E_rev", line=dict(color="#86efac", width=1, dash="dash"),
    )
)
fig.add_trace(
    go.Scatter(
        x=j_range_a_cm2, y=e_rev + eta_act_arr,
        name="+ η_act", line=dict(color="#fbbf24", width=1),
    )
)
fig.add_trace(
    go.Scatter(
        x=j_range_a_cm2, y=e_rev + eta_act_arr + eta_ohm_arr,
        name="+ η_ohm", line=dict(color="#fca5a5", width=1),
    )
)
fig.add_vline(
    x=j_op_a_cm2, line_width=1, line_dash="dot", line_color="#d7dee8",
    annotation_text="operating point",
)
fig.update_layout(
    xaxis_title="Current density [A/cm²]",
    yaxis_title="Cell voltage [V]",
    template="plotly_dark",
    height=480,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- Voltage decomposition at operating point ---------------- #
with st.expander("Voltage decomposition at operating point", expanded=True):
    decomp = pd.DataFrame(
        {
            "Component": [
                "E_rev (reversible)",
                "η_act,anode (OER)",
                "η_act,cathode (HER)",
                "η_ohm (ohmic)",
                "η_conc (mass-transport)",
                "U_cell (total)",
            ],
            "Value [V]": [
                v["e_rev"],
                v["eta_act_anode"],
                v["eta_act_cathode"],
                v["eta_ohm"],
                v["eta_conc"],
                v["u_cell"],
            ],
        }
    )
    st.dataframe(decomp.style.format({"Value [V]": "{:.4f}"}), use_container_width=True)

# ---------------- H2 production details ---------------- #
with st.expander("H₂ production at operating point"):
    h2_df = pd.DataFrame(
        {
            "Quantity": [
                "Current total",
                "Molar flow",
                "Mass flow",
                "Volumetric flow (STP)",
            ],
            "Value": [
                f"{h2['current_a']:.1f} A",
                f"{h2['n_dot_mol_per_s']:.3e} mol/s",
                f"{h2['m_dot_g_per_h']:.2f} g/h",
                f"{h2['v_dot_nm3_per_h']:.4f} Nm³/h",
            ],
        }
    )
    st.dataframe(h2_df, use_container_width=True)

# ---------------- Export ---------------- #
st.subheader("Export polarization curve")
export_df = pd.DataFrame(
    {
        "current_density_a_per_cm2": j_range_a_cm2,
        "current_density_a_per_m2": j_range_si,
        "u_cell_v": u_arr,
        "eta_act_v": eta_act_arr,
        "eta_ohm_v": eta_ohm_arr,
        "eta_conc_v": eta_conc_arr,
        "eta_energy": pol["eta_energy"],
    }
)
buffer = StringIO()
export_df.to_csv(buffer, index=False)
st.download_button(
    label="Download polarization curve CSV",
    data=buffer.getvalue(),
    file_name=f"pem_ec_polarization_T{t_c:.0f}C_p{p_bar:.0f}bar.csv",
    mime="text/csv",
)

# ---------------- Footer ---------------- #
st.divider()
st.caption(
    "pem-ec-designer v0.1 — MIT License. "
    "All equations documented in docs/theory/. "
    "This is a 0D steady-state model; multi-phase flow, thermal gradients, "
    "and degradation are out of scope for this release."
)
