"""Test the local AWS proxy server endpoints."""

import urllib.request
import json
import time

BASE = "http://localhost:8000"


def post(path, data):
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return r.status, json.loads(body)
    except Exception as e:
        return 0, {"error": str(e)}


def get(path):
    req = urllib.request.Request(BASE + path)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode()
            return r.status, json.loads(body)
    except Exception as e:
        return 0, {"error": str(e)}


print("=" * 60)
print(" CREATOR INTELLIGENCE PLATFORM - SERVER VERIFICATION")
print("=" * 60)

# 1. Health
print("\n[1] Health Check")
s, d = get("/api/health")
print(f"    Status: {s} | {d}")

# 2. Creator Assistant Chat
print("\n[2] Creator Assistant - POST /api/chat")
s, d = post(
    "/api/chat", {"message": "Give me one tip for growing a tech YouTube channel"}
)
print(f"    Status: {s}")
if d.get("response"):
    print(f"    Response: {d['response'][:200]}...")
else:
    print(f"    Data: {json.dumps(d)[:300]}")

# 3. Summary Node
print("\n[3] Summary Node - POST /api/summarize")
s, d = post(
    "/api/summarize",
    {
        "contents": [
            "Python programming tips for beginners",
            "How machine learning is changing software development",
            "Top coding interview questions to practice",
        ]
    },
)
print(f"    Status: {s}")
if d.get("summary"):
    print(f"    Summary: {d['summary'][:200]}...")
else:
    print(f"    Data: {json.dumps(d)[:300]}")

# 4. Profile
print("\n[4] Creator Profile - GET /api/profile")
s, d = get("/api/profile")
print(f"    Status: {s} | Keys: {list(d.keys()) if isinstance(d, dict) else d}")

print("\n" + "=" * 60)
