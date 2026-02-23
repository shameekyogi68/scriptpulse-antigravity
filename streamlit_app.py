"""
Proxy entrypoint for Streamlit Community Cloud.
Streamlit Cloud expects `streamlit_app.py` at the root directory by default.
This file redirects execution to the new location `app/streamlit_app.py`.
"""
import sys
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

app_path = os.path.join(root_dir, "app", "streamlit_app.py")

with open(app_path) as f:
    code = compile(f.read(), app_path, 'exec')
    exec(code, globals())
