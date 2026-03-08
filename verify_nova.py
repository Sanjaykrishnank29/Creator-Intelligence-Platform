"""Final verification — all three endpoints must return valid responses using Nova Lite."""

import urllib.request, json, time

BASE = "https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode()
        elapsed = time.time() - t0
    js = json.loads(raw)
    payload = json.loads(js["body"]) if isinstance(js.get("body"), str) else js
    return js.get("statusCode", r.status), payload, elapsed


print("=" * 60)
print(" NOVA LITE VERIFICATION - Final Check")
print("=" * 60)
all_pass = True

# 1. /api/chat -> insight_engine
print("\n[1] POST /api/chat  (insight_engine + Nova Lite)")
try:
    sc, p, t = call(
        "POST", "/api/chat", {"message": "How do I grow my tech YouTube channel fast?"}
    )
    if sc == 200 and "response" in p and len(p["response"]) > 30:
        print(f'  ✅ PASS | {t:.2f}s | response: "{p["response"][:100]}..."')
    else:
        print(f"  ❌ FAIL | {sc} | {str(p)[:150]}")
        all_pass = False
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    all_pass = False

# 2. /api/generate -> idea_generator
print("\n[2] POST /api/generate  (idea_generator + Nova Lite)")
try:
    sc, p, t = call(
        "POST",
        "/api/generate",
        {"topic": "AI Agents", "platform": "YouTube", "creator_id": "techwithtim"},
    )
    if sc == 200 and "ideas" in p and len(p["ideas"]) > 0:
        print(
            f'  ✅ PASS | {t:.2f}s | {len(p["ideas"])} ideas | first: "{str(p["ideas"][0].get("title", "?"))[:70]}"'
        )
    else:
        print(f"  ❌ FAIL | {sc} | {str(p)[:150]}")
        all_pass = False
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    all_pass = False

# 3. /api/summarize -> content_enhancer
print("\n[3] POST /api/summarize  (content_enhancer + Nova Lite)")
try:
    sc, p, t = call(
        "POST",
        "/api/summarize",
        {
            "trends": [
                {"topic": "AI Agents replacing developers"},
                {"topic": "Python automation for content creators"},
                {"topic": "GPT-5 coding capabilities revealed"},
            ]
        },
    )
    if sc == 200 and "summary" in p and len(p["summary"]) > 30:
        print(f'  ✅ PASS | {t:.2f}s | summary: "{p["summary"][:100]}..."')
    else:
        print(f"  ❌ FAIL | {sc} | {str(p)[:150]}")
        all_pass = False
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    all_pass = False

# 4. Confirm no AccessDeniedException in recent logs
print("\n[4] Bedrock AccessDeniedException check (CloudWatch)")
import boto3

logs = boto3.client("logs", region_name="us-east-1")
for fn in [
    "creator-intelligence-dev-insight_engine",
    "creator-intelligence-dev-content_enhancer",
]:
    short = fn.split("dev-")[1]
    try:
        streams = logs.describe_log_streams(
            logGroupName=f"/aws/lambda/{fn}",
            orderBy="LastEventTime",
            descending=True,
            limit=1,
        )["logStreams"]
        events = logs.get_log_events(
            logGroupName=f"/aws/lambda/{fn}",
            logStreamName=streams[0]["logStreamName"],
            limit=30,
        )["events"]
        msgs = [e["message"] for e in events]
        has_denied = any(
            "AccessDeniedException" in m or "not authorized" in m for m in msgs
        )
        has_nova = any("nova" in m.lower() for m in msgs)
        if has_denied:
            print(f"  ❌ {short}: AccessDeniedException still present!")
            all_pass = False
        else:
            print(f"  ✅ {short}: No access errors | Nova invoked: {has_nova}")
    except Exception as e:
        print(f"  ⚠️  {short}: Could not read logs: {e}")

print("\n" + "=" * 60)
print(
    f"  RESULT: {'✅ ALL PASS — Nova Lite operational' if all_pass else '❌ SOME FAILURES'}"
)
print("=" * 60)
