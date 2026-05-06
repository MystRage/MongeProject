import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


# ---------------- PAGE SETUP ----------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
.main-container {
    display: flex;
    justify-content: center;
}
.plot-container {
    width: 70%;
}
</style>
""", unsafe_allow_html=True)


# ---------------- GEOMETRY ----------------
def rotate_about_x(x, y, z, theta):
    y_new = y * np.cos(theta) - z * np.sin(theta)
    z_new = y * np.sin(theta) + z * np.cos(theta)
    return x, y_new, z_new


def build_animation(point):
    x, y, z = point
    steps = 50

    phase_proj = 0.35
    phase_hold = 0.15
    phase_rot = 0.5

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scene"}, {"type": "xy"}]],
        column_widths=[0.6, 0.4],
        subplot_titles=("3D Geometry", "Monge 2D Sheet")
    )

    frames = []

    for i in range(steps):
        t = i / (steps - 1)

        if t < phase_proj:
            alpha = t / phase_proj
            top = (x, y, z * (1 - alpha))
            front = (x, y * (1 - alpha), z)
            theta = 0

        elif t < phase_proj + phase_hold:
            top = (x, y, 0)
            front = (x, 0, z)
            theta = 0

        else:
            alpha = (t - phase_proj - phase_hold) / phase_rot
            top = rotate_about_x(x, y, 0, -alpha * np.pi/2)
            front = (x, 0, z)
            theta = -alpha * np.pi/2

        r = [-30, 30]
        X = np.array([[r[0], r[1]], [r[0], r[1]]])
        Y = np.array([[r[0], r[0]], [r[1], r[1]]])
        Z = np.zeros_like(X)

        Y_rot = Y * np.cos(theta)
        Z_rot = Y * np.sin(theta)

        frames.append(go.Frame(data=[

            # ===== 3D =====
            go.Scatter3d(
                x=[x], y=[y], z=[z],
                mode='markers+text',
                text=["A"],
                textfont=dict(color="black", size=14),
                showlegend=False
            ),

            go.Scatter3d(
                x=[top[0]], y=[top[1]], z=[top[2]],
                mode='markers+text',
                text=["A'"],
                textfont=dict(color="black", size=14),
                showlegend=False
            ),

            go.Scatter3d(
                x=[front[0]], y=[front[1]], z=[front[2]],
                mode='markers+text',
                text=["A''"],
                textfont=dict(color="black", size=14),
                showlegend=False
            ),

            # HP (rotating)
            go.Surface(
                x=X, y=Y_rot, z=Z_rot,
                opacity=0.25,
                showscale=False
            ),

            # VP (fixed)
            go.Surface(
                x=X, y=np.zeros_like(X), z=Y,
                opacity=0.25,
                showscale=False
            ),

            # XY hinge
            go.Scatter3d(
                x=[-30, 30], y=[0, 0], z=[0, 0],
                mode='lines',
                line=dict(width=6),
                showlegend=False
            ),

            # ===== 2D =====
            go.Scatter(
                x=[front[0]], y=[front[2]],
                mode='markers+text',
                marker=dict(size=8),
                text=["A''"],
                textposition="top center",
                textfont=dict(color="black", size=20),
                showlegend=False
            ),

            go.Scatter(
                x=[top[0]], y=[top[2]],
                mode='markers+text',
                marker=dict(size=8),
                text=["A'"],
                textposition="bottom center",
                textfont=dict(color="black", size=20),
                showlegend=False
            ),

            go.Scatter(
                x=[-30, 30], y=[0, 0],
                mode='lines',
                line=dict(width=4, color="black"),
                showlegend=False
            )

        ], traces=list(range(9))))

    fig.add_traces(frames[0].data)

    # ---------------- LAYOUT ----------------
    fig.update_layout(
        height=800,

        paper_bgcolor="white",
        plot_bgcolor="#E5ECF6",   # 🔵 2D light blue

        font=dict(color="black"),
        margin=dict(l=20, r=120, t=50, b=20),

        # 🔵 3D light blue background
        scene=dict(
            xaxis=dict(
                range=[-30, 30],
                backgroundcolor="#E5ECF6",
                gridcolor="white",
                showbackground=True
            ),
            yaxis=dict(
                range=[-30, 30],
                backgroundcolor="#E5ECF6",
                gridcolor="white",
                showbackground=True
            ),
            zaxis=dict(
                range=[-30, 30],
                backgroundcolor="#E5ECF6",
                gridcolor="white",
                showbackground=True
            ),
            aspectmode='cube'
        ),

        # 🔵 2D grid styling
        xaxis=dict(
            range=[-30, 30],
            showgrid=True,
            gridcolor="white",
            tickfont=dict(color="black", size=14),
            zeroline=False
        ),
        yaxis=dict(
            range=[-30, 30],
            scaleanchor="x",
            showgrid=True,
            gridcolor="white",
            tickfont=dict(color="black", size=14),
            zeroline=False
        ),

        # Play button
        updatemenus=[dict(
            type="buttons",
            x=0.05,
            y=1.05,
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 70}}])
            ]
        )]
    )

    fig.frames = frames
    return fig


# ---------------- UI ----------------


col1, col2, col3 = st.columns(3)

with col1:
    x = st.number_input("X", value=10)

with col2:
    y = st.number_input("Y", value=20)

with col3:
    z = st.number_input("Z", value=15)

st.markdown('<div class="main-container"><div class="plot-container">', unsafe_allow_html=True)

if st.button("Render"):
    fig = build_animation((x, y, z))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)