import streamlit as st
import pandas as pd
from datetime import datetime
import threading
import paho.mqtt.client as mqtt

# ----------------- MQTT CONFIG -----------------
MQTT_BROKER = "51.103.121.129"
MQTT_PORT = 1883
MQTT_TOPICS = [
    ("esp32/sensors/temperature", 0),
    ("esp32/sensors/luminosity", 0),
    ("esp32/state/motor", 0),
    ("esp32/state/servo", 0),
    ("esp32/state/buzzer", 0),
    ("esp32/state/alarm", 0),
]

# ----------------- STOCKAGE ---------------------
if "data" not in st.session_state:
    st.session_state.data = []

latest = {
    "temperature": None,
    "luminosity": None,
    "motor": False,
    "servo": False,
    "buzzer": False,
    "alarmDisabled": False
}

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    print("MQTT connected =", rc)
    for topic, q in MQTT_TOPICS:
        client.subscribe(topic)
        print("Subscribed to", topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode()

    # Cast values properly
    if topic == "esp32/sensors/temperature":
        latest["temperature"] = float(value)

    elif topic == "esp32/sensors/luminosity":
        latest["luminosity"] = float(value)

    elif topic == "esp32/state/motor":
        latest["motor"] = (value == "1")

    elif topic == "esp32/state/servo":
        latest["servo"] = (value == "1")

    elif topic == "esp32/state/buzzer":
        latest["buzzer"] = (value == "1")

    elif topic == "esp32/state/alarm":
        latest["alarmDisabled"] = (value == "1")

    # store snapshot
    if latest["temperature"] is not None:
        snapshot = latest.copy()
        snapshot["timestamp"] = datetime.now()
        st.session_state.data.append(snapshot)


# ---------------- MQTT THREAD -------------------
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# ---------------- STREAMLIT UI -------------------
st.set_page_config(page_title="ESP32 Dashboard", layout="wide")
st.title("📡 Dashboard ESP32 - MQTT LIVE")

col1, col2 = st.columns(2)

if len(st.session_state.data) > 0:
    df = pd.DataFrame(st.session_state.data)

    # -------- Temperature --------
    with col1:
        st.subheader("🌡 Température")
        st.metric(
            label="Température actuelle",
            value=f"{df['temperature'].iloc[-1]} °C"
        )
        st.line_chart(df["temperature"], height=250)

    # -------- States --------
    with col2:
        st.subheader("⚙️ États du système")
        last = df.iloc[-1]

        st.toggle("Moteur actif ?", last["motor"], disabled=True)
        st.toggle("Servo actif ?", last["servo"], disabled=True)
        st.toggle("Buzzer actif ?", last["buzzer"], disabled=True)
        st.toggle("Alarme désactivée ?", last["alarmDisabled"], disabled=True)

    st.write("### 🗃 Historique")
    st.dataframe(df[::-1], height=260)
else:
    st.warning("En attente des données MQTT…")
