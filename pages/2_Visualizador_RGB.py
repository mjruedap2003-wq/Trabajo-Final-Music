import streamlit as st
import numpy as np
from PIL import Image
from mqtt_helper import sincronizar_telemetria, enviar_comando
from ui_dj import aplicar_estilo_dj, banner_dj

st.set_page_config(page_title="Visualizador RGB", page_icon="🖼️", layout="centered")
aplicar_estilo_dj()
sincronizar_telemetria()

banner_dj("AMBIENTE 2 • ALBUM ART TO NEOPIXEL SYNC")
st.title("VISUALIZADOR RGB")

st.markdown("Sube la portada de un álbum o cualquier imagen para extraer su color dominante y proyectarlo en los **16 LEDs NeoPixel** de Wokwi.")

archivo = st.file_uploader("📂 Sube una imagen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if archivo is not None:
    img = Image.open(archivo).convert("RGB")
    
    # Calcular color dominante redimensionando a una muestra rápida
    img_pequena = img.resize((50, 50))
    arr = np.array(img_pequena).reshape(-1, 3)
    
    # Filtrar píxeles muy oscuros para obtener el color vibrante principal
    brillo = arr.sum(axis=1)
    vibrantes = arr[brillo > 90] if np.any(brillo > 90) else arr
    r, g, b = vibrantes.mean(axis=0).astype(int)
    hex_color = f"#{r:02x}{g:02x}{b:02x}"

    col_img, col_info = st.columns([1.2, 1])
    with col_img:
        st.image(img, caption="Portada cargada", use_container_width=True)
    with col_info:
        st.markdown(f"""
        <div style="background:{hex_color}; border:3px solid #ffffff; border-radius:15px; height:140px; box-shadow: 0 0 25px {hex_color}; margin-bottom:12px;"></div>
        <p style="text-align:center; font-weight:bold;">RGB: ({r}, {g}, {b})<br>HEX: {hex_color.upper()}</p>
        """, unsafe_allow_html=True)

        if st.button("💡 PROYECTAR COLOR EN WOKWI"):
            enviar_comando(f"RGB:{r},{g},{b}")
            st.success(f"¡Color RGB({r}, {g}, {b}) enviado al anillo NeoPixel!")

st.divider()
st.subheader("🎨 Selector Manual de Escenario")
color_hex = st.color_picker("O elige un color personalizado para la cabina", "#00f0ff")

if st.button("✨ APLICAR COLOR MANUAL A NEOPIXELS"):
    h = color_hex.lstrip("#")
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    enviar_comando(f"RGB:{r},{g},{b}")
    st.success(f"¡LEDs actualizados a RGB({r}, {g}, {b})!")

st.divider()
if st.button("🔄 LEER EVENTOS DE LA MESA WOKWI"):
    sincronizar_telemetria()
    st.rerun()

st.info(f"🎛️ **Estado de la mesa:** {st.session_state.ultimo_evento} | **Tempo:** {st.session_state.bpm_actual} BPM")
