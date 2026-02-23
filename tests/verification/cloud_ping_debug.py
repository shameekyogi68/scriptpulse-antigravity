import urllib.request
import re

url = 'https://scriptpulse-app.streamlit.app/debug_app'
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode('utf-8', errors='ignore')
        print("Status", r.status)
        traces = re.findall(r'(?i)(ModuleNotFoundError|ImportError|SyntaxError|Fatal).*?\n', body)
        if traces:
             print("\n".join(traces))
        else:
             print("No trace found...")
except Exception as e:
     print("Request failed:", e)
