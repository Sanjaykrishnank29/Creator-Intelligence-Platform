"""
Diagnostic script: Fetches the most recent log events from the failing Lambdas
and directly invokes each one to capture the error trace.
"""

import boto3
import json
import time

logs = boto3.client("logs", region_name="us-east-1")
lambda_client = boto3.client("lambda", region_name="us-east-1")

TARGETS = [
    "creator-intelligence-dev-insight_engine",
    "creator-intelligence-dev-content_enhancer",
]


def get_recent_logs(fn_name, max_events=30):
    log_group = f"/aws/lambda/{fn_name}"
    print(f"\n======== LOGS: {fn_name} ========")
    try:
        streams = logs.describe_log_streams(
            logGroupName=log_group, orderBy="LastEventTime", descending=True, limit=3
        ).get("logStreams", [])

        for s in streams[:2]:
            events = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=s["logStreamName"],
                limit=max_events,
            ).get("events", [])
            for e in events:
                msg = e["message"].strip()
                if msg:
                    print(msg)
    except Exception as e:
        print(f"ERROR reading logs: {e}")


def invoke_and_print(fn_name, payload):
    print(f"\n======== INVOKE: {fn_name} ========")
    try:
        res = lambda_client.invoke(
            FunctionName=fn_name, Payload=json.dumps(payload), LogType="Tail"
        )
        status = res["StatusCode"]
        body_raw = res["Payload"].read().decode("utf-8")
        body = json.loads(body_raw)
        print(f"HTTP Status: {status}")
        print(f"Response Body: {json.dumps(body, indent=2)}")
        # Print tail logs
        import base64

        if "LogResult" in res:
            tail = base64.b64decode(res["LogResult"]).decode("utf-8")
            print(f"\nFunction Tail Logs:\n{tail}")
    except Exception as e:
        print(f"ERROR invoking lambda: {e}")


if __name__ == "__main__":
    # 1. Invoke each Lambda and capture output
    invoke_and_print(
        "creator-intelligence-dev-insight_engine",
        {"body": json.dumps({"message": "hi, give me a tip"})},
    )

    invoke_and_print(
        "creator-intelligence-dev-content_enhancer",
        {
            "body": json.dumps(
                {
                    "trends": [
                        {"topic": "AI coding assistants 2025"},
                        {"topic": "Python automation bots"},
                        {"topic": "Machine learning for beginners"},
                    ]
                }
            )
        },
    )

    # 2. Then show CloudWatch logs for additional context
    for t in TARGETS:
        get_recent_logs(t)
