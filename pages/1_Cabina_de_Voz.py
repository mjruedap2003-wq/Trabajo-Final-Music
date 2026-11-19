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
    """Extrae energía RMS (0-100%), frecuencia dominante (Hz) y forma de onda."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        framerate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    if len(audio_np) == 0:
        return 0, 0, np.zeros(50)

    # Normalizar y calcular Energía RMS (0 a 100%)
    norm = audio_np / 32768.0
    rms = np.sqrt(np.mean(norm**2))
    energia_pct = int(np.clip(rms * 350, 0, 100))

    # Frecuencia fundamental aproximada por FFT (rango vocal 85 Hz - 600 Hz)
    fft_vals = np.abs(np.fft.rfft(norm))
    freqs = np.fft.rfftfreq(len(norm), 1.0 / framerate)
    mask = (freqs >= 85) & (freqs <= 600)
    pitch_hz = int(freqs[mask][np.argmax(fft_vals[mask])]) if np.any(mask) else 220

    # Submuestreo de 60 puntos para graficar la onda real de la voz
    paso = max(1, len(norm) // 60)
    onda_vis = np.abs(norm[::paso][:60])
    return energia_pct, pitch_hz, onda_vis

def responder_con_voz(frase):
    """Genera respuesta hablada de confirmación en la interfaz."""
    tts = gTTS(text=frase, lang="es")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp, format="audio/mp3", autoplay=True)

banner_dj("AMBIENTE 1 • VOICE SYNTH, VOCODER & NLP")
st.title("CABINA DE VOZ INTELIGENTE")

# Métricas superiores: Hardware Wokwi + Biometría Vocal
col1, col2, col3, col4 = st.columns(4)
col1.metric("TEMPO FÍSICO", f"{st.session_state.bpm_actual} BPM")
col2.metric("BASS DROPS", f"{st.session_state.drops_count:02d}")
col3.metric("ENERGÍA VOCAL", f"{st.session_state.metricas_voz['energia']} %")
col4.metric("TONO (PITCH)", f"{st.session_state.metricas_voz['pitch']} Hz")

st.subheader("1. Control por Voz Natural y Vocoder")
st.caption(
    "Comandos soportados: **'Fiesta'** · **'Chill'** · **'Alarma'** · "
    "**'Más rápido / Sube'** · **'Más lento / Baja'** · **'Silencio / Stop'** · **'Canta / Vocoder'**"
)

col_opt1, col_opt2 = st.columns(2)
usar_feedback_voz = col_opt1.toggle("🔊 Respuesta hablada de cabina", value=True)
modo_vocoder = col_opt2.toggle("🎹 Replicar tono de mi voz en Wokwi", value=False)

audio = mic_recorder(
    start_prompt="🎤 HABLAR AL MICRÓFONO",
    stop_prompt="⏹️ PROCESAR Y ENVIAR A WOKWI",
    format="wav",
    key="mic_dj"
)

if audio is not None:
    # 1. Análisis acústico directo de la señal de audio
    energia, pitch, onda_voz = analizar_acustica_wav(audio["bytes"])
    st.session_state.metricas_voz = {"energia": energia, "pitch": pitch}
    st.session_state.ultima_onda_voz = onda_voz

    if modo_vocoder and pitch > 0:
        enviar_comando(f"TONE:{pitch}")

    # 2. Reconocimiento de voz (NLP)
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
        audio_data = recognizer.record(source)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-ES").lower()
            st.info(f"🗣️ Reconocido: **'{texto.upper()}'** | Intensidad: **{energia}%** | Frecuencia: **{pitch} Hz**")

            comando_enviado = None
            respuesta_tts = ""

            if any(p in texto for p in ["fiesta", "party", "prendelo", "rumba"]):
                comando_enviado = "MODE:FIESTA"
                respuesta_tts = "Modo fiesta activado."
                st.success("🎉 ¡MODO FIESTA ACTIVADO! Luces neón y riff enviados a Wokwi.")
            elif any(p in texto for p in ["chill", "relajado", "suave", "tranquilo"]):
                comando_enviado = "MODE:CHILL"
                respuesta_tts = "Modo chill ambiental activado."
                st.success("🌊 ¡MODO CHILL ACTIVADO! Iluminación ambiental enviada a Wokwi.")
            elif any(p in texto for p in ["alarma", "alerta", "fuego", "emergencia"]):
                comando_enviado = "MODE:ALARMA"
                respuesta_tts = "Alerta crítica activada."
                st.warning("🚨 ¡MODO ALARMA ACTIVADO! Sirena y estrobo enviados a Wokwi.")
            elif any(p in texto for p in ["rápido", "sube", "acelera", "drop"]):
                comando_enviado = "TEMPO:UP"
                respuesta_tts = "Subiendo intensidad y tempo."
                st.success("⚡ ¡BOOST DE TEMPO! Pulso acelerado enviado a Wokwi.")
            elif any(p in texto for p in ["lento", "baja", "despacio"]):
                comando_enviado = "TEMPO:DOWN"
                respuesta_tts = "Reduciendo velocidad."
                st.info("🐢 Tempo reducido enviado a Wokwi.")
            elif any(p in texto for p in ["silencio", "stop", "para", "apaga", "quieto"]):
                comando_enviado = "MODE:STOP"
                respuesta_tts = "Pista en silencio."
                st.info("🔇 Actuadores en pausa enviados a Wokwi.")
            else:
                st.warning("No reconocí una escena exacta, pero se analizó tu espectro vocal.")

            # Detección de grito / euforia (>80% energía) como disparador extra
            if energia >= 80 and comando_enviado:
                st.toast("🔥 ¡Pico de euforia vocal detectado! Efecto extra disparado.", icon="🔥")

            if comando_enviado:
                enviar_comando(comando_enviado)
                st.session_state.setlist_voz.insert(0, {
                    "Hora": datetime.now().strftime("%H:%M:%S"),
                    "Frase": texto,
                    "Comando MQTT": comando_enviado,
                    "Energía": f"{energia}%",
                    "Pitch": f"{pitch} Hz"
                })
                if usar_feedback_voz and respuesta_tts:
                    responder_con_voz(respuesta_tts)

        except Exception:
            st.error("No se captó voz clara. Habla más cerca del micrófono e inténtalo de nuevo.")

# Visualización de la huella acústica de la última grabación
if st.session_state.ultima_onda_voz is not None:
    st.caption("📈 Huella de amplitud de tu última intervención vocal:")
    st.area_chart(st.session_state.ultima_onda_voz, color="#ff007f", height=120)

st.divider()
st.subheader("2. Pad Manual y Ecualizador Sincronizado")

c1, c2, c3, c4 = st.columns(4)
if c1.button("🎉 FIESTA", use_container_width=True):
    enviar_comando("MODE:FIESTA")
if c2.button("🌊 CHILL", use_container_width=True):
    enviar_comando("MODE:CHILL")
if c3.button("🚨 ALARMA", use_container_width=True):
    enviar_comando("MODE:ALARMA")
if c4.button("🔇 STOP", use_container_width=True):
    enviar_comando("MODE:STOP")

if st.button("🔄 SINCRONIZAR TELEMETRÍA DESDE WOKWI", use_container_width=True):
    sincronizar_telemetria()
    st.rerun()

bpm = st.session_state.bpm_actual
frecuencia = bpm / 60.0
x = np.linspace(0, 4 * np.pi, 40)
onda = np.abs(np.sin(x * frecuencia) * (bpm / 100.0)) + 0.2
st.bar_chart(onda, color="#00f0ff")
st.caption(f"Onda modulada por potenciómetro físico ({bpm} BPM) • {st.session_state.ultimo_evento}")

# Historial de sesión para la sustentación
if st.session_state.setlist_voz:
    with st.expander("📋 Setlist de Comandos Vocales (Historial en Vivo)", expanded=True):
        st.dataframe(st.session_state.setlist_voz, use_container_width=True, hide_index=True)
