import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import streamlit as st
import uuid
import time

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_CMD = "miguel_dj_2026/comando"
TOPIC_TEL = "miguel_dj_2026/telemetria"

def init_mqtt():
    if "bpm_actual" not in st.session_state:
        st.session_state.bpm_actual = 120
    if "drops_count" not in st.session_state:
        st.session_state.drops_count = 0
    if "ultimo_evento" not in st.session_state:
        st.session_state.ultimo_evento = "Esperando señal de la mesa..."

def enviar_comando(comando: str):
    init_mqtt()
    try:
        publish.single(
            topic=TOPIC_CMD,
            payload=comando,
            hostname=BROKER,
            port=PORT,
            qos=1,
            client_id=f"ST-CMD-{uuid.uuid4().hex[:6]}"
        )
    except Exception as e:
        st.error(f"Error enviando orden MQTT: {e}")

def sincronizar_telemetria():
    init_mqtt()
    mensajes = []

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(TOPIC_TEL)

    def on_message(client, userdata, msg):
        mensajes.append(msg.payload.decode("utf-8").strip())

    try:
        client = mqtt.Client(client_id=f"ST-READ-{uuid.uuid4().hex[:6]}")
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, 30)
        client.loop_start()
        time.sleep(0.4)
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass

    for payload in mensajes:
        if payload.startswith("BPM:"):
            try:
                st.session_state.bpm_actual = int(payload.split(":")[1])
                st.session_state.ultimo_evento = f"🎚️ Tempo ajustado a {st.session_state.bpm_actual} BPM"
            except ValueError:
                pass
        elif payload == "PAD:DROP":
            st.session_state.drops_count += 1
            st.session_state.ultimo_evento = f"💥 ¡BASS DROP DISPARADO! (Total: {st.session_state.drops_count})"
