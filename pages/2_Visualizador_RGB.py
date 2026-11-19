import streamlit as st
import numpy as np
from PIL import Image, ImageOps
from mqtt_helper import sincronizar_telemetria, enviar_comando
from ui_dj import aplicar_estilo_dj, banner_dj

st.set_page_config(page_title="Visualizador RGB", page_icon="🖼️", layout="centered")
aplicar_estilo_dj()
sincronizar_telemetria()

# Guarda el último Bass Drop que ya disparó un efecto visual
if "ultimo_drop_visual" not in st.session_state:
    st.session_state.ultimo_drop_visual = st.session_state.drops_count

banner_dj("AMBIENTE 2 • IMAGE-TO-SYNTH & PIXEL MAPPING")
st.title("VISUALIZADOR RGB")

st.markdown("Convierte cualquier imagen o portada en **música y luces**: el sistema analiza su **temperatura de color** y **luminosidad** para componer un riff en el buzzer y mapear su paleta en los 16 NeoPixels.")

archivo = st.file_uploader("📂 Sube una imagen o portada (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if archivo is not None:
    img = Image.open(archivo).convert("RGB")
    
    # Solo aplica el efecto UNA VEZ si llegó un Bass Drop nuevo desde Wokwi
    if st.session_state.drops_count > st.session_state.ultimo_drop_visual:
        img_mostrar = ImageOps.solarize(img, threshold=128)
        efecto_txt = "⚡ REMIX VISUAL MOMENTÁNEO (Bass Drop recibido)"
        # Actualiza el registro para que en la siguiente interacción vuelva a la original
        st.session_state.ultimo_drop_visual = st.session_state.drops_count
    else:
        img_mostrar = img
        efecto_txt = "🎨 MODO ORIGINAL"

    # Extraer 3 colores representativos dividiendo la imagen en tercios
    img_small = img.resize((60, 60))
    arr = np.array(img_small)
    
    c1_rgb = arr[:, :20].mean(axis=(0, 1)).astype(int)
    c2_rgb = arr[:, 20:40].mean(axis=(0, 1)).astype(int)
    c3_rgb = arr[:, 40:].mean(axis=(0, 1)).astype(int)

    # Color dominante global
    r, g, b = arr.mean(axis=(0, 1)).astype(int)
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    brillo = int((0.299 * r + 0.587 * g + 0.114 * b))

    # Determinar el género/escala musical según la colorimetría
    if r > b and r > g:
        vibe = "🔥 CALIDA / ENERGÉTICA (Escala Mayor Rápida)"
        estilo_code = "WARM"
    elif b > r and b > g:
        vibe = "❄️ FRÍA / AMBIENTAL (Arpegio Profundo)"
        estilo_code = "COLD"
    else:
        vibe = "🌿 NEÓN / SYNTHWAVE (Secuencia Electrónica)"
        estilo_code = "NEON"

    col_img, col_info = st.columns([1.2, 1])
    with col_img:
        st.image(img_mostrar, caption=efecto_txt, use_container_width=True)
    with col_info:
        # Mostrar paleta de 3 colores extraídos
        p1, p2, p3 = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in (c1_rgb, c2_rgb, c3_rgb)]
        st.markdown(f"""
        <div style="display:flex; height:70px; border-radius:12px; overflow:hidden; border:2px solid #fff; margin-bottom:10px;">
            <div style="flex:1; background:{p1};"></div>
            <div style="flex:1; background:{p2};"></div>
            <div style="flex:1; background:{p3};"></div>
        </div>
        <p style="font-size:0.85rem; margin:4px 0;"><b>Vibe detectado:</b><br>{vibe}</p>
        <p style="font-size:0.85rem; margin:4px 0;"><b>Luminosidad:</b> {brillo}/255</p>
        """, unsafe_allow_html=True)

        if st.button("🎹 SINTETIZAR IMAGEN EN WOKWI"):
            comando = f"SYNTH:{c1_rgb[0]},{c1_rgb[1]},{c1_rgb[2]}|{c2_rgb[0]},{c2_rgb[1]},{c2_rgb[2]}|{estilo_code}|{brillo}"
            enviar_comando(comando)
            st.success("¡Melodía y paleta RGB proyectadas en la mesa DJ!")

st.divider()
st.subheader("🎨 Selector Rápido de Escena")
color_hex = st.color_picker("O elige un color sólido para los NeoPixels", "#00f0ff")

if st.button("✨ APLICAR COLOR MANUAL"):
    h = color_hex.lstrip("#")
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    enviar_comando(f"RGB:{r},{g},{b}")
    st.success(f"¡LEDs actualizados a RGB({r}, {g}, {b})!")

st.divider()
if st.button("🔄 SINCRONIZAR CON MESA WOKWI"):
    sincronizar_telemetria()
    st.rerun()

st.info(f"🎛️ **Estado físico:** {st.session_state.ultimo_evento} | **Tempo:** {st.session_state.bpm_actual} BPM")
