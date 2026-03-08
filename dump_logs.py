import boto3
import time

logs_client = boto3.client("logs", region_name="us-east-1")


def dump_logs(function_name):
    print(f"\n===== LOGS FOR {function_name} =====")
    log_group = f"/aws/lambda/{function_name}"
    try:
        streams = logs_client.describe_log_streams(
            logGroupName=log_group, orderBy="LastEventTime", descending=True, limit=2
        )
        if not streams.get("logStreams"):
            print("No streams found.")
            return

        for s in streams["logStreams"]:
            print(f"\nStream: {s['logStreamName']}")
            events = logs_client.get_log_events(
                logGroupName=log_group, logStreamName=s["logStreamName"], limit=50
            )
            for e in events["events"]:
                print(e["message"].strip())
    except Exception as ex:
        print(f"Error: {ex}")


if __name__ == "__main__":
    dump_logs("creator-intelligence-dev-insight_engine")
    dump_logs("creator-intelligence-dev-idea_generator")
