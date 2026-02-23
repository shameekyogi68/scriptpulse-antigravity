import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://scriptpulse-app.streamlit.app/~/+')
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print("Status", response.status)
except Exception as e:
    print("Error:", e)
