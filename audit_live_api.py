"""
Full audit of the live API Gateway endpoints to discover all errors.
"""

import urllib.request
import json
import urllib.error

BASE = "https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod"

PASS = "✅"
FAIL = "❌"


def post(path, body):
    url = BASE + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            status = r.status
            try:
                js = json.loads(raw)
                # unwrap lambda envelope
                if isinstance(js, dict) and "body" in js:
                    payload = json.loads(js["body"])
                    return status, js.get("statusCode", status), payload
                return status, status, js
            except:
                return status, status, raw
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return e.code, e.code, body
    except Exception as e:
        return 0, 0, str(e)


def get(path, params=""):
    url = BASE + path + ("?" + params if params else "")
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
            status = r.status
            try:
                js = json.loads(raw)
                if isinstance(js, dict) and "body" in js:
                    payload = json.loads(js["body"])
                    return status, js.get("statusCode", status), payload
                return status, status, js
            except:
                return status, status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.code, e.read().decode()
    except Exception as e:
        return 0, 0, str(e)


results = []


def check(name, http_status, lambda_status, payload, success_key=None):
    ok = lambda_status == 200 and (success_key is None or success_key in str(payload))
    icon = PASS if ok else FAIL
    results.append((icon, name, lambda_status, payload))
    preview = str(payload)[:200]
    print(f"{icon} [{lambda_status}] {name}")
    print(f"        {preview}")
    print()


print("=" * 70)
print(" LIVE API GATEWAY - FULL AUDIT")
print(f" Base: {BASE}")
print("=" * 70)

# 1. Chat (insight_engine)
print("\n--- TEST 1: Creator Assistant Chat (/api/chat) ---")
s, ls, p = post("/api/chat", {"message": "Give me a tip for tech YouTube"})
check("POST /api/chat", s, ls, p, "response")

# 2. Generate ideas (idea_generator)
print("\n--- TEST 2: Idea Generator (/api/generate) ---")
s, ls, p = post(
    "/api/generate",
    {"topic": "Python programming", "platform": "YouTube", "creator_id": "techwithtim"},
)
check("POST /api/generate", s, ls, p, "ideas")

# 3. Summarize (content_enhancer)
print("\n--- TEST 3: Content Summarize (/api/summarize) ---")
s, ls, p = post(
    "/api/summarize",
    {
        "trends": [
            {"topic": "Python automation 2025"},
            {"topic": "AI coding tools"},
            {"topic": "System design interviews"},
        ]
    },
)
check("POST /api/summarize  [trends format]", s, ls, p, "summary")

# 4. GET /api/posts (content_ingestion)
print("\n--- TEST 4: Posts History (/api/posts) ---")
s, ls, p = get("/api/posts", "creator_id=techwithtim")
check("GET /api/posts", s, ls, p)

# 5. GET /api/profile (insight_engine)
print("\n--- TEST 5: Creator Profile (/api/profile) ---")
s, ls, p = get("/api/profile")
check("GET /api/profile", s, ls, p)

# 6. Predict (prediction_api)
print("\n--- TEST 6: Predict (/api/predict) ---")
s, ls, p = post(
    "/api/predict",
    {
        "creator_id": "techwithtim",
        "engagement_ratio": 0.1,
        "title_length": 45,
        "trend_velocity": 0.8,
        "sentiment_score": 0.9,
    },
)
check("POST /api/predict", s, ls, p)

# Summary
print("\n" + "=" * 70)
print(" SUMMARY")
print("=" * 70)
passed = sum(1 for r in results if r[0] == PASS)
print(f"  {passed}/{len(results)} endpoints passing")
for r in results:
    print(f"  {r[0]} {r[1]}: {r[2]}")
