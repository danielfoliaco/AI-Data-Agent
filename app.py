import streamlit as st
import os

# 1. We will load the API key securely through the cloud server later!
api_key = os.environ.get("GEMINI_API_KEY")

# 2. Configure our web app layout
st.set_page_config(page_title="AI Data Agent", layout="wide")
st.title("🤖 Super Agent: Data Command Center")

# 3. Check if the connection works
if not api_key:
    st.error("⚠️ API Key not configured in the cloud yet.")
else:
    st.success("✅ Cloud Station Connected to Gemini API!")

# 4. Phase 2: The File Intake System
st.header("Data Intake")
uploaded_file = st.file_uploader("Upload an Excel or CSV file to begin", type=["csv", "xlsx"])

if uploaded_file is not None:
    st.info(f"File '{uploaded_file.name}' received! The Super Agent is standing by.")
