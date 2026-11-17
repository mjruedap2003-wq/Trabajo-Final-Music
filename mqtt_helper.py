import paho.mqtt.client as mqtt
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

    if "mqtt_client" not in st.session_state or not st.session_state.mqtt_client.is_connected():
        # Diccionario compartido en memoria para el hilo en segundo plano de MQTT
        shared_data = {
            "bpm": st.session_state.bpm_actual,
            "drops": st.session_state.drops_count,
            "evento": st.session_state.ultimo_evento,
        }

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe(TOPIC_TEL)

        def on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8").strip()
            if payload.startswith("BPM:"):
                try:
                    shared_data["bpm"] = int(payload.split(":")[1])
                    shared_data["evento"] = f"🎚️ Tempo ajustado a {shared_data['bpm']} BPM"
                except ValueError:
                    pass
            elif payload == "PAD:DROP":
                shared_data["drops"] += 1
                shared_data["evento"] = f"💥 ¡BASS DROP DISPARADO! (Total: {shared_data['drops']})"

        client = mqtt.Client(client_id=f"Streamlit-DJ-{uuid.uuid4().hex[:8]}")
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        inicio = time.time()
        while not client.is_connected() and (time.time() - inicio) < 2.0:
            time.sleep(0.1)

        st.session_state.mqtt_client = client
        st.session_state.mqtt_shared = shared_data

def sincronizar_telemetria():
    init_mqtt()
    st.session_state.bpm_actual = st.session_state.mqtt_shared["bpm"]
    st.session_state.drops_count = st.session_state.mqtt_shared["drops"]
    st.session_state.ultimo_evento = st.session_state.mqtt_shared["evento"]

def enviar_comando(comando: str):
    init_mqtt()
    info = st.session_state.mqtt_client.publish(TOPIC_CMD, comando, qos=1)
    info.wait_for_publish(timeout=2.0)
