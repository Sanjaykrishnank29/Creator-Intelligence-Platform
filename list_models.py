import boto3
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"


def list_bedrock_models():
    try:
        bedrock = boto3.client(
            "bedrock",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION,
        )
        response = bedrock.list_foundation_models()
        print("Available Models (Filtering for Claude 3.5):")
        for model in response["modelSummaries"]:
            if "claude-3-5" in model["modelId"].lower():
                print(
                    f"- {model['modelId']} (Status: {model.get('modelLifecycle', {}).get('status', 'Unknown')})"
                )
    except Exception as e:
        print(f"Error listing models: {e}")


if __name__ == "__main__":
    list_bedrock_models()
