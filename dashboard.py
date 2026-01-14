import streamlit as st
import requests
import pandas as pd
import time

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard ESP32 - Data -",
    layout="wide"
)

# ---------------------------------------------------------
# FIREBASE URL (ADAPTÉ À TA BASE)
# ---------------------------------------------------------
FIREBASE_URL = (
    "https://projet-final-9ef58-default-rtdb.europe-west1.firebasedatabase.app"
    "/esp32/sensors.json"
)

# ---------------------------------------------------------
# SESSION STATE (HISTORIQUE)
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = {
        "time": [],
        "temperature": [],
        "humidity": [],
        "luminosity": []
    }

# ---------------------------------------------------------
# TITRE
# ---------------------------------------------------------
st.markdown("""
# **Projet Final**
### **A304 – Systèmes Embarqués | A311 – Industrie 4.0**
#### **Esdras Guevara — NODE 1**
---
""")

st.title("📡 Dashboard ESP32 — Données Firebase (Temps réel)")

# ---------------------------------------------------------
# LECTURE FIREBASE (POLLING HTTP)
# ---------------------------------------------------------
placeholder = st.empty()

while True:
    try:
        response = requests.get(FIREBASE_URL, timeout=5)
        data = response.json()

        temperature = data.get("temperature", 0)
        humidity = data.get("humidity", 0)
        luminosity = data.get("luminosity", 0)

        # Historique
        t = time.strftime("%H:%M:%S")
        hist = st.session_state.history
        hist["time"].append(t)
        hist["temperature"].append(temperature)
        hist["humidity"].append(humidity)
        hist["luminosity"].append(luminosity)

        with placeholder.container():

            # -------------------------------
            # BLOCS VALEURS
            # -------------------------------
            st.markdown("## 📌 Valeurs actuelles")

            c1, c2, c3 = st.columns(3)
            c1.metric("🌡 Température", f"{temperature} °C")
            c2.metric("💧 Humidité", f"{humidity} %")
            c3.metric("💡 Luminosité", f"{luminosity} %")

            st.divider()

            # -------------------------------
            # GRAPHIQUES
            # -------------------------------
            st.subheader("📈 Évolution des mesures")

            df = pd.DataFrame(hist)

            g1, g2, g3 = st.columns(3)

            with g1:
                st.line_chart(df["temperature"])

            with g2:
                st.line_chart(df["humidity"])

            with g3:
                st.line_chart(df["luminosity"])

    except Exception as e:
        st.error("Erreur de connexion à Firebase")

    time.sleep(1)
