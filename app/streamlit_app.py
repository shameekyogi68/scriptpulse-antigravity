import sys
import streamlit as st
st.set_page_config(page_title="ScriptPulse Rescue Mode", layout="wide")
st.title("Streamlit Runtime Debugger")

try:
    import pandas
    st.write("Pandas:", pandas.__version__)
    
    import plotly
    st.write("Plotly:", plotly.__version__)
    
    st.write("Attempting full engine import...")
    from scriptpulse.pipeline import runner
    st.success("Runner imported successfully!")
    st.write("All paths resolved on Streamlit Cloud.")
except Exception as e:
    st.error(f"Fatal Import Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
