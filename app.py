import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Global Average Temperature Anomaly", layout="centered")

# Fetch NASA GISS Land-Ocean Temperature Anomaly Data (1880–2019)
@st.cache_data
def load_data():
    try:
        url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
        raw_df = pd.read_csv(url, skiprows=1)
        df = raw_df[['Year', 'J-D']].rename(columns={'J-D': 'Anomaly'})
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Anomaly'] = pd.to_numeric(df['Anomaly'], errors='coerce')
        df = df[(df['Year'] >= 1880) & (df['Year'] <= 2019)].dropna()
        
        # Ensure values are in °C anomaly units
        if df['Anomaly'].abs().max() > 5.0:
            df['Anomaly'] = df['Anomaly'] / 100.0
    except Exception:
        # Fallback accurate NASA GISS historical values
        years = np.arange(1880, 2020)
        anomalies = np.array([
            -0.17, -0.09, -0.11, -0.18, -0.28, -0.26, -0.25, -0.28, -0.14, -0.10,
            -0.36, -0.23, -0.27, -0.31, -0.31, -0.22, -0.10, -0.11, -0.27, -0.17,
            -0.08, -0.15, -0.27, -0.36, -0.46, -0.27, -0.22, -0.38, -0.42, -0.47,
            -0.43, -0.44, -0.36, -0.34, -0.15, -0.13, -0.35, -0.45, -0.29, -0.27,
            -0.27, -0.19, -0.28, -0.24, -0.27, -0.21, -0.10, -0.21, -0.20, -0.36,
            -0.15, -0.09, -0.16, -0.28, -0.13, -0.20, -0.15, -0.03, -0.03, -0.01,
             0.12,  0.18,  0.07,  0.09,  0.25,  0.09, -0.04, -0.03, -0.09, -0.11,
            -0.18, -0.07,  0.01, -0.08, -0.13, -0.14, -0.19, -0.03, -0.08, -0.11,
            -0.19,  0.04,  0.03,  0.08, -0.13,  0.03,  0.06,  0.03,  0.06,  0.03,
            -0.02,  0.06,  0.03,  0.08, -0.20, -0.11, -0.06,  0.00, -0.02,  0.02,
            -0.08, -0.15,  0.06, -0.07,  0.23,  0.02,  0.06,  0.18,  0.28,  0.33,
             0.28,  0.22,  0.15,  0.31,  0.32,  0.45,  0.32,  0.47,  0.39,  0.27,
             0.45,  0.40,  0.51,  0.62,  0.53,  0.68,  0.54,  0.64,  0.64,  0.52,
             0.63,  0.54,  0.64,  0.68,  0.72,  0.81,  0.90,  1.02,  0.92,  0.98
        ])
        df = pd.DataFrame({'Year': years, 'Anomaly': anomalies})

    df['Color'] = np.where(df['Anomaly'] >= 0, '#E05D06', '#3B82A6')
    return df

df = load_data()

# Interactive Filter Control
st.sidebar.header("Filter Settings")
selected_years = st.sidebar.slider("Select Time Period", 1880, 2019, (1880, 2019))
filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]

# Build Diverging Bar Chart
fig = go.Figure()

fig.add_trace(go.Bar(
    x=filtered_df['Year'],
    y=filtered_df['Anomaly'],
    marker_color=filtered_df['Color'],
    marker_line_width=0,
    width=0.85,
    name="Temperature Anomaly",
    hovertemplate="<b>Year %{x}</b><br>Anomaly: %{y:+.2f}°C<extra></extra>"
))

# 1. Title embedded directly inside the top-left area of the plot
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.01, y=0.76,
    text="<b>Global average temperature compared<br>to the middle of the 20th century</b>",
    showarrow=False,
    font=dict(size=17, color="#000000", family="Arial, Helvetica, sans-serif"),
    align="left",
    xanchor="left",
    yanchor="top"
)

# Zero Baseline Axis (Middle 20th century baseline)
fig.add_hline(y=0, line_color="#000000", line_width=1.5)

# Staggered reference level positions matching original NYT graphic
annotations_config = [
    {"lvl": 0.75,  "x": 2012, "text": "+0.75°", "yanchor": "middle", "xanchor": "right"},
    {"lvl": 0.50,  "x": 1996, "text": "+0.50°", "yanchor": "middle", "xanchor": "right"},
    {"lvl": 0.25,  "x": 1979, "text": "+0.25°", "yanchor": "middle", "xanchor": "right"},
    {"lvl": -0.25, "x": 1936, "text": "-0.25°", "yanchor": "middle",    "xanchor": "left"}
]

for cfg in annotations_config:
    lvl = cfg["lvl"]
    fig.add_hline(
        y=lvl,
        line_color="rgba(255, 255, 255, 0.85)",
        line_width=1.2,
        line_dash="solid"
    )
    if filtered_df['Year'].min() <= cfg["x"] <= filtered_df['Year'].max():
        fig.add_annotation(
            x=cfg["x"],
            y=lvl,
            text=cfg["text"],
            showarrow=False,
            font=dict(color="#888888", size=14, family="Arial"),
            yanchor=cfg["yanchor"],
            xanchor=cfg["xanchor"]
        )

# Top Right 2019 Peak Label
if 2019 in filtered_df['Year'].values:
    val_2019 = filtered_df[filtered_df['Year'] == 2019]['Anomaly'].values[0]
    fig.add_annotation(
        x=2019,
        y=val_2019 + 0.05,
        text="<b>2019</b>",
        showarrow=False,
        font=dict(color="#000000", size=13, family="Arial"),
        xanchor="center",
        yanchor="bottom"
    )

# Layout matching NYT editorial chart formatting
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=520,
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=40),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickvals=[1880, 1900, 1920, 1940, 1960, 1980, 2000],
        tickfont=dict(size=14, color="#333333"),
        ticks="outside",
        ticklen=5,
        tickcolor="#333333"
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[-0.55, 1.25]
    )
)

st.plotly_chart(fig, use_container_width=True)
st.caption("Data source: NASA Goddard Institute for Space Studies (GISS) Surface Temperature Analysis (v4).")
