# File: frontend/frontend_ui.py

import streamlit as st
import requests
from fpdf import FPDF
from datetime import datetime
import os

# Setup
st.set_page_config(page_title="MediCopilot", layout="centered")
st.title("🩺 MediCopilot — AI Health Assistant")
st.markdown("Enter your **symptoms** or **health query** below and get medical insight.")

# Session state for response
if "last_query" not in st.session_state:
    st.session_state["last_query"] = ""
if "last_response" not in st.session_state:
    st.session_state["last_response"] = ""

# Input
user_input = st.text_area("📝 Describe your symptoms or ask a question:", height=150)

# Query API
if st.button("🔍 Get Advice"):
    if user_input.strip():
        with st.spinner("Consulting MediCopilot..."):
            res = requests.post("http://127.0.0.1:8000/query", json={"message": user_input})
            if res.status_code == 200:
                response_text = res.json()["response"]
                st.success("✅ Response:")
                st.markdown(response_text)

                st.session_state["last_query"] = user_input
                st.session_state["last_response"] = response_text
            else:
                st.error("❌ Error from API: " + res.text)
    else:
        st.warning("Please enter your symptoms or query.")

# Export to PDF (with DejaVu font support)
if st.session_state["last_response"]:
    if st.button("📄 Export to PDF"):
        try:
            pdf = FPDF()
            pdf.add_page()

            # Make sure these font files exist in your project folder
            pdf.add_font('DejaVu', '', 'DejaVuLGCSans.ttf', uni=True)
            pdf.add_font('DejaVu', 'B', 'DejaVuLGCSans-Bold.ttf', uni=True)

            pdf.set_font("DejaVu", "B", 16)
            pdf.cell(0, 10, "🩺 MediCopilot – Medical Summary", ln=True)

            pdf.set_font("DejaVu", "", 12)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            pdf.cell(0, 10, f"Generated on: {timestamp}", ln=True)
            pdf.ln(5)

            # Query and response
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(0, 10, "📝 Your Query:", ln=True)
            pdf.set_font("DejaVu", "", 12)
            pdf.multi_cell(0, 10, st.session_state["last_query"])
            pdf.ln(2)

            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(0, 10, "🤖 MediCopilot Response:", ln=True)
            pdf.set_font("DejaVu", "", 12)
            pdf.multi_cell(0, 10, st.session_state["last_response"])
            pdf.ln(5)

            # Footer
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(200, 0, 0)
            pdf.multi_cell(0, 10, "⚠ This is an AI-generated summary. Always consult a healthcare professional.")
            pdf.set_text_color(0, 0, 0)

            file_path = "Medical_Summary.pdf"
            pdf.output(file_path)

            with open(file_path, "rb") as f:
                st.download_button("📥 Download Summary PDF", data=f, file_name=file_path, mime="application/pdf")

        except Exception as e:
            st.error(f"PDF Generation Error: {e}")

# Show Query History
st.markdown("---")
st.subheader("📜 Recent Queries")

res = requests.get("http://127.0.0.1:8000/history")
if res.status_code == 200:
    history = res.json()["history"]
    for entry in history:
        st.markdown(f"**🕒 {entry['timestamp']}**")
        st.markdown(f"- **Query**: {entry['user_query']}")
        st.markdown(f"- **Response**: {entry['response']}")
        st.markdown("---")
else:
    st.error("❌ Failed to load history from backend.")
