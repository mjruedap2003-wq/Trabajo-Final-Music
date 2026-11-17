import streamlit as st
from mqtt_helper import init_mqtt, sincronizar_telemetria, enviar_comando
from ui_dj import aplicar_estilo_dj, banner_dj

st.set_page_config(page_title="Neon DJ Booth IoT", page_icon="🎧", layout="centered")
aplicar_estilo_dj()
sincronizar_telemetria()

banner_dj("MASTER CONSOLE • CONECTADO A ESP32 WOKWI")
st.title("NEON DJ BOOTH")
st.markdown("<p style='text-align:center; color:#94a3b8;'>MESA DE MEZCLAS MULTIMODAL BIDIRECCIONAL</p>", unsafe_allow_html=True)

# Panel de telemetría física recibida desde Wokwi
col1, col2 = st.columns(2)
col1.metric("TEMPO (POTENCIÓMETRO)", f"{st.session_state.bpm_actual} BPM")
col2.metric("BASS DROPS (BOTÓN FX)", f"{st.session_state.drops_count:02d}")

st.info(f"📡 **Última señal desde Wokwi:** {st.session_state.ultimo_evento}")

if st.button("🔄 SINCRONIZAR CONTROLES DE WOKWI"):
    sincronizar_telemetria()
    st.rerun()

st.divider()

st.subheader("🎛️ Ambientes de Interacción")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div style="border: 2px solid #00f0ff; border-radius: 12px; padding: 18px; background: rgba(0,240,255,0.06);">
        <h3 style="margin-top:0; font-size:1.05rem;">🎙️ 1. Cabina de Voz</h3>
        <p style="font-size:0.85rem; color:#cbd5e1;">Controla las escenas de luces NeoPixel y riffs del Buzzer mediante comandos de voz.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div style="border: 2px solid #ff007f; border-radius: 12px; padding: 18px; background: rgba(255,0,127,0.06);">
        <h3 style="margin-top:0; font-size:1.05rem;">🖼️ 2. Visualizador RGB</h3>
        <p style="font-size:0.85rem; color:#cbd5e1;">Sube la portada de un álbum o imagen para proyectar su paleta RGB en el escenario físico.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.caption("Usa el menú lateral izquierdo para entrar a cada ambiente, o prueba la conexión rápida aquí:")
if st.button("🔊 PROBAR SEÑAL EN MESA (MODE:FIESTA)"):
    enviar_comando("MODE:FIESTA")
    st.success("¡Señal enviada! Mira las luces NeoPixel y escucha el buzzer en Wokwi.")
