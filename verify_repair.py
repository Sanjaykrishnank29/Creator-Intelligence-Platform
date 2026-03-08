import boto3
import json
import hashlib

client = boto3.client("lambda", region_name="us-east-1")


def test_lambda(name, payload):
    print(f"\n--- Testing {name} ---")
    try:
        res = client.invoke(
            FunctionName=f"creator-intelligence-dev-{name}",
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": json.dumps(payload)}),
        )
        resp = json.loads(res["Payload"].read().decode("utf-8"))
        status = resp.get("statusCode")
        body = json.loads(resp.get("body", "{}"))
        print(f"Status: {status}")

        # Pretty print a bit of the body
        body_str = json.dumps(body, indent=2)
        print(f"Body snippet:\n{body_str[:500]}...")
        return status, body
    except Exception as e:
        print(f"Error: {e}")
        return None, None


if __name__ == "__main__":
    # 1. Test Assistant (Sonnet)
    print("Testing Task 1: Creator Assistant...")
    test_lambda(
        "insight_engine", {"message": "What are the best hooks for tech videos?"}
    )

    # 2. Test Summarization (Nova Lite)
    print("\nTesting Task 4: News Summarization...")
    test_lambda(
        "content_enhancer",
        {"trends": [{"topic": "OpenAI Sora updates"}, {"topic": "TikTok ban news"}]},
    )

    # 3. Test Idea Generation (Sonnet + Titan + Semantic Matching)
    print("\nTesting Task 2 & 3: Semantic Idea Generation...")
    # This requires TrendSignals and CreatorContent to have data.
    # Let's hope there's some, otherwise it will use the fallback niche-only prompt.
    test_lambda(
        "idea_generator",
        {"creator_id": "youtube_main_channel", "niche": "AI and Coding"},
    )
