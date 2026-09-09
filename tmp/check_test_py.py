import requests
r = requests.get("https://codebridgeai.vercel.app/api/test")
print("TEST.PY STATUS:", r.status_code)
print("TEST.PY BODY:", r.text)
