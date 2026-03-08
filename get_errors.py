import boto3
import time

logs_client = boto3.client("logs", region_name="us-east-1")


def get_recent_errors(function_name):
    print(f"\n--- Recent ERRORs for {function_name} ---")
    log_group = f"/aws/lambda/{function_name}"
    try:
        response = logs_client.filter_log_events(
            logGroupName=log_group, filterPattern="ERROR", limit=5, interleaved=True
        )
        for event in response["events"]:
            ts = time.ctime(event["timestamp"] / 1000)
            print(f"[{ts}] {event['message'].strip()}")
    except Exception as e:
        print(f"Error fetching logs for {function_name}: {e}")


if __name__ == "__main__":
    get_recent_errors("creator-intelligence-dev-insight_engine")
    get_recent_errors("creator-intelligence-dev-idea_generator")
    get_recent_errors("creator-intelligence-dev-content_enhancer")
