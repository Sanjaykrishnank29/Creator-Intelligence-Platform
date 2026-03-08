import boto3
import os
import zipfile
import io
import json
import time
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"
PROJECT = "creator-intelligence"
ENV = "dev"
ROLE_NAME = f"{PROJECT}-{ENV}-lambda-execution-role"


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def get_account_id():
    sts = get_client("sts")
    return sts.get_caller_identity()["Account"]


def create_zip(lambda_dir, common_dir):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add lambda files
        for root, _, files in os.walk(lambda_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, lambda_dir)
                zf.write(full_path, rel_path)

        # Add common files
        if common_dir:
            for root, _, files in os.walk(common_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.join(
                        "lambdas", "common", os.path.relpath(full_path, common_dir)
                    )
                    zf.write(full_path, rel_path)

    buf.seek(0)
    return buf.read()


def deploy_lambdas():
    l_client = get_client("lambda")
    account_id = get_account_id()
    role_arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"

    packages = [
        {"name": "idea_generator", "handler": "main.lambda_handler"},
        {"name": "prediction_api", "handler": "main.lambda_handler"},
        {"name": "insight_engine", "handler": "main.lambda_handler"},
        {"name": "content_enhancer", "handler": "main.lambda_handler"},
        {"name": "content_ingestion", "handler": "main.lambda_handler"},
        {"name": "trend_collector", "handler": "main.lambda_handler"},
        {"name": "feedback_ingest", "handler": "main.lambda_handler"},
    ]

    common_dir = os.path.abspath("lambdas/common")

    for pkg in packages:
        fn_name = f"{PROJECT}-{ENV}-{pkg['name']}"
        lambda_dir = os.path.abspath(f"lambdas/{pkg['name']}")

        print(f"Packaging {fn_name}...")
        zip_content = create_zip(lambda_dir, common_dir)

        try:
            print(f"Deploying {fn_name}...")
            l_client.create_function(
                FunctionName=fn_name,
                Runtime="python3.11",
                Role=role_arn,
                Handler=pkg["handler"],
                Code={"ZipFile": zip_content},
                Timeout=30,
                MemorySize=256,
                Environment={
                    "Variables": {
                        "TRENDS_TABLE": f"{PROJECT}-{ENV}-TrendSignals",
                        "CONTENT_TABLE": f"{PROJECT}-{ENV}-CreatorContent",
                        "CACHE_TABLE": f"{PROJECT}-{ENV}-LLMCache",
                        "PREDICTIONS_TABLE": f"{PROJECT}-{ENV}-Predictions",
                        "PROFILES_TABLE": f"{PROJECT}-{ENV}-CreatorProfiles",
                        "DATASET_BUCKET": f"{PROJECT}-{ENV}-datasets",
                        "SAGEMAKER_ENDPOINT_NAME": f"{PROJECT}-{ENV}-serverless-endpoint",
                        "FEEDBACK_STREAM": f"{PROJECT}-{ENV}-FeedbackStream",
                        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),
                        "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID", ""),
                    }
                },
            )
            print(f"✅ Lambda {fn_name} created.")
        except l_client.exceptions.ResourceConflictException:
            print(f"Updating code for {fn_name}...")
            l_client.update_function_code(FunctionName=fn_name, ZipFile=zip_content)
            print("Waiting for code update to stabilize...")
            time.sleep(5)
            print(f"Updating config for {fn_name}...")
            l_client.update_function_configuration(
                FunctionName=fn_name,
                Environment={
                    "Variables": {
                        "TRENDS_TABLE": f"{PROJECT}-{ENV}-TrendSignals",
                        "CONTENT_TABLE": f"{PROJECT}-{ENV}-CreatorContent",
                        "CACHE_TABLE": f"{PROJECT}-{ENV}-LLMCache",
                        "PREDICTIONS_TABLE": f"{PROJECT}-{ENV}-Predictions",
                        "PROFILES_TABLE": f"{PROJECT}-{ENV}-CreatorProfiles",
                        "DATASET_BUCKET": f"{PROJECT}-{ENV}-datasets",
                        "SAGEMAKER_ENDPOINT_NAME": f"{PROJECT}-{ENV}-serverless-endpoint",
                        "FEEDBACK_STREAM": f"{PROJECT}-{ENV}-FeedbackStream",
                        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),
                        "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID", ""),
                    }
                },
            )
            print(f"✅ Lambda {fn_name} updated.")
        except Exception as e:
            print(f"❌ Error deploying {fn_name}: {e}")


if __name__ == "__main__":
    deploy_lambdas()
