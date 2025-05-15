import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
from clinical_guidelines import get_ventilation_guidelines
import google.generativeai as genai
import os




st.set_page_config(page_title="AI ICU Ventilator Assistant", layout="wide")
st.title("🫁 AI-Assisted ICU Ventilation Dashboard")
# --- Doctor Login ---
st.sidebar.title("👨‍⚕️ Doctor Login")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "doctor" and password == "icu123":
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")
    st.stop()
# --- Real-Time Simulation ---
import random

if st.checkbox("🕒 Enable Real-Time Vitals Simulation"):
    st.info("Vitals will update every 2 seconds. Stop to freeze values.")
    for i in range(10):  # simulate 10 intervals
        heart_rate = random.randint(70, 100)
        spo2 = random.randint(90, 100)
        resp_rate = random.randint(18, 28)
        ph = round(random.uniform(7.35, 7.45), 2)
        pao2 = random.randint(70, 100)
        paco2 = random.randint(35, 50)
        st.write(f"Update {i+1}: HR={heart_rate}, SpO2={spo2}, RR={resp_rate}, pH={ph}")
        time.sleep(2)


# -------------------- Sidebar Input -------------------- #
st.sidebar.header("🔍 Input Patient Vitals")
heart_rate = st.sidebar.slider("Heart Rate", 60, 130, 85)
spo2 = st.sidebar.slider("SpO2", 85, 100, 95)
resp_rate = st.sidebar.slider("Respiratory Rate", 10, 40, 20)
ph = st.sidebar.slider("pH", 7.2, 7.6, 7.4)
pao2 = st.sidebar.slider("PaO2", 50, 200, 80)
paco2 = st.sidebar.slider("PaCO2", 20, 70, 40)
tv_prev = st.sidebar.slider("Previous Tidal Volume (ml)", 300, 600, 450)
peep_prev = st.sidebar.slider("Previous PEEP", 3, 10, 5)

# -------------------- Main Container -------------------- #
col1, col2 = st.columns(2)

st.subheader("📋 Current Vitals Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("❤️ Heart Rate", f"{heart_rate} bpm")
    st.metric("🫀 PaO2", f"{pao2} mmHg")

with col2:
    st.metric("🫁 SpO2", f"{spo2} %")
    st.metric("🧪 pH", f"{ph}")

with col3:
    st.metric("💨 Resp Rate", f"{resp_rate} bpm")
    st.metric("🫀 PaCO2", f"{paco2} mmHg")


with col2:
    if st.button("🧠 Predict Tidal Volume"):
        with st.spinner("Consulting AI..."):
            time.sleep(1)  # simulate delay
            response = requests.post("http://localhost:8000/predict_tv", json={
                "HeartRate": heart_rate,
                "SpO2": spo2,
                "RespiratoryRate": resp_rate,
                "pH": ph,
                "PaO2": pao2,
                "PaCO2": paco2,
                "TV_previous": tv_prev,
                "PEEP_previous": peep_prev
            })

            if response.status_code == 200:
                result = response.json()
                tv = result['recommended_tidal_volume']
                st.success(f"✅ Recommended Tidal Volume: **{tv} ml**")
                st.balloons()

                # Calculate weaning readiness (demo rule-based)
                score = 0
                score += 20 if 7.35 <= ph <= 7.45 else 0
                score += 20 if 90 <= spo2 <= 100 else 0
                score += 20 if resp_rate <= 25 else 0
                score += 20 if 35 <= pao2 <= 100 else 0
                score += 20 if 35 <= paco2 <= 50 else 0

                status = "✅ Ready for Weaning" if score >= 80 else "⚠️ Not Yet Ready"
                st.info(f"🧮 Weaning Readiness Score: **{score}/100** — {status}")
            else:
                st.error("❌ Prediction failed. Check your backend API.")
from reportlab.pdfgen import canvas

def generate_pdf(dataframe):
    c = canvas.Canvas("icu_summary.pdf")
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, "🩺 ICU Patient Summary Report")

    y = 770
    for index, row in dataframe.iterrows():
        row_data = ", ".join([f"{col}: {row[col]}" for col in dataframe.columns])
        c.drawString(40, y, row_data[:110])  # line clip
        y -= 20
        if y < 100:
            break

    c.save()
    st.success("✅ PDF generated: icu_summary.pdf")

if st.button("📄 Export Latest Logs to PDF"):
    try:
        df_log = pd.read_csv("icu_log.csv").tail(5)
        generate_pdf(df_log)
        with open("icu_summary.pdf", "rb") as f:
            st.download_button("⬇️ Download ICU Summary PDF", f, file_name="icu_summary.pdf")
    except FileNotFoundError:
        st.error("Log file not found.")
   
# -------------------- Live Chart Placeholder -------------------- #
st.subheader("📈 Live Trend of Vitals (Simulated)")
sample_data = pd.DataFrame({
    "Time (min)": list(range(10)),
    "SpO2": [94, 95, 93, 96, 95, 97, 94, 96, 95, 94],
    "RR": [20, 21, 22, 23, 22, 21, 20, 20, 19, 20]
})

fig = px.line(sample_data, x="Time (min)", y=["SpO2", "RR"], title="Trend of SpO2 and RR")
st.plotly_chart(fig, use_container_width=True)

# -------------------- Alert -------------------- #
if spo2 < 90 or ph < 7.25:
    st.error("🚨 Critical Alert: Patient shows signs of respiratory distress!")

st.markdown("---")
st.caption("Powered by AI | Built for ICU heroes 💙")
# -------------------- Prediction History -------------------- #
st.subheader("📝 Previous Predictions Log")
try:
    df_log = pd.read_csv("icu_log.csv")
    st.dataframe(df_log.tail(10), use_container_width=True)

    if st.checkbox("📊 Show Tidal Volume Trend Chart"):
        fig2 = px.line(df_log, y="Predicted_TV", title="Tidal Volume Prediction History")
        st.plotly_chart(fig2, use_container_width=True)
except FileNotFoundError:
    st.warning("Prediction log file not found. Predictions will appear here after the first run.")

# -------------------- Interpretation -------------------- #
if 'tv' in locals():
    explanation = []
    if resp_rate > 25:
        explanation.append("High RR → May need increased tidal support.")
    if paco2 > 50:
        explanation.append("High PaCO2 → Possible hypoventilation.")
    if ph < 7.35:
        explanation.append("Low pH → Risk of acidosis.")

    if explanation:
        st.info("📌 **Rationale for Tidal Volume Recommendation:**")
        for point in explanation:
            st.write(f"• {point}")
# Set your Gemini API key
genai.configure(api_key="AIzaSyBdJX-NuK0Q0a5a85rDVZTbwbWGz_oHzqk")


# Create the chatbot model (you can cache it)
@st.cache_resource
def get_gemini_chat():
    return genai.GenerativeModel("gemini-1.5-pro-latest").start_chat(history=[])

chat = get_gemini_chat()

st.subheader("💬 AI Medical Assistant Chatbot")
user_input = st.text_input("Ask a question about ventilation, vitals, or conditions", key="chat_input")

if user_input:
    with st.spinner("Thinking..."):
        response = chat.send_message(user_input)
        st.markdown(f"👨‍⚕️ **You:** {user_input}")
        st.markdown(f"🤖 **AI:** {response.text}")

    if st.checkbox("🕑 Show Full Chat History"):
        for msg in chat.history:
            role = "👨‍⚕️" if msg.role == "user" else "🤖"
            st.markdown(f"**{role}**: {msg.parts[0].text}")

st.subheader("🩺 Condition-Specific Ventilation Guidance")

condition = st.selectbox("Select Condition", ["ARDS", "COPD", "Restrictive", "Head Injury", "Weaning"])
guidelines = get_ventilation_guidelines(condition)

st.markdown("### 📋 Clinical Guidelines for " + condition)
for line in guidelines:
    st.markdown(f"- {line}")
