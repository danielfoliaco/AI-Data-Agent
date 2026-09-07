import streamlit as st
import os
import pandas as pd
from google import genai

# 1. Setup and Connect
api_key = os.environ.get("GEMINI_API_KEY")
st.set_page_config(page_title="AI Data Agent", layout="wide")
st.title("🤖 Super Agent: Data Command Center")

if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)
st.success("✅ Cloud Station Connected to Gemini API!")

# 2. File Intake
st.header("1. Data Intake")
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 3. Read and Display the Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.info(f"File loaded successfully! The dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
        
        # Show a preview of the data
        st.write("### Data Preview")
        st.dataframe(df.head(5))
        
        # 4. The Super Agent Chat
        st.header("2. Talk to the Super Agent")
        user_prompt = st.text_area("What would you like me to do with this data? (e.g., 'What are the key trends?' or 'Are there any missing values?')")
        
        if st.button("Run Analysis"):
            with st.spinner("The Super Agent is analyzing your data..."):
                # We send a sample of the data + the user's question to the AI
                data_sample = df.head(10).to_csv(index=False)
                ai_prompt = f"Here is a sample of the user's dataset:\n{data_sample}\n\nThe user asks: {user_prompt}\n\nAct as an expert data analyst and provide a clear, professional answer."
                
                # Ask Gemini
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=ai_prompt,
                )
                
                st.write("### Super Agent Response")
                st.write(response.text)
                
    except Exception as e:
        st.error(f"Error reading file: {e}")
