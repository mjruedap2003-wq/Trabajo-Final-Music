import streamlit as st
import numpy as np
import io
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from mqtt_helper import sincronizar_telemetria, enviar_comando
from ui_dj import aplicar_estilo_dj, banner_dj

st.set_page_config(page_title="Cabina de Voz DJ", page_icon="🎙️", layout="centered")
aplicar_estilo_dj()
sincronizar_telemetria()

banner_dj("AMBIENTE 1 • VOICE SYNTH & SOUND FX")
st.title("CABINA DE VOZ")

col1, col2 = st.columns(2)
col1.metric("TEMPO FÍSICO", f"{st.session_state.bpm_actual} BPM")
col2.metric("BASS DROPS", f"{st.session_state.drops_count:02d}")

st.subheader("1. Dispara una Escena por Voz")
st.caption("Di: **'Fiesta'**, **'Chill'** o **'Alarma'**")

audio = mic_recorder(start_prompt="🎤 HABLAR AL MICRÓFONO", stop_prompt="⏹️ ENVIAR ESCENA A WOKWI", format="wav", key="mic_dj")

if audio is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            st.info(f"🗣️ Comando reconocido: **'{texto.upper()}'**")

            if "fiesta" in texto or "party" in texto:
                enviar_comando("MODE:FIESTA")
                st.success("🎉 ¡MODO FIESTA ACTIVADO! Luces neón y riff enviados a Wokwi.")
            elif "chill" in texto or "relajado" in texto or "suave" in texto:
                enviar_comando("MODE:CHILL")
                st.success("🌊 ¡MODO CHILL ACTIVADO! Iluminación ambiental enviada a Wokwi.")
            elif "alarma" in texto or "alerta" in texto or "fuego" in texto:
                enviar_comando("MODE:ALARMA")
                st.warning("🚨 ¡MODO ALARMA ACTIVADO! Sirena y estrobo enviados a Wokwi.")
            else:
                st.warning("No reconocí el modo. Intenta decir 'Fiesta', 'Chill' o 'Alarma'.")
        except Exception:
            st.error("No se captó audio claro. Intenta hablar más cerca del micrófono.")

st.divider()
st.subheader("2. Control Manual y Ecualizador en Vivo")

c1, c2, c3 = st.columns(3)
if c1.button("🎉 FIESTA"):
    enviar_comando("MODE:FIESTA")
if c2.button("🌊 CHILL"):
    enviar_comando("MODE:CHILL")
if c3.button("🚨 ALARMA"):
    enviar_comando("MODE:ALARMA")

# Ecualizador dinámico que reacciona a los BPM físicos del potenciómetro en Wokwi
if st.button("🔄 ACTUALIZAR ECUALIZADOR DESDE WOKWI"):
    sincronizar_telemetria()
    st.rerun()

bpm = st.session_state.bpm_actual
frecuencia = bpm / 60.0
x = np.linspace(0, 4 * np.pi, 40)
onda = np.abs(np.sin(x * frecuencia) * (bpm / 100.0)) + 0.2
st.bar_chart(onda, color="#00f0ff")
st.caption(f"Visualización de onda modulada por el potenciómetro físico ({bpm} BPM) • {st.session_state.ultimo_evento}")
