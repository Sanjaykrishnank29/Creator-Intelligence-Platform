import boto3
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"
PROJECT = "creator-intelligence"
ENV = "dev"
BUCKET = f"{PROJECT}-{ENV}-datasets"


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def get_account_id():
    return get_client("sts").get_caller_identity()["Account"]


def setup_sagemaker():
    s3 = get_client("s3")
    sm = get_client("sagemaker")
    account_id = get_account_id()
    role_arn = f"arn:aws:iam::{account_id}:role/{PROJECT}-{ENV}-lambda-execution-role"

    model_artifact = "sm_model/model.tar.gz"
    s3_key = "models/model.tar.gz"

    # 1. Upload Model to S3
    print(f"Uploading model to s3://{BUCKET}/{s3_key}...")
    s3.upload_file(model_artifact, BUCKET, s3_key)

    model_name = f"{PROJECT}-{ENV}-xgboost-model"
    container = f"683313684715.dkr.ecr.{REGION}.amazonaws.com/sagemaker-xgboost:1.7-1"  # Public XGBoost image

    # 2. Create Model
    print(f"Creating SageMaker Model: {model_name}...")
    try:
        sm.create_model(
            ModelName=model_name,
            PrimaryContainer={
                "Image": container,
                "ModelDataUrl": f"s3://{BUCKET}/{s3_key}",
            },
            ExecutionRoleArn=role_arn,
        )
    except sm.exceptions.ClientError:
        print("ℹ️ Model already exists.")

    # 3. Create Endpoint Config
    config_name = f"{PROJECT}-{ENV}-serverless-config"
    print(f"Creating Endpoint Config: {config_name}...")
    try:
        sm.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    "VariantName": "AllTraffic",
                    "ModelName": model_name,
                    "ServerlessConfig": {"MemorySizeInMB": 2048, "MaxConcurrency": 10},
                }
            ],
        )
    except sm.exceptions.ClientError:
        print("ℹ️ Config already exists.")

    # 4. Create Endpoint
    ep_name = f"{PROJECT}-{ENV}-serverless-endpoint"
    print(f"Creating Endpoint: {ep_name}...")
    try:
        sm.create_endpoint(EndpointName=ep_name, EndpointConfigName=config_name)
        print(f"✅ Endpoint {ep_name} creation initiated.")
    except sm.exceptions.ClientError:
        print("ℹ️ Endpoint already exists.")


if __name__ == "__main__":
    setup_sagemaker()
