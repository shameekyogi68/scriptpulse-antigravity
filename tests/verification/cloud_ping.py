import urllib.request
import json
try:
    req = urllib.request.Request('https://scriptpulse-app.streamlit.app/_stcore/health')
    with urllib.request.urlopen(req, timeout=15) as response:
        print(f"Health API Code: {response.status}")
        print(response.read().decode('utf-8'))
except Exception as e:
    print("Health Request failed:", e)

try:
    req = urllib.request.Request('https://scriptpulse-app.streamlit.app/main')
    with urllib.request.urlopen(req, timeout=15) as response:
        print(f"Main App Code: {response.status}")
except Exception as e:
    print("/main Request failed:", e)
