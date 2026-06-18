from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.io as pio
import json

app = Flask(__name__)

# Disable Plotly's default template so it can't inject sizing/colors
pio.templates.default = "none"

REPORT_DATA = {
    "empresa": "C&C Asociados Oriente S.A.S.",
    "trabajador": "Robinson Arley Pamplona Ríos",
    "cedula": "71.004.778",
    "labor": "Conductor de Volqueta",
    "area": "Operativa",
    "fecha_muestreo": "15/04/2026",
    "jornada": "8:30 a.m. – 4:30 p.m.",
    "tiempo_muestreo_min": 480,
    "temperatura_c": 28,
    "presion_mmhg": 641,
    "caudal_promedio_lpm": 1.72,
    "caudal_corregido_lpm": 1.436,
    "volumen_muestra_l": 689.4,
    "tlv_fr_original": 3.0,
    "tlv_fr_corregido": 2.484,
    "tlv_silice_original": 0.025,
    "tlv_silice_corregido": 0.0212,
    "conc_fr_mgm3": 0.006,
    "conc_cuarzo_mgm3": 0.003,
    "conc_cristobalita_mgm3": 0.003,
    "loq_fr_mgm3": 0.012,
    "loq_cuarzo_mgm3": 0.006,
    "loq_cristobalita_mgm3": 0.006,
    "metodologia": "NIOSH 7500 / NIOSH 0600",
    "tecnica_analitica": "Difracción de Rayos X + Gravimetría",
    "laboratorio": "Conhintec Labs (AIHA LAP, ISO/IEC 17025:2017)",
}

IR_FR_EST     = REPORT_DATA["conc_fr_mgm3"]    / REPORT_DATA["tlv_fr_corregido"]
IR_SILICE_EST = REPORT_DATA["conc_cuarzo_mgm3"] / REPORT_DATA["tlv_silice_corregido"]
IR_FR_PCT     = IR_FR_EST * 100
IR_SILICE_PCT = IR_SILICE_EST * 100

NARANJA = "#E85D1A"
VERDE   = "#22C55E"
AMARILLO= "#F59E0B"
ROJO    = "#EF4444"
BLANCO  = "#F9F7F4"
AZUL    = "#3B82F6"
GRAFITO = "#1C1C1E"


def base_layout(height, ml=65, mr=45, mt=55, mb=50):
    # NOTE: width/height/autosize are set on the client (JS) using the real
    # measured container width, so we deliberately do NOT set them here.
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=BLANCO),
        margin=dict(l=ml, r=mr, t=mt, b=mb),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=BLANCO)),
    )


def _clean(fig):
    """Serialize to JSON and strip any leftover width that would
    prevent the chart from filling its container."""
    d = json.loads(fig.to_json())
    d["layout"].pop("width", None)
    d["layout"]["autosize"] = True
    return d


def gauge(value, title, color=VERDE):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"size": 30, "color": BLANCO}},
        title={"text": title, "font": {"size": 13, "color": "#94A3B8"}},
        # Centered domain — the gauge sits in the middle of its card
        domain={"x": [0.0, 1.0], "y": [0.0, 0.92]},
        gauge={
            "axis": {
                "range": [0, 120],
                "tickcolor": "#64748B",
                "tickfont": {"color": "#94A3B8", "size": 10},
                "tickvals": [0, 10, 50, 90, 100, 120],
                "ticktext": ["0", "10%", "50%", "90%", "TLV", ">TLV"],
            },
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 10],    "color": "rgba(34,197,94,0.18)"},
                {"range": [10, 50],   "color": "rgba(245,158,11,0.18)"},
                {"range": [50, 90],   "color": "rgba(249,115,22,0.18)"},
                {"range": [90, 100],  "color": "rgba(239,68,68,0.18)"},
                {"range": [100, 120], "color": "rgba(239,68,68,0.30)"},
            ],
            "threshold": {
                "line": {"color": NARANJA, "width": 3},
                "thickness": 0.85,
                "value": 100,
            },
        },
    ))
    fig.update_layout(**base_layout(260, ml=30, mr=30, mt=45, mb=20))
    return _clean(fig)


def chart_conc_vs_tlv():
    ag   = ["Fracción Respirable", "Cuarzo (Sílice)", "Cristobalita"]
    conc = [0.006, 0.003, 0.003]
    loq  = [0.012, 0.006, 0.006]
    tlv  = [2.484, 0.0212, 0.0212]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Conc. estimada (½ LOQ)", x=ag, y=conc,
        marker_color=VERDE, text=[f"{v:.4f}" for v in conc],
        textposition="outside", textfont=dict(color=BLANCO, size=11)))
    fig.add_trace(go.Bar(name="LOQ", x=ag, y=loq,
        marker_color=AMARILLO, text=[f"{v:.4f}" for v in loq],
        textposition="outside", textfont=dict(color=BLANCO, size=11)))
    fig.add_trace(go.Bar(name="TLV-TWA Corregido", x=ag, y=tlv,
        marker_color=ROJO, text=[f"{v:.4f}" for v in tlv],
        textposition="outside", textfont=dict(color=BLANCO, size=11)))
    layout = base_layout(360, ml=70, mr=30, mt=55, mb=45)
    layout.update(
        barmode="group",
        title=dict(text="Concentraciones medidas vs Límites permisibles (mg/m³)",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        yaxis=dict(title="mg/m³", gridcolor="rgba(255,255,255,0.07)",
                   color="#94A3B8", type="log", automargin=True),
        xaxis=dict(color="#94A3B8", automargin=True),
    )
    fig.update_layout(**layout)
    return _clean(fig)


def chart_radar():
    cats = ["Hermeticidad<br>cabina", "EPP<br>disponible", "Prácticas<br>seguras",
            "Polvo<br>ambiental", "Exposición<br>directa", "Control<br>administrativo"]
    ctrl = [9, 7, 8, 3, 2, 7]
    risk = [10 - v for v in ctrl]
    fig = go.Figure()
    for vals, name, col, fill in [
        (ctrl, "Control / Protección", VERDE,   "rgba(34,197,94,0.12)"),
        (risk, "Factor de Riesgo",     NARANJA, "rgba(232,93,26,0.12)")]:
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", name=name, line_color=col, fillcolor=fill))
    layout = base_layout(380, ml=60, mr=60, mt=55, mb=40)
    layout.update(
        title=dict(text="Control vs Factor de Riesgo (escala 0–10)",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            domain=dict(x=[0, 1], y=[0, 1]),
            radialaxis=dict(visible=True, range=[0, 10],
                            gridcolor="rgba(255,255,255,0.10)", color="#94A3B8",
                            tickfont=dict(size=9)),
            angularaxis=dict(color=BLANCO, tickfont=dict(size=10),
                             gridcolor="rgba(255,255,255,0.10)")),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=BLANCO),
                    orientation="h", yanchor="bottom", y=-0.12,
                    xanchor="center", x=0.5),
    )
    fig.update_layout(**layout)
    return _clean(fig)


def chart_timeline():
    horas  = [8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5]
    etiq   = ["Taller Zamora", "Salida taller", "Ruta Argos", "Ruta Argos",
              "Entrada planta", "Ascenso frente", "Cargue volqueta", "Descenso carga",
              "Ruta Mincivil", "Ruta Mincivil", "Ruta Mincivil", "Botadero",
              "Descarga material", "Retorno", "Taquilla ⚠️", "Retorno base", "Fin jornada"]
    riesgo  = [1, 1, 2, 2, 2, 5, 4, 3, 2, 2, 2, 4, 5, 2, 6, 2, 1]
    colores = [VERDE if r <= 2 else (AMARILLO if r <= 4 else (NARANJA if r <= 6 else ROJO)) for r in riesgo]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=horas, y=riesgo, mode="lines+markers",
        name="Nivel de riesgo", line=dict(color=NARANJA, width=2.5),
        marker=dict(size=10, color=colores, line=dict(color=GRAFITO, width=1.2)),
        text=etiq, hovertemplate="<b>%{text}</b><br>%{x:.1f}h · Riesgo %{y}/10<extra></extra>",
        fill="tozeroy", fillcolor="rgba(232,93,26,0.07)"))
    fig.add_hline(y=5, line_dash="dash", line_color=AMARILLO,
        annotation_text="Nivel de acción (50% TLV)", annotation_font_color=AMARILLO,
        annotation_position="top left")
    fig.add_hline(y=9, line_dash="dash", line_color=ROJO,
        annotation_text="Límite TLV", annotation_font_color=ROJO,
        annotation_position="top left")
    fig.add_trace(go.Scatter(x=[15.5], y=[6], mode="markers",
        name="Descenso del vehículo", marker=dict(size=16, color=ROJO,
        symbol="triangle-up", line=dict(color=BLANCO, width=1.5))))
    layout = base_layout(320, ml=70, mr=40, mt=50, mb=50)
    layout.update(
        title=dict(text="Perfil de riesgo durante la jornada laboral",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        xaxis=dict(title="Hora", tickvals=[8.5, 10, 11, 12, 13, 14, 15, 16, 16.5],
                   ticktext=["8:30", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "16:30"],
                   color="#94A3B8", gridcolor="rgba(255,255,255,0.07)", automargin=True),
        yaxis=dict(title="Riesgo relativo (0–10)", range=[0, 11],
                   color="#94A3B8", gridcolor="rgba(255,255,255,0.07)", automargin=True),
    )
    fig.update_layout(**layout)
    return _clean(fig)


def chart_variables():
    variables = ["Taquilla / control operativo", "Frente de explotación (cargue)",
                 "Botadero Mincivil (descarga)", "Vías no pavimentadas", "Polvo ambiental zona minera",
                 "Temperatura alta (28 °C)", "Presión atmosférica baja (641 mmHg)",
                 "Hermeticidad de cabina", "Uso de EPP respiratorio", "Permanencia dentro del vehículo"]
    impacto = [7.5, 6.5, 5.5, 5.0, 6.0, 2.5, 1.5, -8.5, -6.0, -9.0]
    colores = [ROJO if v > 0 else VERDE for v in impacto]
    textos  = [f"+{v}" if v > 0 else str(v) for v in impacto]
    fig = go.Figure(go.Bar(x=impacto, y=variables, orientation="h",
        marker_color=colores, text=textos, textposition="outside",
        textfont=dict(color=BLANCO, size=11), cliponaxis=False))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.3)", line_width=1.5)
    layout = base_layout(420, ml=20, mr=60, mt=55, mb=50)
    layout.update(
        title=dict(text="Variables que más influyen en la exposición a sílice",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        xaxis=dict(title="Impacto relativo (+ aumenta riesgo / – lo reduce)",
                   range=[-12, 11], color="#94A3B8", gridcolor="rgba(255,255,255,0.07)"),
        yaxis=dict(color=BLANCO, automargin=True),
    )
    fig.update_layout(**layout)
    return _clean(fig)


def chart_silicosis():
    años      = list(range(0, 36))
    r_actual  = [min(100, (a ** 1.3) * 0.08) for a in años]
    r_accion  = [min(100, (a ** 1.5) * 0.35) for a in años]
    r_sobre   = [min(100, (a ** 1.8) * 0.90) for a in años]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=años, y=r_actual, name="Condición actual (< LOQ)",
        line=dict(color=VERDE, width=2.5), fill="tozeroy", fillcolor="rgba(34,197,94,0.07)"))
    fig.add_trace(go.Scatter(x=años, y=r_accion, name="50% TLV — nivel de acción",
        line=dict(color=AMARILLO, width=2.5, dash="dash")))
    fig.add_trace(go.Scatter(x=años, y=r_sobre, name="Exposición > TLV",
        line=dict(color=ROJO, width=2.5, dash="dot")))
    fig.add_vrect(x0=0, x1=5, fillcolor="rgba(239,68,68,0.04)", line_width=0,
        annotation_text="Aguda", annotation_font_color=ROJO, annotation_position="top left")
    fig.add_vrect(x0=5, x1=10, fillcolor="rgba(245,158,11,0.04)", line_width=0,
        annotation_text="Acelerada", annotation_font_color=AMARILLO, annotation_position="top left")
    fig.add_vrect(x0=10, x1=35, fillcolor="rgba(59,130,246,0.04)", line_width=0,
        annotation_text="Crónica", annotation_font_color=AZUL, annotation_position="top left")
    layout = base_layout(340, ml=70, mr=40, mt=55, mb=50)
    layout.update(
        title=dict(text="Progresión del riesgo acumulado de Silicosis por nivel de exposición",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        xaxis=dict(title="Años de exposición", range=[0, 35],
                   color="#94A3B8", gridcolor="rgba(255,255,255,0.07)", automargin=True),
        yaxis=dict(title="Riesgo relativo acumulado (%)", range=[0, 105],
                   color="#94A3B8", gridcolor="rgba(255,255,255,0.07)", automargin=True),
    )
    fig.update_layout(**layout)
    return _clean(fig)


def chart_ruta():
    nombres = ["Taller de Zamora", "Planta Argos", "Frente Explotación", "Botadero Mincivil", "Taquilla"]
    lons    = [-75.552, -75.545, -75.540, -75.480, -75.490]
    lats    = [6.265, 6.280, 6.285, 6.330, 6.320]
    risks   = [1, 5, 7, 5, 6]
    colores = [VERDE if r <= 2 else (AMARILLO if r <= 4 else (NARANJA if r <= 6 else ROJO)) for r in risks]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lons, y=lats, mode="lines",
        line=dict(color="rgba(232,93,26,0.4)", width=2, dash="dot"), showlegend=False))
    fig.add_trace(go.Scatter(x=lons, y=lats, mode="markers+text",
        marker=dict(size=[14 + r * 2 for r in risks], color=colores,
                    line=dict(color=BLANCO, width=1.5)),
        text=nombres, textposition="top center", textfont=dict(color=BLANCO, size=10),
        name="Puntos de ruta", hovertemplate="<b>%{text}</b><extra></extra>"))
    layout = base_layout(300, ml=70, mr=30, mt=55, mb=50)
    layout.update(
        showlegend=False,
        title=dict(text="Ruta operativa y puntos de riesgo (referencial)",
                   font=dict(color=BLANCO, size=13), x=0.5, xanchor="center"),
        xaxis=dict(title="Longitud", color="#94A3B8",
                   gridcolor="rgba(255,255,255,0.06)", automargin=True),
        yaxis=dict(title="Latitud", color="#94A3B8",
                   gridcolor="rgba(255,255,255,0.06)", automargin=True),
    )
    fig.update_layout(**layout)
    return _clean(fig)


@app.route("/")
def index():
    kpis = {
        "ir_silice_pct": round(IR_SILICE_PCT, 2),
        "ir_fr_pct":     round(IR_FR_PCT, 2),
        "grado_riesgo":  1,
        "clasificacion": "No Exposición",
        "reeval":        "3 – 5 años",
        "tlv_silice":    REPORT_DATA["tlv_silice_corregido"],
        "tlv_fr":        REPORT_DATA["tlv_fr_corregido"],
        "loq_cuarzo":    REPORT_DATA["loq_cuarzo_mgm3"],
        "loq_fr":        REPORT_DATA["loq_fr_mgm3"],
        "temperatura":   REPORT_DATA["temperatura_c"],
        "presion":       REPORT_DATA["presion_mmhg"],
        "volumen":       REPORT_DATA["volumen_muestra_l"],
        "caudal":        REPORT_DATA["caudal_corregido_lpm"],
        "jornada_min":   REPORT_DATA["tiempo_muestreo_min"],
        "trabajador":    REPORT_DATA["trabajador"],
        "labor":         REPORT_DATA["labor"],
        "fecha":         REPORT_DATA["fecha_muestreo"],
        "empresa":       REPORT_DATA["empresa"],
        "metodo":        REPORT_DATA["metodologia"],
        "laboratorio":   REPORT_DATA["laboratorio"],
    }
    return render_template("dashboard.html", kpis=kpis)


@app.route("/api/charts")
def api_charts():
    return jsonify({
        "gauge_silice":          gauge(round(IR_SILICE_PCT, 2), "Índice de Riesgo — Sílice (Cuarzo)", VERDE),
        "gauge_fr":              gauge(round(IR_FR_PCT, 2), "Índice de Riesgo — Fracción Respirable", VERDE),
        "conc_vs_tlv":           chart_conc_vs_tlv(),
        "radar":                 chart_radar(),
        "timeline":              chart_timeline(),
        "variables_impacto":     chart_variables(),
        "silicosis_progresion":  chart_silicosis(),
        "mapa_ruta":             chart_ruta(),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050)
