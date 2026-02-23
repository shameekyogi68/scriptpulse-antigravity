import urllib.request
import re

url = 'https://scriptpulse-app.streamlit.app/'
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode('utf-8', errors='ignore')
        
        # Streamlit logs the exception in window.streamlitDebug
        debug_json = re.search(r'window\.streamlitDebug\s*=\s*({.*?});', body, re.DOTALL)
        if debug_json:
            print("Found Streamlit Debug JSON:")
            print(debug_json.group(1)[:1500])
        else:
            print("No internal debug JSON. Search for trace:")
            traces = re.findall(r'(?i)(ModuleNotFoundError|ImportError|SyntaxError).*?\n', body)
            if traces:
                 print("\n".join(traces))
            else:
                 print("No trace found. Length of response:", len(body))
                 print("First 200 chars:", body[:200])
except Exception as e:
    print("Failed to fetch:", e)
