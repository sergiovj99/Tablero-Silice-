# Tablero de Riesgo por Sílice — C&C Asociados Oriente S.A.S.

Dashboard Flask para visualización de indicadores de exposición a sílice cristalina
basado en el informe técnico de Colmena Seguros (Orden 2130062, abril 2026).

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

Luego abrir: http://localhost:5050

## Estructura

```
silice_dashboard/
├── app.py                 # Aplicación Flask + generación de gráficas Plotly
├── requirements.txt
├── templates/
│   └── dashboard.html     # UI del tablero
└── static/
    └── img/
        └── logo_cc.png    # Logo corporativo C&C
```

## Gráficas incluidas

- Velocímetros de índice de riesgo (sílice + fracción respirable)
- Barras comparativas: concentraciones vs TLV vs LOQ
- Radar: factores de control vs riesgo
- Perfil de riesgo por jornada laboral (línea temporal)
- Variables de mayor impacto en la exposición (barras horizontales)
- Ruta operativa con puntos de riesgo
- Proyección epidemiológica de silicosis por nivel de exposición

## Normativa base

- ACGIH TLV-TWA 2024
- NIOSH 7500 / NIOSH 0600
- Resolución 2400/1979 (Colombia)
- GATISO-NEUMO 2007
- IARC Grupo 1

## Nota técnica

Plotly.js está incluido localmente en `static/js/plotly.min.js`, por lo que
el tablero funciona sin conexión a internet (no depende de un CDN externo).
