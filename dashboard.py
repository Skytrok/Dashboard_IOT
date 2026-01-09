import streamlit as st
import paho.mqtt.client as mqtt
import time
import pandas as pd
import plotly.graph_objs as go

# ---------------------------------------------------------
# MQTT CONFIG
# ---------------------------------------------------------
BROKER = "51.103.121.129"
PORT = 1883

TOPIC_TEMP = "esp32/sensors/temperature"
TOPIC_LUMI = "esp32/sensors/luminosity"

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "temperature" not in st.session_state:
    st.session_state.temperature = 0

if "luminosity" not in st.session_state:
    st.session_state.luminosity = 0

if "history" not in st.session_state:
    st.session_state.history = {
        "time": [],
        "temperature": [],
        "luminosity": []
    }

# ---------------------------------------------------------
# POLLING MQTT : Connexion courte compatible Streamlit Cloud
# ---------------------------------------------------------
def poll_mqtt():
    client = mqtt.Client()
    received = {"temperature": None, "luminosity": None}

    def on_message(client, userdata, msg):
        value = msg.payload.decode()
        topic = msg.topic

        if topic == TOPIC_TEMP:
            received["temperature"] = float(value)

        elif topic == TOPIC_LUMI:
            received["luminosity"] = float(value)

    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.subscribe(TOPIC_TEMP)
        client.subscribe(TOPIC_LUMI)
        client.loop_start()

        time.sleep(0.4)   # attendre les messages MQTT

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print("MQTT ERROR:", e)
        return None

    return received

# ---------------------------------------------------------
# LECTURE MQTT
# ---------------------------------------------------------
msg = poll_mqtt()

if msg:
    if msg["temperature"] is not None:
        st.session_state.temperature = msg["temperature"]

    if msg["luminosity"] is not None:
        st.session_state.luminosity = msg["luminosity"]

    t = time.strftime("%H:%M:%S")
    st.session_state.history["time"].append(t)
    st.session_state.history["temperature"].append(st.session_state.temperature)
    st.session_state.history["luminosity"].append(st.session_state.luminosity)

# ---------------------------------------------------------
# TITRE DU PROJET
# ---------------------------------------------------------
st.markdown("""
# **Projet Final**
### **A304 – Systèmes Embarqués | A311 – Industrie 4.0**
#### **Esdras Guevara — NODE 1**
---
""")

# ---------------------------------------------------------
# UI - BLOCS VALEURS NUMÉRIQUES
# ---------------------------------------------------------
st.title("📡 Dashboard ESP32 — Température & Luminosité (MQTT Live)")

st.markdown("## 📌 Valeurs actuelles")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="🌡 Température",
        value=f"{st.session_state.temperature:.1f} °C"
    )

with col2:
    st.metric(
        label="💡 Luminosité",
        value=f"{st.session_state.luminosity:.1f} %"
    )

st.divider()

# ---------------------------------------------------------
# GRAPHIQUE TEMPÉRATURE
# ---------------------------------------------------------
st.subheader("📈 Température en temps réel")

df = pd.DataFrame(st.session_state.history)

if len(df) > 1:
    st.line_chart(df["temperature"])
else:
    st.info("En attente de données MQTT…")

# ---------------------------------------------------------
# GRAPHIQUE LUMINOSITÉ
# ---------------------------------------------------------
st.subheader("📈 Luminosité en temps réel")

if len(df) > 1:
    st.line_chart(df["luminosity"])

# ---------------------------------------------------------
# AUTO-REFRESH
# ---------------------------------------------------------
time.sleep(1)
st.rerun()
