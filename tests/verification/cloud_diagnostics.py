import subprocess
import urllib.request
import re

url = "https://scriptpulse-app.streamlit.app/~/+"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode('utf-8', errors='ignore')
        
        # Searching for the hidden JSON payload that Streamlit sometimes injects
        debug_trace = re.search(r'streamlitDebug\s*=\s*(.*?);', body, re.DOTALL)
        if debug_trace:
             print("FOUND STREAMLIT DEBUG TRACE:")
             print(debug_trace.group(1)[:2000])
        else:
             print("No hidden debug trace in HTML. Checking raw exception signatures...")
             errors = re.findall(r'(?i)(Exception|Traceback|Error).*?\n', body)
             print(errors if errors else "No visible errors.")
             print("HTML Length:", len(body))
except Exception as e:
    print("Fetch Failed:", e)
