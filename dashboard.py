from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import os
import random
import numpy as np
import google.generativeai as genai
from clinical_guidelines import get_ventilation_guidelines
from reportlab.pdfgen import canvas

# Gemini Setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- Page Setup -------------------- #
st.set_page_config(page_title="AI ICU Ventilator Assistant", layout="wide")
st.title("🫁 AI-Assisted ICU Ventilation Dashboard")

# -------------------- Animated Doctor Login -------------------- #
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

# -------------------- Real-Time Vitals Simulation -------------------- #
if st.checkbox("🕒 Enable Real-Time Vitals Simulation"):
    st.info("Vitals will update every 2 seconds. Stop to freeze values.")
    for i in range(10):
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
weight = st.sidebar.slider("Weight (kg)", 40, 150, 70)
height = st.sidebar.slider("Height (cm)", 140, 200, 170)
bmi = round(weight / ((height / 100) ** 2), 2)
st.sidebar.markdown(f"**Calculated BMI:** {bmi}")

heart_rate = st.sidebar.slider("Heart Rate", 60, 130, 85)
spo2 = st.sidebar.slider("SpO2", 85, 100, 95)
resp_rate = st.sidebar.slider("Respiratory Rate", 10, 40, 20)
ph = st.sidebar.slider("pH", 7.2, 7.6, 7.4)
pao2 = st.sidebar.slider("PaO2", 50, 200, 80)
paco2 = st.sidebar.slider("PaCO2", 20, 70, 40)
tv_prev = st.sidebar.slider("Previous Tidal Volume (ml)", 300, 600, 450)
peep_prev = st.sidebar.slider("Previous PEEP", 3, 10, 5)

# -------------------- Main Vitals Summary -------------------- #
col1, col2, col3 = st.columns(3)
st.subheader("📋 Current Vitals Summary")

with col1:
    st.metric("❤️ Heart Rate", f"{heart_rate} bpm")
    st.metric("🫀 PaO2", f"{pao2} mmHg")
    st.metric("⚖️ Weight", f"{weight} kg")

with col2:
    st.metric("🫁 SpO2", f"{spo2} %")
    st.metric("🧪 pH", f"{ph}")
    st.metric("📏 Height", f"{height} cm")

with col3:
    st.metric("💨 Resp Rate", f"{resp_rate} bpm")
    st.metric("🫀 PaCO2", f"{paco2} mmHg")
    st.metric("📊 BMI", f"{bmi}")
# -------------------- Weaning Score Calculation Function -------------------- #
def calculate_weaning_score(spo2, ph, rr, pao2, paco2, tv_ml):
    tv_liters = tv_ml / 1000
    rsbi = rr / tv_liters if tv_liters else 999
    score = 0
    if 7.35 <= ph <= 7.45: score += 25
    if spo2 >= 92: score += 25
    if rr < 30: score += 25
    if rsbi < 105: score += 25
    status = "✅ Ready for Weaning" if score >= 75 else "⚠️ Not Yet Ready"
    return score, rsbi, status


# -------------------- Predict Tidal Volume -------------------- #
with col2:
    if st.button("🧠 Predict Tidal Volume"):
        with st.spinner("Consulting AI..."):
            time.sleep(1)

            response = requests.post("http://localhost:8000/predict_tv", json={
                "HeartRate": heart_rate,
                "SpO2": spo2,
                "RespiratoryRate": resp_rate,
                "pH": ph,
                "PaO2": pao2,
                "PaCO2": paco2,
                "TV_previous": tv_prev,
                "PEEP_previous": peep_prev,
                "Weight": weight,
                "Height": height,
                "BMI": bmi
            })

            if response.status_code == 200:
                result = response.json()
                tv = result['recommended_tidal_volume']
                st.success(f"✅ Recommended Tidal Volume: **{tv} ml**")
                

                # --- Weaning Score ---
                score, rsbi, status = calculate_weaning_score(spo2, ph, resp_rate, pao2, paco2, tv)
                st.info(f"🧮 Weaning Readiness Score: **{score}/100** — {status} (RSBI = {rsbi:.2f})")

                # --- Confidence Interval ---
                ci_lower = tv - 15
                ci_upper = tv + 15
                st.caption(f"📉 95% Confidence Interval: {ci_lower:.1f} ml – {ci_upper:.1f} ml")

                # --- AI Explanation using Gemini ---
                try:
                    explanation_prompt = f"""
You are an AI ICU assistant. A patient has the following vitals:
- Heart Rate: {heart_rate} bpm
- SpO2: {spo2}%
- Respiratory Rate: {resp_rate} breaths/min
- pH: {ph}
- PaO2: {pao2} mmHg
- PaCO2: {paco2} mmHg
- Weight: {weight} kg
- Height: {height} cm
- BMI: {bmi}

The AI model has predicted a tidal volume of {tv} ml for this patient.

Explain in simple clinical terms **why this tidal volume might have been recommended** based on the above vitals.
"""
                    chat = model.start_chat()
                    gemini_response = chat.send_message(explanation_prompt)
                    st.info("💬 **Gemini AI Explanation:**")
                    st.write(gemini_response.text)

                except Exception as e:
                    st.warning(f"Could not generate AI explanation: {e}")

            else:
                st.error("❌ Prediction failed. Check your backend API.")


# -------------------- Show SHAP Summary Plot -------------------- #
if os.path.exists("shap_summary_plot.png"):
    st.subheader("📊 Model Explainability (SHAP)")
    st.image("shap_summary_plot.png", caption="Feature Impact on Tidal Volume Prediction")
    if st.button("📤 Export Explanation to PDF"):
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Tidal Volume Prediction Explanation", ln=1, align='C')
        pdf.image("shap_summary_plot.png", x=10, y=30, w=190)
        pdf.output("icu_explanation.pdf")
        with open("icu_explanation.pdf", "rb") as f:
            st.download_button("⬇️ Download Explanation PDF", f, file_name="icu_explanation.pdf")

# -------------------- Export Latest Logs to PDF -------------------- #
def generate_pdf(dataframe):
    c = canvas.Canvas("icu_summary.pdf")
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, "🩺 ICU Patient Summary Report")

    y = 770
    for index, row in dataframe.iterrows():
        row_data = ", ".join([f"{col}: {row[col]}" for col in dataframe.columns])
        c.drawString(40, y, row_data[:110])
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

# -------------------- Live Trend Chart -------------------- #
st.subheader("📈 Live Trend of Vitals (Simulated)")
sample_data = pd.DataFrame({
    "Time (min)": list(range(10)),
    "SpO2": [94, 95, 93, 96, 95, 97, 94, 96, 95, 94],
    "RR": [20, 21, 22, 23, 22, 21, 20, 20, 19, 20]
})
fig = px.line(sample_data, x="Time (min)", y=["SpO2", "RR"], title="Trend of SpO2 and RR")
st.plotly_chart(fig, use_container_width=True)

# -------------------- Critical Alert -------------------- #
if spo2 < 90 or ph < 7.25:
    st.error("🚨 Critical Alert: Patient shows signs of respiratory distress!")

st.markdown("---")
st.caption("Powered by AI | Built for ICU heroes 💙")

# -------------------- Prediction History -------------------- #
st.subheader("📝 Previous Predictions Log")
try:
    df_log = pd.read_csv("icu_log.csv", header=0)

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

# -------------------- Clinical Guidelines -------------------- #
st.subheader("🩺 Condition-Specific Ventilation Guidance")
condition = st.selectbox("Select Condition", ["ARDS", "COPD", "Restrictive", "Head Injury", "Weaning"])
guidelines = get_ventilation_guidelines(condition)
st.markdown("### 📋 Clinical Guidelines for " + condition)
for line in guidelines:
    st.markdown(f"- {line}")
# -------------------- Floating Chatbot Assistant -------------------- #
st.markdown(
    """
    <style>
    .floating-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #25D366;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 28px;
        text-align: center;
        line-height: 60px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        z-index: 9999;
        cursor: pointer;
    }
    .floating-button:hover {
        background-color: #128C7E;
    }
    </style>
    <div onclick="document.querySelector('button[data-testid=chatbot-toggle]').click()" class="floating-button">💬</div>
    """,
    unsafe_allow_html=True,
)



# -------------------- Gemini Chatbot -------------------- #
st.subheader("🤖 Ask the ICU Assistant ")
st.caption("Ask about ICU parameters, ventilator settings, clinical tips, etc.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask your medical question...")

if user_input:
    with st.spinner("AI is thinking..."):
        try:
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(user_input)
            st.session_state.chat_history.append({"role": "user", "parts": [user_input]})
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
        except Exception as e:
            st.error(f"Error: {e}")

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["parts"][0])
    else:
        st.chat_message("assistant").write(msg["parts"][0])
