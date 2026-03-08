import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def audit_resources():
    print(f"--- Auditing AWS Resources in {REGION} ---")

    # Check IAM Account
    try:
        sts = get_client("sts")
        identity = sts.get_caller_identity()
        print(f"IAM Identity: {identity['Arn']}")
    except Exception as e:
        print(f"IAM Error: {e}")

    # 1. DynamoDB Tables
    try:
        ddb = get_client("dynamodb")
        tables = ddb.list_tables()["TableNames"]
        print(f"DynamoDB Tables ({len(tables)}): {tables}")
    except Exception as e:
        print(f"DynamoDB Error: {e}")

    # 2. S3 Buckets
    try:
        s3 = get_client("s3")
        buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
        print(f"S3 Buckets: {buckets}")
    except Exception as e:
        print(f"S3 Error: {e}")

    # 3. Lambda Functions
    try:
        l_client = get_client("lambda")
        functions = [f["FunctionName"] for f in l_client.list_functions()["Functions"]]
        print(f"Lambda Functions: {functions}")
    except Exception as e:
        print(f"Lambda Error: {e}")

    # 4. API Gateway
    try:
        apigw = get_client("apigateway")
        apis = [a["name"] for a in apigw.get_rest_apis()["items"]]
        print(f"API Gateways: {apis}")
    except Exception as e:
        print(f"APIGW Error: {e}")


if __name__ == "__main__":
    audit_resources()
