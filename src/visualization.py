"""
Plotly-Zeichenfunktionen für den Visual Stack Designer (v0.4).

Reine Streamlit-taugliche Figures, keine Bilder/Assets, kein JS. Alle Layer
maßstabsgetreu aus SI-Dicken der Preset-Specs. Bei N > max_visible_cells wird
die Stack-Mitte zu einer grauen "... N remaining ..."-Box kollabiert, damit
Plotly bei 200 Zellen nicht erstickt.
"""

from __future__ import annotations

import plotly.graph_objects as go

from src.assembly import StackAssembly, bpp_outer_dimensions_m
from src.components import (
    BIPOLAR_PLATES,
    GASKETS,
    open_area_ratio,
)

# ---- Farbpalette (hex, konsistent über alle Views) ---- #
_COLORS: dict[str, str] = {
    "end_plate": "#4a5568",
    "current_collector": "#b08d57",
    "bpp": "#718096",
    "gdl_anode": "#a0aec0",
    "gdl_cathode": "#cbd5e0",
    "catalyst_anode": "#2d3748",
    "catalyst_cathode": "#1a202c",
    "membrane": "#63b3ed",
    "gasket": "#fbd38d",
    "collapsed": "#edf2f7",
    "channel": "#2c5282",
    "land": "#a0aec0",
    "port": "#c53030",
    "active_area": "#e6fffa",
    "frame": "#fbd38d",
}


def _layer(y_bottom: float, thickness_m: float, label: str, kind: str, ref: str):
    """Interne Hilfe — erzeugt Bar-Trace in mm, vertikal gestapelt."""
    t_mm = thickness_m * 1000.0
    return go.Bar(
        x=[t_mm],
        y=[label],
        base=[y_bottom],
        orientation="h",
        marker_color=_COLORS.get(kind, "#999"),
        hovertemplate=(f"<b>{label}</b><br>Thickness: {t_mm:.3g} mm<br>Ref: {ref}<extra></extra>"),
        showlegend=False,
    )


def draw_layer_cross_section(
    a: StackAssembly,
    *,
    max_visible_cells: int = 6,
) -> go.Figure:
    """
    Seitenansicht des Stacks, maßstabsgetreu in mm.

    Aufbau (bottom → top): EndPlate, CurrentCollector, dann pro Zelle
    [BPP, GDL_a, Cat_a, Membran, Cat_c, GDL_c, BPP, Gasket×2], schließlich
    CurrentCollector, EndPlate. Bei N > max_visible_cells werden nur 3
    Zellen oben + 3 unten gezeichnet, Mitte als graue "... X remaining ..."-Box.
    """
    mem = a.membrane_spec()
    ag = a.anode_gdl_spec()
    cg = a.cathode_gdl_spec()
    cat_a = a.anode_catalyst_spec()
    cat_c = a.cathode_catalyst_spec()
    bpp = a.bipolar_plate_spec()
    gk = a.gasket_spec()
    ep = a.end_plate_spec()
    cc = a.current_collector_spec()

    fig = go.Figure()
    y_labels: list[str] = []
    y_cursor = 0.0

    def add(thickness: float, label: str, kind: str, ref: str):
        nonlocal y_cursor
        y_labels.append(label)
        fig.add_trace(_layer(y_cursor, thickness, label, kind, ref))
        y_cursor += thickness * 1000.0

    add(ep.thickness_m, f"EndPlate ({ep.material})", "end_plate", ep.ref)
    add(
        cc.thickness_m,
        f"CurrentCollector ({cc.material})",
        "current_collector",
        cc.ref,
    )

    def add_cell(idx: int):
        add(bpp.thickness_m, f"BPP #{idx} (anode-side)", "bpp", bpp.ref)
        add(gk.compressed_thickness_m, f"Gasket #{idx}-a", "gasket", gk.ref)
        add(ag.thickness_m, f"GDL anode #{idx}", "gdl_anode", ag.ref)
        add(
            a.catalyst_layer_thickness_m,
            f"Catalyst anode #{idx} ({cat_a.name})",
            "catalyst_anode",
            cat_a.ref,
        )
        add(mem.thickness_m, f"Membrane #{idx} ({mem.name})", "membrane", mem.ref)
        add(
            a.catalyst_layer_thickness_m,
            f"Catalyst cathode #{idx} ({cat_c.name})",
            "catalyst_cathode",
            cat_c.ref,
        )
        add(cg.thickness_m, f"GDL cathode #{idx}", "gdl_cathode", cg.ref)
        add(gk.compressed_thickness_m, f"Gasket #{idx}-c", "gasket", gk.ref)
        add(bpp.thickness_m, f"BPP #{idx} (cathode-side)", "bpp", bpp.ref)

    n = a.n_cells
    if n <= max_visible_cells:
        for i in range(1, n + 1):
            add_cell(i)
    else:
        half = max_visible_cells // 2
        for i in range(1, half + 1):
            add_cell(i)
        # Compressed middle
        hidden = n - 2 * half
        add_thickness_mm = hidden * 2  # ~2 mm pro kollabierter Zelle (nur optisch)
        y_labels.append(f"... {hidden} cells collapsed ...")
        fig.add_trace(
            go.Bar(
                x=[add_thickness_mm],
                y=[f"... {hidden} cells collapsed ..."],
                base=[y_cursor],
                orientation="h",
                marker_color=_COLORS["collapsed"],
                marker_line_color="#718096",
                marker_line_width=1,
                hovertemplate=(
                    f"<b>{hidden} cells collapsed for display</b><br>"
                    f"(real thickness: {hidden * sum([bpp.thickness_m * 2, ag.thickness_m, cg.thickness_m, 2 * a.catalyst_layer_thickness_m, mem.thickness_m, 2 * gk.compressed_thickness_m]) * 1000:.2f} mm)"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        y_cursor += add_thickness_mm
        for i in range(n - half + 1, n + 1):
            add_cell(i)

    add(
        cc.thickness_m,
        f"CurrentCollector ({cc.material})",
        "current_collector",
        cc.ref,
    )
    add(ep.thickness_m, f"EndPlate ({ep.material})", "end_plate", ep.ref)

    fig.update_layout(
        title=f"Stack cross-section — {n} cells, active area {a.active_area_m2 * 1e4:.1f} cm²",
        xaxis_title="Thickness [mm]",
        yaxis=dict(autorange="reversed"),
        barmode="stack",
        height=max(400, min(1200, 20 * len(y_labels))),
        margin=dict(l=180, r=20, t=50, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def draw_bpp_top_view(
    bpp_name: str,
    active_area_m2: float,
    gasket_name: str,
    *,
    aspect_ratio: float = 1.0,
    resolution_px: int = 600,
) -> go.Figure:
    """
    Draufsicht der Bipolarplatte mit Flow-Field-Pattern, Gasket-Rahmen und
    Inlet/Outlet-Ports in diagonalen Ecken. Einheit Achsen: mm.

    aspect_ratio = active_width / active_height, dimensionslos, > 0.
    aspect_ratio=1.0 → quadratisch (v0.4-Default).
    """
    if bpp_name not in BIPOLAR_PLATES:
        raise KeyError(f"BPP preset {bpp_name!r} not in BIPOLAR_PLATES")
    if gasket_name not in GASKETS:
        raise KeyError(f"Gasket preset {gasket_name!r} not in GASKETS")
    if aspect_ratio <= 0:
        raise ValueError(f"aspect_ratio={aspect_ratio} must be positive")
    bpp = BIPOLAR_PLATES[bpp_name]
    gk = GASKETS[gasket_name]

    aw_m = (active_area_m2 * aspect_ratio) ** 0.5
    ah_m = (active_area_m2 / aspect_ratio) ** 0.5
    bpp_w_m = aw_m + 2 * gk.frame_width_m
    bpp_h_m = ah_m + 2 * gk.frame_width_m

    # alles in mm
    bpp_w_mm = bpp_w_m * 1000.0
    bpp_h_mm = bpp_h_m * 1000.0
    frame_mm = gk.frame_width_m * 1000.0
    active_w_mm = aw_m * 1000.0
    active_h_mm = ah_m * 1000.0
    ch_w_mm = bpp.channel_width_m * 1000.0
    pitch_mm = bpp.channel_pitch_m * 1000.0

    fig = go.Figure()

    # BPP-Außenrechteck
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=bpp_w_mm,
        y1=bpp_h_mm,
        line=dict(color="#2d3748", width=2),
        fillcolor=_COLORS["bpp"],
        layer="below",
    )
    # Gasket-Frame (gezeichnet als Outline zwischen äußerer Kante und Active Area)
    fig.add_shape(
        type="rect",
        x0=frame_mm / 2,
        y0=frame_mm / 2,
        x1=bpp_w_mm - frame_mm / 2,
        y1=bpp_h_mm - frame_mm / 2,
        line=dict(color="#744210", width=frame_mm),
        fillcolor="rgba(0,0,0,0)",
        layer="below",
    )
    # Active Area
    fig.add_shape(
        type="rect",
        x0=frame_mm,
        y0=frame_mm,
        x1=frame_mm + active_w_mm,
        y1=frame_mm + active_h_mm,
        line=dict(color="#234e52", width=1),
        fillcolor=_COLORS["active_area"],
        layer="below",
    )

    # Flow pattern innerhalb active area (rechteckig)
    _draw_flow_pattern(
        fig,
        x0=frame_mm,
        y0=frame_mm,
        width_mm=active_w_mm,
        height_mm=active_h_mm,
        pattern=bpp.flow_pattern,
        ch_w_mm=ch_w_mm,
        pitch_mm=pitch_mm,
    )

    # Ports (Kreise) in diagonalen Ecken
    port_r_mm = min(frame_mm * 0.35, 4.0)
    for px, py in [
        (frame_mm / 2, bpp_h_mm - frame_mm / 2),  # inlet top-left
        (bpp_w_mm - frame_mm / 2, frame_mm / 2),  # outlet bottom-right
    ]:
        fig.add_shape(
            type="circle",
            x0=px - port_r_mm,
            y0=py - port_r_mm,
            x1=px + port_r_mm,
            y1=py + port_r_mm,
            line=dict(color="#742a2a", width=1.5),
            fillcolor=_COLORS["port"],
            layer="above",
        )

    oar = open_area_ratio(bpp)
    fig.update_layout(
        title=(
            f"BPP top view — {bpp.flow_pattern} · {bpp.material} · "
            f"{bpp_w_mm:.1f} × {bpp_h_mm:.1f} mm · open-area {oar * 100:.0f}%"
        ),
        xaxis=dict(
            range=[-2, max(bpp_w_mm, bpp_h_mm) + 2],
            scaleanchor="y",
            scaleratio=1,
            title="x [mm]",
        ),
        yaxis=dict(range=[-2, max(bpp_w_mm, bpp_h_mm) + 2], title="y [mm]"),
        height=resolution_px,
        width=resolution_px,
        plot_bgcolor="#fafafa",
        showlegend=False,
    )
    return fig


def _draw_flow_pattern(
    fig: go.Figure,
    *,
    x0: float,
    y0: float,
    width_mm: float,
    height_mm: float,
    pattern: str,
    ch_w_mm: float,
    pitch_mm: float,
) -> None:
    """
    Zeichnet Flow-Field-Kanäle als SVG-Rechtecke auf fig.

    Kanäle laufen horizontal (entlang x); Anzahl der Kanäle ergibt sich aus
    `height_mm / pitch_mm`, Kanallänge aus `width_mm`. Bei quadratischer
    Fläche ist width == height, sonst rechteckig (v0.5).
    """
    if pitch_mm <= 0 or width_mm <= 0 or height_mm <= 0:
        return
    n_channels = max(1, int(height_mm // pitch_mm))
    if pattern == "parallel":
        for i in range(n_channels):
            cy = y0 + pitch_mm * (i + 0.5)
            fig.add_shape(
                type="rect",
                x0=x0 + 2.0,
                y0=cy - ch_w_mm / 2,
                x1=x0 + width_mm - 2.0,
                y1=cy + ch_w_mm / 2,
                line=dict(width=0),
                fillcolor=_COLORS["channel"],
                layer="above",
            )
    elif pattern == "serpentine":
        # Meander: horizontal pass mit U-Turn am Rand
        for i in range(n_channels):
            cy = y0 + pitch_mm * (i + 0.5)
            left = x0 + 2.0 if i % 2 == 0 else x0 + pitch_mm
            right = x0 + width_mm - pitch_mm if i % 2 == 0 else x0 + width_mm - 2.0
            fig.add_shape(
                type="rect",
                x0=left,
                y0=cy - ch_w_mm / 2,
                x1=right,
                y1=cy + ch_w_mm / 2,
                line=dict(width=0),
                fillcolor=_COLORS["channel"],
                layer="above",
            )
        # Verticals als Turns
        for i in range(n_channels - 1):
            cy1 = y0 + pitch_mm * (i + 0.5)
            cy2 = y0 + pitch_mm * (i + 1.5)
            cx = x0 + width_mm - pitch_mm if i % 2 == 0 else x0 + pitch_mm
            fig.add_shape(
                type="rect",
                x0=cx - ch_w_mm / 2,
                y0=min(cy1, cy2),
                x1=cx + ch_w_mm / 2,
                y1=max(cy1, cy2),
                line=dict(width=0),
                fillcolor=_COLORS["channel"],
                layer="above",
            )
    elif pattern == "interdigitated":
        # abwechselnd Inlet-Finger (links) / Outlet-Finger (rechts)
        finger_len = width_mm * 0.9
        for i in range(n_channels):
            cy = y0 + pitch_mm * (i + 0.5)
            if i % 2 == 0:
                # inlet finger (links)
                fig.add_shape(
                    type="rect",
                    x0=x0 + 2.0,
                    y0=cy - ch_w_mm / 2,
                    x1=x0 + 2.0 + finger_len,
                    y1=cy + ch_w_mm / 2,
                    line=dict(width=0),
                    fillcolor=_COLORS["channel"],
                    layer="above",
                )
            else:
                # outlet finger (rechts)
                fig.add_shape(
                    type="rect",
                    x0=x0 + width_mm - 2.0 - finger_len,
                    y0=cy - ch_w_mm / 2,
                    x1=x0 + width_mm - 2.0,
                    y1=cy + ch_w_mm / 2,
                    line=dict(width=0),
                    fillcolor=_COLORS["channel"],
                    layer="above",
                )
    else:
        raise ValueError(f"unknown flow_pattern {pattern!r}")


def draw_gasket_outline(gasket_name: str, active_area_m2: float) -> go.Figure:
    """Standalone Gasket-Outline mit Cut-Out für Active Area. Für Material-Tab."""
    if gasket_name not in GASKETS:
        raise KeyError(f"Gasket preset {gasket_name!r} not in GASKETS")
    gk = GASKETS[gasket_name]
    active_edge = (active_area_m2**0.5) * 1000.0
    frame = gk.frame_width_m * 1000.0
    outer = active_edge + 2 * frame
    fig = go.Figure()
    # Außenkontur
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=outer,
        y1=outer,
        line=dict(color="#744210", width=2),
        fillcolor=_COLORS["frame"],
    )
    # Cut-out
    fig.add_shape(
        type="rect",
        x0=frame,
        y0=frame,
        x1=frame + active_edge,
        y1=frame + active_edge,
        line=dict(color="#234e52", width=1),
        fillcolor="white",
    )
    fig.update_layout(
        title=f"Gasket {gk.name} — frame {frame:.1f} mm, compressed {gk.compressed_thickness_m * 1e6:.0f} µm",
        xaxis=dict(scaleanchor="y", scaleratio=1, title="x [mm]"),
        yaxis=dict(title="y [mm]"),
        height=400,
        width=400,
        plot_bgcolor="#fafafa",
        showlegend=False,
    )
    return fig


def draw_assembly_summary(a: StackAssembly) -> go.Figure:
    """2-Panel-Figure: Querschnitt links, BPP-Top rechts. Für Export."""
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Cross-section", "BPP top view"),
        column_widths=[0.5, 0.5],
    )
    # Placeholder — echte Komposition braucht Trace-Kopie; für v0.4 reicht,
    # dass die beiden Einzel-Figures verfügbar sind. Hier nur minimaler Smoke-Test.
    w, _ = bpp_outer_dimensions_m(a)
    fig.add_trace(
        go.Bar(x=[1], y=["stack"], showlegend=False, marker_color="#999"),
        row=1,
        col=1,
    )
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=w * 1000,
        y1=w * 1000,
        line=dict(color="#2d3748"),
        fillcolor="#718096",
        row=1,
        col=2,
    )
    fig.update_layout(
        title=f"Assembly summary — {a.n_cells} cells",
        height=500,
    )
    return fig
