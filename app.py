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
st.header("1. Data Intake")
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.txt'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"File loaded successfully! {df.shape[0]} rows and {df.shape[1]} columns.")
        
        with st.expander("Preview Raw Data"):
            st.dataframe(df.head())
        
        # Phase 1: Reporting Engine
        st.header("2. Reporting & Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Interactive Chat")
            user_prompt = st.text_area("Ask a specific question about the data:")
            if st.button("Ask Agent"):
                with st.spinner("Analyzing..."):
                    data_sample = df.head(15).to_csv(index=False)
                    ai_prompt = f"Data Sample:\n{data_sample}\n\nQuestion: {user_prompt}\nProvide a professional answer."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=ai_prompt)
                    st.info(response.text)
                    
        with col2:
            st.subheader("Extensive Reports")
            if st.button("Generate Executive Report"):
                with st.spinner("Drafting comprehensive report..."):
                    data_sample = df.head(25).to_csv(index=False)
                    columns_list = ", ".join(df.columns.tolist())
                    ai_prompt = f"Data Columns: {columns_list}\nData Sample:\n{data_sample}\n\nAct as a Senior Statistician. Generate a comprehensive, multi-paragraph markdown report analyzing this dataset. Include potential risks, key metrics to watch, and strategic recommendations."
                    report = client.models.generate_content(model='gemini-2.5-flash', contents=ai_prompt)
                    st.markdown("### Executive Summary")
                    st.markdown(report.text)
                    
                    st.download_button(
                        label="Download Report as .txt",
                        data=report.text,
                        file_name="Executive_Report.txt",
                        mime="text/plain"
                    )

        # Phase 1.5: Dynamic Dashboards
        st.divider()
        st.header("3. Dynamic Visualizations")
        
        # Auto-detect numeric columns for charts
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()
        
        if len(numeric_cols) > 0:
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            with chart_col1:
                chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Scatter Plot", "Line Chart"])
            with chart_col2:
                x_axis = st.selectbox("Select X-Axis", all_cols)
            with chart_col3:
                y_axis = st.selectbox("Select Y-Axis", numeric_cols)
                
            if st.button("Generate Chart"):
                if chart_type == "Bar Chart":
                    fig = px.bar(df, x=x_axis, y=y_axis, template="plotly_dark" if dark_mode else "plotly_white")
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df, x=x_axis, y=y_axis, template="plotly_dark" if dark_mode else "plotly_white")
                else:
                    fig = px.line(df, x=x_axis, y=y_axis, template="plotly_dark" if dark_mode else "plotly_white")
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns detected to build charts.")

        # Phase 3 Preview: Export Engine
        st.divider()
        st.header("4. Export Workspace")
        csv_data = df.to_csv(index=False, sep=',')
        st.download_button(
            label="Download Data (Comma Separated CSV)",
            data=csv_data,
            file_name="Processed_Data.csv",
            mime="text/csv"
        )
                
    except Exception as e:
        st.error(f"Error reading file: {e}")
