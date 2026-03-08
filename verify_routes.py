import boto3, json

# Test 1: Direct Lambda invocation of insight_engine
lmb = boto3.client("lambda", region_name="us-east-1")
print("--- Direct insight_engine invocation ---")
r = lmb.invoke(
    FunctionName="creator-intelligence-dev-insight_engine",
    Payload=json.dumps(
        {
            "httpMethod": "POST",
            "path": "/api/chat",
            "body": json.dumps({"message": "Give me a tip for tech YouTube"}),
        }
    ),
)
body_raw = r["Payload"].read().decode()
body = json.loads(body_raw)
print("Status:", body.get("statusCode"))
inner = json.loads(body.get("body", "{}"))
print("Has response key:", "response" in inner)
print("Preview:", str(inner)[:300])

# Test 2: Check actual API Gateway integration
print("\n--- API Gateway integration for /api/chat ---")
apigw = boto3.client("apigateway", region_name="us-east-1")
api_id = "f3hmrjp4v5"
resources = apigw.get_resources(restApiId=api_id, limit=100)["items"]
for r in resources:
    path = r.get("path", "")
    if path in ["/api/chat", "/api/summarize", "/api/generate"]:
        methods = r.get("resourceMethods", {})
        for method in methods:
            if method == "OPTIONS":
                continue
            try:
                integ = apigw.get_integration(
                    restApiId=api_id, resourceId=r["id"], httpMethod=method
                )
                uri = integ.get("uri", "")
                fn = (
                    uri.split(":function:")[1].split("/")[0]
                    if ":function:" in uri
                    else "(unknown)"
                )
                print(f"  {method} {path} -> {fn}")
            except Exception as e:
                print(f"  {method} {path} -> ERROR: {e}")
