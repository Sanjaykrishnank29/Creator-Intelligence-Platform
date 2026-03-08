import urllib.request, json

url = "https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod/api/generate"
data = json.dumps(
    {"topic": "cooking tips", "platform": "TikTok", "creator_id": "techwithtim"}
).encode()
req = urllib.request.Request(
    url, data=data, headers={"Content-Type": "application/json"}, method="POST"
)
try:
    with urllib.request.urlopen(req) as r:
        raw = r.read().decode()
    js = json.loads(raw)
    payload = json.loads(js["body"]) if isinstance(js.get("body"), str) else js
    print("HTTP 200")
    if "ideas" in payload:
        for i, idx in enumerate(payload["ideas"]):
            print(f"{i + 1}. {idx.get('title')}")
            print(f"   {idx.get('explanation')}")
    else:
        print("No ideas array found:", str(payload)[:200])
except Exception as e:
    print("Error:", e)
