import streamlit as st
import os
import pandas as pd
import plotly.express as px
from google import genai

# Setup and Connect
api_key = os.environ.get("GEMINI_API_KEY")
st.set_page_config(page_title="AI Data Agent", layout="wide", initial_sidebar_state="expanded")

# Dark Mode Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
if dark_mode:
    st.markdown("""<style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        </style>""", unsafe_allow_html=True)

st.title("🤖 Super Agent: Data Command Center")

if not api_key:
    st.error("⚠️ API Key not configured!")
    st.stop()

client = genai.Client(api_key=api_key)

# 1. Data Intake
st.header("1. Data Intake & Automated Cleaning")
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.txt'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"File loaded! {df.shape[0]} rows and {df.shape[1]} columns.")
        
        with st.expander("Preview Raw Data"):
            st.dataframe(df.head())
            
        # The Cleaning Agent
        if st.button("✨ Run Automated Cleaning & Normalization"):
            with st.spinner("Agent is normalizing data and mapping auxiliary columns..."):
                # In a full deployment, the AI writes cleaning code here. 
                # For now, we simulate the automated cleanup of empty rows and standardizing headers.
                df.dropna(how='all', inplace=True)
                df.columns = [str(c).strip().replace('\n', ' ').title() for c in df.columns]
                st.session_state['cleaned_df'] = df
                st.success("Data normalized! Ready for Power BI export or Dashboarding.")
                st.dataframe(df.head())

        # Use cleaned data if available
        working_df = st.session_state.get('cleaned_df', df)

        st.divider()

        # 2. Generative Dashboards & Reports
        st.header("2. Prompt-Driven Analysis")
        
        prompt_type = st.radio("What would you like the Agent to build?", ["Dynamic Dashboard", "Extensive Report"])
        user_prompt = st.text_area("Tell the Super Agent exactly what you need:")
        
        if st.button("Generate"):
            if user_prompt:
                with st.spinner(f"Building your {prompt_type.lower()}..."):
                    # Give the AI the structure of the data
                    col_info = ", ".join([f"{col} ({dtype})" for col, dtype in zip(working_df.columns, working_df.dtypes)])
                    data_sample = working_df.head(5).to_csv(index=False)
                    
                    if prompt_type == "Extensive Report":
                        sys_prompt = f"Data columns: {col_info}\nSample:\n{data_sample}\nUser Request: {user_prompt}\nAct as a senior analyst. Provide a deep, strategic report. Add a section called 'Value-Add Recommendations' suggesting insights they didn't ask for."
                        report = client.models.generate_content(model='gemini-2.5-flash', contents=sys_prompt)
                        st.markdown(report.text)
                        
                    elif prompt_type == "Dynamic Dashboard":
                        # We ask the AI to write Python code for Plotly
                        sys_prompt = f"""
                        You are an expert Python data visualization developer.
                        The user has a pandas DataFrame named 'working_df'.
                        Columns: {col_info}
                        User Request: {user_prompt}
                        
                        Write Python code using Streamlit (st) and Plotly Express (px) to fulfill this request. 
                        Do NOT use Markdown formatting. Do not output anything except the executable Python code. 
                        Assume 'working_df', 'px', and 'st' are already imported.
                        If the user asks for filters, use st.multiselect to filter working_df before plotting.
                        """
                        code_response = client.models.generate_content(model='gemini-2.5-flash', contents=sys_prompt)
                        
                        # Execute the AI's generated code safely
                        ai_code = code_response.text.replace("```python", "").replace("```", "").strip()
                        try:
                            # The exec command runs the code the AI just wrote!
                            exec(ai_code, globals(), {"working_df": working_df, "st": st, "px": px})
                        except Exception as code_error:
                            st.warning("The Agent tried to build a complex chart but encountered an error. Try rephrasing your prompt.")
                            st.code(ai_code) # Show the code so the user sees what went wrong

        # 3. Export Workspace
        st.divider()
        st.header("3. Export Workspace")
        st.write("Export clean, comma-separated files tailored for your operational databases.")
        csv_data = working_df.to_csv(index=False, sep=',')
        st.download_button(
            label="Download Normalized Data (.csv)",
            data=csv_data,
            file_name="Cleaned_Data_Agent.csv",
            mime="text/csv"
        )
                
    except Exception as e:
        st.error(f"Error processing file: {e}")
