import urllib.request
import json

base_url = "https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod/api"

print("=========================================")
print("🚀 TESTING POST /api/generate")
print("=========================================")
url = f"{base_url}/generate"
payload = {"topic": "AI agents", "platform": "youtube"}
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    url, data=data, headers={"Content-Type": "application/json"}, method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"✅ Status Code: {response.status}")
        response_body = response.read().decode("utf-8")
        parsed = json.loads(response_body)
        print(json.dumps(parsed, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, "read"):
        print(e.read().decode("utf-8"))

print("\n=========================================")
print("🚀 TESTING GET /api/profile")
print("=========================================")
url = f"{base_url}/profile"
req = urllib.request.Request(
    url, headers={"Content-Type": "application/json"}, method="GET"
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"✅ Status Code: {response.status}")
        response_body = response.read().decode("utf-8")
        parsed = json.loads(response_body)
        print(json.dumps(parsed, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")
    if hasattr(e, "read"):
        print(e.read().decode("utf-8"))
