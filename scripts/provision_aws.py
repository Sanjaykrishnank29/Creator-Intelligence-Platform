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


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def create_dynamodb_tables():
    dynamodb = get_client("dynamodb")
    tables = [
        {
            "TableName": f"{PROJECT}-{ENV}-CreatorProfiles",
            "KeySchema": [{"AttributeName": "creator_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "creator_id", "AttributeType": "S"}
            ],
        },
        {
            "TableName": f"{PROJECT}-{ENV}-CreatorContent",
            "KeySchema": [
                {"AttributeName": "creator_id", "KeyType": "HASH"},
                {"AttributeName": "content_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "creator_id", "AttributeType": "S"},
                {"AttributeName": "content_id", "AttributeType": "S"},
                {"AttributeName": "topic", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "TopicIndex",
                    "KeySchema": [
                        {"AttributeName": "topic", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        {
            "TableName": f"{PROJECT}-{ENV}-Predictions",
            "KeySchema": [
                {"AttributeName": "creator_id", "KeyType": "HASH"},
                {"AttributeName": "prediction_id", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "creator_id", "AttributeType": "S"},
                {"AttributeName": "prediction_id", "AttributeType": "S"},
                {"AttributeName": "content_id", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "content_index",
                    "KeySchema": [
                        {"AttributeName": "content_id", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        {
            "TableName": f"{PROJECT}-{ENV}-TrendSignals",
            "KeySchema": [
                {"AttributeName": "topic", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "topic", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
        },
        {
            "TableName": f"{PROJECT}-{ENV}-LLMCache",
            "KeySchema": [{"AttributeName": "input_hash", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "input_hash", "AttributeType": "S"}
            ],
        },
    ]

    for table_config in tables:
        name = table_config["TableName"]
        try:
            print(f"Creating table {name}...")
            params = {
                "TableName": name,
                "KeySchema": table_config["KeySchema"],
                "AttributeDefinitions": table_config["AttributeDefinitions"],
                "BillingMode": "PAY_PER_REQUEST",
            }
            if "GlobalSecondaryIndexes" in table_config:
                params["GlobalSecondaryIndexes"] = table_config[
                    "GlobalSecondaryIndexes"
                ]

            dynamodb.create_table(**params)
            print(f"✅ Table {name} creation initiated.")
        except dynamodb.exceptions.ResourceInUseException:
            print(f"ℹ️ Table {name} already exists.")
        except Exception as e:
            print(f"❌ Error creating table {name}: {e}")


def create_s3_buckets():
    s3 = get_client("s3")
    buckets = [f"{PROJECT}-{ENV}-static-website", f"{PROJECT}-{ENV}-datasets"]

    for bucket in buckets:
        try:
            print(f"Creating bucket {bucket}...")
            if REGION == "us-east-1":
                s3.create_bucket(Bucket=bucket)
            else:
                s3.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={"LocationConstraint": REGION},
                )
            print(f"✅ Bucket {bucket} created.")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"ℹ️ Bucket {bucket} already owned by you.")
        except s3.exceptions.BucketAlreadyExists:
            print(f"ℹ️ Bucket {bucket} already exists globally.")
        except Exception as e:
            print(f"❌ Error creating bucket {bucket}: {e}")


def create_lambda_roles():
    iam = get_client("iam")
    role_name = f"{PROJECT}-{ENV}-lambda-execution-role"

    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    try:
        print(f"Creating IAM role {role_name}...")
        role = iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        print(f"✅ Role {role_name} created.")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️ Role {role_name} already exists.")

    # Attach Basic Execution Role
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    # Attach Full Access for Hackathon (Least privilege later)
    iam.attach_role_policy(
        RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    )
    iam.attach_role_policy(
        RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
    )
    iam.attach_role_policy(
        RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    )
    print(f"✅ Policies attached to {role_name}.")


if __name__ == "__main__":
    create_dynamodb_tables()
    create_s3_buckets()
    create_lambda_roles()
