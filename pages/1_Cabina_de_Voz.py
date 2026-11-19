import streamlit as st
import numpy as np
import io
import wave
from datetime import datetime
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from mqtt_helper import sincronizar_telemetria, enviar_comando
from ui_dj import aplicar_estilo_dj, banner_dj

st.set_page_config(page_title="Cabina de Voz DJ", page_icon="🎙️", layout="centered")
aplicar_estilo_dj()
sincronizar_telemetria()

if "setlist_voz" not in st.session_state:
    st.session_state.setlist_voz = []
if "ultima_onda_voz" not in st.session_state:
    st.session_state.ultima_onda_voz = None
if "metricas_voz" not in st.session_state:
    st.session_state.metricas_voz = {"energia": 0, "pitch": 0}

def analizar_acustica_wav(wav_bytes):
    """Extrae energía RMS (0-100%), frecuencia dominante (Hz) y forma de onda vocal."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        framerate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    if len(audio_np) == 0:
        return 0, 0, np.zeros(60)

    norm = audio_np / 32768.0
    rms = np.sqrt(np.mean(norm**2))
    energia_pct = int(np.clip(rms * 350, 0, 100))

    fft_vals = np.abs(np.fft.rfft(norm))
    freqs = np.fft.rfftfreq(len(norm), 1.0 / framerate)
    mask = (freqs >= 85) & (freqs <= 600)
    pitch_hz = int(freqs[mask][np.argmax(fft_vals[mask])]) if np.any(mask) else 220

    # Extrae 80 puntos de amplitud para mostrar tanto los picos altos como los niveles bajitos
    paso = max(1, len(norm) // 80)
    onda_vis = np.abs(norm[::paso][:80])
    return energia_pct, pitch_hz, onda_vis

def responder_con_voz(frase):
    """Genera respuesta hablada de confirmación en la interfaz."""
    tts = gTTS(text=frase, lang="es")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp, format="audio/mp3", autoplay=True)

banner_dj("AMBIENTE 1 • VOICE SYNTH & VOCODER")
st.title("CABINA DE VOZ INTELIGENTE")

# Métricas superiores
col1, col2, col3, col4 = st.columns(4)
col1.metric("VELOCIDAD (BPM)", f"{st.session_state.bpm_actual}")
col2.metric("BASS DROPS", f"{st.session_state.drops_count:02d}")
col3.metric("ENERGÍA VOCAL", f"{st.session_state.metricas_voz['energia']} %")
col4.metric("TONO (PITCH)", f"{st.session_state.metricas_voz['pitch']} Hz")

st.subheader("1. Control por Voz y Vocoder")
st.caption(
    "Comandos: **'Fiesta'** · **'Chill'** · **'Alarma'** · "
    "**'Más rápido'** · **'Más lento'** · **'Silencio'**"
)

col_opt1, col_opt2 = st.columns(2)
usar_feedback_voz = col_opt1.toggle("🔊 Respuesta hablada de cabina", value=True)
modo_vocoder = col_opt2.toggle("🎹 Replicar tono de mi voz en Wokwi", value=True)

audio = mic_recorder(
    start_prompt="🎤 HABLAR AL MICRÓFONO",
    stop_prompt="⏹️ PROCESAR Y ENVIAR A WOKWI",
    format="wav",
    key="mic_dj"
)

if audio is not None:
    energia, pitch, onda_voz = analizar_acustica_wav(audio["bytes"])
    st.session_state.metricas_voz = {"energia": energia, "pitch": pitch}
    st.session_state.ultima_onda_voz = onda_voz

    if modo_vocoder and pitch > 0:
        enviar_comando(f"TONE:{pitch}")

    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            st.info(f"🗣️ Reconocido: **'{texto.upper()}'** | Intensidad: **{energia}%** | Tono: **{pitch} Hz**")

            comando_enviado = None
            respuesta_tts = ""

            if any(p in texto for p in ["fiesta", "party", "prendelo", "rumba"]):
                comando_enviado = "MODE:FIESTA"
                respuesta_tts = "Modo fiesta activado."
                st.success("🎉 ¡MODO FIESTA ACTIVADO! Luces y melodía enviadas a Wokwi.")
            elif any(p in texto for p in ["chill", "relajado", "suave", "tranquilo"]):
                comando_enviado = "MODE:CHILL"
                respuesta_tts = "Modo chill activado."
                st.success("🌊 ¡MODO CHILL ACTIVADO! Ambiente suave enviado a Wokwi.")
            elif any(p in texto for p in ["alarma", "alerta", "fuego", "emergencia"]):
                comando_enviado = "MODE:ALARMA"
                respuesta_tts = "Alerta activada."
                st.warning("🚨 ¡MODO ALARMA ACTIVADO! Sirena enviada a Wokwi.")
            elif any(p in texto for p in ["rápido", "sube", "acelera", "corto"]):
                comando_enviado = "TEMPO:UP"
                respuesta_tts = "Notas más cortas y rápidas."
                st.success("⚡ ¡Notas más cortas y rápidas enviadas a Wokwi!")
            elif any(p in texto for p in ["lento", "baja", "despacio", "largo"]):
                comando_enviado = "TEMPO:DOWN"
                respuesta_tts = "Notas más largas y lentas."
                st.info("🐢 Notas más largas y sostenidas enviadas a Wokwi.")
            elif any(p in texto for p in ["silencio", "stop", "para", "apaga", "quieto"]):
                comando_enviado = "MODE:STOP"
                respuesta_tts = "Silencio."
                st.info("🔇 Actuadores detenidos en Wokwi.")

            if energia >= 80 and comando_enviado:
                st.toast("🔥 ¡Pico alto de voz detectado!", icon="🔥")

            if comando_enviado:
                enviar_comando(comando_enviado)
                st.session_state.setlist_voz.insert(0, {
                    "Hora": datetime.now().strftime("%H:%M:%S"),
                    "Frase": texto,
                    "Comando": comando_enviado,
                    "Tono": f"{pitch} Hz"
                })
                if usar_feedback_voz and respuesta_tts:
                    responder_con_voz(respuesta_tts)

        except Exception:
            if not modo_vocoder:
                st.error("No se captó voz clara. Intenta hablar más cerca del micrófono.")

# Gráfica rojiza/magenta de los picos y niveles bajos de tu voz
if st.session_state.ultima_onda_voz is not None:
    st.caption("📈 Nivel de Voz en Tiempo Real (Picos altos y niveles bajos):")
    st.area_chart(st.session_state.ultima_onda_voz, color="#ff0055", height=150)

st.divider()
st.subheader("2. Pad de Disparo Rápido")

c1, c2, c3, c4 = st.columns(4)
if c1.button("🎉 FIESTA", use_container_width=True):
    enviar_comando("MODE:FIESTA")
if c2.button("🌊 CHILL", use_container_width=True):
    enviar_comando("MODE:CHILL")
if c3.button("🚨 ALARMA", use_container_width=True):
    enviar_comando("MODE:ALARMA")
if c4.button("🔇 STOP", use_container_width=True):
    enviar_comando("MODE:STOP")

if st.button("🔄 SINCRONIZAR DATOS DE WOKWI", use_container_width=True):
    sincronizar_telemetria()
    st.rerun()

if st.session_state.setlist_voz:
    with st.expander("📋 Historial de Comandos Vocales", expanded=True):
        st.dataframe(st.session_state.setlist_voz, use_container_width=True, hide_index=True)
