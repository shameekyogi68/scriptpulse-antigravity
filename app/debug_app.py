import streamlit as st
st.set_page_config(page_title="Debug Streamlit")

st.title("Streamlit Runtime Debugger")

try:
    import sys
    import os
    st.write("System Paths:", sys.path)
    
    import pandas
    st.write("Pandas:", pandas.__version__)
    
    import plotly
    st.write("Plotly:", plotly.__version__)
    
    import scriptpulse.utils.logger
    st.write("ScriptPulse Base Path found.")
    
    st.write("Attempting full runner import...")
    import scriptpulse.pipeline.runner as runner
    st.success("Runner imported successfully!")
    
    st.write("Testing pre-load...")
    import app.streamlit_app as main_app
    st.write("Main App modules loaded safely.")
except Exception as e:
    st.error(f"Fatal Import Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
