import streamlit as st
import os
import pandas as pd
import plotly.express as px
from google import genai
import openai
import anthropic

# --- APP SETUP ---
st.set_page_config(page_title="AI Data Agent", layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR & AI SELECTION ---
st.sidebar.title("⚙️ Agent Settings")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

if dark_mode:
    st.markdown("""<style>.stApp { background-color: #0E1117; color: #FAFAFA; }</style>""", unsafe_allow_html=True)

# The Dropdown for AI Selection
ai_choice = st.sidebar.selectbox(
    "Select AI Engine", 
    ["Google Gemini (Free 1500/day)", "DeepSeek (Free 5M Trial)", "OpenAI ChatGPT ($5 Trial)", "Anthropic Claude ($5 Trial)", "xAI Grok (Promo)"]
)

# Load Keys from Streamlit Secrets / Environment
gemini_key = os.environ.get("GEMINI_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
grok_key = os.environ.get("GROK_API_KEY")

# Unified AI Routing Function
def get_ai_response(prompt, choice):
    try:
        if choice == "Google Gemini (Free 1500/day)":
            if not gemini_key: return "⚠️ GEMINI_API_KEY is missing in Streamlit Secrets."
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            return response.text
            
        elif choice == "OpenAI ChatGPT ($5 Trial)":
            if not openai_key: return "⚠️ OPENAI_API_KEY is missing in Streamlit Secrets."
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content
            
        elif choice == "Anthropic Claude ($5 Trial)":
            if not anthropic_key: return "⚠️ ANTHROPIC_API_KEY is missing in Streamlit Secrets."
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(model="claude-3-5-haiku-latest", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
            return response.content[0].text
            
        elif choice == "DeepSeek (Free 5M Trial)":
            if not deepseek_key: return "⚠️ DEEPSEEK_API_KEY is missing in Streamlit Secrets."
            # DeepSeek uses the OpenAI library architecture
            client = openai.OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content
            
        elif choice == "xAI Grok (Promo)":
            if not grok_key: return "⚠️ GROK_API_KEY is missing in Streamlit Secrets."
            client = openai.OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            response = client.chat.completions.create(model="grok-beta", messages=[{"role": "user", "content": prompt}])
            return response.choices[0].message.content
            
    except Exception as e:
        return f"API Error: {e}"

st.title("🤖 Super Agent: Data Command Center")

# --- MAIN APP LOGIC ---
st.header("1. Data Intake & Automated Cleaning")
uploaded_file = st.file_uploader("Upload an Excel, CSV, or TXT file", type=["csv", "xlsx", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.txt'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success(f"File loaded! {df.shape[0]} rows and {df.shape[1]} columns.")
        
        with st.expander("Preview Raw Data"):
            st.dataframe(df.head())
            
        if st.button("✨ Run Automated Cleaning & Normalization"):
            with st.spinner("Normalizing data..."):
                df.dropna(how='all', inplace=True)
                df.columns = [str(c).strip().replace('\n', ' ').title() for c in df.columns]
                st.session_state['cleaned_df'] = df
                st.success("Data normalized and formatted.")
                st.dataframe(df.head())

        working_df = st.session_state.get('cleaned_df', df)
        st.divider()

        # Generative Section
        st.header("2. Prompt-Driven Analysis")
        prompt_type = st.radio("What would you like to build?", ["Dynamic Dashboard", "Extensive Report"])
        user_prompt = st.text_area("Tell the Super Agent exactly what you need:")
        
        if st.button("Generate"):
            if user_prompt:
                with st.spinner(f"Routing your request to {ai_choice}..."):
                    col_info = ", ".join([f"{col} ({dtype})" for col, dtype in zip(working_df.columns, working_df.dtypes)])
                    data_sample = working_df.head(5).to_csv(index=False)
                    
                    if prompt_type == "Extensive Report":
                        sys_prompt = f"Data columns: {col_info}\nSample:\n{data_sample}\nUser Request: {user_prompt}\nAct as a senior analyst. Provide a deep, strategic report. Add a section called 'Value-Add Recommendations' suggesting insights they didn't ask for."
                        
                        report_text = get_ai_response(sys_prompt, ai_choice)
                        st.markdown(report_text)
                        
                    elif prompt_type == "Dynamic Dashboard":
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
                        
                        code_response = get_ai_response(sys_prompt, ai_choice)
                        
                        # Execute AI Code
                        ai_code = code_response.replace("```python", "").replace("```", "").strip()
                        
                        if "API Error" in ai_code or "missing in Streamlit Secrets" in ai_code:
                            st.error(ai_code)
                        else:
                            try:
                                exec(ai_code, globals(), {"working_df": working_df, "st": st, "px": px})
                            except Exception as code_error:
                                st.warning("The Agent encountered a syntax error while building this specific chart structure. Please try rephrasing the prompt.")
                                st.code(ai_code)
                                
        # Export Engine
        st.divider()
        st.header("3. Export Workspace")
        st.write("Export pristine, comma-separated files tailored for standard BI schema imports.")
        csv_data = working_df.to_csv(index=False, sep=',')
        st.download_button(
            label="Download Normalized Data (.csv)",
            data=csv_data,
            file_name="Cleaned_Data_Agent.csv",
            mime="text/csv"
        )
                
    except Exception as e:
        st.error(f"Error processing file: {e}")
