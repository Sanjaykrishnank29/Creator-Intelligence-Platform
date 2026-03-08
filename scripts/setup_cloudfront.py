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


def setup_cloudfront():
    cf = get_client("cloudfront")
    s3_bucket_domain = (
        f"{PROJECT}-{ENV}-static-website.s3-website-{REGION}.amazonaws.com"
    )
    # Note: For S3 Website endpoints, we use a Custom Origin, not S3 Origin

    api_id = "f3hmrjp4v5"  # From previous step
    api_domain = f"{api_id}.execute-api.{REGION}.amazonaws.com"

    dist_config = {
        "CallerReference": str(time.time()),
        "Aliases": {"Quantity": 0},
        "DefaultRootObject": "index.html",
        "Origins": {
            "Quantity": 2,
            "Items": [
                {
                    "Id": "S3-Website",
                    "DomainName": s3_bucket_domain,
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "http-only",
                    },
                },
                {
                    "Id": "APIGateway",
                    "DomainName": api_domain,
                    "OriginPath": "/prod",  # API Gateway stage
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "https-only",
                    },
                },
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "S3-Website",
            "ForwardedValues": {"QueryString": False, "Cookies": {"Forward": "none"}},
            "TrustedSigners": {"Enabled": False, "Quantity": 0},
            "ViewerProtocolPolicy": "redirect-to-https",
            "MinTTL": 0,
        },
        "CacheBehaviors": {
            "Quantity": 1,
            "Items": [
                {
                    "PathPattern": "/api/*",
                    "TargetOriginId": "APIGateway",
                    "ForwardedValues": {
                        "QueryString": True,
                        "Cookies": {"Forward": "all"},
                        "Headers": {"Quantity": 1, "Items": ["Authorization"]},
                    },
                    "TrustedSigners": {"Enabled": False, "Quantity": 0},
                    "ViewerProtocolPolicy": "https-only",
                    "MinTTL": 0,
                    "AllowedMethods": {
                        "Quantity": 7,
                        "Items": [
                            "GET",
                            "HEAD",
                            "POST",
                            "PUT",
                            "PATCH",
                            "OPTIONS",
                            "DELETE",
                        ],
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    },
                }
            ],
        },
        "CustomErrorResponses": {
            "Quantity": 2,
            "Items": [
                {
                    "ErrorCode": 404,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 10,
                },
                {
                    "ErrorCode": 403,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 10,
                },
            ],
        },
        "Comment": f"{PROJECT} {ENV} Distribution",
        "Enabled": True,
    }

    try:
        # Check if distribution already exists
        dists = cf.list_distributions()
        dist_id = None
        if "Items" in dists.get("DistributionList", {}):
            for d in dists["DistributionList"]["Items"]:
                if d["Comment"] == f"{PROJECT} {ENV} Distribution":
                    dist_id = d["Id"]
                    break

        if dist_id:
            print(f"Updating existing CloudFront Distribution: {dist_id}...")
            config = cf.get_distribution_config(Id=dist_id)
            etag = config["ETag"]
            # Update config with new changes
            new_config = config["DistributionConfig"]
            new_config["CustomErrorResponses"] = dist_config["CustomErrorResponses"]

            response = cf.update_distribution(
                Id=dist_id, IfMatch=etag, DistributionConfig=new_config
            )
            print(f"✅ Distribution updated: {response['Distribution']['DomainName']}")
        else:
            print("Creating CloudFront Distribution (this can take 5-10 mins)...")
            response = cf.create_distribution(DistributionConfig=dist_config)
            print(f"✅ Distribution created: {response['Distribution']['DomainName']}")

        print(f"Status: {response['Distribution']['Status']}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    setup_cloudfront()
