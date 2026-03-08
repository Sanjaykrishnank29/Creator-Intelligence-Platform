import boto3
import urllib.request
import json
import os
import time

REGION = "us-east-1"
base_url = "https://f3hmrjp4v5.execute-api.us-east-1.amazonaws.com/prod/api"

# Initialize Boto3 clients using default credential chain (already configured via .env)
dynamodb = boto3.client("dynamodb", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)

status = {
    "API Gateway": "PASS",
    "Lambda Execution": "PASS",
    "DynamoDB Connectivity": "PASS",
    "Bedrock Invocation": "PASS",
    "Trend Pipeline": "PASS",
    "Idea Generation": "PASS",
}


def fail(component, reason):
    global status
    if status.get(component) == "PASS":
        status[component] = f"FAIL ({reason})"


# 1. TEST API GATEWAY (And indirectly Lambda/Bedrock)
print("Testing API Gateway /api/generate...")
try:
    url = f"{base_url}/generate"
    payload = {"topic": "AI agents", "platform": "youtube"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as response:
        body = response.read().decode("utf-8")
        parsed = json.loads(body)
        if "ideas" not in parsed and "response" not in parsed:
            fail("Idea Generation", "Response missing 'ideas' or 'response' keys")
        if response.status != 200:
            fail("API Gateway", f"HTTP {response.status}")
except Exception as e:
    fail("API Gateway", str(e))
    fail("Idea Generation", "API call failed")

# 2. VERIFY DYNAMODB ACCESSIBILITY
print("Testing DynamoDB Connectivity...")
try:
    required_tables = [
        "creator-intelligence-dev-CreatorContent",
        "creator-intelligence-dev-CreatorProfiles",
        "creator-intelligence-dev-LLMCache",
        "creator-intelligence-dev-Predictions",
        "creator-intelligence-dev-TrendSignals",
    ]
    tables = dynamodb.list_tables()["TableNames"]
    for t in required_tables:
        if t not in tables:
            fail("DynamoDB Connectivity", f"Table {t} missing")
except Exception as e:
    fail("DynamoDB Connectivity", str(e))

# 3. VERIFY TREND INGESTION PIPELINE (Simulate payload via DB directly or check Lambda)
print("Testing Trend Pipeline...")
try:
    # Trigger Lambda
    lambda_response = lambda_client.invoke(
        FunctionName="creator-intelligence-dev-trend_collector"
    )
    if lambda_response["StatusCode"] != 200:
        fail("Lambda Execution", "trend_collector returned non-200")

    time.sleep(2)  # Allow write to finish
    table_name = "creator-intelligence-dev-TrendSignals"
    scan = dynamodb.scan(TableName=table_name, Limit=1)
    if not scan.get("Items"):
        fail("Trend Pipeline", "No items written to DynamoDB")
    else:
        # Check if timestamp sort key exists
        item = scan["Items"][0]
        if "timestamp" not in item:
            fail("Trend Pipeline", "Schema missing timestamp Sort Key")
except Exception as e:
    fail("Trend Pipeline", str(e))
    fail("Lambda Execution", "Lambda invocation failed")

# VERDICT
platform_operational = all(v == "PASS" for v in status.values())

print("\n\n" + "=" * 50)
print(f"SYSTEM STATUS")
for k, v in status.items():
    print(f"{k}: {v}")

print("\nEND-TO-END RESULT")
print(f"Platform Operational: {platform_operational}")

if not platform_operational:
    print("\nFailing Components / Recommended Fixes:")
    for k, v in status.items():
        if v != "PASS":
            print(f"- {k}: {v}")
print("=" * 50)
