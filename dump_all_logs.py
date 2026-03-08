import boto3
import json

logs = boto3.client("logs", region_name="us-east-1")


def dump_all(name):
    print(f"\n--- {name} ---")
    log_group = f"/aws/lambda/{name}"
    try:
        # Get last 5 streams to be sure
        streams = logs.describe_log_streams(
            logGroupName=log_group, orderBy="LastEventTime", descending=True, limit=5
        ).get("logStreams", [])
        for s in streams:
            print(f"Stream: {s['logStreamName']}")
            events = logs.get_log_events(
                logGroupName=log_group, logStreamName=s["logStreamName"], limit=50
            ).get("events", [])
            for e in events:
                print(e["message"].strip())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    dump_all("creator-intelligence-dev-insight_engine")
    dump_all("creator-intelligence-dev-idea_generator")
