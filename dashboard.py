import streamlit as st
import paho.mqtt.client as mqtt
import time
import pandas as pd

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard ESP32",
    layout="wide"
)

# Rafraîchissement UI (OBLIGATOIRE avec MQTT)
st.experimental_autorefresh(interval=1000)

# ---------------------------------------------------------
# MQTT CONFIG
# ---------------------------------------------------------
BROKER = "51.103.121.129"
PORT = 1883

TOPIC_TEMP = "esp32/sensors/temperature"
TOPIC_LUMI = "esp32/sensors/luminosity"
TOPIC_HUM  = "esp32/sensors/humidity"

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0
if "luminosity" not in st.session_state:
    st.session_state.luminosity = 0.0
if "humidity" not in st.session_state:
    st.session_state.humidity = 0.0
if "history" not in st.session_state:
    st.session_state.history = {
        "time": [],
        "temperature": [],
        "luminosity": [],
        "humidity": []
    }

# ---------------------------------------------------------
# MQTT CLIENT (PERSISTANT)
# ---------------------------------------------------------
if "mqtt_started" not in st.session_state:

    def on_message(client, userdata, msg):
        try:
            value = float(msg.payload.decode())

            if msg.topic == TOPIC_TEMP:
                st.session_state.temperature = value
            elif msg.topic == TOPIC_LUMI:
                st.session_state.luminosity = value
            elif msg.topic == TOPIC_HUM:
                st.session_state.humidity = value

            t = time.strftime("%H:%M:%S")
            st.session_state.history["time"].append(t)
            st.session_state.history["temperature"].append(st.session_state.temperature)
            st.session_state.history["luminosity"].append(st.session_state.luminosity)
            st.session_state.history["humidity"].append(st.session_state.humidity)

        except:
            pass

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe([
        (TOPIC_TEMP, 0),
        (TOPIC_LUMI, 0),
        (TOPIC_HUM, 0)
    ])
    client.loop_start()

    st.session_state.mqtt_started = True
    st.session_state.mqtt_client = client

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.markdown("""
# **Projet Final**
### **A304 – Systèmes Embarqués | A311 – Industrie 4.0**
#### **Esdras Guevara — NODE 1**
---
""")

st.title("📡 Dashboard ESP32 — Capteurs MQTT Live")

st.markdown("## 📌 Valeurs actuelles")
c1, c2, c3 = st.columns(3)

c1.metric("🌡 Température", f"{st.session_state.temperature:.1f} °C")
c2.metric("💡 Luminosité", f"{st.session_state.luminosity:.1f} %")
c3.metric("💧 Humidité", f"{st.session_state.humidity:.1f} %")

st.divider()

st.subheader("📈 Mesures en temps réel")
df = pd.DataFrame(st.session_state.history)

g1, g2, g3 = st.columns(3)

with g1:
    st.line_chart(df["temperature"]) if len(df) > 1 else st.info("En attente de données MQTT…")

with g2:
    st.line_chart(df["luminosity"]) if len(df) > 1 else st.info("En attente de données MQTT…")

with g3:
    st.line_chart(df["humidity"]) if len(df) > 1 else st.info("En attente de données MQTT…")
