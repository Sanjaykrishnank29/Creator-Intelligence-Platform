import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"


def test_haiku():
    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )

        # Test with Claude 3 Haiku
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Confirm you are working. Just say 'Haiku is active'.",
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
        return False


if __name__ == "__main__":
    test_haiku()
