import urllib.request
import ast
req = urllib.request.Request('https://raw.githubusercontent.com/shameekyogi68/scriptpulse-antigravity/main/scriptpulse/agents/structure_agent.py')
try:
    with urllib.request.urlopen(req) as res:
        source = res.read().decode('utf-8')
        try:
            ast.parse(source)
            print("StructureAgent Syntax OK on cloud!")
        except Exception as e:
            print("Syntax Error Found in Cloud File:")
            print(e)
except Exception as e:
    print("Fetch failed", e)
