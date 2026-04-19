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
from src.stack import Stack
from src.thermal import ThermalModel, E_TN_STANDARD
from src.materials import (
    MEMBRANES,
    CATALYSTS_ANODE,
    CATALYSTS_CATHODE,
    GDL_ANODE,
    GDL_CATHODE,
    membrane_names,
    anode_catalyst_names,
    cathode_catalyst_names,
    anode_gdl_names,
    cathode_gdl_names,
)

# ---- Page config ---- #
st.set_page_config(
    page_title="PEM-EC Designer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("PEM Electrolysis Cell Designer")
st.caption(
    "Physics-based simulation of proton-exchange-membrane water electrolysis — "
    "cell, stack and thermal analysis. All calculations in strict SI."
)

# ---------------- Sidebar: Material-Presets ---------------- #
st.sidebar.header("Materials")

membrane_sel = st.sidebar.selectbox(
    "Membrane", membrane_names(),
    index=membrane_names().index("Nafion 212"),
    help="Preset selects thickness + conductivity + water uptake",
)
membrane = MEMBRANES[membrane_sel]
st.sidebar.caption(
    f"→ {membrane.thickness_m*1e6:.0f} μm, σ={membrane.conductivity_sm:.1f} S/m, "
    f"λ_max={membrane.water_uptake:.0f}"
)

cat_anode_sel = st.sidebar.selectbox(
    "Anode catalyst (OER)", anode_catalyst_names(),
    index=0,
)
cat_anode = CATALYSTS_ANODE[cat_anode_sel]

cat_cathode_sel = st.sidebar.selectbox(
    "Cathode catalyst (HER)", cathode_catalyst_names(),
    index=0,
)
cat_cathode = CATALYSTS_CATHODE[cat_cathode_sel]

gdl_anode_sel = st.sidebar.selectbox("GDL anode", anode_gdl_names(), index=0)
gdl_cathode_sel = st.sidebar.selectbox("GDL cathode", cathode_gdl_names(), index=0)
gdl_a = GDL_ANODE[gdl_anode_sel]
gdl_c = GDL_CATHODE[gdl_cathode_sel]

# ---------------- Sidebar: Operating conditions ---------------- #
st.sidebar.header("Operating conditions")
t_c = st.sidebar.slider("Temperature [°C]", 25.0, 120.0, 80.0, 1.0)
p_bar = st.sidebar.slider("Pressure [bar]", 1.0, 50.0, 10.0, 0.5)
j_op_a_cm2 = st.sidebar.slider(
    "Operating current density [A/cm²]", 0.05, 3.0, 1.0, 0.05
)

# ---------------- Sidebar: Stack geometry ---------------- #
st.sidebar.header("Stack geometry")
n_cells = st.sidebar.number_input(
    "Number of cells [–]", min_value=1, max_value=500, value=20, step=1,
)
active_area_cm2 = st.sidebar.number_input(
    "Active area per cell [cm²]", min_value=1.0, max_value=10_000.0,
    value=100.0, step=1.0,
)

# ---------------- Sidebar: Thermal ---------------- #
st.sidebar.header("Thermal management")
coolant_dt_k = st.sidebar.slider(
    "Coolant ΔT [K]", 1.0, 20.0, 5.0, 0.5,
    help="Allowed coolant-loop temperature rise",
)
coolant_cp = st.sidebar.number_input(
    "Coolant cp [J/(kg·K)]", min_value=1000.0, max_value=5000.0,
    value=4196.0, step=10.0,
    help="Water @ 80 °C ≈ 4196 J/(kg·K)",
)

# ---------------- Build models ---------------- #
cell = Electrochemistry.from_engineering(
    temperature_celsius=t_c,
    pressure_bar=p_bar,
    membrane_conductivity_s_per_m=membrane.conductivity_sm,
    membrane_thickness_um=membrane.thickness_m * 1e6,
    j0_anode_a_per_cm2=cat_anode.j0_a_m2 / 1e4,
    j0_cathode_a_per_cm2=cat_cathode.j0_a_m2 / 1e4,
    alpha_anode=cat_anode.alpha,
    alpha_cathode=cat_cathode.alpha,
    r_gdl_anode_ohm_cm2=gdl_a.r_specific_ohm_m2 * 1e4,
    r_gdl_cathode_ohm_cm2=gdl_c.r_specific_ohm_m2 * 1e4,
)

area_si = U.cm2_to_m2(active_area_cm2)
j_op_si = U.a_per_cm2_to_a_per_m2(j_op_a_cm2)

stack = Stack(cell=cell, n_cells=int(n_cells), active_area_si=area_si)
thermal = ThermalModel(
    cell=cell, n_cells=int(n_cells), active_area_si=area_si,
    coolant_cp=coolant_cp, coolant_dt_k=coolant_dt_k,
)

# ---------------- Operating-point calculations ---------------- #
v = cell.cell_voltage(j_op_si)
eff = cell.efficiency(j_op_si)
stack_v = stack.stack_voltage(j_op_si)
stack_p = stack.stack_power(j_op_si)
stack_h2 = stack.stack_h2_production(j_op_si)
heat = thermal.heat_generation(j_op_si)
cooling = thermal.cooling_flow(j_op_si)
thermal_eff = thermal.thermal_efficiency(j_op_si)

# ---------------- Top KPIs (Stack level) ---------------- #
st.subheader(f"Stack @ {j_op_a_cm2:.2f} A/cm² — {int(n_cells)} cells × {active_area_cm2:.0f} cm²")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Stack voltage", f"{stack_v['u_stack']:.1f} V")
col2.metric("Stack power", f"{stack_p['p_electric_kw']:.2f} kW")
col3.metric("H₂ production", f"{stack_h2['m_dot_kg_per_h']*1000:.0f} g/h")
col4.metric("Energy efficiency", f"{eff['eta_energy']*100:.1f} %")
col5.metric("Waste heat", f"{heat['q_stack_kw']:.2f} kW")

# ---------------- Tabs ---------------- #
tab_pol, tab_stack, tab_thermal, tab_mat, tab_export = st.tabs(
    ["Polarization", "Stack Analysis", "Thermal", "Materials", "Export"]
)

# ===================== TAB 1: Polarization ===================== #
with tab_pol:
    j_range_a_cm2 = np.linspace(0.05, 3.0, 80)
    j_range_si = U.a_per_cm2_to_a_per_m2(j_range_a_cm2)
    pol = cell.polarization_curve(j_range_si)

    u_arr = pol["u_cell"]
    eta_act = pol["eta_act_total"]
    eta_ohm = pol["eta_ohm"]
    e_rev = cell.e_rev

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=j_range_a_cm2, y=u_arr, name="U_cell",
        line=dict(color="#7dd3fc", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=j_range_a_cm2, y=np.full_like(j_range_a_cm2, e_rev),
        name="E_rev", line=dict(color="#86efac", width=1, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=j_range_a_cm2, y=np.full_like(j_range_a_cm2, E_TN_STANDARD),
        name="E_tn (thermoneutral)", line=dict(color="#fca5a5", width=1, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=j_range_a_cm2, y=e_rev + eta_act,
        name="+ η_act", line=dict(color="#fbbf24", width=1),
    ))
    fig.add_trace(go.Scatter(
        x=j_range_a_cm2, y=e_rev + eta_act + eta_ohm,
        name="+ η_ohm", line=dict(color="#c084fc", width=1),
    ))
    fig.add_vline(x=j_op_a_cm2, line_dash="dot", line_color="#d7dee8",
                  annotation_text="operating point")
    fig.update_layout(
        xaxis_title="Current density [A/cm²]",
        yaxis_title="Cell voltage [V]",
        template="plotly_dark", height=500,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Voltage decomposition @ operating point**")
    decomp = pd.DataFrame({
        "Component": ["E_rev", "η_act,anode (OER)", "η_act,cathode (HER)",
                      "η_ohm", "η_conc", "U_cell (total)"],
        "Value [V]": [v["e_rev"], v["eta_act_anode"], v["eta_act_cathode"],
                      v["eta_ohm"], v["eta_conc"], v["u_cell"]],
    })
    st.dataframe(decomp.style.format({"Value [V]": "{:.4f}"}),
                 use_container_width=True, hide_index=True)

# ===================== TAB 2: Stack Analysis ===================== #
with tab_stack:
    st.markdown("### Stack polarization curve")
    stack_pol = stack.polarization_curve(j_range_si)

    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(
        x=j_range_a_cm2, y=stack_pol["u_stack"],
        name=f"U_stack ({int(n_cells)} cells)",
        line=dict(color="#7dd3fc", width=3),
    ))
    fig_s.update_layout(
        xaxis_title="Current density [A/cm²]",
        yaxis_title="Stack voltage [V]",
        template="plotly_dark", height=400,
    )
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("### Stack power curve")
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(
        x=j_range_a_cm2, y=stack_pol["p_electric_w"] / 1000.0,
        name="P_electric", line=dict(color="#fbbf24", width=3),
    ))
    fig_p.update_layout(
        xaxis_title="Current density [A/cm²]",
        yaxis_title="Stack electrical power [kW]",
        template="plotly_dark", height=400,
    )
    st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("### Stack summary @ operating point")
    stack_df = pd.DataFrame({
        "Quantity": [
            "Number of cells", "Active area per cell [cm²]",
            "Total active area [m²]",
            "Cell voltage [V]", "Stack voltage [V]",
            "Stack current [A]",
            "Electric power [kW]", "Hydrogen LHV power [kW]",
            "Waste heat [kW]",
            "H₂ [kg/h]", "H₂ [Nm³/h]",
        ],
        "Value": [
            f"{int(n_cells)}", f"{active_area_cm2:.1f}",
            f"{int(n_cells) * area_si:.4f}",
            f"{stack_v['u_cell']:.3f}", f"{stack_v['u_stack']:.1f}",
            f"{stack_v['current_a']:.1f}",
            f"{stack_p['p_electric_kw']:.3f}",
            f"{stack_p['p_h2_lhv_kw']:.3f}",
            f"{stack_p['p_waste_kw']:.3f}",
            f"{stack_h2['m_dot_kg_per_h']:.3f}",
            f"{stack_h2['v_dot_nm3_per_h']:.3f}",
        ],
    })
    st.dataframe(stack_df, use_container_width=True, hide_index=True)

# ===================== TAB 3: Thermal ===================== #
with tab_thermal:
    st.markdown("### Thermal balance @ operating point")

    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.metric("U_cell / E_tn ratio", f"{v['u_cell']/E_TN_STANDARD:.3f}",
                  help="> 1 = exothermic operation")
    col_t2.metric("Heat generation", f"{heat['q_stack_kw']:.2f} kW",
                  help=f"per stack ({int(n_cells)} cells)")
    col_t3.metric("Thermal efficiency (HHV)",
                  f"{thermal_eff['eta_thermal_hhv']*100:.1f} %")

    st.markdown("### Cooling requirement")
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Coolant ΔT", f"{coolant_dt_k:.1f} K")
    col_c2.metric("Coolant mass flow", f"{cooling['m_dot_kg_per_h']:.1f} kg/h")
    col_c3.metric("Coolant volume flow", f"{cooling['v_dot_l_per_min']:.2f} L/min")

    if cooling["heating_needed"]:
        st.warning("Operating point is endothermic — cell requires external heating")

    st.markdown("### Heat generation vs. current density")
    q_vs_j = np.array([
        thermal.heat_generation(j_si)["q_stack_w"] / 1000.0
        for j_si in j_range_si
    ])
    fig_q = go.Figure()
    fig_q.add_trace(go.Scatter(
        x=j_range_a_cm2, y=q_vs_j,
        name="Q_stack", line=dict(color="#fca5a5", width=3),
    ))
    fig_q.add_hline(y=0, line_dash="dot", line_color="#6b7280")
    fig_q.update_layout(
        xaxis_title="Current density [A/cm²]",
        yaxis_title="Waste heat [kW]",
        template="plotly_dark", height=400,
    )
    st.plotly_chart(fig_q, use_container_width=True)

    st.caption(
        "Thermoneutral voltage E_tn = ΔH / (n·F) ≈ 1.481 V at 298.15 K (HHV basis). "
        "U_cell > E_tn → exothermic (cooling required). "
        "U_cell < E_tn → endothermic (heating required). "
        "PEM-EC typically operates exothermically above ~0.1 A/cm²."
    )

# ===================== TAB 4: Materials ===================== #
with tab_mat:
    st.markdown("### Selected materials")

    mat_df = pd.DataFrame({
        "Component": ["Membrane", "Anode catalyst", "Cathode catalyst",
                      "GDL anode", "GDL cathode"],
        "Name": [membrane.name, cat_anode.name, cat_cathode.name,
                 gdl_a.name, gdl_c.name],
        "Key property": [
            f"{membrane.thickness_m*1e6:.0f} μm, σ={membrane.conductivity_sm:.1f} S/m",
            f"j0={cat_anode.j0_a_m2:.1f} A/m², α={cat_anode.alpha:.2f}, "
            f"{cat_anode.loading_mg_cm2:.1f} mg/cm²",
            f"j0={cat_cathode.j0_a_m2:.0f} A/m², α={cat_cathode.alpha:.2f}, "
            f"{cat_cathode.loading_mg_cm2:.1f} mg/cm²",
            f"R={gdl_a.r_specific_ohm_m2*1e4:.3f} Ω·cm², ε={gdl_a.porosity:.2f}",
            f"R={gdl_c.r_specific_ohm_m2*1e4:.3f} Ω·cm², ε={gdl_c.porosity:.2f}",
        ],
        "Reference": [
            membrane.ref, cat_anode.ref, cat_cathode.ref, gdl_a.ref, gdl_c.ref,
        ],
    })
    st.dataframe(mat_df, use_container_width=True, hide_index=True)

    st.markdown("### Available presets")
    with st.expander("All membranes"):
        mem_all = pd.DataFrame([
            {"Name": m.name,
             "Thickness [μm]": m.thickness_m * 1e6,
             "σ [S/m]": m.conductivity_sm,
             "λ_max": m.water_uptake,
             "EW [g/mol]": m.ewt_g_mol,
             "Ref": m.ref}
            for m in MEMBRANES.values()
        ])
        st.dataframe(mem_all, use_container_width=True, hide_index=True)

    with st.expander("All catalysts"):
        cat_all = pd.DataFrame([
            {"Name": c.name, "Side": c.side, "j0 [A/m²]": c.j0_a_m2,
             "α": c.alpha, "Loading [mg/cm²]": c.loading_mg_cm2, "Ref": c.ref}
            for c in list(CATALYSTS_ANODE.values()) + list(CATALYSTS_CATHODE.values())
        ])
        st.dataframe(cat_all, use_container_width=True, hide_index=True)

# ===================== TAB 5: Export ===================== #
with tab_export:
    st.markdown("### Export polarization curve")
    export_df = pd.DataFrame({
        "current_density_a_per_cm2": j_range_a_cm2,
        "u_cell_v": pol["u_cell"],
        "u_stack_v": stack_pol["u_stack"],
        "p_electric_w": stack_pol["p_electric_w"],
        "eta_act_v": pol["eta_act_total"],
        "eta_ohm_v": pol["eta_ohm"],
        "eta_energy": pol["eta_energy"],
    })
    buffer = StringIO()
    export_df.to_csv(buffer, index=False)
    st.download_button(
        label="Download polarization curve CSV",
        data=buffer.getvalue(),
        file_name=(
            f"pem_ec_{membrane_sel.replace(' ', '_')}_"
            f"N{int(n_cells)}_T{t_c:.0f}C_p{p_bar:.0f}bar.csv"
        ),
        mime="text/csv",
    )

    st.markdown("### Export stack summary")
    summary_df = pd.DataFrame({
        "key": [
            "membrane", "anode_catalyst", "cathode_catalyst",
            "n_cells", "active_area_cm2", "temperature_c", "pressure_bar",
            "j_op_a_cm2", "u_cell_v", "u_stack_v", "current_a",
            "p_electric_kw", "p_h2_lhv_kw", "q_waste_kw",
            "m_h2_kg_per_h", "v_h2_nm3_per_h",
            "coolant_m_kg_per_h", "coolant_v_l_per_min",
            "eta_energy", "eta_thermal_hhv",
        ],
        "value": [
            membrane_sel, cat_anode_sel, cat_cathode_sel,
            int(n_cells), active_area_cm2, t_c, p_bar,
            j_op_a_cm2, v["u_cell"], stack_v["u_stack"], stack_v["current_a"],
            stack_p["p_electric_kw"], stack_p["p_h2_lhv_kw"], heat["q_stack_kw"],
            stack_h2["m_dot_kg_per_h"], stack_h2["v_dot_nm3_per_h"],
            cooling["m_dot_kg_per_h"], cooling["v_dot_l_per_min"],
            eff["eta_energy"], thermal_eff["eta_thermal_hhv"],
        ],
    })
    sum_buffer = StringIO()
    summary_df.to_csv(sum_buffer, index=False)
    st.download_button(
        label="Download operating-point summary CSV",
        data=sum_buffer.getvalue(),
        file_name=f"pem_ec_summary_N{int(n_cells)}_T{t_c:.0f}C.csv",
        mime="text/csv",
    )

# ---------------- Footer ---------------- #
st.divider()
st.caption(
    f"pem-ec-designer v0.2 — MIT License · 78 tests passing · "
    "0D steady-state model · Stack + Thermal-0D + Material-Presets."
)
