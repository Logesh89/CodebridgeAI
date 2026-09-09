import requests

try:
    res = requests.get("https://codebridgeai.vercel.app/api/v1/health")
    print("HEALTH STATUS:", res.status_code)
    print("HEALTH BODY:", res.text[:500])
except Exception as e:
    print("HEALTH ERR:", e)

try:
    res2 = requests.post(
        "https://codebridgeai.vercel.app/api/v1/auth/google",
        json={"email": "udayrise7666@gmail.com"}
    )
    print("GOOGLE STATUS:", res2.status_code)
    print("GOOGLE BODY:", res2.text[:500])
except Exception as e:
    print("GOOGLE ERR:", e)
