import boto3
import json

client = boto3.client("lambda", region_name="us-east-1")


def test_lambda(name, payload):
    print(f"\n--- Testing {name} ---")
    try:
        res = client.invoke(FunctionName=name, Payload=json.dumps(payload))
        status = res["StatusCode"]
        body = json.loads(res["Payload"].read().decode("utf-8"))
        print(f"Status: {status}")
        print(f"Body: {json.dumps(body, indent=2)}")
        return body
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # 1. Test Insight Engine (Profile)
    test_lambda(
        "creator-intelligence-dev-insight_engine",
        {"path": "/profile", "httpMethod": "GET"},
    )

    # 2. Test Insight Engine (Strategist Chat)
    test_lambda(
        "creator-intelligence-dev-insight_engine",
        {"body": json.dumps({"message": "Tell me about my audience."})},
    )

    # 3. Test Idea Generator
    test_lambda(
        "creator-intelligence-dev-idea_generator",
        {"body": json.dumps({"niche": "coding", "platform": "YouTube"})},
    )

    # 4. Test Prediction API (Should return 503 with our new message)
    test_lambda(
        "creator-intelligence-dev-prediction_api",
        {
            "body": json.dumps(
                {
                    "creator_id": "techwithtim",
                    "engagement_ratio": 0.1,
                    "title_length": 45,
                    "trend_velocity": 0.8,
                    "sentiment_score": 0.9,
                }
            )
        },
    )
