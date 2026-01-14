import streamlit as st
import paho.mqtt.client as mqtt
import time
import pandas as pd

# ---------------------------------------------------------
# CONFIG PAGE (PLEINE LARGEUR)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard ESP32",
    layout="wide"
)

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
# MQTT CLIENT PERSISTANT (LA CLÉ DU PROBLÈME)
# ---------------------------------------------------------
if "mqtt_client" not in st.session_state:

    client = mqtt.Client()

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

    client.on_message = on_message
    client.connect(BROKER, PORT, 60)

    client.subscribe([
        (TOPIC_TEMP, 0),
        (TOPIC_LUMI, 0),
        (TOPIC_HUM, 0)
    ])

    client.loop_start()
    st.session_state.mqtt_client = client

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
# DASHBOARD
# ---------------------------------------------------------
st.title("📡 Dashboard ESP32 — Capteurs MQTT Live")

# ---------------------------------------------------------
# BLOCS VALEURS NUMÉRIQUES
# ---------------------------------------------------------
st.markdown("## 📌 Valeurs actuelles")

val_col1, val_col2, val_col3 = st.columns(3)

with val_col1:
    st.metric("🌡 Température", f"{st.session_state.temperature:.1f} °C")

with val_col2:
    st.metric("💡 Luminosité", f"{st.session_state.luminosity:.1f} %")

with val_col3:
    st.metric("💧 Humidité", f"{st.session_state.humidity:.1f} %")

st.divider()

# ---------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------
st.subheader("📈 Mesures en temps réel")

df = pd.DataFrame(st.session_state.history)

graph_col1, graph_col2, graph_col3 = st.columns(3)

with graph_col1:
    st.markdown("### 🌡 Température")
    if len(df) > 1:
        st.line_chart(df["temperature"])
    else:
        st.info("En attente de données MQTT…")

with graph_col2:
    st.markdown("### 💡 Luminosité")
    if len(df) > 1:
        st.line_chart(df["luminosity"])
    else:
        st.info("En attente de données MQTT…")

with graph_col3:
    st.markdown("### 💧 Humidité")
    if len(df) > 1:
        st.line_chart(df["humidity"])
    else:
        st.info("En attente de données MQTT…")

# ---------------------------------------------------------
# AUTO-REFRESH (léger)
# ---------------------------------------------------------
time.sleep(1)
st.rerun()

