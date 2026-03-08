import boto3
import os
import json
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"  # Common region for Bedrock


def test_aws_connectivity():
    print("--- Testing AWS Connectivity ---")
    try:
        sts = boto3.client(
            "sts",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )
        identity = sts.get_caller_identity()
        print(f"SUCCESS: Connected as {identity['Arn']}")
        return True
    except Exception as e:
        print(f"FAILED: STS connection error: {e}")
        return False


def test_bedrock_access():
    print("\n--- Testing Amazon Bedrock Access ---")
    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )

        # Test a simple invocation with Claude 3.5 Sonnet
        model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Confirm you are working. Just say 'Bedrock is active'.",
                    }
                ],
            }
        )

        response = bedrock.invoke_model(modelId=model_id, body=body)

        response_body = json.loads(response.get("body").read())
        print(f"SUCCESS: Bedrock responded: {response_body['content'][0]['text']}")
        return True
    except Exception as e:
        print(f"FAILED: Bedrock access error: {e}")
        print(
            "Tip: Ensure you have 'Anthropic Claude 3.5 Sonnet' enabled in Bedrock Model Access."
        )
        return False


if __name__ == "__main__":
    if test_aws_connectivity():
        test_bedrock_access()
