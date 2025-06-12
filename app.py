import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Funktioner ---
def horizons(a, M=1):
    r_plus = M + np.sqrt(M**2 - a**2)
    r_minus = M - np.sqrt(M**2 - a**2)
    return r_plus, r_minus

def ergospheres_theta(theta, a, M=1):
    r_ergo_plus = M + np.sqrt(M**2 - (a * np.cos(theta))**2)
    r_ergo_minus = M - np.sqrt(M**2 - (a * np.cos(theta))**2)
    return r_ergo_plus, r_ergo_minus

def photon_sphere(a, M=1, prograde=True):
    sign = -1 if prograde else 1
    return 2*M*(1 + np.cos((2/3) * np.arccos(sign*a/M)))

def isco(a, M=1, prograde=True):
    Z1 = 1 + (1 - a**2)**(1/3) * ((1 + a)**(1/3) + (1 - a)**(1/3))
    Z2 = np.sqrt(3 * a**2 + Z1**2)
    sign = -1 if prograde else 1
    return 3 + Z2 + sign * np.sqrt((3 - Z1) * (3 + Z1 + 2 * Z2))

def kerr_surface(r, a, half=False):
    theta = np.linspace(0, np.pi, 100)
    phi = np.linspace(0, np.pi if half else 2*np.pi, 100)
    Theta, Phi = np.meshgrid(theta, phi)
    X = np.sqrt(r**2 + a**2) * np.sin(Theta) * np.cos(Phi)
    Y = np.sqrt(r**2 + a**2) * np.sin(Theta) * np.sin(Phi)
    Z = r * np.cos(Theta)
    return X, Y, Z

def ergo_surface(r_func, a, half=False):
    theta = np.linspace(0, np.pi, 100)
    phi = np.linspace(0, np.pi if half else 2*np.pi, 100)
    Theta, Phi = np.meshgrid(theta, phi)
    R = r_func(Theta)

    X = np.sqrt(R**2 + a**2) * np.sin(Theta) * np.cos(Phi)
    Y = np.sqrt(R**2 + a**2) * np.sin(Theta) * np.sin(Phi)
    Z = R * np.cos(Theta)
    return X, Y, Z

# --- Layout ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 14px !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-size: 16px !important;
        margin-bottom: 0.4rem;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stSlider, .stColorPicker, .stCheckbox {
        margin-bottom: 4px;
    }
    .stDivider {
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .stMarkdown {
        margin-bottom: 4px;
    }
    .stTitle {
        font-size: 16px !important;
        margin-bottom: 0.4rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Två kolumner ---
left, right = st.columns([1, 2], gap="large")

with left:
    st.title("Kerr-svarta hål (av Kristoffer Å)")
    st.markdown("### Inställningar")

    a = st.slider("Rotation (a)", 0.0, 1.0, 0.8)
    if a == 0:
        show_rs_plus = False
        show_rs_minus = False
        show_re_plus = False
        show_re_minus = False
        show_isco = False
        st.markdown("ℹ️ Visualisering i Schwarzschild-gränsen (a = 0)")
    show_surfaces = st.checkbox("Visa ytor (skal)", value=False)
    half_model = st.checkbox("Visa som öppet skal (halv kropp)", value=True)

    st.markdown("### Visa / Opacitet / Färg")

    cols = st.columns(4)

    with cols[0]:
        show_rs_plus = st.checkbox("rs⁺", True)
        rs_plus_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_rs+")
        rs_plus_color = st.color_picker("Färg", "#d3d3d3", key="col_rs+")
        show_rs_minus = st.checkbox("rs⁻", True)
        rs_minus_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_rs-")
        rs_minus_color = st.color_picker("Färg", "#dda0dd", key="col_rs-")

    with cols[1]:
        show_re_plus = st.checkbox("re⁺", True)
        re_plus_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_re+")
        re_plus_color = st.color_picker("Färg", "#add8e6", key="col_re+")
        show_re_minus = st.checkbox("re⁻", True)
        re_minus_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_re-")
        re_minus_color = st.color_picker("Färg", "#87cefa", key="col_re-")

    with cols[2]:
        show_photon = st.checkbox("ro", True)
        photon_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_photon")
        photon_color = st.color_picker("Färg", "#ffe4b5", key="col_photon")
        show_isco = st.checkbox("ISCOs", False)
        isco_opacity = st.slider("Opacitet", 0.1, 1.0, 1.0, key="op_isco")
        isco_pro_color = st.color_picker("Färg +", "#90ee90", key="col_isco+")
        isco_retro_color = st.color_picker("Färg -", "#c0f0c0", key="col_isco-")

    with cols[3]:
        show_equator_lines = st.checkbox("Visa ekvatorlinjer", value=True)
        show_equator_labels = st.checkbox("Visa etiketter", value=True)
        show_singularity_label = st.checkbox("Visa singularitetsetikett", value=True)
        sing_color = st.color_picker("Färg singularitet", "#f08080", key="col_sing")

# --- Beräkningar ---
r_s_plus, r_s_minus = horizons(a)
r_e_plus, r_e_minus = ergospheres_theta(np.pi/2, a)  # <== den här behövs!
photon_pro = photon_sphere(a)
isco_pro = isco(a, prograde=True)
isco_retro = isco(a, prograde=False)

fig = go.Figure()

def add_surface(r, a, opacity, color, half):
    X, Y, Z = kerr_surface(r, a, half)
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        opacity=opacity,
        surfacecolor=np.zeros_like(Z),
        colorscale=[[0, color], [1, color]],
        showscale=False
    ))

def add_ergo_surface(r_func, a, opacity, color, half):
    X, Y, Z = ergo_surface(r_func, a, half)
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        opacity=opacity,
        surfacecolor=np.zeros_like(Z),
        colorscale=[[0, color], [1, color]],
        showscale=False
    ))

# --- Lägg till skal ---
if show_surfaces and show_rs_plus:
    add_surface(r_s_plus, a, rs_plus_opacity, rs_plus_color, half_model)
if show_surfaces and show_rs_minus:
    add_surface(r_s_minus, a, rs_minus_opacity, rs_minus_color, half_model)
if show_surfaces and show_re_plus:
    add_ergo_surface(lambda theta: ergospheres_theta(theta, a)[0], a, re_plus_opacity, re_plus_color, half_model)
if show_surfaces and show_re_minus:
    add_ergo_surface(lambda theta: ergospheres_theta(theta, a)[1], a, re_minus_opacity, re_minus_color, half_model)
if show_surfaces and show_photon:
    add_surface(photon_pro, a, photon_opacity, photon_color, half_model)
if show_surfaces and show_isco:
    add_surface(isco_pro, a, isco_opacity, isco_pro_color, half_model)
    add_surface(isco_retro, a, isco_opacity, isco_retro_color, half_model)

# --- Singularitet ---
phi = np.linspace(0, 2*np.pi, 100)
x_s = a * np.cos(phi)
y_s = a * np.sin(phi)
z_s = np.zeros_like(phi)

if a == 0:
    # Punkt-singularitet i origo
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=6, color=sing_color),
        showlegend=False
    ))
else:
    # Ring-singularitet
    fig.add_trace(go.Scatter3d(
        x=x_s, y=y_s, z=z_s,
        mode='lines+markers',
        marker=dict(size=3, color=sing_color),
        line=dict(color=sing_color, width=6),
        showlegend=False
    ))

# Singularitetsetikett
# Singularitetsetikett
if show_equator_labels and show_singularity_label:
    if a == 0:
        x_lab, y_lab = 0, 0
        z_lab = 0.4
    else:
        angle = 3.8 * np.pi
        x_lab = a * np.cos(angle)
        y_lab = a * np.sin(angle)
        z_lab = 0.2 + 0.05 * np.sqrt(x_lab**2 + y_lab**2)

    fig.add_trace(go.Scatter3d(
        x=[x_lab, x_lab], y=[y_lab, y_lab], z=[0, z_lab],
        mode='lines',
        line=dict(color='black', width=1),
        showlegend=False
    ))
    
    if not show_surfaces:
        # Vit bakgrund bakom texten – endast om skal inte visas
        fig.add_trace(go.Scatter3d(
            x=[x_lab], y=[y_lab], z=[z_lab],
            mode='text',
            text=["<b>Singularitet</b>"],
            textfont=dict(color='white', size=17),
            showlegend=False
        ))

    # Svart förgrundstext
    fig.add_trace(go.Scatter3d(
        x=[x_lab], y=[y_lab], z=[z_lab],
        mode='text',
        text=["<b>Singularitet</b>"],
        textfont=dict(color='black', size=16),
        showlegend=False
    ))


# --- Rs, 1.5Rs, ISCO etiketter (endast Schwarzschild) ---
if show_equator_labels and a == 0.0:
    label_angle = 7 * np.pi / 4  # 315°
    for r_val, label in zip([2.0, 3.0, 6.0], ['Händelsehorisont (Rs)', 'Fotonsfär (1.5Rs)', 'ISCO (3Rs)']):
        x_pos = r_val * np.cos(label_angle)
        y_pos = r_val * np.sin(label_angle)
        fig.add_trace(go.Scatter3d(
            x=[0, x_pos], y=[0, y_pos], z=[0, 0],
            mode='lines',
            line=dict(color='black', width=1),
            showlegend=False
        ))
        fig.add_trace(go.Scatter3d(
            x=[x_pos], y=[y_pos], z=[0],
            mode='markers+text',
            marker=dict(size=4, color='black'),
            text=[f"<b>{label}</b>"],
            textposition='top center',
            textfont=dict(color='black', size=15),
            showlegend=False
        ))

def plot_equator(r_val, color, name):
    if a == 0 and name in ["rs−", "re+", "re-"]:
        return  # Dölj dessa helt vid Schwarzschild

    r = np.sqrt(r_val**2 + a**2)
    phi = np.linspace(0, 2*np.pi, 200)
    X_eq = r * np.cos(phi)
    Y_eq = r * np.sin(phi)
    Z_eq = np.zeros_like(phi)

    if show_equator_lines:
        fig.add_trace(go.Scatter3d(x=X_eq, y=Y_eq, z=Z_eq,
            mode='lines', line=dict(color=color, width=7)))

    # Dölj vissa etiketter i Schwarzschild
    hide_labels_in_schwarzschild = ["rs+", "isco +", "ro", "isco −"]
    # Förgrund och ev. vit bakgrund
    if show_equator_labels and not (a == 0 and name in hide_labels_in_schwarzschild):
        label_boost = {
            "rs+": 1.6,
            "rs−": 1.4,
            "re+": 1.2,
            "re-": 1.8,
            "ro": 1.5,
            "isco +": 0.8,
            "isco −": 0.7
        }
        max_r = max(r_s_plus, r_s_minus, r_e_plus, r_e_minus, photon_pro, isco_pro, isco_retro)
        scale = 0.6
        boost = label_boost.get(name, 1.0)
        z_offset = boost * (0.1 + scale * (1 - r_val / max_r))
        fig.add_trace(go.Scatter3d(
            x=[0, 0], y=[-r, -r], z=[0, z_offset],
            mode='lines', line=dict(color='black', width=4), showlegend=False
        ))
        
        if not show_surfaces:
            # Bakgrund (vit) – endast när skal inte visas
            fig.add_trace(go.Scatter3d(
                x=[0], y=[-r], z=[z_offset],
                mode='text',
                text=[f"<b>{name}</b>"],
                textfont=dict(color='white', size=20),
                showlegend=False
            ))
        
        # Förgrund (svart)
        fig.add_trace(go.Scatter3d(
            x=[0], y=[-r], z=[z_offset],
            mode='text',
            text=[f"<b>{name}</b>"],
            textfont=dict(color='black', size=18),
            showlegend=False
        ))

if show_rs_plus:
    plot_equator(r_s_plus, rs_plus_color, "rs+")
if show_rs_minus:
    plot_equator(r_s_minus, rs_minus_color, "rs−")
if show_re_plus:
    plot_equator(r_e_plus, re_plus_color, "re+")
if show_re_minus:
    plot_equator(r_e_minus, re_minus_color, "re-")
if show_photon:
    plot_equator(photon_pro, photon_color, "ro")
if show_isco:
    plot_equator(isco_pro, isco_pro_color, "isco +")
    plot_equator(isco_retro, isco_retro_color, "isco −")

# --- Layout ---
fig.update_layout(
    scene=dict(
        xaxis=dict(title='X', backgroundcolor='white', color='gray'),
        yaxis=dict(title='Y', backgroundcolor='white', color='gray'),
        zaxis=dict(title='Z', backgroundcolor='white', color='gray'),
        aspectmode='data',
        bgcolor='white',
        camera=dict(eye=dict(x=-1.5, y=-1.5, z=0.8))
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    paper_bgcolor='white',
    height=700,
    showlegend=False
)

# --- Visualisering ---
with right:
    st.plotly_chart(fig, use_container_width=True)

# --- Export ---
st.markdown("### Exportera visualiseringen")
if st.button("Spara som PNG"):
    now = datetime.datetime.now().strftime("%y%m%d%H%M")  # Ex: 2504161928
    filename = f"BH_sim_{now}.png"
    fig.write_image(filename, width=1200, height=800)
    st.success(f"✅ Bild sparad som \"{filename}\"")

