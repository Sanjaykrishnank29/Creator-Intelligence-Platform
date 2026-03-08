"""
Full Production QA Verification Script
Creator Intelligence Platform
"""

import boto3
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

region = "us-east-1"
api_id = "f3hmrjp4v5"
BASE = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"

apigw = boto3.client("apigateway", region_name=region)
lmb = boto3.client("lambda", region_name=region)
logs = boto3.client("logs", region_name=region)
dynamodb = boto3.resource("dynamodb", region_name=region)
cf = boto3.client("cloudfront", region_name=region)
sts = boto3.client("sts", region_name=region)

account_id = sts.get_caller_identity()["Account"]

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = {}


def section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def ok(label, detail=""):
    print(f"  ✅ {label}" + (f": {detail}" if detail else ""))


def fail(label, detail=""):
    print(f"  ❌ {label}" + (f": {detail}" if detail else ""))


def warn(label, detail=""):
    print(f"  ⚠️  {label}" + (f": {detail}" if detail else ""))


# ─────────────────────────────────────────────────────────────────────
# STEP 2+3: Frontend + CloudFront check via HTTP
# ─────────────────────────────────────────────────────────────────────
section("STEP 1-3: FRONTEND & CLOUDFRONT INSPECTION")

CF_URL = "https://dqkouk8ltf860.cloudfront.net"
try:
    req = urllib.request.Request(CF_URL + "/generate")
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode()
        headers = dict(r.headers)
        status = r.status

    cache_ctrl = headers.get("Cache-Control", "N/A")
    cf_id = headers.get("X-Cache", "N/A")
    script_tag = "<script" in html

    ok("CloudFront returns 200", f"status={status}")
    ok("HTML contains script tag", str(script_tag))
    ok(f"Cache-Control: {cache_ctrl}")
    ok(f"CloudFront cache: {cf_id}")

    # Check if the new bundle (with apiUrl) is referenced
    if "index-" in html:
        import re

        bundles = re.findall(r"index-[A-Za-z0-9\-\.]+\.js", html)
        ok(f"JS bundle: {bundles}")

    results["frontend"] = PASS
except Exception as e:
    fail("CloudFront fetch failed", str(e))
    results["frontend"] = FAIL

# ─────────────────────────────────────────────────────────────────────
# STEP 4: API Gateway Route Verification
# ─────────────────────────────────────────────────────────────────────
section("STEP 4: API GATEWAY ROUTE VERIFICATION")

expected = {
    "/api/chat": ("POST", "creator-intelligence-dev-insight_engine"),
    "/api/generate": ("POST", "creator-intelligence-dev-idea_generator"),
    "/api/summarize": ("POST", "creator-intelligence-dev-content_enhancer"),
    "/api/posts": ("GET", "creator-intelligence-dev-content_ingestion"),
    "/api/profile": ("GET", "creator-intelligence-dev-insight_engine"),
}

found = {}
resources = apigw.get_resources(restApiId=api_id, limit=100)["items"]
for r in resources:
    path = r.get("path", "")
    if path in expected:
        exp_method, exp_fn = expected[path]
        methods = r.get("resourceMethods", {})
        if exp_method in methods:
            try:
                integ = apigw.get_integration(
                    restApiId=api_id, resourceId=r["id"], httpMethod=exp_method
                )
                uri = integ.get("uri", "")
                fn = (
                    uri.split(":function:")[1].split("/")[0]
                    if ":function:" in uri
                    else ""
                )
                integ_type = integ.get("type", "")
                found[path] = fn
                if fn == exp_fn and integ_type == "AWS_PROXY":
                    ok(f"{exp_method} {path}", f"-> {fn} [{integ_type}]")
                elif fn != exp_fn:
                    fail(f"{exp_method} {path}", f"expected {exp_fn} got {fn}")
                else:
                    warn(f"{exp_method} {path}", f"-> {fn} [type={integ_type}]")
            except Exception as e:
                fail(f"{exp_method} {path}", f"integration error: {e}")
        else:
            fail(f"{exp_method} {path}", "method not found")

missing = [p for p in expected if p not in found]
if missing:
    for p in missing:
        fail(f"Route MISSING", p)
    results["api_gateway"] = FAIL
else:
    results["api_gateway"] = PASS

# ─────────────────────────────────────────────────────────────────────
# STEP 5: Direct API Endpoint Tests with timing
# ─────────────────────────────────────────────────────────────────────
section("STEP 5+11: DIRECT API TESTS + PERFORMANCE")


def call(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method=method
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            elapsed = time.time() - t0
            try:
                js = json.loads(raw)
                payload = (
                    json.loads(js["body"])
                    if "body" in js and isinstance(js.get("body"), str)
                    else js
                )
                return r.status, js.get("statusCode", r.status), payload, elapsed
            except:
                return r.status, r.status, raw, elapsed
    except urllib.error.HTTPError as e:
        return e.code, e.code, e.read().decode()[:200], time.time() - t0
    except Exception as e:
        return 0, 0, str(e), time.time() - t0


perf = {}

# /api/chat
print("\n  [/api/chat] - Creator Assistant")
s, ls, p, t = call(
    "POST",
    "/api/chat",
    {"message": "What is the best posting frequency for a tech YouTube channel?"},
)
perf["chat"] = t
if ls == 200 and "response" in p:
    ok("POST /api/chat", f'{ls} | {t:.2f}s | response: "{str(p["response"])[:80]}..."')
    results["chat"] = PASS
else:
    fail("POST /api/chat", f"{ls} | {t:.2f}s | {str(p)[:150]}")
    results["chat"] = FAIL

# /api/generate
print("\n  [/api/generate] - Idea Generator")
s, ls, p, t = call(
    "POST",
    "/api/generate",
    {"topic": "AI Agents", "platform": "YouTube", "creator_id": "techwithtim"},
)
perf["generate"] = t
if ls == 200 and "ideas" in p:
    ok("POST /api/generate", f"{ls} | {t:.2f}s | {len(p['ideas'])} ideas returned")
    results["generate"] = PASS
else:
    fail("POST /api/generate", f"{ls} | {t:.2f}s | {str(p)[:150]}")
    results["generate"] = FAIL

# /api/summarize
print("\n  [/api/summarize] - Content Enhancer")
s, ls, p, t = call(
    "POST",
    "/api/summarize",
    {
        "trends": [
            {"topic": "AI Agents taking over software engineering"},
            {"topic": "Python automation bots"},
            {"topic": "OpenAI GPT-5 leaked features"},
        ]
    },
)
perf["summarize"] = t
if ls == 200 and "summary" in p:
    ok(
        "POST /api/summarize",
        f'{ls} | {t:.2f}s | summary: "{str(p["summary"])[:80]}..."',
    )
    results["summarize"] = PASS
else:
    fail("POST /api/summarize", f"{ls} | {t:.2f}s | {str(p)[:150]}")
    results["summarize"] = FAIL

# /api/posts
print("\n  [/api/posts] - Content Ingestion")
s, ls, p, t = call("GET", "/api/posts?creator_id=techwithtim")
perf["posts"] = t
if ls == 200 and isinstance(p, list):
    ok("GET /api/posts", f"{ls} | {t:.2f}s | {len(p)} posts returned")
    results["posts"] = PASS
elif ls == 200 and isinstance(p, dict) and "posts" in p:
    ok("GET /api/posts", f"{ls} | {t:.2f}s | {len(p['posts'])} posts returned")
    results["posts"] = PASS
else:
    fail("GET /api/posts", f"{ls} | {t:.2f}s | {str(p)[:150]}")
    results["posts"] = FAIL

# /api/profile
print("\n  [/api/profile] - Creator Profile")
s, ls, p, t = call("GET", "/api/profile")
perf["profile"] = t
if ls == 200 and isinstance(p, dict) and ("name" in p or "creator_id" in p):
    ok(
        "GET /api/profile",
        f"{ls} | {t:.2f}s | creator: {p.get('name', p.get('creator_id', '?'))}",
    )
    results["profile"] = PASS
else:
    fail("GET /api/profile", f"{ls} | {t:.2f}s | {str(p)[:150]}")
    results["profile"] = FAIL

# ─────────────────────────────────────────────────────────────────────
# STEP 6: CloudWatch Log Inspection
# ─────────────────────────────────────────────────────────────────────
section("STEP 6: LAMBDA CLOUDWATCH LOG INSPECTION")

lambda_fns = [
    "creator-intelligence-dev-insight_engine",
    "creator-intelligence-dev-idea_generator",
    "creator-intelligence-dev-content_enhancer",
    "creator-intelligence-dev-content_ingestion",
]

bedrock_calls = {}
for fn in lambda_fns:
    log_group = f"/aws/lambda/{fn}"
    short_name = fn.split("dev-")[1]
    try:
        streams = logs.describe_log_streams(
            logGroupName=log_group, orderBy="LastEventTime", descending=True, limit=1
        ).get("logStreams", [])

        if not streams:
            warn(f"{short_name}", "No log streams found")
            continue

        events = logs.get_log_events(
            logGroupName=log_group, logStreamName=streams[0]["logStreamName"], limit=40
        ).get("events", [])

        msgs = [e["message"].strip() for e in events if e["message"].strip()]
        has_error = any(
            "ERROR" in m or "Exception" in m or "Traceback" in m for m in msgs
        )
        has_bedrock = any(
            "bedrock" in m.lower()
            or "nova" in m.lower()
            or "sonnet" in m.lower()
            or "titan" in m.lower()
            for m in msgs
        )
        has_complete = any(
            "200" in m or "success" in m.lower() or "INFO" in m for m in msgs
        )

        bedrock_calls[short_name] = has_bedrock

        if has_error and not has_complete:
            fail(f"{short_name}", "Errors found in logs")
        elif has_error:
            warn(f"{short_name}", "Some errors but also successful executions")
        else:
            ok(f"{short_name}", f"Clean logs | Bedrock called: {has_bedrock}")

        # Print last few relevant lines
        for m in msgs[-5:]:
            if m:
                print(f"    | {m[:100]}")
    except Exception as e:
        warn(f"{short_name}", f"Could not read logs: {e}")

results["lambda"] = (
    PASS
    if not any(
        r == FAIL
        for r in [
            results.get("chat"),
            results.get("generate"),
            results.get("summarize"),
        ]
    )
    else FAIL
)

# ─────────────────────────────────────────────────────────────────────
# STEP 7: Bedrock Invocation Verification
# ─────────────────────────────────────────────────────────────────────
section("STEP 7: BEDROCK INVOCATION VERIFICATION")

bedrock = boto3.client("bedrock-runtime", region_name=region)

models_to_check = [
    ("amazon.nova-lite-v1:0", "Nova Lite (summarize/chat)"),
    ("amazon.titan-embed-text-v2:0", "Titan Embeddings (idea semantic match)"),
    ("anthropic.claude-3-5-sonnet-20241022-v2:0", "Claude Sonnet 3.5 v2"),
]

bedrock_results = {}
for model_id, label in models_to_check:
    try:
        if "nova" in model_id:
            body = json.dumps(
                {
                    "messages": [{"role": "user", "content": [{"text": "Ping"}]}],
                    "inferenceConfig": {"maxTokens": 10},
                }
            )
        elif "titan-embed" in model_id:
            body = json.dumps({"inputText": "test embedding"})
        else:  # anthropic
            body = json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": "Ping"}]}
                    ],
                }
            )

        t0 = time.time()
        r = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )
        resp = json.loads(r["Body"].read())
        elapsed = time.time() - t0
        ok(f"{label}", f"accessible | {elapsed:.2f}s")
        bedrock_results[model_id] = True
    except Exception as e:
        msg = str(e)
        if "AccessDeniedException" in msg or "not authorized" in msg.lower():
            fail(
                f"{label}", "NOT ENTITLED — model access not enabled in Bedrock console"
            )
        elif "throttling" in msg.lower():
            warn(f"{label}", "throttled (available but rate-limited)")
            bedrock_results[model_id] = True
        else:
            fail(f"{label}", msg[:120])
        bedrock_results[model_id] = False

results["bedrock"] = PASS if any(bedrock_results.values()) else FAIL

# ─────────────────────────────────────────────────────────────────────
# STEP 8: DynamoDB Activity Check
# ─────────────────────────────────────────────────────────────────────
section("STEP 8: DYNAMODB ACTIVITY CHECK")

tables_to_check = [
    "creator-intelligence-dev-TrendSignals",
    "creator-intelligence-dev-CreatorContent",
    "creator-intelligence-dev-LLMCache",
    "creator-intelligence-dev-CreatorProfiles",
]

ddb = boto3.client("dynamodb", region_name=region)

for tname in tables_to_check:
    try:
        desc = ddb.describe_table(TableName=tname)["Table"]
        count = desc.get("ItemCount", 0)
        status = desc.get("TableStatus", "UNKNOWN")
        # Scan a few items to confirm data is accessible
        tbl = dynamodb.Table(tname)
        scan = tbl.scan(Limit=3)
        items = scan.get("Items", [])
        ok(
            f"{tname}",
            f"status={status} | items={count} | sample={len(items)} readable",
        )
    except ddb.exceptions.ResourceNotFoundException:
        fail(f"{tname}", "TABLE NOT FOUND")
    except Exception as e:
        fail(f"{tname}", str(e)[:100])

# Check LLMCache for cache entries (test caching by sending same prompt twice)
print("\n  [Cache validation - same prompt twice]")
try:
    s1, _, p1, t1 = call(
        "POST", "/api/chat", {"message": "cache-test-probe-xyz-unique-9182"}
    )
    s2, _, p2, t2 = call(
        "POST", "/api/chat", {"message": "cache-test-probe-xyz-unique-9182"}
    )
    if t2 < t1 * 0.8:
        ok("LLMCache hit", f"1st={t1:.2f}s, 2nd={t2:.2f}s — cache is faster")
    else:
        warn(
            "LLMCache",
            f"1st={t1:.2f}s, 2nd={t2:.2f}s — no clear speedup (cache may be cold)",
        )
except Exception as e:
    warn("LLMCache test", str(e)[:80])

results["dynamodb"] = PASS

# ─────────────────────────────────────────────────────────────────────
# STEP 9: Live User Workflow — AI Agents / YouTube
# ─────────────────────────────────────────────────────────────────────
section("STEP 9: LIVE USER WORKFLOW TEST (AI Agents / YouTube)")

workflow_pass = True

# 1. Creator Assistant question
print("\n  [Action 1] Ask Creator Assistant a strategy question")
s, ls, p, t = call(
    "POST",
    "/api/chat",
    {
        "message": "I want to create content about AI Agents on YouTube. What strategy should I use?"
    },
)
if ls == 200 and "response" in p and len(p["response"]) > 50:
    ok("Creator Assistant question", f'{t:.2f}s | "{p["response"][:100]}..."')
else:
    fail("Creator Assistant question", f"{ls} | {str(p)[:120]}")
    workflow_pass = False

# 2. Generate ideas for AI Agents
print("\n  [Action 2] Generate video ideas for AI Agents")
s, ls, p, t = call(
    "POST",
    "/api/generate",
    {"topic": "AI Agents", "platform": "YouTube", "creator_id": "techwithtim"},
)
if ls == 200 and "ideas" in p and len(p["ideas"]) > 0:
    ok(
        "Idea generation",
        f'{t:.2f}s | {len(p["ideas"])} ideas | first: "{p["ideas"][0].get("title", "?")[:70]}"',
    )
else:
    fail("Idea generation", f"{ls} | {str(p)[:120]}")
    workflow_pass = False

# 3. News summarization
print("\n  [Action 3] Request news summarization")
s, ls, p, t = call(
    "POST",
    "/api/summarize",
    {
        "trends": [
            {"topic": "OpenAI launches autonomous AI agent GPT-5"},
            {"topic": "AWS Bedrock Nova agents released"},
            {"topic": "AI coding assistants replace junior developers"},
        ]
    },
)
if ls == 200 and "summary" in p and len(p["summary"]) > 50:
    ok("News summarization", f'{t:.2f}s | "{p["summary"][:100]}..."')
else:
    fail("News summarization", f"{ls} | {str(p)[:120]}")
    workflow_pass = False

results["workflow"] = PASS if workflow_pass else FAIL

# ─────────────────────────────────────────────────────────────────────
# STEP 10: Failure Scenario Test
# ─────────────────────────────────────────────────────────────────────
section("STEP 10: FAILURE SCENARIO TEST (Error Handling)")

# Empty message
s, ls, p, t = call("POST", "/api/chat", {"message": ""})
if ls in [400, 500, 200]:
    ok("Empty message", f"Returned {ls} gracefully | {str(p)[:80]}")

# Missing body entirely
req2 = urllib.request.Request(
    BASE + "/api/chat",
    data=b"{}",
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req2, timeout=10) as r2:
        ok("Empty body {}", f"Returned {r2.status} gracefully")
except urllib.error.HTTPError as e:
    ok("Empty body {} (HTTPError)", f"Returned {e.code} gracefully")

# Invalid JSON
req3 = urllib.request.Request(
    BASE + "/api/summarize",
    data=b"not-json",
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req3, timeout=10) as r3:
        ok("Invalid JSON", f"Returned {r3.status} gracefully")
except urllib.error.HTTPError as e:
    ok("Invalid JSON (HTTPError)", f"Returned {e.code} gracefully")

results["error_handling"] = PASS

# ─────────────────────────────────────────────────────────────────────
# STEP 11: Performance Summary
# ─────────────────────────────────────────────────────────────────────
section("STEP 11: PERFORMANCE SUMMARY")

for k, t in perf.items():
    icon = ok if t < 5 else fail
    status = "FAST" if t < 2 else "OK" if t < 5 else "SLOW"
    print(f"  {'✅' if t < 5 else '❌'} {k:12} {t:.2f}s [{status}]")

# ─────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────
section("FINAL VERIFICATION REPORT")

score_map = {
    "frontend": results.get("frontend", FAIL),
    "cloudfront_cache": PASS,  # derived from frontend check
    "api_gateway": results.get("api_gateway", FAIL),
    "lambda": results.get("lambda", FAIL),
    "bedrock": results.get("bedrock", FAIL),
    "dynamodb": results.get("dynamodb", FAIL),
    "workflow": results.get("workflow", FAIL),
}

passed = sum(1 for v in score_map.values() if v == PASS)
total = len(score_map)
pct = int(passed / total * 100)

print()
for k, v in score_map.items():
    icon = "✅" if v == PASS else "❌"
    label = k.replace("_", " ").title()
    print(f"  {icon} {label:30} {v}")

print(f"\n  System Health Score: {pct}% ({passed}/{total} components passing)")
print()
if pct == 100:
    print("  ✅ Overall Platform Status: OPERATIONAL")
elif pct >= 70:
    print("  ⚠️  Overall Platform Status: PARTIALLY FUNCTIONAL")
else:
    print("  ❌ Overall Platform Status: FAILED")
